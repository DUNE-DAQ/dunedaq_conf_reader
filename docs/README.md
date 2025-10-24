# A python-native reader for the DUNE-DAQ OKS data

This repo makes the information inside the "OKS jsonified" available to the offline. These are found in the run registry.

This repo installs 2 executables, that can be installed without the DAQ:
- `dunedaq-conf-downloader` to retrieve configurations from the run registry,
- `dunedaq-conf-reader` to parse the jsonified OKS and display "interesting" variables in the configuration.

## Installation
```bash
$ git clone https://github.com/plasorak/offline_conf_reader.git
$ cd offline_conf_reader
$ python -m venv venv
$ source venv/bin/activate
(venv) $ pip install .
```

And next time you log on:
```bash
$ cd offline_conf_reader/
$ source venv/bin/activate
```

If you don't have `~/.drunc.json`, `dunedaq-conf-downloader` will not work. Get it from DAQ people.

## Python usage
 - Import the `DUNEDAQConfDataExtractor`,
 - Create an instance of that class, with the path of the file you are reading, and the `Session` identifier.

```python
from dunedaq_conf_reader.dunedaq_conf_data_extractor import DUNEDAQConfDataExtractor
cde = DUNEDAQConfDataExtractor("path/to/file.data.json", "session_name")
```

You can now access (some of) the  variables:
 - `buffer`: Not accessible
 - `ac_couple`: `dict[str,bool]`
 - `pulse_dac`: Not accessible
 - `pulser`: `dict[str,bool]`
 - `baseline`: `dict[str,int]`
 - `gain`: `dict[str,int]`
 - `leak`: Not accessible
 - `leak_10x`: `dict[str,bool]`
 - `peak_time`: `dict[str,int]`
 - `enable_femb_fake_data`: Not accessible
 - `test_cap`: `dict[str,bool]`
 - `APAs`: `list[int]`
 - `FEMBs`: Not accessible
 - `pulse_period`: `dict[str,int]`
 - `phase_group`: Not accessible
 - `phases`: Not accessible
 - `offline_data_stream`: str
 - `op_env`: str
 - `tpg_channel_map`: str

```python
>> print(cde.baseline)
>> {'crp4-wiec_femb0': 2, 'crp4-wiec_femb1': 2, 'crp4-wiec_femb2': 2, 'crp4-wiec_femb3': 2, 'crp5-wiec_femb0': 2, 'crp5-wiec_femb1': 2, 'crp5-wiec_femb2': 2, 'crp5-wiec_femb3': 2}
```

## Bash usage
After `pip install`'ing above, you can do:
```bash
dunedaq-conf-downloader show-last-n-run-metadata 10
# Displaying the metadata for the last 10 runs
#                                                          Run Metadata
# ┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Run Number ┃ Start time                    ┃ Stop time                     ┃ Detector ID   ┃ Run type ┃ Software version    ┃
# ┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
# │ 36600      │ Tue, 20 May 2025 14:46:24 GMT │ Tue, 20 May 2025 14:48:03 GMT │ np02-detector │ TEST     │ fddaq-v5.3.1-a9-1   │
# │ 36599      │ Tue, 20 May 2025 14:25:30 GMT │ Tue, 20 May 2025 14:26:29 GMT │ np02-detector │ TEST     │ fddaq-v5.3.1-a9-1   │
# │ 36598      │ Tue, 20 May 2025 12:27:53 GMT │ None                          │ np02-detector │ TEST     │ fddaq-v5.3.2-rc1-a9 │
# │ 36597      │ Tue, 20 May 2025 12:27:39 GMT │ None                          │ np02-detector │ TEST     │ fddaq-v5.3.1-a9-1   │
# │ 36596      │ Tue, 20 May 2025 12:20:52 GMT │ Tue, 20 May 2025 12:22:38 GMT │ np02-detector │ TEST     │ fddaq-v5.3.1-a9-1   │
# │ 36595      │ Tue, 20 May 2025 12:16:30 GMT │ None                          │ np02-detector │ TEST     │ fddaq-v5.3.2-rc1-a9 │
# │ 36594      │ Tue, 20 May 2025 12:04:41 GMT │ Tue, 20 May 2025 12:09:59 GMT │ np02-detector │ TEST     │ fddaq-v5.3.2-rc1-a9 │
# │ 36593      │ Tue, 20 May 2025 10:05:37 GMT │ None                          │ np02-detector │ TEST     │ fddaq-v5.3.2-rc1-a9 │
# │ 36592      │ Tue, 20 May 2025 09:29:40 GMT │ Tue, 20 May 2025 10:01:43 GMT │ np02-detector │ TEST     │ fddaq-v5.3.2-rc1-a9 │
# │ 36591      │ Tue, 20 May 2025 09:24:09 GMT │ Tue, 20 May 2025 09:48:16 GMT │ np02-detector │ TEST     │ fddaq-v5.3.1-a9-1   │
# └────────────┴───────────────────────────────┴───────────────────────────────┴───────────────┴──────────┴─────────────────────┘

### then
dunedaq-conf-downloader download-run-conf 36598
# Downloading configuration for run 36598
# Configuration for run 36598 downloaded in run_36598, to show the configuration, use:
# dunedaq-conf-reader run_36598/tmpyonzimsb.data.json np02-session

### or
dunedaq-conf-downloader download-last-n-run-conf 10
# Downloading the last 10 run configurations
# Downloading configuration for run 36600
# Configuration for run 36600 downloaded in run_36600, to show the configuration, use:
# dunedaq-conf-reader run_36600/tmpqly2pyg9.data.json np02-session
# Downloading configuration for run 36599
# Configuration for run 36599 downloaded in run_36599, to show the configuration, use:
# dunedaq-conf-reader run_36599/tmpcrem2c33.data.json np02-session
# Downloading configuration for run 36598
# Configuration for run 36598 downloaded in run_36598, to show the configuration, use:
# dunedaq-conf-reader run_36598/tmpyonzimsb.data.json np02-session
# Downloading configuration for run 36597
# Configuration for run 36597 downloaded in run_36597, to show the configuration, use:
# dunedaq-conf-reader run_36597/tmpgt3i6dnk.data.json np02-session
# Downloading configuration for run 36596
# Configuration for run 36596 downloaded in run_36596, to show the configuration, use:
# dunedaq-conf-reader run_36596/tmpmmhr4obw.data.json np02-session
# Downloading configuration for run 36595
# Configuration for run 36595 downloaded in run_36595, to show the configuration, use:
# dunedaq-conf-reader run_36595/tmpxecfkfpz.data.json np02-session
# Downloading configuration for run 36594
# Configuration for run 36594 downloaded in run_36594, to show the configuration, use:
# dunedaq-conf-reader run_36594/tmpih8qifn0.data.json np02-session
# Downloading configuration for run 36593
# Configuration for run 36593 downloaded in run_36593, to show the configuration, use:
# dunedaq-conf-reader run_36593/tmp2pvsudxg.data.json np02-session
# Downloading configuration for run 36592
# Configuration for run 36592 downloaded in run_36592, to show the configuration, use:
# dunedaq-conf-reader run_36592/tmp99y9s66j.data.json np02-session
# Downloading configuration for run 36591
# Configuration for run 36591 downloaded in run_36591, to show the configuration, use:
# dunedaq-conf-reader run_36591/tmppfm01eo_.data.json np02-session
```

After which, as advertised, you can do:
```bash
dunedaq-conf-reader /path/to/file.data.json session_name variable0_name variable1_name...
```

For example:
```bash
dunedaq-conf-reader run_36599/tmpcrem2c33.data.json np02-session cold strobe_delay
# cold CRP4-WIEC: False
# cold CRP5-WIEC: False
# strobe_delay CRP4-WIEC FEMB0: 255
# strobe_delay CRP4-WIEC FEMB1: 255
# strobe_delay CRP4-WIEC FEMB2: 255
# strobe_delay CRP4-WIEC FEMB3: 255
# strobe_delay CRP5-WIEC FEMB0: 255
# strobe_delay CRP5-WIEC FEMB1: 255
# strobe_delay CRP5-WIEC FEMB2: 255
# strobe_delay CRP5-WIEC FEMB3: 255
```

## Developper
... Please run `pytest` everytime you make a modification and make sure it passes!
