import config
import util
import os

from menu import Info

class ImageInfo(Info):
    def __init__(self, file, calling_info = None, duration = 0):
        Info.__init__(self)
        self.type     = 'image'
        self.file     = file
        self.image    = file
        self.duration = duration

        self.calling_info = calling_info
        
        self.name    = os.path.splitext(os.path.basename(file))[0]
