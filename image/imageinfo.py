import config
import util
import os

from menu import Info

class ImageInfo(Info):
    def __init__(self, file, duration = 0):
        Info.__init__(self)
        self.type     = 'image'
        self.file     = file
        self.image    = file
        self.duration = duration

        self.name    = os.path.splitext(os.path.basename(file))[0]
