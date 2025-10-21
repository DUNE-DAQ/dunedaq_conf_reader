from dataclasses import dataclass, Field, fields
import json
from pathlib import Path
import logging
from dunedaq_conf_reader.oks_utils import find_session, get, get_applications, get_one_object, find_key_value

detector_types = ['CRP', 'APA']

leak_dict = {
    0: 500,
    1: 100,
}

@dataclass
class DUNEDAQConfDataExtractor:
    oks_file_path: Path
    session_name:str
    load_json:bool = False

    # WIB settings
    adc_test_pattern     : dict[str,bool] = None
    cold                 : dict[str,bool] = None
    detector_type        : dict[str,int ] = None
    pulser               : dict[str,bool] = None
    pulse_dac            : dict[str,int ] = None

    # FEMB settings
    ac_couple            : dict[str,bool] = None
    baseline             : dict[str,int ] = None
    buffering            : dict[str,int ] = None
    enabled              : dict[str,bool] = None
    gain                 : dict[str,int ] = None
    gain_match           : dict[str,bool] = None
    leak                 : dict[str,int ] = None
    leak_10x             : dict[str,bool] = None
    leak_f               : dict[str,float] = None # calculated from the above 2
    peak_time            : dict[str,int ] = None
    strobe_delay         : dict[str,int ] = None
    strobe_length        : dict[str,int ] = None
    strobe_skip          : dict[str,int ] = None
    test_cap             : dict[str,bool] = None

    # Run settings
    offline_data_stream  : str = None
    op_env               : str = None
    tpg_channel_map      : str = None

    def __post_init__(self):
        if self.oks_file_path == None or self.session_name == None:
            return

        # WIB settings
        self.adc_test_pattern = {}
        self.cold             = {}
        self.detector_type    = {}
        self.pulser           = {}
        self.pulse_dac        = {}

        # FEMB settings
        self.ac_couple        = {}
        self.baseline         = {}
        self.buffering        = {}
        self.enabled          = {}
        self.gain             = {}
        self.gain_match       = {}
        self.leak             = {}
        self.leak_10x         = {}
        self.leak_f           = {} # calculated from the above 2
        self.peak_time        = {}
        self.pulse_period     = {}
        self.strobe_delay     = {}
        self.strobe_length    = {}
        self.strobe_skip      = {}
        self.test_cap         = {}

        #detector settings
        self.offline_data_stream = ''
        self.op_env              = ''
        self.tpg_channel_map     = ''

        if self.load_json: 
            conf_data = self.oks_file_path
        else:
            conf_data = {}
            with open(self.oks_file_path) as f:
                conf_data = json.load(f)

        session = find_session(conf_data, self.session_name)
        #print(f'----session name {self.session_name} found the following session: {session}')
        logging.debug(f'{session=}')
        wiec_applications = get_applications(
            conf_data,
            session,
            application_class_name="WIECApplication"
        )
        logging.info(f'Found {len(wiec_applications)} WIEC applications')

        detector_config = get_one_object(
                conf_data,
                class_name="DetectorConfig")

        self.offline_data_stream = find_key_value(detector_config, "offline_data_stream")
        self.op_env              = find_key_value(detector_config, "op_env")
        self.tpg_channel_map     = find_key_value(detector_config, "tpg_channel_map")

        for wiec_application in wiec_applications:
            wib = wiec_application['__name'].split("@")[0].upper()

            logging.info(f'Processing WIEC application: \'{wib}\'')

            wib_module_conf = get(conf_data, wiec_application, "wib_module_conf")
            wib_settings = get(conf_data, wib_module_conf, "settings")

            self.pulser[wib] = get(conf_data, wib_settings, "pulser")
            logging.info(f'  - \'pulser\': {self.pulser[wib]}')

            wib_pulser_setting = get(conf_data, wib_settings, "wib_pulser")
            self.pulse_dac[wib] = get(conf_data, wib_pulser_setting, "pulse_dac")
            logging.info(f'  - \'pulse_dac\': {self.pulse_dac[wib]}')

            self.adc_test_pattern[wib] = get(conf_data, wib_settings, "adc_test_pattern")
            logging.info(f'  - \'adc_test_pattern\': {self.adc_test_pattern[wib]}')

            self.cold[wib] = get(conf_data, wib_settings, "cold")
            logging.info(f'  - \'cold\': {self.cold[wib]}')

            self.detector_type[wib] = get(conf_data, wib_settings, "detector_type")
            logging.info(f'  - \'detector_type\': {self.detector_type[wib]}')

            fembs = {
                (wib, i): get(conf_data, wib_settings, f"femb{i}")
                for i in range(4)
            }

            self.extract_femb_variables(conf_data, self.ac_couple    , "ac_couple"    , fembs)
            self.extract_femb_variables(conf_data, self.baseline     , "baseline"     , fembs)
            self.extract_femb_variables(conf_data, self.buffering    , "buffering"    , fembs)
            self.extract_femb_variables(conf_data, self.enabled      , "enabled"      , fembs)
            self.extract_femb_variables(conf_data, self.gain         , "gain"         , fembs)
            self.extract_femb_variables(conf_data, self.gain_match   , "gain_match"   , fembs)
            self.extract_femb_variables(conf_data, self.leak_10x     , "leak_10x"     , fembs)
            self.extract_femb_variables(conf_data, self.leak         , "leak"         , fembs)

            for key, value in self.leak.items():
                if wib != key[0]:
                    continue
                self.leak_f[key] = leak_dict[value] * (10 if self.leak_10x[key] else 1)
                logging.info(f'  - \'leak_f\' ({key}): {self.leak_f[key]}')

            self.extract_femb_variables(conf_data, self.peak_time    , "peak_time"    , fembs)
            self.extract_femb_variables(conf_data, self.strobe_delay , "strobe_delay" , fembs)
            self.extract_femb_variables(conf_data, self.strobe_length, "strobe_length", fembs)
            self.extract_femb_variables(conf_data, self.strobe_skip  , "strobe_skip"  , fembs)
            self.extract_femb_variables(conf_data, self.test_cap     , "test_cap"     , fembs)


    def extract_femb_variables(self, conf_data, field_to_fill, name, fembs):
        for key, conf in fembs.items():
            field_to_fill[key] = get(conf_data, conf, name)
            logging.info(f'  - \'{name}\' (FEMB {key[1]}): {field_to_fill[key]}')
