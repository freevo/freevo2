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
# Revision 1.64  2004/08/23 14:33:45  dischi
# oops, revert last change
#
# Revision 1.63  2004/08/23 14:31:38  dischi
# support new animation code
#
# Revision 1.62  2004/08/23 12:38:44  dischi
# adjust to new display code
#
# Revision 1.61  2004/08/22 20:16:52  dischi
# update to new mevas based gui code
#
# Revision 1.60  2004/08/05 17:31:59  dischi
# remove bad hack
#
# Revision 1.59  2004/08/01 10:44:40  dischi
# make the viewer an "Application"
#
# Revision 1.58  2004/07/27 18:53:07  dischi
# switch to new layer code and add basic animation support
#
# Revision 1.57  2004/07/26 18:10:18  dischi
# move global event handling to eventhandler.py
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


import os

import config 
import util
import rc
import plugin
import gui

from event import *
from eventhandler import Application
import gui.animation as animation


_singleton = None

def get_singleton():
    global _singleton
    if _singleton == None:
        _singleton = ImageViewer()
    return _singleton



class ImageViewer(Application):
    """
    Full screen image viewer for imageitems
    """
    def __init__(self):
        """
        create an image viewer application
        """
        Application.__init__(self, 'image viewer', 'image', True)

        self.osd_mode = 0    # Draw file info on the image
        self.zoom = 0   # Image zoom
        self.zoom_btns = { str(IMAGE_NO_ZOOM):0, str(IMAGE_ZOOM_GRID1):1,
                           str(IMAGE_ZOOM_GRID2):2, str(IMAGE_ZOOM_GRID3):3,
                           str(IMAGE_ZOOM_GRID4):4, str(IMAGE_ZOOM_GRID5):5,
                           str(IMAGE_ZOOM_GRID6):6, str(IMAGE_ZOOM_GRID7):7,
                           str(IMAGE_ZOOM_GRID8):8, str(IMAGE_ZOOM_GRID9):9 }

        self.slideshow   = False
        self.last_image  = (None, None)
        self.bitmapcache = util.objectcache.ObjectCache(3, desc='viewer')
        self.osd_text    = None
        self.osd_box     = None

        self.filename    = None
        self.rotation    = None
        self.zomm        = None


    def destroy(self):
        """
        Destroy the viewer. This clears the cache and removes the application
        from the eventhandler stack. It is still possible to show() this
        object again.
        """
        Application.destroy(self)
        _debug_('destroy image viewer')
        self.bitmapcache = util.objectcache.ObjectCache(3, desc='viewer')
        
        
    def view(self, item, zoom=0, rotation=0):
        """
        Show the image
        """
        if zoom:
            self.evt_context = 'image_zoom'
        else:
            self.evt_context = 'image'

        filename      = item.filename
        self.fileitem = item

        self.show()

        if not self.last_image[0]:
            gui.display.update()

        # only load new image when the image changed
        if self.filename == filename and self.zoom == zoom and \
           self.rotation == rotation and len(filename) > 0:
            # same image, only update the osd and the timer
            self.drawosd()
            gui.display.update()
            return
        
        self.filename = filename
        self.rotation = rotation
            
        if filename and len(filename) > 0:
            image = gui.imagelib.load(filename, cache=self.bitmapcache)
        else:
            # Using Container-Image
            image = item.loadimage()
            
        if not image:
            # txt = gui.Text(_('Can\'t Open Image\n\'%s\'') % (filename),
            #                config.OSD_OVERSCAN_X + 20,
            #                config.OSD_OVERSCAN_Y + 20,
            #                gui.width - 2 * config.OSD_OVERSCAN_X - 40,
            #                gui.height - 2 * config.OSD_OVERSCAN_Y - 40,
            #                self.osd.getfont(config.OSD_DEFAULT_FONTNAME,
            #                                 config.OSD_DEFAULT_FONTSIZE),
            #                fgcolor=self.osd.COL_ORANGE,
            #                align_h='center', align_v='center', mode='soft')
            return
        
        width, height = image.width, image.height
            
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
                scale_x = float(gui.width) / (height / 3)
                scale_y = float(gui.height) / (width / 3)
                scale = min(scale_x, scale_y)

                # read comment for the bbw and bbh calculations below
                bbw = min(max((width / 3) * scale, gui.height), width) / scale
                bbh = min(max((height / 3) * scale, gui.width), height) / scale

            else:
                scale_x = float(gui.width) / (width / 3)
                scale_y = float(gui.height) / (height / 3)
                scale = min(scale_x, scale_y)

                # the bb width is the width / 3 * scale, to avoid black bars left
                # and right exapand it to the osd.width but not if this is more than the
                # image width (same for height)
                bbw = min(max((width / 3) * scale, gui.width), width) / scale
                bbh = min(max((height / 3) * scale, gui.height), height) / scale
                

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
            scale_x = float(gui.width) / width
            scale_y = float(gui.height) / height
            scale   = min(scale_x, scale_y)
            new_w, new_h = int(scale*width), int(scale*height)


        # Now we have all necessary informations about zoom yes/no and
        # the kind of rotation
        
        x = (gui.width - new_w) / 2
        y = (gui.height - new_h) / 2
        
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

        image = image.copy()
        # get bounding box
        if bbw and bbh and (bbw != gui.width or bbh != gui.height):
            image.crop((bbx, bby), (bbw, bbh))

        # scale to fit
        if scale != 1 and scale != 0:
            image.scale((int(float(image.width) * scale),
                         int(float(image.height) * scale)))
            
        # rotate
        if self.rotation:
            image.rotate(self.rotation)

        image = gui.Image(image, (x, y))


        if (last_image and self.last_image[0] != item and
            config.IMAGEVIEWER_BLEND_MODE != None):
            gui.display.add_child(image)

            if 0:
                import time
                t1 = time.time()

            frames = 20
            a = animation.Transition([self.last_image[1]], [image], frames,
                                     (gui.width, gui.height))
            a.start()
            while a.running():
                animation.render().update()

            if 0:
                t2 = time.time()
                print "Animation took", t2-t1, " - frames", frames, \
                      " - %.2f fps" % (frames/(t2-t1))

            if self.last_image[1]:
                self.last_image[1].unparent()

        else:
            if self.last_image[1]:
                self.last_image[1].unparent()
            gui.display.add_child(image)
        
        self.drawosd()
        gui.display.update()
        
        # start timer
        if self.fileitem.duration:
            rc.register(self.signalhandler, False, self.fileitem.duration)
            self.slideshow = True
            
        self.last_image = (item, image)

        # XXX Hack to move the selected item to the current showing image
        if item.parent and hasattr(item.parent, 'menu') and item.parent.menu and \
               item in item.parent.menu.choices:
            item.parent.menu.set_selection(item)

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


    def cache(self, fileitem):
        """
        cache the next image (most likely we need this)
        """
        if fileitem.filename and len(fileitem.filename) > 0:
            gui.imagelib.load(fileitem.filename, cache=self.bitmapcache)
        

    def signalhandler(self):
        """
        time is up for slideshow
        """
        self.hide()
        self.eventhandler(PLAY_END)
        self.slideshow = False
        

    def eventhandler(self, event, menuw=None):
        """
        handle incoming events
        """
        if event == PAUSE or event == PLAY:
            if self.slideshow:
                self.post_event(Event(OSD_MESSAGE, arg=_('pause')))
                self.slideshow = False
                rc.unregister(self.signalhandler)
            else:
                self.post_event(Event(OSD_MESSAGE, arg=_('play')))
                self.slideshow = True
                rc.register(self.signalhandler, False, 100)
            return True
        
        if event == STOP:
            _debug_('event == STOP: clear image viewer')
            if self.last_image[1]:
                self.last_image[1].unparent()
            self.last_image = (None, None)

            if self.osd_text:
                self.osd_text.unparent()
                self.osd_text = None
            if self.osd_box:
                self.osd_box.unparent()
                self.osd_box = None

            self.destroy()
            self.filename = None
            self.slideshow = False
            rc.unregister(self.signalhandler)
            return True


        # up and down will stop the slideshow and pass the
        # event to the playlist
        if event == PLAYLIST_NEXT or event == PLAYLIST_PREV:
            self.slideshow = False
            rc.unregister(self.signalhandler)
            self.fileitem.eventhandler(event)
            return True
            
        # rotate image
        if event == IMAGE_ROTATE:
            if event.arg == 'left':
                rotation = (self.rotation + 270) % 360
            else:
                rotation = (self.rotation + 90) % 360
            self.fileitem['rotation'] = rotation
            self.view(self.fileitem, zoom=self.zoom, rotation=rotation)
            return True

        # show/hide image information
        if event == TOGGLE_OSD:
            self.osd_mode = (self.osd_mode + 1) % (len(config.IMAGEVIEWER_OSD) + 1)
            self.drawosd()
            gui.display.update()
            return True

        # zoom to one third of the image
        # 1 is upper left, 9 is lower right, 0 zoom off
        if str(event) in self.zoom_btns:
            zoom = self.zoom_btns[str(event)]
            if zoom:
                # Zoom one third of the image, don't load the next
                # image in the list
                self.view(self.fileitem, zoom=zoom, rotation=self.rotation)
            else:
                # Display entire picture, don't load next image in case
                # the user wants to zoom around some more.
                self.view(self.fileitem, zoom=0, rotation=self.rotation)
            return True                

        if event == IMAGE_MOVE:
            coord = event.arg
            if isinstance(self.zoom, int):
                zoom = self.zoom, coord[0], coord[1]
            else:
                zoom = self.zoom[0], self.zoom[1] + coord[0], self.zoom[2] + coord[1]
            self.view(self.fileitem, zoom=zoom, rotation=self.rotation)
            return True
        
        # save the image with the current rotation
        if event == IMAGE_SAVE:
            if self.rotation and os.path.splitext(self.filename)[1] == ".jpg":
                cmd = 'jpegtran -copy all -rotate %s -outfile /tmp/freevo-iview %s' \
                      % ((self.rotation + 180) % 360, self.filename)
                os.system(cmd)
                os.system('mv /tmp/freevo-iview %s' % self.filename)
                self.rotation = 0
            return True                

        return self.fileitem.eventhandler(event)

            
    def drawosd(self):
        """
        draw the image osd
        """
        newosd = True
        
        # remove old osd text:
        if self.osd_text:
            self.osd_text.unparent()
            self.osd_text = None
            newosd = False


        if not self.osd_mode:
            # remove old osd bar:
            if self.osd_box:
                self.osd_box.unparent()
                self.osd_box = None
            plugin.getbyname('idlebar').hide()
            return

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
            
        self.osd_text = gui.Textbox(osdstring,
                                    (config.OSD_OVERSCAN_X + 10, config.OSD_OVERSCAN_Y + 10),
                                    (gui.width - 2 * config.OSD_OVERSCAN_X - 20,
                                     gui.height - 2 * config.OSD_OVERSCAN_Y - 20),
                                    gui.get_font('default'), 'left', 'bottom', mode='soft')
        self.osd_text.set_zindex(2)
        gui.display.add_child(self.osd_text)

        rect = self.osd_text.get_size()

        if rect[1] < 100:
            # text too small, set to a minimum position
            self.osd_text.set_pos((self.osd_text.get_pos()[0], gui.height - \
                                   config.OSD_OVERSCAN_Y - 100))
            rect = rect[0], 100
            
        # now draw a box around the osd
        if self.osd_box:
            # check if the old one is ok for us
            if self.osd_box.get_size()[1] == rect[1] + 20:
                # perfect match, no need to redraw
                return
            self.osd_box.unparent()


        # build a new rectangle.
        pos  = (0, self.osd_text.get_pos()[1] - 10)
        size = (gui.width, rect[1] + 20)
        background = gui.imagelib.load('background', (gui.width, gui.height))
        if background:
            background.crop(pos, size)
            self.osd_box = gui.Image(background, pos)
            self.osd_box.set_alpha(230)
        if not background:
            self.osd_box = gui.Rectangle(pos, size, 0xaa000000)

        self.osd_box.set_zindex(1)
        gui.display.add_child(self.osd_box)
        
        # FIXME: better integration, just a performance test
        if newosd:
            # show the idlebar but not update the screen now
            plugin.getbyname('idlebar').show(False)

            _debug_('Test code: animate the osd input')

            move_y = self.osd_box.get_size()[1]

            for o in (self.osd_box, self.osd_text):
                x, y = o.get_pos()
                _debug_('hide %s at %s' % (o, y + move_y))
                o.set_pos((x, y + move_y))

            a = animation.Move([self.osd_box, self.osd_text], animation.VERTICAL, 20, -move_y)
            a.start()
            while a.running():
                animation.render().update()
