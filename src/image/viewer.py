# -*- coding: iso-8859-1 -*-
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
# Revision 1.71  2004/10/06 19:24:01  dischi
# switch from rc.py to pyNotifier
#
# Revision 1.70  2004/09/13 18:00:50  dischi
# last cleanups for the image module in Freevo
#
# Revision 1.69  2004/09/12 21:19:36  mikeruelle
# for those of us without idlebars
#
# Revision 1.68  2004/09/07 18:57:43  dischi
# image viwer auto slideshow
#
# Revision 1.67  2004/08/27 14:22:01  dischi
# The complete image code is working again and should not crash. The zoom
# handling got a complete rewrite. Only the gphoto plugin is not working
# yet because my camera is a storage device.
#
# Revision 1.66  2004/08/25 12:51:45  dischi
# moved Application for eventhandler into extra dir for future templates
#
# Revision 1.65  2004/08/23 20:36:42  dischi
# rework application handling
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

__all__ = [ 'imageviewer' ]

# external imports
import notifier

# python imports
import os

# freevo imports
import config
import util
import plugin
import gui

# Transition/Move/VERTICAL
from gui.animation import *

from event import *
from application import Application


_singleton = None

def imageviewer():
    """
    return the global image viewer object
    """
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
        self.bitmapcache = util.objectcache.ObjectCache(3, desc='viewer')
        self.slideshow   = True
        self.last_image  = None
        self.last_item   = None
        self.osd_text    = None
        self.osd_box     = None
        self.filename    = None
        self.rotation    = None
        self.zomm        = None
        self._timer_id   = None


    def hide(self):
        """
        Hide the viewer. This clears the cache and removes the application
        from the eventhandler stack. It is still possible to show() this
        object again.
        """
        Application.hide(self)
        if self.last_image:
            self.last_image.unparent()
        self.last_image = None
        self.last_item  = None

        # remove the osd
        if self.osd_text:
            self.osd_text.unparent()
            self.osd_text = None
        if self.osd_box:
            self.osd_box.unparent()
            self.osd_box = None

        self.osd_mode = 0
        self.filename = None
        # we don't need the signalhandler anymore
        notifier.removeTimer( self._timer_id )
        self._timer_id = None
        # reset bitmap cache
        self.bitmapcache = util.objectcache.ObjectCache(3, desc='viewer')


    def view(self, item, zoom=0, rotation=0):
        """
        Show the image
        """
        if zoom:
            self.set_event_context('image_zoom')
        else:
            self.set_event_context('image')

        filename      = item.filename
        self.fileitem = item

        self.show()

        if not self.last_item:
            # We just started, update the screen to make it
            # empty (all hides from the menu are updated)
            gui.display.update()

        # only load new image when the image changed
        if self.filename == filename and self.rotation == rotation and \
               len(filename) > 0:
            if self.zoom == zoom:
                # same image, only update the osd and the timer
                self.drawosd()
                gui.display.update()
                return
            if not isinstance(zoom, int):
                # only zoom change
                self.last_image.set_pos((-zoom[0], -zoom[1]))
                self.zoom = zoom
                gui.display.update()
                return
            if self.zoom and zoom:
                _debug_('FIXME: do not create the complete image again')

        self.filename = filename
        self.rotation = rotation

        if filename and len(filename) > 0:
            image = gui.imagelib.load(filename, cache=self.bitmapcache)
        else:
            # Using Container-Image
            image = item.loadimage()

        if not image:
            # FIXME: add error message to the screen
            return

        width, height = image.width, image.height

        # Bounding box default values
        bbx = bby = bbw = bbh = 0

        if self.rotation % 180:
            height, width = width, height

        if zoom:
            # Translate the 9-element grid to bounding boxes
            bb = { 1:(0,0), 2:(1,0), 3:(2,0),
                   4:(0,1), 5:(1,1), 6:(2,1),
                   7:(0,2), 8:(1,2), 9:(2,2) }

            # get bbx and bby were to start showing
            bbx = (bb[zoom][0] * width) / 3
            bby = (bb[zoom][1] * height) / 3

            # calculate the scaling that the image is 3 times that big
            # as the screen (3 times because we have a 3x3 grid)
            scale_x = float(gui.width*3) / width
            scale_y = float(gui.height*3) / height
            scale   = min(scale_x, scale_y)

            # create bbx and bby were to start showing the zoomed image
            bbx, bby = int(scale*bbx), int(scale*bby)
            if int(width*scale) - bbx < gui.width:
                bbx = int(width*scale) - gui.width
            if int(height*scale) - bby < gui.height:
                bby = int(height*scale) - gui.height
            # calculate new width and height after scaling
            width  = int(scale * 3 * width)
            height = int(scale * 3 * height)


        else:
            # No zoom, scale image that it fits the screen
            scale_x = float(gui.width) / width
            scale_y = float(gui.height) / height
            scale   = min(scale_x, scale_y)
            # calculate new width and height after scaling
            width  = int(scale * width)
            height = int(scale * height)

        # Now we have all necessary informations about zoom yes/no and
        # the kind of rotation
        x = max((gui.width - width) / 2, 0)
        y = max((gui.height - height) / 2, 0)

        # copy the image because we will change it (scale, rotate)
        image = image.copy()

        # scale to fit
        if scale != 1 and scale != 0:
            image.scale((int(float(image.width) * scale),
                         int(float(image.height) * scale)))

        # rotate
        if self.rotation:
            image.rotate(self.rotation)

        if zoom:
            # position image at bbx and bby
            image = gui.Image(image, (x-bbx, y-bby))
            zoom = bbx, bby
        else:
            # position image at x/y value
            image = gui.Image(image, (x, y))

        if (self.last_image and self.last_item != item and
            config.IMAGEVIEWER_BLEND_MODE != None):
            # blend over to the new image
            gui.display.add_child(image)
            a = Transition([self.last_image], [image], 20,
                           (gui.width, gui.height))
            # start the animation and wait until it's done
            a.start()
            a.wait()
        else:
            # add the new image
            gui.display.add_child(image)

        # remove the last image if there is one
        if self.last_image:
            self.last_image.unparent()

        # draw the osd
        self.drawosd()

        # update the screen
        gui.display.update()

        # start timer
        if self.fileitem.duration and self.slideshow and \
               self._timer_id == None:
            cb = notifier.Callback( self.fileitem.duration * 1000 )
            self._timer_id = notifier.addTimer( self.signalhandler, cb )

        self.last_image = image
        self.last_item  = item

        # XXX Hack to move the selected item to the current showing image
        if item.parent and hasattr(item.parent, 'menu') and \
               item.parent.menu and item in item.parent.menu.choices:
            item.parent.menu.set_selection(item)
        self.zoom = zoom
        return None


    def stop(self):
        """
        Stop the current viewing
        """
        Application.stop(self)


    def cache(self, fileitem):
        """
        Cache the next image (most likely we need this)
        """
        if fileitem.filename and len(fileitem.filename) > 0:
            gui.imagelib.load(fileitem.filename, cache=self.bitmapcache)


    def signalhandler(self):
        """
        This signalhandler is called for slideshows when
        the duration is over.
        """
        self.hide()
        self._timer_id = None
        self.eventhandler(PLAY_END)

        return False

    def eventhandler(self, event, menuw=None):
        """
        handle incoming events
        """
        if event == PAUSE or event == PLAY:
            if self.slideshow:
                self.post_event(Event(OSD_MESSAGE, arg=_('pause')))
                self.slideshow = False
                notifier.removeTimer( self._timer_id )
                self._timer_id = None
            else:
                self.post_event(Event(OSD_MESSAGE, arg=_('play')))
                self.slideshow = True
                cb = notifier.Callback( 1000 )
                self._timer_id = notifier.addTimer( self.signalhandler, cb )
            return True

        if event == STOP:
            self.stop()
            return True

        if event == PLAYLIST_NEXT or event == PLAYLIST_PREV:
            # up and down will stop the slideshow and pass the
            # event to the playlist
            notifier.removeTimer( self._timer_id )
            self._timer_id = None
            self.fileitem.eventhandler(event)
            return True

        if event == IMAGE_ROTATE:
            # rotate image
            if event.arg == 'left':
                rotation = (self.rotation + 270) % 360
            else:
                rotation = (self.rotation + 90) % 360
            self.fileitem['rotation'] = rotation
            self.view(self.fileitem, zoom=self.zoom, rotation=rotation)
            return True

        if event == TOGGLE_OSD:
            # show/hide image information
            self.osd_mode = (self.osd_mode+1) % (len(config.IMAGEVIEWER_OSD)+1)
            self.drawosd()
            gui.display.update()
            return True

        if str(event) in self.zoom_btns:
            # zoom to one third of the image
            # 1 is upper left, 9 is lower right, 0 zoom off
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
            # move inside a zoomed image
            coord = event.arg   # arg are absolute x,y positions
            zoom = self.zoom[0] + coord[0], self.zoom[1] + coord[1]
            self.view(self.fileitem, zoom=zoom, rotation=self.rotation)
            return True

        if event == IMAGE_SAVE:
            # save the image with the current rotation
            if self.rotation and os.path.splitext(self.filename)[1] == ".jpg":
                cmd = 'jpegtran -copy all -rotate %s -outfile /tmp/fiview %s' \
                      % ((self.rotation + 180) % 360, self.filename)
                os.system(cmd)
                os.system('mv /tmp/fiview %s' % self.filename)
                self.rotation = 0
            return True

        # pass not handled event to the item
        return self.fileitem.eventhandler(event)


    def drawosd(self):
        """
        draw the image osd
        """
        if self.osd_text:
            # if osd_text is preset, remove it
            self.osd_text.unparent()
            self.osd_text = None
            newosd = False
        else:
            # it's a new osd, let it move in
            newosd = True

        if not self.osd_mode:
            # remove the bar, the osd is disabled
            if self.osd_box:
                self.osd_box.unparent()
                self.osd_box = None
            # also hide the idlebar to get 'fullscreen' back
            if plugin.getbyname('idlebar'):
                plugin.getbyname('idlebar').hide()
            return

        # create the osdstring to write
        osdstring = u''
        for strtag in config.IMAGEVIEWER_OSD[self.osd_mode-1]:
            i = self.fileitem.getattr(strtag[1])
            if i:
                osdstring += u' %s %s' % (Unicode(strtag[0]), Unicode(i))

	if osdstring == '':
            # If after all that there is nothing then tell the users that
	    osdstring = _('No information available')
        else:
            # remove the first space from the string
            osdstring = osdstring[1:]

        # create the text widget
        pos = (config.OSD_OVERSCAN_X + 10, config.OSD_OVERSCAN_Y + 10)
        size = (gui.width - 2 * config.OSD_OVERSCAN_X - 20,
                gui.height - 2 * config.OSD_OVERSCAN_Y - 20)
        self.osd_text = gui.Textbox(osdstring, pos, size,
                                    gui.get_font('default'),
                                    'left', 'bottom', mode='soft')
        # add the text widget to the screen, make sure the zindex
        # is 2 (== above the image and the box)
        self.osd_text.set_zindex(2)
        gui.display.add_child(self.osd_text)

        # create a box around the text
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

        # put the rectangle on the screen and set the zindex to 1
        # (between image and text)
        self.osd_box.set_zindex(1)
        gui.display.add_child(self.osd_box)

        if newosd:
            # show the idlebar but not update the screen now
            if plugin.getbyname('idlebar'):
                plugin.getbyname('idlebar').show(False)
            # get y movement value
            move_y = self.osd_box.get_size()[1]
            # hide the widgets to let them move in
            self.osd_box.move_relative((0, move_y))
            self.osd_text.move_relative((0, move_y))
            # start Move animation and wait for it to finish
            objects = [self.osd_box, self.osd_text]
            a = MoveAnimation(objects, VERTICAL, 20, -move_y)
            a.start()
            a.wait()
