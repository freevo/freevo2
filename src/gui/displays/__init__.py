import config

# FIXME: make dynamic import here
from sdl import Display as SDL
from imlib2 import Display as Imlib2
from bmovl import Display as Bmovl
from bmovl2 import Display as Bmovl2

# FIXME: move this to freevo_config.py
if hasattr(config, 'BMOVL_OSD_VIDEO'):
    DEFAULT_DISPLAY = 'Bmovl'
else:
    DEFAULT_DISPLAY = 'SDL'


def default():
    """
    return the default display for Freevo
    """
    return eval(DEFAULT_DISPLAY)((config.CONF.width, config.CONF.height), True)


def new(display, size):
    """
    return a new display
    """
    return eval(display)(size)
    
