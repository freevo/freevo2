# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# viewer.py - Freevo image viewer
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2006 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
# -----------------------------------------------------------------------------

__all__ = [ 'viewer' ]

# python imports
import os
import logging

# kaa imports
import kaa.notifier
from kaa.strutils import to_unicode

# freevo imports
from freevo.ui import plugin, gui
from freevo.ui.gui import theme, imagelib, widgets
from freevo.ui.config import config

# cache for loading images
from freevo.ui.util import ObjectCache

# Transition/Move/VERTICAL
from freevo.ui.gui.animation import *

from freevo.ui.event import *
from freevo.ui.application import Application, STATUS_RUNNING, STATUS_STOPPING, \
     STATUS_STOPPED, STATUS_IDLE, CAPABILITY_TOGGLE, CAPABILITY_FULLSCREEN

# get logging object
log = logging.getLogger('image')

# global viewer, will be set to the ImageViewer
viewer = None

# gui.display.overscan config
overscan = config.gui.display.overscan
# set config to image.viewer config
config = config.image.viewer

# FIXME: this belongs to the theme
IMAGEVIEWER_OSD = [
    # First OSD info
    [ (_('Title')+': ',      'name'),
      (_('Description')+': ','description'),
      (_('Author')+': ',     'author') ],

    # Second OSD info
    [ (_('Title')+': ',    'name'),
      (_('Date')+': ' ,    'date'),
      ('W:',               'width'),
      ('H:',               'height'),
      (_('Model')+': ',    'hardware'),
      (_('Software')+': ', 'software') ]
    ]

class ImageViewer(Application):
    """
    Full screen image viewer for imageitems
    """
    def __init__(self):
        """
        create an image viewer application
        """
        capabilities = (CAPABILITY_TOGGLE, CAPABILITY_FULLSCREEN)
        Application.__init__(self, 'imageviewer', 'image', capabilities)

        self.osd_mode = 0    # Draw file info on the image
        self.zoom = 0   # Image zoom
        self.zoom_btns = { str(IMAGE_NO_ZOOM):0, str(IMAGE_ZOOM_GRID1):1,
                           str(IMAGE_ZOOM_GRID2):2, str(IMAGE_ZOOM_GRID3):3,
                           str(IMAGE_ZOOM_GRID4):4, str(IMAGE_ZOOM_GRID5):5,
                           str(IMAGE_ZOOM_GRID6):6, str(IMAGE_ZOOM_GRID7):7,
                           str(IMAGE_ZOOM_GRID8):8, str(IMAGE_ZOOM_GRID9):9 }
        self.bitmapcache = ObjectCache(3, desc='viewer')
        self.slideshow   = True
        self.last_image  = None
        self.last_item   = None
        self.osd_text    = None
        self.osd_box     = None
        self.filename    = None
        self.rotation    = None
        self.zomm        = None
        self.sshow_timer = kaa.notifier.OneShotTimer(self._next)
        self.signals['stop'].connect_weak(self._cleanup)


    def _cleanup(self):
        """
        Application not running anymore, free cache and remove items
        from the screen.
        """
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
        self.sshow_timer.stop()
        # reset bitmap cache
        self.bitmapcache = ObjectCache(3, desc='viewer')


    def _next(self):
        """
        Send PLAY_END to show next image.
        """
        event = Event(PLAY_END, self.item)
        event.set_handler(self.eventhandler)
        event.post()


    def view(self, item, zoom=0, rotation=0):
        """
        Show the image
        """
        if zoom:
            self.set_eventmap('image_zoom')
        else:
            self.set_eventmap('image')

        filename      = item.filename
        self.item = item

        if not self.last_item:
            # We just started, update the screen to make it
            # empty (all hides from the menu are updated)
            self.engine.update()

        self.status = STATUS_RUNNING

        # only load new image when the image changed
        if self.filename == filename and self.rotation == rotation and \
               len(filename) > 0:
            if self.zoom == zoom:
                # same image, only update the osd and the timer
                self.drawosd()
                self.engine.update()
                return
            if not isinstance(zoom, int):
                # only zoom change
                self.last_image.set_pos((-zoom[0], -zoom[1]))
                self.zoom = zoom
                self.engine.update()
                return
            if self.zoom and zoom:
                log.info('FIXME: do not create the complete image again')

        self.filename = filename
        self.rotation = rotation

        if filename and len(filename) > 0:
            image = self.bitmapcache[filename]
            if not image:
                image = imagelib.load(filename)
                self.bitmapcache[filename] = image
        else:
            # Using Container-Image
            image = item.loadimage()

        if not image:
            # FIXME: add error message to the screen
            return

        width, height = image.width, image.height
        gui_width = gui.get_display().width
        gui_height = gui.get_display().height

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
            scale_x = float(gui_width*3) / width
            scale_y = float(gui_height*3) / height
            scale   = min(scale_x, scale_y)

            # create bbx and bby were to start showing the zoomed image
            bbx, bby = int(scale*bbx), int(scale*bby)
            if int(width*scale) - bbx < gui_width:
                bbx = int(width*scale) - gui_width
            if int(height*scale) - bby < gui_height:
                bby = int(height*scale) - gui_height
            # calculate new width and height after scaling
            width  = int(scale * 3 * width)
            height = int(scale * 3 * height)


        else:
            # No zoom, scale image that it fits the screen
            scale_x = float(gui_width) / width
            scale_y = float(gui_height) / height
            scale   = min(scale_x, scale_y)
            # calculate new width and height after scaling
            width  = int(scale * width)
            height = int(scale * height)

        # Now we have all necessary informations about zoom yes/no and
        # the kind of rotation
        x = max((gui_width - width) / 2, 0)
        y = max((gui_height - height) / 2, 0)

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
            image = widgets.Image(image, (x-bbx, y-bby))
            zoom = bbx, bby
        else:
            # position image at x/y value
            image = widgets.Image(image, (x, y))

        if (self.last_image and self.last_item != item and
            config.blend_mode != 'none'):
            # blend over to the new image
            gui.get_display().add_child(image)
            a = Transition([self.last_image], [image], 20,
                           (gui_width, gui_height), config.blend_mode)
            # start the animation and wait until it's done
            a.start()
            a.wait()
        else:
            # add the new image
            gui.get_display().add_child(image)

        # remove the last image if there is one
        if self.last_image:
            self.last_image.unparent()

        # draw the osd
        self.drawosd()

        # update the screen
        self.engine.update()

        # start timer
        if self.item.duration and self.slideshow and \
               not self.sshow_timer.active():
            self.sshow_timer.start(self.item.duration)

        # Notify everyone about the viewing
        if self.last_item != item:
            PLAY_START.post(item)

        self.last_image = image
        self.last_item  = item

        self.zoom = zoom
        return None


    def stop(self):
        """
        Stop the current viewing
        """
        if self.get_status() != STATUS_RUNNING:
            # already stopped
            return True
        # set status to stopping
        self.status = STATUS_STOPPING
        event = Event(PLAY_END, self.item)
        event.set_handler(self.eventhandler)
        event.post()


    def cache(self, item):
        """
        Cache the next image (most likely we need this)
        """
        if item.filename and len(item.filename) > 0 and \
               not self.bitmapcache[item.filename]:
            image = imagelib.load(item.filename)
            self.bitmapcache[item.filename] = image


    def eventhandler(self, event):
        """
        Handle incoming events
        """
        if event == PAUSE or event == PLAY:
            if self.slideshow:
                OSD_MESSAGE.post(_('pause'))
                self.slideshow = False
                self.sshow_timer.stop()
            else:
                OSD_MESSAGE.post(_('play'))
                self.slideshow = True
                self.sshow_timer.start(1)
            return True

        if event == STOP:
            self.stop()
            self.item.eventhandler(event)
            return True

        if event == PLAYLIST_NEXT or event == PLAYLIST_PREV:
            # up and down will stop the slideshow and pass the
            # event to the playlist
            self.sshow_timer.stop()
            self.item.eventhandler(event)
            return True

        if event == PLAY_END:
            # Viewing is done, set application to stopped
            self.status = STATUS_STOPPED
            self.item.eventhandler(event)
            if self.status == STATUS_STOPPED:
                self.status = STATUS_IDLE
            return True

        if event == IMAGE_ROTATE:
            # rotate image
            if event.arg == 'left':
                rotation = (self.rotation + 270) % 360
            else:
                rotation = (self.rotation + 90) % 360
            self.item['rotation'] = rotation
            self.view(self.item, zoom=self.zoom, rotation=rotation)
            return True

        if event == TOGGLE_OSD:
            # show/hide image information
            self.osd_mode = (self.osd_mode+1) % (len(IMAGEVIEWER_OSD)+1)
            self.drawosd()
            self.engine.update()
            return True

        if str(event) in self.zoom_btns:
            # zoom to one third of the image
            # 1 is upper left, 9 is lower right, 0 zoom off
            zoom = self.zoom_btns[str(event)]
            if zoom:
                # Zoom one third of the image, don't load the next
                # image in the list
                self.view(self.item, zoom=zoom, rotation=self.rotation)
            else:
                # Display entire picture, don't load next image in case
                # the user wants to zoom around some more.
                self.view(self.item, zoom=0, rotation=self.rotation)
            return True

        if event == IMAGE_MOVE:
            # move inside a zoomed image
            coord = event.arg   # arg are absolute x,y positions
            zoom = self.zoom[0] + coord[0], self.zoom[1] + coord[1]
            self.view(self.item, zoom=zoom, rotation=self.rotation)
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
        return self.item.eventhandler(event)


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
        for strtag in IMAGEVIEWER_OSD[self.osd_mode-1]:
            i = str(self.item[strtag[1]])
            if i:
                osdstring += u' %s %s' % (to_unicode(strtag[0]), to_unicode(i))

	if osdstring == '':
            # If after all that there is nothing then tell the users that
	    osdstring = _('No information available')
        else:
            # remove the first space from the string
            osdstring = osdstring[1:]

        gui_width = gui.get_display().width
        gui_height = gui.get_display().height

        # create the text widget
        pos = (overscan.x + 10, overscan.y + 10)
        size = (gui_width - 2 * overscan.x - 20,
                gui_height - 2 * overscan.y - 20)
        self.osd_text = widgets.Textbox(osdstring, pos, size,
                                        theme.font('default'),
                                        'left', 'bottom', mode='soft')
        # add the text widget to the screen, make sure the zindex
        # is 2 (== above the image and the box)
        self.osd_text.set_zindex(2)
        gui.get_display().add_child(self.osd_text)

        # create a box around the text
        rect = self.osd_text.get_size()

        if rect[1] < 100:
            # text too small, set to a minimum position
            self.osd_text.set_pos((self.osd_text.get_pos()[0], gui_height - \
                                   overscan.y - 100))
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
        size = (gui_width, rect[1] + 20)
        background = imagelib.load('background', (gui_width, gui_height))
        if background:
            background.crop(pos, size)
            self.osd_box = widgets.Image(background, pos)
            self.osd_box.set_alpha(230)
        if not background:
            self.osd_box = widgets.Rectangle(pos, size, 0xaa000000L)

        # put the rectangle on the screen and set the zindex to 1
        # (between image and text)
        self.osd_box.set_zindex(1)
        gui.get_display().add_child(self.osd_box)

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

# set viewer object
viewer = ImageViewer()
