import config
import util
import os

import viewer


from item import Item

class ImageItem(Item):
    def __init__(self, file, parent, name = None, duration = 0):
        Item.__init__(self)
        self.type     = 'image'
        self.file     = file
        self.image    = file
        self.duration = duration

        self.parent = parent

        if name:
            self.name = name
        else:
            self.name    = os.path.splitext(os.path.basename(file))[0]

        self.image_viewer = viewer.get_singleton()

        
    def actions(self):
        return [ ( self.view, 'View Image' ) ]

    def cache(self):
        self.image_viewer.cache(self)

    def view(self, arg=None, menuw=None):
        self.parent.current_item = self
        self.image_viewer.view(self)

        if self.parent and hasattr(self.parent, 'cache_next'):
            self.parent.cache_next()
