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

import exif

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
    def cache_file(self, filename, cachename):
        image = Image.open(filename)
        width, height = image.size

        scale_x = scale_y = 1.0
        if width > osd.width: scale_x = float(osd.width) / width
        if height > osd.height: scale_y = float(osd.height) / height

        scale = min(scale_x, scale_y)
        
        new_w, new_h = int(scale*width), int(scale*height)

        im_res = image.resize((new_w,new_h))
        im_res.save(cachename,'PNG')

        
    def view(self, filename, number, playlist):

        self.filename = filename
        self.playlist = playlist
        self.number = number
        self.rotation = 0
        self.osd = 0

        
        rc.app = self.eventhandler


        # XXX Alternative version of the code below, use "if 1" to enable
        # XXX This version uses the OSD server JPEG support and bitmap scaling

        if 0:
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
            osd.drawstring(os.path.basename(filename), 10, osd.height - 30, \
                           fgcolor=osd.COL_ORANGE)
            osd.update()

            return


        osd.clearscreen(color=osd.COL_BLACK)

        # draw the current image
        image_file = (config.FREEVO_CACHEDIR + '/' +
                      os.path.basename('image-viewer-%s.png' % number))

        if not os.path.isfile(image_file):
            osd.drawstring('please wait...', osd.width/2 - 60, osd.height/2 - 10,
                           fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
            osd.update()
            osd.clearscreen(color=osd.COL_BLACK)
            self.cache_file(filename, image_file)

        (w, h) = util.pngsize(image_file)
        osd.drawbitmap(image_file, (osd.width - w) / 2, (osd.height - h) / 2)
        osd.update()

        # cache the next image (most likely we need this)
        if self.playlist != []:
            pos = self.playlist.index(self.filename)
            pos = (pos+1) % len(self.playlist)
            filename = self.playlist[pos]

            image_file = (config.FREEVO_CACHEDIR + '/' +
                          os.path.basename('image-viewer-%s.png' % pos))

            if not os.path.isfile(image_file):
                self.cache_file(filename, image_file)



    
    def eventhandler(self, event):

        if event == rc.STOP or event == rc.EXIT:
            rc.app = None
            menuwidget.refresh()

        if event == rc.UP:
            if self.playlist == []:
                rc.app = None
                menuwidget.refresh()
            else:
                # Go to the previous image in the list
                pos = self.playlist.index(self.filename)
                pos = (pos-1) % len(self.playlist)
                filename = self.playlist[pos]
                self.view(filename, pos, self.playlist)

        if event == rc.DOWN:
            if self.playlist == []:
                rc.app = None
                menuwidget.refresh()
            else:
                # Go to the next image in the list
                pos = self.playlist.index(self.filename)
                pos = (pos+1) % len(self.playlist)
                filename = self.playlist[pos]
                self.view(filename, pos, self.playlist)


        # rotate image
        if event == rc.LEFT or event == rc.RIGHT:
            pos = self.playlist.index(self.filename)
            image_file = (config.FREEVO_CACHEDIR + '/' +
                          os.path.basename('image-viewer-%s.png' % pos))

            osd.clearscreen(color=osd.COL_BLACK)
            osd.drawstring('please wait...', osd.width/2 - 60, osd.height/2 - 10,
                           fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
            osd.update()
            osd.clearscreen(color=osd.COL_BLACK)

            if event == rc.LEFT:
                self.rotation = self.rotation - 90 % 360
            else:
                self.rotation = self.rotation + 90 % 360

            image = Image.open(self.filename).rotate(self.rotation)
            width, height = image.size

            scale_x = scale_y = 1.0
            if width > osd.width: scale_x = float(osd.width) / width
            if height > osd.height: scale_y = float(osd.height) / height

            scale = min(scale_x, scale_y)
            
            new_w, new_h = int(scale*width), int(scale*height)
            
            im_res = image.resize((new_w,new_h))
            im_res.save(image_file,'PNG')

            osd.drawbitmap(image_file, (osd.width - new_w) / 2, (osd.height - new_h) / 2)
            osd.update()
            

        # print image information
        if event == rc.DISPLAY:
            if self.osd:
                osd.clearscreen(color=osd.COL_BLACK)
                self.view(self.filename, self.playlist.index(self.filename), self.playlist)
                self.osd = 0
            else:
                f=open(self.filename, 'rb')
                tags=exif.process_file(f)

                pos = 30

                if tags.has_key('Image DateTime'):
                    osd.drawstring('%s' % tags['Image DateTime'], 10, osd.height - 30, \
                                   fgcolor=osd.COL_ORANGE)
                    pos = 60
                    
                osd.drawstring(os.path.basename(self.filename), 10, osd.height - pos, \
                               fgcolor=osd.COL_ORANGE)
                self.osd = 1
                
            osd.update()
            
