#if 0
# -----------------------------------------------------------------------
# iview.py - Freevo image viewer
# -----------------------------------------------------------------------
# $Id$
#
# Notes: You can only zoom a rotated image with OSD_SDL enabled
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2002/08/11 13:42:35  dischi
# o Fixed the zoom and rotate handling. If the OSD_SDL is enabled you
#   can zoom (1-9) an rotated image. Without OSD_SDL you zoom the normal
#   image.
#
# o Rotation with OSD_SDL works now without tmp file directly in the
#   osd_sdl.py
#
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# -----------------------------------------------------------------------
#endif


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
    osd = 0    # Draw file info on the image
    zoom = 0   # Image zoom
    zoom_btns = { rc.K0:0, rc.K1:1, rc.K2:2, rc.K3:3, rc.K4:4,
                  rc.K5:5, rc.K6:6, rc.K7:7, rc.K8:8, rc.K9:9 }

   
    def view(self, filename, number, playlist, zoom=0, rotation=0):

        self.filename = filename
        self.playlist = playlist
        self.number = number
        self.rotation = rotation

        
        rc.app = self.eventhandler


        osd.loadbitmap(filename)

        image = Image.open(filename)
        width, height = image.size

        # Bounding box default values
        bbx = bby = bbw = bbh = 0

        if zoom:
            # Translate the 9-element grid to bounding boxes
            if 'OSD_SDL' in dir(config) and self.rotation == 90:
                bb = { 1:(2,0), 2:(2,1), 3:(2,2),
                       4:(1,0), 5:(1,1), 6:(1,2),
                       7:(0,0), 8:(0,1), 9:(0,2) }
            elif 'OSD_SDL' in dir(config) and self.rotation == 180:
                bb = { 1:(2,2), 2:(1,2), 3:(0,2),
                       4:(2,1), 5:(1,1), 6:(0,1),
                       7:(2,0), 8:(1,0), 9:(0,0) }
            elif 'OSD_SDL' in dir(config) and self.rotation == 270:
                bb = { 1:(0,2), 2:(0,1), 3:(0,0),
                       4:(1,2), 5:(1,1), 6:(1,0),
                       7:(2,2), 8:(2,1), 9:(2,0) }
            else:
                bb = { 1:(0,0), 2:(1,0), 3:(2,0),
                       4:(0,1), 5:(1,1), 6:(2,1),
                       7:(0,2), 8:(1,2), 9:(2,2) }

            h, v = bb[zoom]

            # Bounding box center
            bbcx = ([1, 3, 5][h]) * width / 6
            bbcy = ([1, 3, 5][v]) * height / 6

            if 'OSD_SDL' in dir(config) and self.rotation % 180:
                # different calculations because image width is screen height
                scale_x = float(osd.width) / (height / 3)
                scale_y = float(osd.height) / (width / 3)
                scale = min(scale_x, scale_y)

                # read comment for the bbw and bbh calculations below
                bbw = min(max((width / 3) * scale, osd.height), width) / scale
                bbh = min(max((height / 3) * scale, osd.width), height) / scale

            else:
                scale_x = float(osd.width) / (width / 3)
                scale_y = float(osd.height) / (height / 3)
                scale = min(scale_x, scale_y)

                # the bb width is the width / 3 * scale, to avoid black bars left
                # and right exapand it to the osd.width but not if this is more than the
                # image width (same for height)
                bbw = min(max((width / 3) * scale, osd.width), width) / scale
                bbh = min(max((height / 3) * scale, osd.height), height) / scale
                

            # calculate the beginning of the bounding box
            bbx = max(0, bbcx - bbw/2)
            bby = max(0, bbcy - bbh/2)

            if bbx + bbw > width:  bbx = width - bbw
            if bby + bbh > height: bby = height - bbh

            if 'OSD_SDL' in dir(config) and self.rotation % 180:
                new_h, new_w = bbw * scale, bbh * scale
            else:
                new_w, new_h = bbw * scale, bbh * scale



        else:
            if 'OSD_SDL' in dir(config) and self.rotation % 180:  
                height, width = image.size
                
            # scale_x = scale_y = 1.0
            # if width > osd.width: scale_x = float(osd.width) / width
            # if height > osd.height: scale_y = float(osd.height) / height
            scale_x = float(osd.width) / width
            scale_y = float(osd.height) / height
            
            scale = min(scale_x, scale_y)
            
            new_w, new_h = int(scale*width), int(scale*height)


        # Now we have all necessary informations about zoom yes/no and
        # the kind of rotation
        
        x = (osd.width - new_w) / 2
        y = (osd.height - new_h) / 2
        
        osd.clearscreen(color=osd.COL_BLACK)
        if 'OSD_SDL' in dir(config):
            osd.drawbitmap(filename, x, y, scale, bbx, bby, bbw, bbh,
                           rotation = self.rotation)
        else:
            osd.drawbitmap(filename, x, y, scale, bbx, bby, bbw, bbh)

        # update the OSD
        self.drawosd()

        # draw
        osd.update()
        
        # cache the next image (most likely we need this)
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
            osd.clearscreen(color=osd.COL_BLACK)

            if event == rc.LEFT:
                self.rotation = (self.rotation + 270) % 360
            else:
                self.rotation = (self.rotation + 90) % 360


            if 'OSD_SDL' in dir(config):  
                image = Image.open(self.filename)
                
                if self.rotation % 180:
                    height, width = image.size
                else:
                    width, height = image.size
                    
                scale_x = scale_y = 1.0
                if width > osd.width: scale_x = float(osd.width) / width
                if height > osd.height: scale_y = float(osd.height) / height
                
                scale = min(scale_x, scale_y)
                
                new_w, new_h = int(scale*width), int(scale*height)
                
                osd.drawbitmap(self.filename, (osd.width-new_w) / 2, (osd.height-new_h) / 2,
                               scaling=scale, rotation=self.rotation)

            else:
                osd.drawstring('please wait...', osd.width/2 - 60, osd.height/2 - 10,
                               fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
                osd.update()
                osd.clearscreen(color=osd.COL_BLACK)

                pos = self.playlist.index(self.filename)
                image_file = (config.FREEVO_CACHEDIR + '/' +
                              os.path.basename('image-viewer-%s.png' % pos))
                
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

        # zoom to one third of the image
        # 1 is upper left, 9 is lower right, 0 zoom off
        if event in self.zoom_btns:
            self.zoom = self.zoom_btns[event]
                
            if self.zoom:
                # Zoom one third of the image, don't load the next
                # image in the list
                self.view(self.filename, self.playlist.index(self.filename),
                          self.playlist, zoom=self.zoom, rotation = self.rotation)
            else:
                # Display entire picture, don't load next image in case
                # the user wants to zoom around some more.
                self.view(self.filename, self.playlist.index(self.filename),
                          self.playlist, zoom=0, rotation = self.rotation)
                

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
            
