import mevas
from mevas.displays.imlib2canvas import Imlib2Canvas

class Display(Imlib2Canvas):
    def __init__(self, size, default=False):
        Imlib2Canvas.__init__(self, size)

    def hide(self):
        pass

    def show(self):
        pass

