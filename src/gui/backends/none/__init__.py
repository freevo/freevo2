# reuse some sdl backend stuff
from gui.backends.sdl import get_renderer
from screen import Screen

def get_screen(*args):
    return Screen(*args)
