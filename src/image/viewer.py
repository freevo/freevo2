#if 0 /*
# -----------------------------------------------------------------------
# viewer.py - Freevo image viewer
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.34  2003/11/28 20:08:57  dischi
# renamed some config variables
#
# Revision 1.33  2003/11/23 19:48:59  krister
# Added optional new blend settings (nr of steps and total time), must be enabled explicitly in freevo_config
#
# Revision 1.32  2003/11/21 12:22:15  dischi
# move blending effect to osd.py
#
# Revision 1.31  2003/11/21 11:46:51  dischi
# blend one image to the next, better rotation support
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
# ----------------------------------------------------------------------- */
#endif


import os.path
import Image
import signal
import os
import time
import plugin

import config # Configuration file. 
import osd    # The OSD class, used to communicate with the OSD daemon
import event as em
import objectcache
import rc

from gui.GUIObject import GUIObject
from gui.AlertBox import AlertBox

osd        = osd.get_singleton()  # Create the OSD object


# Module variable that contains an initialized ImageViewer() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = ImageViewer()
        
    return _singleton


class ImageViewer(GUIObject):

    def __init__(self):
        GUIObject.__init__(self)
        self.osd_mode = 0    # Draw file info on the image
        self.zoom = 0   # Image zoom
        self.zoom_btns = { str(em.IMAGE_NO_ZOOM):0, str(em.IMAGE_ZOOM_GRID1):1,
                           str(em.IMAGE_ZOOM_GRID2):2, str(em.IMAGE_ZOOM_GRID3):3,
                           str(em.IMAGE_ZOOM_GRID4):4, str(em.IMAGE_ZOOM_GRID5):5,
                           str(em.IMAGE_ZOOM_GRID6):6, str(em.IMAGE_ZOOM_GRID7):7,
                           str(em.IMAGE_ZOOM_GRID8):8, str(em.IMAGE_ZOOM_GRID9):9 }

        self.slideshow   = TRUE  # currently in slideshow mode
        self.alertbox    = None  # AlertBox active
        self.app_mode    = 'image'
        self.bitmapcache = objectcache.ObjectCache(3, desc='viewer')
        self.last_image  = (None, None)
        
    def view(self, item, zoom=0, rotation=0):
        filename = item.filename

        self.fileitem = item
        self.parent   = item.menuw
        
        self.filename = filename
        self.rotation = rotation

        if filename and len(filename) > 0:
            image = osd.loadbitmap(filename, cache=self.bitmapcache)
        else:
            # Using Container-Image
            image = item.loadimage()

        rc.app(self)

        if not image:
            osd.clearscreen(color=osd.COL_BLACK)
            osd.update()
            self.alertbox = AlertBox(parent=self,
                                     text=_("Can't Open Image\n'%s'") % (filename))
            self.alertbox.show()
            return
        
	width, height = image.get_size()
            
        # Bounding box default values
        bbx = bby = bbw = bbh = 0

        if zoom:
            # Translate the 9-element grid to bounding boxes
            if self.rotation == 90:
                bb = { 1:(2,0), 2:(2,1), 3:(2,2),
                       4:(1,0), 5:(1,1), 6:(1,2),
                       7:(0,0), 8:(0,1), 9:(0,2) }
            elif self.rotation == 180:
                bb = { 1:(2,2), 2:(1,2), 3:(0,2),
                       4:(2,1), 5:(1,1), 6:(0,1),
                       7:(2,0), 8:(1,0), 9:(0,0) }
            elif self.rotation == 270:
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

            if self.rotation % 180:
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

            if self.rotation % 180:
                new_h, new_w = bbw * scale, bbh * scale
            else:
                new_w, new_h = bbw * scale, bbh * scale



        else:
            if self.rotation % 180:  
                height, width = width, height
                
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
        
        last_image = self.last_image[1]

        if (last_image and self.last_image[0] != item and
            (config.IMAGEVIEWER_BLEND_SPEED or config.IMAGEVIEWER_BLEND_STEPS)):
            screen = osd.screen.convert()
            screen.fill((0,0,0,0))
            screen.blit(osd.zoomsurface(image, scale, bbx, bby, bbw, bbh,
                                        rotation = self.rotation).convert(), (x, y))
            # update the OSD
            self.drawosd(layer=screen)

            # XXX Choose the new style blending if so configured
            if config.IMAGEVIEWER_BLEND_STEPS:
                osd.update(blend_surface=screen,
                           blend_steps=config.IMAGEVIEWER_BLEND_STEPS,
                           blend_time=config.IMAGEVIEWER_BLEND_TIME)
            else:
                osd.update(blend_surface=screen, blend_speed=config.IMAGEVIEWER_BLEND_SPEED)

        else:
            osd.clearscreen(color=osd.COL_BLACK)
            osd.drawsurface(image, x, y, scale, bbx, bby, bbw, bbh,
                            rotation = self.rotation)

            # update the OSD
            self.drawosd()

        if plugin.getbyname('osd'):
            plugin.getbyname('osd').draw(('osd', None), osd)
            
        # draw
        osd.update()

        # start timer
        if self.fileitem.duration:
            signal.signal(signal.SIGALRM, self.signalhandler)
            signal.alarm(self.fileitem.duration)

        self.last_image  = (item, (image, x, y, scale, bbx, bby, bbw, bbh,
                                   self.rotation))
        return None


    def redraw(self):
        self.view(self.fileitem, zoom=self.zoom, rotation=self.rotation)
        
    def cache(self, fileitem):
        # cache the next image (most likely we need this)
        osd.loadbitmap(fileitem.filename, cache=self.bitmapcache)
        

    def signalhandler(self, signum, frame):
        if rc.app() == self.eventhandler and self.slideshow:
            self.last_image  = None, None
            rc.app(None)
            self.eventhandler(em.PLAY_END)


    def eventhandler(self, event, menuw=None):
        #if event == rc.SELECT and self.alertbox:
        #    self.alertbox.destroy()
        #    self.alertbox = None
        #    return TRUE
        
        if event == em.PAUSE or event == em.PLAY:
            if self.slideshow:
                self.slideshow = FALSE
                signal.alarm(0)
            else:
                self.slideshow = TRUE
                signal.alarm(1)
            return TRUE
        
        elif event == em.STOP:
            self.last_image  = None, None
            rc.app(None)
            signal.alarm(0)
            self.fileitem.eventhandler(event)
            return TRUE

        # up and down will stop the slideshow and pass the
        # event to the playlist
        elif event == em.PLAYLIST_NEXT or event == em.PLAYLIST_PREV:
            self.slideshow = FALSE
            signal.alarm(0)
            self.fileitem.eventhandler(event)
            return TRUE
            
        # rotate image
        elif event == em.IMAGE_ROTATE:
            if event.arg == 'left':
                self.rotation = (self.rotation + 270) % 360
            else:
                self.rotation = (self.rotation + 90) % 360
            self.fileitem.rotation = self.rotation
            self.view(self.fileitem, zoom=self.zoom, rotation=self.rotation)
            return TRUE

        # print image information
        elif event == em.TOGGLE_OSD:
            self.osd_mode = {0:1, 1:2, 2:0}[self.osd_mode] # Toggle on/off
            # Redraw
            self.view(self.fileitem, zoom=self.zoom, rotation = self.rotation)
            return TRUE

        # zoom to one third of the image
        # 1 is upper left, 9 is lower right, 0 zoom off
        elif str(event) in self.zoom_btns:
            self.zoom = self.zoom_btns[str(event)]
                
            if self.zoom:
                # Zoom one third of the image, don't load the next
                # image in the list
                self.view(self.fileitem, zoom=self.zoom, rotation = self.rotation)
            else:
                # Display entire picture, don't load next image in case
                # the user wants to zoom around some more.
                self.view(self.fileitem, zoom=0, rotation = self.rotation)
            return TRUE                

        # save the image with the current rotation
        elif event == em.IMAGE_SAVE:
            if self.rotation and os.path.splitext(self.filename)[1] == ".jpg":
                cmd = 'jpegtran -copy all -rotate %s -outfile /tmp/freevo-iview %s' \
                      % ((self.rotation + 180) % 360, self.filename)
                os.system(cmd)
                os.system('mv /tmp/freevo-iview %s' % self.filename)
                self.rotation = 0
                osd.bitmapcache.__delitem__(self.filename)
                return TRUE                

        else:
            return self.fileitem.eventhandler(event)

            
    def drawosd(self, layer=None):

        if not self.osd_mode: return

        elif self.osd_mode == 1:
	    # This is where we add a caption.  Only if playlist is empty
            # May need to check the caption too?
            osdstring = []

	    # Here we set up the tags that we want to put in the display
	    # Using the following fields
            tags_check = [[_('Title: '),      'name'],
                          [_('Description: '),'description']
                          ]



        elif self.osd_mode == 2:    
           # This is where we add a caption.  Only if playlist is empty
	   # create an array with Exif tags as above
	   osdstring = []
           tags_check = [ [_('Title: '),   'name'],
                          [_('Date: ') ,   'date'],
	                  ['W:',           'width'],
			  ['H:',           'height'],
			  [_('Model:'),    'hardware'],
			  [_('Software:'), 'software']
			 ]

           # FIXME: add this informations to mmpython:
           
           # ['Exp:','EXIF ExposureTime','ExposureTime','EXIF'],
           # ['F/','EXIF FNumber','FNumber','EXIF'],
           # ['FL:','EXIF FocalLength','FocalLength','EXIF'],
           # ['ISO:','EXIF ISOSpeedRatings','ISOSpeedRatings','EXIF'],
           # ['Meter:','EXIF MeteringMode','MeteringMode','EXIF'],
           # ['Light:','EXIF LightSource','LightSource','EXIF'],
           # ['Flash:','EXIF Flash','Flash','EXIF'],
           # ['Make:','Image Make','Make','EXIF'],

        for strtag in tags_check:
            i = self.fileitem.getattr(strtag[1])
            if i:
                osdstring.append('%s %s' % (strtag[0], i))

	# If after all that there is nothing then tell the users that
	if osdstring == []:
	    osdstring = [_('No information available')]
	
	# Now sort the text into lines of length line_length
        line = 0
	if config.OSD_OVERSCAN_X:
	    line_length = 35
	else:
	    line_length = 60
        prt_line = ['']

        for textstr in osdstring:
            if len(textstr) > line_length:
                # This is to big so just print it for now but wrap later
                if prt_line[line] == '':
                    prt_line[line] = textstr
                else:
                    prt_line.append(textstr)
                    line += 1
            elif len(textstr + '   ' + prt_line[line] )  > line_length:
                # Too long for one line so print the last and then new
                line += 1
                prt_line.append(textstr)
            else:
                if prt_line[line] == '':
                    prt_line[line] = textstr
                else:
                    prt_line[line] += '   ' + textstr

        # Create a black box for text
        osd.drawbox(config.OSD_OVERSCAN_X,
                    osd.height - (config.OSD_OVERSCAN_X + 25 + (len(prt_line) * 30)),
                    osd.width, osd.height, width=-1, 
                    color=((60 << 24) | osd.COL_BLACK), layer=layer)

	# Now print the Text
        for line in range(len(prt_line)):
            h=osd.height - (40 + config.OSD_OVERSCAN_Y + ((len(prt_line) - line - 1) * 30))
            osd.drawstring(prt_line[line], 15 + config.OSD_OVERSCAN_X, h,
                           fgcolor=osd.COL_ORANGE, layer=layer)


