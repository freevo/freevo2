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
    osd = 1    # Draw file info on the image
    zoom = 0   # Image zoom
    zoom_btns = { rc.K0:0, rc.K1:1, rc.K2:2, rc.K3:3, rc.K4:4,
                  rc.K5:5, rc.K6:6, rc.K7:7, rc.K8:8, rc.K9:9 }

   
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

        
    def view(self, filename, number, playlist, zoom=0):

        self.filename = filename
        self.playlist = playlist
        self.number = number
        self.rotation = 0

        
        rc.app = self.eventhandler


        # XXX Alternative version of the code below, use "if 1" to enable
        # XXX This version uses the OSD server JPEG support and bitmap scaling

        if 1:
            osd.loadbitmap(filename)

            image = Image.open(filename)
            width, height = image.size

            # Bounding box default values
            bbx = bby = bbw = bbh = 0
            if zoom:
                width = width / 3
                height = height / 3

                # Translate the 9-element grid to bounding boxes
                bb = { 1:(0,0), 2:(1,0), 3:(2,0),
                       4:(0,1), 5:(1,1), 6:(2,1),
                       7:(0,2), 8:(1,2), 9:(2,2) }
                h, v = bb[zoom]

                # Bounding box (x;y) position
                bbx = [0, width, 2*width][h]
                bby = [0, height, 2*height][v]

                # Get one 1/3 of the image
                bbw = width
                bbh = height
                
            # scale_x = scale_y = 1.0
            # if width > osd.width: scale_x = float(osd.width) / width
            # if height > osd.height: scale_y = float(osd.height) / height
            scale_x = float(osd.width) / width
            scale_y = float(osd.height) / height

            scale = min(scale_x, scale_y)

            new_w, new_h = int(scale*width), int(scale*height)

            x = (osd.width - new_w) / 2
            y = (osd.height - new_h) / 2

            print width, height, scale, new_w, new_h, x, y

            osd.drawbitmap(filename, x, y, scale, bbx, bby, bbw, bbh)
            self.osd = 0  # don't draw osd as default
            osd.update()

            # cache the next image (most likely we need this)
            # XXX use a separate function like above...
            if self.playlist != []:
                pos = self.playlist.index(self.filename)
                pos = (pos+1) % len(self.playlist)
                filename = self.playlist[pos]

                image = Image.open(filename)
                width, height = image.size

                scale_x = scale_y = 1.0
                if width > osd.width: scale_x = float(osd.width) / width
                if height > osd.height: scale_y = float(osd.height) / height

                scale = min(scale_x, scale_y)

                # This will both load the next image into the load cache,
                # zoom it into the zoom cache.
                osd.zoombitmap(filename, scale)

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
            self.osd = {0:1, 1:0}[self.osd] # Toggle on/off
            
            if self.osd:
                self.drawosd()
                osd.update()
            else:
                # Redraw without the OSD
                self.view(self.filename, self.playlist.index(self.filename),
                          self.playlist)

        # XXX Test, zoom to one third of the image
        # XXX 1 is upper left, 9 is lower right, 0 zoom off
        if event in self.zoom_btns:
            self.zoom = self.zoom_btns[event]
                
            if self.zoom:
                # Zoom one third of the image, don't load the next
                # image in the list
                self.view(self.filename, self.playlist.index(self.filename),
                          self.playlist, zoom=self.zoom)
            else:
                # Display entire picture, don't load next image in case
                # the user wants to zoom around some more.
                self.view(self.filename, self.playlist.index(self.filename),
                          self.playlist, zoom=0)
                

    def drawosd(self):

        if not self.osd: return
        
        f = open(self.filename, 'r')
        tags = exif.process_file(f)

        # Make the background darker for the OSD info
        osd.drawbox(0, osd.height - 90, 350, osd.height, width=-1,
                    color=((60 << 24) | osd.COL_BLACK))
        
        pos = 50

        if tags.has_key('Image DateTime'):
            osd.drawstring('%s' % tags['Image DateTime'], 20, osd.height - pos, 
                           fgcolor=osd.COL_ORANGE)
            pos += 30
            
        osd.drawstring(os.path.basename(self.filename), 20, osd.height - pos, 
                       fgcolor=osd.COL_ORANGE)

        pos += 30
            
        if self.zoom:
            osd.drawstring('Zoom = %s' % self.zoom, 20, osd.height - pos, 
                           fgcolor=osd.COL_ORANGE)
            
