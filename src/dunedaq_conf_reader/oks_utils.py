from copy import deepcopy
import logging
from re import match

class OKSValueError(Exception):
    pass

def find_key_value(d, target_key):
    if not isinstance(d, dict):
        raise TypeError("Expected a dictionary as input")

    for key in d:
        if key == target_key:
            return d[key]
    return None

def get_many_object(conf_data, object_name=None, object_id=None, class_name=None):
    ret = []

    should_check_id    = object_id   is not None
    should_check_name  = object_name is not None
    should_check_class = class_name  is not None

    for key, value in conf_data.items():
        if should_check_name and not key.startswith(object_name+"@"):
            continue

        if should_check_id and value.get('_id', {}).get('$oid', None) != object_id:
            continue

        if should_check_class and value['__type'] != class_name:
            continue

        r = deepcopy(value)
        r["__name"] = key
        ret.append(r)


    if ret == []:
        raise OKSValueError(f'Expected to find at least one object ({object_id=}, {class_name=}), but found none')

    return ret


def get_one_object(conf_data, object_name=None, object_id=None, class_name=None):
    ret = get_many_object(conf_data, object_name, object_id, class_name)

    if len(ret) != 1:
        raise OKSValueError(f'Expected to find exactly one object ({object_id=}, {class_name=}), but found {len(ret)}')

    return ret[0]


def get_many_relation_by_class(conf_data, start_object, class_name=None):
    ret = []

    for key, values in start_object.items():

        if key in ["__type", "_id"]:
            continue

        if not isinstance(values, list):
            continue

        for value in values:
            if not isinstance(value, dict):
                continue

            if "$id" not in value:
                continue

            ret += [
                get_one_object(
                    conf_data,
                    object_id = value["$id"],
                    class_name = class_name
                )
            ]


    return ret


def get_many_relation_by_name(conf_data, start_object, object_name):
    ret = None

    for key, values in start_object.items():
        if key != object_name:
            continue

        if not isinstance(values, list):
            continue

        if ret is None:
            ret = []

        for value in values:
            if not isinstance(value, dict):
                continue

            if "$id" not in value:
                continue



            ret += [
                get_one_object(
                    conf_data,
                    object_id = value["$id"],
                )
            ]

    if ret is None:
        raise OKSValueError(f'\'{object_name}\' not found in {list(start_object.keys())}')

    return ret


def get_one_relation_by_class(conf_data, start_object, class_name=None):
    ret = []

    for key, value in start_object.items():

        if key in ["__type", "_id"]:
            continue

        if not isinstance(value, dict):
            continue

        if value.get("$id"):
            obj = get_one_object(
                conf_data,
                object_id = value["$id"],
            )
            if obj.get("__type") != class_name:
                continue

            ret += [obj]

    if len(ret) != 1:
        raise OKSValueError(f'Expected to find exactly one relation (class {class_name}), but found {len(ret)}')

    return ret[0]


def get_one_relation_by_name(conf_data, start_object, object_name):
    ret = []

    for key, value in start_object.items():

        if key != object_name:
            continue

        if not isinstance(value, dict):
            continue

        if value.get("$id"):
            obj = get_one_object(
                conf_data,
                object_id = value["$id"],
            )

            ret += [obj]

    if len(ret) != 1:
        raise OKSValueError(f'Expected to find exactly one relation (class \'{object_name}\'), but found {len(ret)}')

    return ret[0]


def get_one_attribute(conf_data, start_object, attribute_name):
    ret = []

    for key, value in start_object.items():

        if key != attribute_name:
            continue

        if isinstance(value, dict):
            raise OKSValueError(f'\'{attribute_name}\' seems to be a relation, not an attribute')

        ret += [value]

    if len(ret) != 1:
        raise OKSValueError(f'Expected to find exactly one attribute ({attribute_name=}), but found {len(ret)}')

    return ret[0]


def find_session(conf_data, session_name):

    session = get_one_object(
        conf_data = conf_data,
        class_name = 'Session',
        object_name = session_name
    )
    if not session:
        raise OKSValueError(f'Session \'{session_name}\' not found')
    return session


def collect_all_applications(conf_data, segment_data):

    applications = get(conf_data, segment_data, object_name="applications")
    segments = get(conf_data, segment_data, object_name="segments")

    for segment in segments:
        applications += collect_all_applications(conf_data, segment)

    return applications


def get_applications(conf_data, session_data, application_name=None, application_class_name=None):
    should_check_name = application_name is not None
    should_check_class = application_class_name is not None
    segment = get(conf_data, session_data, "segment")

    applications = collect_all_applications(conf_data, segment)

    ret = []
    for application in applications:
        if should_check_name and not match(application_name, application["__name"]):
            continue
        if should_check_class and application.get("__type") != application_class_name:
            continue
        ret += [application]

    return ret


def is_enabled(conf_data, session_data, object_data):
    disabled = get_one_attribute(conf_data, session_data, "disabled")
    if object_data.get("_id", {}).get("$oid", None) in disabled:
        return False
    return True


def get(conf_data, start_object, object_name):
    logging.debug(f'Getting {object_name=} from {start_object}')
    try:
        ret = get_many_relation_by_name(
            conf_data,
            start_object,
            object_name = object_name,
        )
        logging.debug(f'\'{object_name}\' multiple relations found in {list(start_object.keys())}')
        return ret
    except OKSValueError as e:
        logging.debug(f'\'{object_name}\' multiple relations NOT found in {list(start_object.keys())}: {e}')

    try:
        ret = get_one_relation_by_name(
            conf_data,
            start_object,
            object_name = object_name,
        )
        logging.debug(f'\'{object_name}\' single relation found in {list(start_object.keys())}')
        return ret
    except OKSValueError as e:
        logging.debug(f'\'{object_name}\' single relation NOT found in {list(start_object.keys())}: {e}')

    try:
        ret = get_one_attribute(
            conf_data,
            start_object,
            attribute_name = object_name,
        )
        logging.debug(f'\'{object_name}\' attribute found in {list(start_object.keys())}')
        return ret
    except OKSValueError as e:
        logging.debug(f'\'{object_name}\' attribute NOT found in {list(start_object.keys())}: {e}')

    raise OKSValueError(f'\'{object_name}\' not found in {start_object}')
