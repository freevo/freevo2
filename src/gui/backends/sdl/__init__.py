_renderer = None
_screen   = None

from screen import Screen
from renderer import Renderer

def get_screen(*args):
    global _screen
    if not _screen:
        _screen = Screen(*args)
    return _screen
        
def get_renderer(*args):
    global _renderer
    print 'go', _renderer
    if not _renderer:
        _renderer = Renderer(*args)
    return _renderer
        
from layer import Layer
from font import Font
from keyboard import Keyboard
