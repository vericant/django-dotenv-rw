import os
import sys
import warnings
from collections import OrderedDict


def load_dotenv(dotenv_path):
    """
    Read a .env file and load into os.environ.
    """
    if not os.path.exists(dotenv_path):
        warnings.warn("can't read {} - it doesn't exist.".format(dotenv_path))
        return None
    for k, v in parse_dotenv(dotenv_path):
        os.environ.setdefault(k, v)
    return True


def read_dotenv(dotenv_path=None):
    """
    Prior name of load_dotenv function.

    Deprecated and pending removal

    If not given a path to a dotenv path, does filthy magic stack backtracking
    to find manage.py and then find the dotenv.
    """
    warnings.warn("read_dotenv deprecated, use load_dotenv instead")
    if dotenv_path is None:
        warnings.warn("read_dotenv without an explicit path is deprecated and will be removed soon")
        frame = sys._getframe()
        dotenv_path = os.path.join(os.path.dirname(frame.f_back.f_code.co_filename), '.env')
    return load_dotenv(dotenv_path)


def get_key(dotenv_path, key_to_get):
    """
    Gets the value of a given key from the given .env

    If the .env path given doesn't exist, fails
    """
    key_to_get = str(key_to_get)
    if not os.path.exists(dotenv_path):
        warnings.warn("can't read {} - it doesn't exist.".format(dotenv_path))
        return None
    dotenv_as_dict = OrderedDict(parse_dotenv(dotenv_path))
    if key_to_get in dotenv_as_dict:
        return dotenv_as_dict[key_to_get]
    else:
        warnings.warn("key {} not found in {}.".format(key_to_get, dotenv_path))
        return None


def set_key(dotenv_path, key_to_set, value_to_set):
    """
    Adds or Updates a key/value to the given .env

    If the .env path given doesn't exist, fails instead of risking creating
    an orphan .env somewhere in the filesystem
    """
    key_to_set = str(key_to_set)
    value_to_set = str(value_to_set).strip("'").strip('"')
    if not os.path.exists(dotenv_path):
        warnings.warn("can't write to {} - it doesn't exist.".format(dotenv_path))
        return None
    dotenv_as_dict = OrderedDict(parse_dotenv(dotenv_path))
    dotenv_as_dict[key_to_set] = value_to_set
    success = flatten_and_write(dotenv_path, dotenv_as_dict)
    return success, key_to_set, value_to_set


def unset_key(dotenv_path, key_to_unset):
    """
    Removes a given key from the given .env

    If the .env path given doesn't exist, fails
    If the given key doesn't exist in the .env, fails
    """
    key_to_unset = str(key_to_unset)
    if not os.path.exists(dotenv_path):
        warnings.warn("can't delete from {} - it doesn't exist.".format(dotenv_path))
        return None
    dotenv_as_dict = OrderedDict(parse_dotenv(dotenv_path))
    if key_to_unset in dotenv_as_dict:
        dotenv_as_dict.pop(key_to_unset, None)
    else:
        warnings.warn("key {} not removed from {} - key doesn't exist.".format(key_to_unset, dotenv_path))
        return None
    success = flatten_and_write(dotenv_path, dotenv_as_dict)
    return success, key_to_unset


def parse_dotenv(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            v = v.strip("'").strip('"')
            yield k, v


def flatten_and_write(dotenv_path, dotenv_as_dict):
    with open(dotenv_path, "w") as f:
        for k, v in dotenv_as_dict.items():
            f.write('{}="{}"\r\n'.format(k, v))
    return True
