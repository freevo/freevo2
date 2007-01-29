from keymap import KEYBOARD_MAP, REMOTE_MAP, DIRECTFB_MAP
from eventmap import EVENTMAP

# set key mapping for input
_mapping = None

def set_mapping(mapping):
    """
    Set new key mapping.
    """
    global _mapping
    _mapping = mapping


def get_mapping():
    """
    Get current key mapping.
    """
    return _mapping
