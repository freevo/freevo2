# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# viewer.py - Freevo image viewer
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        Change the signal stuff for slideshows
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.57  2004/07/26 18:10:18  dischi
# move global event handling to eventhandler.py
#
# Revision 1.56  2004/07/25 19:47:38  dischi
# use application and not rc.app
#
# Revision 1.55  2004/07/25 18:18:30  dischi
# use new gui code
#
# Revision 1.54  2004/07/24 12:24:02  dischi
# reflect gui changes
#
# Revision 1.53  2004/07/22 21:21:48  dischi
# small fixes to fit the new gui code
#
# Revision 1.52  2004/07/11 10:39:45  dischi
# replaced AlertBox with normal warning on screen
#
# Revision 1.51  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.50  2004/06/03 18:23:31  dischi
# put image viewer osd into config
#
# Revision 1.49  2004/05/31 10:45:27  dischi
# update to new callback handling in rc
#
# Revision 1.48  2004/05/12 18:56:36  dischi
# add keys to move inside a zoom image in image viewer
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


import signal
import os

import config 
import util

import eventhandler

from event import *

import time
# from gui.animation import render, Transition
import gui

# Module variable that contains an initialized ImageViewer() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = ImageViewer()
        
    return _singleton


class ImageViewer:

    def __init__(self):
        self.osd_mode = 0    # Draw file info on the image
        self.zoom = 0   # Image zoom
        self.zoom_btns = { str(IMAGE_NO_ZOOM):0, str(IMAGE_ZOOM_GRID1):1,
                           str(IMAGE_ZOOM_GRID2):2, str(IMAGE_ZOOM_GRID3):3,
                           str(IMAGE_ZOOM_GRID4):4, str(IMAGE_ZOOM_GRID5):5,
                           str(IMAGE_ZOOM_GRID6):6, str(IMAGE_ZOOM_GRID7):7,
                           str(IMAGE_ZOOM_GRID8):8, str(IMAGE_ZOOM_GRID9):9 }

        self.slideshow   = True  # currently in slideshow mode
        self.app_mode    = 'image'
        self.last_image  = (None, None)
        self.parent      = None
        self.free_cache()
        self.osd_text    = None
        self.osd_box     = None

        self.filename    = None
        self.rotation    = None
        self.zomm        = None


    def free_cache(self):
        """
        free the current cache to save memory
        """
        self.bitmapcache = util.objectcache.ObjectCache(3, desc='viewer')
        if self.parent and self.free_cache in self.parent.show_callbacks: 
            self.parent.show_callbacks.remove(self.free_cache)

        

    def view(self, item, zoom=0, rotation=0):
        if zoom:
            self.app_mode    = 'image_zoom'
        else:
            self.app_mode    = 'image'

        eventhandler.append(self)

        swidth  = gui.get_screen().width
        sheight = gui.get_screen().height
            
        filename      = item.filename
        self.fileitem = item
        self.parent   = item.menuw
        screen        = gui.get_screen()

        if not self.free_cache in item.menuw.show_callbacks: 
            item.menuw.show_callbacks.append(self.free_cache)
        
        # only load new image when the image changed
        if self.filename == filename and self.zoom == zoom and \
           self.rotation == rotation and len(filename) > 0:
            # same image, only update the osd and the timer
            self.drawosd()
            screen.update()
            return
        
        self.filename = filename
        self.rotation = rotation
            
        if filename and len(filename) > 0:
            image = gui.get_renderer().loadbitmap(filename, cache=self.bitmapcache)
        else:
            # Using Container-Image
            image = item.loadimage()
            
        if not image:
            # txt = gui.Text(_('Can\'t Open Image\n\'%s\'') % (filename),
            #                config.OSD_OVERSCAN_X + 20,
            #                config.OSD_OVERSCAN_Y + 20,
            #                swidth - 2 * config.OSD_OVERSCAN_X - 40,
            #                sheight - 2 * config.OSD_OVERSCAN_Y - 40,
            #                self.osd.getfont(config.OSD_DEFAULT_FONTNAME,
            #                                 config.OSD_DEFAULT_FONTSIZE),
            #                fgcolor=self.osd.COL_ORANGE,
            #                align_h='center', align_v='center', mode='soft')
            # gui.get_screen.add('content', txt)
            # gui.get_screen.update()
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

            if isinstance(zoom, int):
                h, v = bb[zoom]
            else:
                h, v = bb[zoom[0]]
                
            # Bounding box center
            bbcx = ([1, 3, 5][h]) * width / 6
            bbcy = ([1, 3, 5][v]) * height / 6

            if self.rotation % 180:
                # different calculations because image width is screen height
                scale_x = float(swidth) / (height / 3)
                scale_y = float(sheight) / (width / 3)
                scale = min(scale_x, scale_y)

                # read comment for the bbw and bbh calculations below
                bbw = min(max((width / 3) * scale, sheight), width) / scale
                bbh = min(max((height / 3) * scale, swidth), height) / scale

            else:
                scale_x = float(swidth) / (width / 3)
                scale_y = float(sheight) / (height / 3)
                scale = min(scale_x, scale_y)

                # the bb width is the width / 3 * scale, to avoid black bars left
                # and right exapand it to the osd.width but not if this is more than the
                # image width (same for height)
                bbw = min(max((width / 3) * scale, swidth), width) / scale
                bbh = min(max((height / 3) * scale, sheight), height) / scale
                

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
            scale_x = float(swidth) / width
            scale_y = float(sheight) / height
            scale   = min(scale_x, scale_y)
            new_w, new_h = int(scale*width), int(scale*height)


        # Now we have all necessary informations about zoom yes/no and
        # the kind of rotation
        
        x = (swidth - new_w) / 2
        y = (sheight - new_h) / 2
        
        last_image = self.last_image[1]

        if not isinstance(zoom, int):
            # change zoom based on rotation
            if self.rotation == 90:  
                zoom = zoom[0], -zoom[2], zoom[1]
            if self.rotation == 180:  
                zoom = zoom[0], -zoom[1], -zoom[2]
            if self.rotation == 270:  
                zoom = zoom[0], zoom[2], -zoom[1]

            # don't move outside the image
            if bbx + zoom[1] < 0:
                zoom = zoom[0], -bbx, zoom[2]
            if bbx + zoom[1] > width - bbw:
                zoom = zoom[0], width - (bbw + bbx), zoom[2]
            if bby + zoom[2] < 0:
                zoom = zoom[0], zoom[1], -bby
            if bby + zoom[2] > height - bbh:
                zoom = zoom[0], zoom[1], height - (bbh + bby)

            # change bbx
            bbx += zoom[1]
            bby += zoom[2]

        # FIXME: bring back animation 
        # if (last_image and self.last_image[0] != item and
        #     config.IMAGEVIEWER_BLEND_MODE != None):
        #     screen = self.osd.screen.convert()
        #     screen.fill((0,0,0,0))
        #     screen.blit(self.osd.zoomsurface(image, scale, bbx, bby, bbw, bbh,
        #                                 rotation = self.rotation).convert(), (x, y))
        #     # update the OSD
        #     self.drawosd(layer=screen)
        
        #     blend = Transition(self.osd.screen, screen, config.IMAGEVIEWER_BLEND_MODE)
        #     blend.start()
        #     while not blend.finished:
        #         rc.poll()
        #     blend.remove()
        # else:

        image = gui.get_renderer().zoombitmap(image, scale, bbx, bby, bbw, bbh,
                                              rotation = self.rotation)
        image = gui.Image(x, y, x+image.get_size()[0], y+image.get_size()[1], image)

        if self.last_image[1]:
            screen.remove('bg', self.last_image[1])
        screen.add('bg', image)

        self.drawosd()
        screen.update()
        
        # start timer
        if self.fileitem.duration:
            signal.signal(signal.SIGALRM, self.signalhandler)
            signal.alarm(self.fileitem.duration)

        self.last_image = (item, image)

        # XXX Hack to move the selected item to the current showing image
        # XXX TODO: find a way to add it to directory.py or playlist.py
        if item.parent and hasattr(item.parent, 'menu') and item.parent.menu and \
               item in item.parent.menu.choices:
            item.parent.menu.selected = item
            item.menuw.force_page_rebuild = True

        # save zoom, but revert the rotation mix up
        if not isinstance(zoom, int) and self.rotation:
            if self.rotation == 90:  
                zoom = zoom[0], zoom[2], -zoom[1]
            if self.rotation == 180:  
                zoom = zoom[0], -zoom[1], -zoom[2]
            if self.rotation == 270:  
                zoom = zoom[0], -zoom[2], zoom[1]
        self.zoom = zoom
        return None


    def redraw(self):
        self.view(self.fileitem, zoom=self.zoom, rotation=self.rotation)

        
    def cache(self, fileitem):
        # cache the next image (most likely we need this)
        gui.get_renderer().loadbitmap(fileitem.filename, cache=self.bitmapcache)
        

    def signalhandler(self, signum, frame):
        print 'signal'
        if eventhandler.get() == self and self.slideshow:
            eventhandler.remove(self)
            self.eventhandler(PLAY_END)


    def eventhandler(self, event, menuw=None):
        if event == PAUSE or event == PLAY:
            if self.slideshow:
                eventhandler.post(Event(OSD_MESSAGE, arg=_('pause')))
                self.slideshow = False
                signal.alarm(0)
            else:
                eventhandler.post(Event(OSD_MESSAGE, arg=_('play')))
                self.slideshow = True
                signal.alarm(1)
            return True
        
        elif event == STOP:
            print 'clear image viewer'
            
            screen = gui.get_screen()
            if self.last_image[1]:
                screen.remove('bg', self.last_image[1])
            self.last_image = (None, None)

            if self.osd_text:
                screen.remove('content', self.osd_text)
                self.osd_text = None
            if self.osd_box:
                screen.remove('alpha', self.osd_box)
                self.osd_box = None

            self.filename = None
            eventhandler.remove(self)
            signal.alarm(0)
            self.fileitem.eventhandler(event)
            return True


        # up and down will stop the slideshow and pass the
        # event to the playlist
        elif event == PLAYLIST_NEXT or event == PLAYLIST_PREV:
            self.slideshow = False
            signal.alarm(0)
            self.fileitem.eventhandler(event)
            return True
            
        # rotate image
        elif event == IMAGE_ROTATE:
            if event.arg == 'left':
                self.rotation = (self.rotation + 270) % 360
            else:
                self.rotation = (self.rotation + 90) % 360
            self.fileitem['rotation'] = self.rotation
            self.view(self.fileitem, zoom=self.zoom, rotation=self.rotation)
            return True

        # print image information
        elif event == TOGGLE_OSD:
            self.osd_mode = (self.osd_mode + 1) % (len(config.IMAGEVIEWER_OSD) + 1)
            # Redraw
            self.view(self.fileitem, zoom=self.zoom, rotation = self.rotation)
            return True

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
            return True                

        elif event == IMAGE_MOVE:
            coord = event.arg
            if isinstance(self.zoom, int):
                self.zoom = self.zoom, coord[0], coord[1]
            else:
                self.zoom = self.zoom[0], self.zoom[1] + coord[0], self.zoom[2] + coord[1]
            self.view(self.fileitem, zoom=self.zoom, rotation = self.rotation)
            return True
        
        # save the image with the current rotation
        elif event == IMAGE_SAVE:
            if self.rotation and os.path.splitext(self.filename)[1] == ".jpg":
                cmd = 'jpegtran -copy all -rotate %s -outfile /tmp/freevo-iview %s' \
                      % ((self.rotation + 180) % 360, self.filename)
                os.system(cmd)
                os.system('mv /tmp/freevo-iview %s' % self.filename)
                self.rotation = 0
                gui.get_renderer().bitmapcache.__delitem__(self.filename)
                return True                

        else:
            return self.fileitem.eventhandler(event)

            
    def drawosd(self):
        """
        draw the image osd
        """
        screen = gui.get_screen()
        newosd = True
        
        # remove old osd text:
        if self.osd_text:
            screen.remove('content', self.osd_text)
            self.osd_text = None
            newosd = False


        if not self.osd_mode:
            # remove old osd bar:
            if self.osd_box:
                screen.remove('alpha', self.osd_box)
                self.osd_box = None
            return

        swidth  = gui.get_screen().width
        sheight = gui.get_screen().height

        osdstring = u''
        for strtag in config.IMAGEVIEWER_OSD[self.osd_mode-1]:
            i = self.fileitem.getattr(strtag[1])
            if i:
                osdstring += u' %s %s' % (Unicode(strtag[0]), Unicode(i))
        
	# If after all that there is nothing then tell the users that
	if osdstring == '':
	    osdstring = _('No information available')
        else:
            osdstring = osdstring[1:]
            
        self.osd_text = gui.Text(config.OSD_OVERSCAN_X + 10, config.OSD_OVERSCAN_Y + 10,
                                 screen.width - config.OSD_OVERSCAN_X - 10,
                                 screen.height - config.OSD_OVERSCAN_Y -10,
                                 osdstring, gui.get_font('default'),
                                 screen.height - 2 * config.OSD_OVERSCAN_Y - 20,
                                 'left', 'bottom', mode='soft')

        rect = self.osd_text.calculate()[1]
        if rect[1] > screen.height - config.OSD_OVERSCAN_Y - 100:
            # text too small, enhance it
            self.osd_text.y1 = screen.height - config.OSD_OVERSCAN_Y - 100
            self.osd_text.align_v = 'top'
            self.osd_text.modified()
        else:
            # fit in rect to avoid complete redraw
            self.osd_text.set_position(rect[0], rect[1], rect[2], rect[3])

        rect = self.osd_text.calculate()[1]

        # now draw a box around the osd
        r = gui.Rectangle(-2, rect[1] - 10, screen.width+2, screen.height+2,
                          0xaa000000, 2, 0xffffff, 1)

        if r != self.osd_box:
            if self.osd_box:
                screen.remove('alpha', self.osd_box)
            self.osd_box = r
            screen.add('alpha', self.osd_box)

        screen.add('content', self.osd_text)

        # FIXME: better integration, just a performance test
        if newosd:
            print 'let us animate the osd input'
            max_height = self.osd_box.height

            for o in (self.osd_box, self.osd_text):
                o.set_position(o.x1, o.y1 + max_height, o.x2, o.y2 + max_height)

            screen.update()
            for i in range(max_height / 4):
                for o in (self.osd_box, self.osd_text):
                    o.set_position(o.x1, o.y1 - 4, o.x2, o.y2 - 4)
                screen.update()
                
