from plugin import Plugin

class PluginInterface(Plugin):
    """
    Basic class to allow input plugins to be loaded.
    """
    pass


from keymap import KEYBOARD_MAP, REMOTE_MAP, DIRECTFB_MAP
from eventmap import EVENTMAP

from interface import set_mapping, get_mapping, InputPlugin
