#
# iview.py
#
# This is the Freevo image viewer
#
# $Id$

import sys
import random
import time, os, glob, imghdr
import string, popen2, fcntl, select, struct
import Image


# Configuration file. Determines where to look for image files, etc
import config

# Various utilities
import util

# The menu widget class
import menu

# The skin class
import skin

# The OSD class, used to communicate with the OSD daemon
import osd

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc


# Create the remote control object
rc = rc.get_singleton()


# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

# Create the OSD object
osd = osd.get_singleton()

# Create the MenuWidget object
menuwidget = menu.get_singleton()


# Module variable that contains an initialized ImageViewer() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = ImageViewer()
        
    return _singleton


class ImageViewer:
        
    def view(self, filename, number, playlist):
        self.filename = filename
        self.playlist = playlist
        self.number = number
    
        rc.app = self.eventhandler

        osd.clearscreen(color=osd.COL_BLACK)
        osd.update()



        # XXX New version of the code below, use "if 0" to disable
        # XXX This version uses the OSD server JPEG support and bitmap scaling
        # XXX It also scales the bitmap to max resolution while maintaining the aspect ratio
        # XXX and places it in the middle of the screen. The filename is displayed in the corner.
        if 1:
            osd.drawstring('please wait...', osd.width/2 - 60, osd.height/2 - 10,
                           fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
            osd.update()

            image = Image.open(filename)
            width, height = image.size

            scale_x = scale_y = 1.0
            if width > osd.width: scale_x = float(osd.width) / width
            if height > osd.height: scale_y = float(osd.height) / height

            scale = min(scale_x, scale_y)

            new_w, new_h = int(scale*width), int(scale*height)

            x = (osd.width - new_w) / 2
            y = (osd.height - new_h) / 2

            print width, height, scale, new_w, new_h, x, y

            osd.drawbitmap(filename, x, y, scale)
            osd.drawstring(os.path.basename(filename), 10, osd.height - 30, fgcolor=osd.COL_ORANGE)
            osd.update()

            return













        # draw the current image
        image_file = (config.FREEVO_CACHEDIR + '/' +
                      os.path.basename('image-viewer-%s.png' % number))

        if not os.path.isfile(image_file):
            osd.drawstring('please wait...', 50, 280,
                           fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
            osd.update()
            osd.clearscreen(color=osd.COL_BLACK)
            im = Image.open(filename)
            im_res = im.resize((osd.width,osd.height))
            im_res.save(image_file,'PNG')

        osd.drawbitmap(image_file)
        osd.update()

        # cache the next image (most likely we need this)
        if self.playlist != []:
            pos = self.playlist.index(self.filename)
            pos = (pos+1) % len(self.playlist)
            filename = self.playlist[pos]

            image_file = (config.FREEVO_CACHEDIR + '/' +
                          os.path.basename('image-viewer-%s.png' % pos))

            if not os.path.isfile(image_file):
                im = Image.open(filename)
                im_res = im.resize((osd.width,osd.height))
                im_res.save(image_file,'PNG')



    
    def eventhandler(self, event):
        if event == rc.STOP or event == rc.SELECT or event == rc.EXIT:
            rc.app = None
            menuwidget.refresh()
        if event == rc.LEFT or event == rc.UP:
            if self.playlist == []:
                rc.app = None
                menuwidget.refresh()
            else:
                # Go to the previous image in the list
                pos = self.playlist.index(self.filename)
                pos = (pos-1) % len(self.playlist)
                filename = self.playlist[pos]
                self.view(filename, pos, self.playlist)

        if event == rc.RIGHT or event == rc.DOWN:
            if self.playlist == []:
                rc.app = None
                menuwidget.refresh()
            else:
                # Go to the next image in the list
                pos = self.playlist.index(self.filename)
                pos = (pos+1) % len(self.playlist)
                filename = self.playlist[pos]
                self.view(filename, pos, self.playlist)


