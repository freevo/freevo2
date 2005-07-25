# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# detach.py - Detach plugin for the audio player
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains the audio detach plugin which makes it possible to detach
# from the usual player view. This makes it possible to browse files while
# still playing music. The plugin can optionally draw the current playing song
# info to the idlebar. Furthermore, when detached -- it is possible to control
# the player with the TOGGLE_CONTROL event.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: ?
# Maintainer:    Viggo Fredriksen <viggo@katatonic.org>
#
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
# -----------------------------------------------------------------------------

# python modules
import os.path
import kaa.mevas.image
import kaa.notifier

# freevo modules
import gui
import gui.imagelib
import gui.widgets
import gui.theme
import plugin
import config

from gui.animation.base import BaseAnimation
from plugins.idlebar    import IdleBarPlugin
from audio.player       import audioplayer
from audio.audioitem    import AudioItem
from controlpanel       import *
from event              import *

DETACH_AUDIO_STOP = Event('DETACH_AUDIO_STOP')


class PluginInterface(IdleBarPlugin):
    """
    A detached audioplayer view for freevo.
    """
    def __init__(self, show_detachbar=True):
        """
        init the idlebar
        """
        IdleBarPlugin.__init__(self)
        config.EVENTS['audio']['DISPLAY'] = Event(FUNCTION_CALL, self.detach)
        plugin.register(self, 'audio.detach')

        # register for events
        handler = kaa.notifier.EventHandler(self.eventhandler)
        handler.register((PLAY_START, DETACH_AUDIO_STOP))

        self.visible    = False
        self.detached   = False
        self.animation  = None
        self.controlbar = None
        self.y1         = 0
        self.w          = 0
        self.max_height = 50
        self.max_width  = 150
        self.item       = None
        self.show_detachbar = show_detachbar


    def draw(self, width, height):
        """
        Dummy method for the idlebar, only sets
        boundries for the detached bar to draw to.
        """
        if self.max_width > width:
            self.max_width = width
        if self.max_height > height:
            self.max_height = height

        self.y1 = int((height-self.max_height) / 2)

        if self.w == 0 or self.w == self.max_width:
            width = self.w
            self.w = self.NO_CHANGE
        else:
            width = self.w

        return width


    def detach(self,a=None):
        """
        Shows or hides the detached view
        according to its current status.
        """

        p = audioplayer()

        if self.visible:
            # hide the detached player show the player
            self.hide()
            p.show()
            self.detached = False

        else:
            # hide the audioplayer and show the itemmenu
            p.hide()

            # hack to make it work properly with overscan
            # resets the self.__x and self.__y variables
            self.clear()

            self.detached = True

            # show the detachbar
            # XXX FIXME: add config-var here
            self.show()


    def show(self):
        """
        Shows the detached view.
        """

        if self.visible:
            return

        # set up a controlbar
        a_handler = audioplayer().eventhandler
        path = os.path.join(config.ICON_DIR, 'misc','audio_')

        handlers = [ ( _('Prev'), '%sprev.png' % path,
                       a_handler, PLAYLIST_PREV),
                     ( _('Rew'), '%srew.png'  % path,
                       a_handler, Event(SEEK, -10)),
                     ( _('Pause'), '%spause.png'% path,
                       a_handler, PAUSE ),
                     ( _('Play'), '%splay.png' % path,
                       a_handler, PLAY ),
                     ( _('Stop'), '%sstop.png' % path,
                       self.eventhandler, STOP ),
                     ( _('FFwd'), '%sffwd.png' % path,
                       a_handler, Event(SEEK, 10)),
                     ( _('Next'), '%snext.png' % path,
                       a_handler, PLAYLIST_NEXT),
                     ( _('Show Player'), '%sshow.png' % path,
                       self.detach, None) ]

        self.controlbar = ButtonPanel( _('Audio Player'),
                                       handlers,
                                       default_action=3)

        controlpanel().register(self.controlbar)

        self.w       = self.max_width
        self.visible = True

        # do not show the detached view if not configured
        if not self.show_detachbar:
            return

        width  = self.max_width  - 10
        height = self.max_height - 10

        y1 = self.y1
        x1 = 5

        textinfo, image, item = self.format_info()

        ft  = gui.theme.font('detached player time')
        fi  = gui.theme.font('detached player info')
        fth = ft.height
        fih = fi.height

        # Draw coverimage
        # FIXME: Find a more suitable default image?
        if not image:
            image = os.path.join(config.IMAGE_DIR, 'gant', 'music.png')

        cover = gui.widgets.Image((image, (None, height)),(x1, y1))
        iw,ih = cover.get_size()
        self.objects.append(cover)

        # create a marquee for showing item info
        info = kaa.mevas.image.CanvasImage( (width - iw - 6, fih) )
        info.set_pos( (x1 + iw + 4, y1 + ih - fih - 2) )

        # create text objects to be shown as
        # iteminfo on the detachbar
        tobjs = []
        for string in textinfo:
            tobjs.append(gui.widgets.Text(string, (0, 0),
                                          (fi.stringsize(string), fih),
                                          fi, align_v='top', align_h='left') )

        self.objects.append(info)

        # create canvas for showing elapsed time
        w = ft.stringsize(u'00:00')
        elapsed = kaa.mevas.image.CanvasImage((w, fth))
        elapsed.set_pos( (x1 + width - w, y1) )
        self.objects.append(elapsed)

        self.animation = DetachbarAnimation(tobjs, info, item, elapsed, ft)
        self.animation.start()

        plugin.getbyname('idlebar').update()


    def hide(self):
        """
        Hides the detached view.
        """

        if not self.visible:
            return

        if self.controlbar:
            # unregister the controlbar.
            controlpanel().unregister(self.controlbar)
            self.controlbar = None

        if self.animation and self.animation.running():
            # Stop the scroller
            self.animation.finish()

        self.clear()
        self.w         = 0
        self.visible   = False


    def eventhandler(self, event):
        """
        Catches the play events
        """

        if event == STOP and self.detached:
            # this event STOP has nothing to do with the normal stop because
            # this eventhandler is only called for the registered events
            # PLAY_START and PLAY_END
            return audioplayer().eventhandler(STOP)

        if event == DETACH_AUDIO_STOP:
            # The audio stopped, we got an event from the animation. So we
            # need to hide now, update the idlebar and than update the screen
            # to show an idlebar without us.
            self.hide()

            idlebar = plugin.getbyname('idlebar')
            if idlebar:
                # update the idlebar
                idlebar.update()

            gui.display.update()
            return True

        elif event == PLAY_START and isinstance(event.arg, AudioItem) and \
          self.detached:
            # An audio item has started playing and we are in detached mode.
            # This is our item and we should show ourself
            self.hide()
            self.show()
            return True

        return False


    def format_info(self):
        """
        Format text shown in the scolleranim

        XXX: Maybe make this configurable?
        """
        item  = audioplayer().item
        info  = item.info
        image = item.image

        textinfo = []

        # trackno - title
        if info['trackno'] and info['title']:
            textinfo.append( _('Title: %s - %s') % (info['trackno'],
                                                    info['title']) )
        elif info['title']:
            textinfo.append( _('Title: %s') % info['title'] )
        else:
            textinfo.append( _('Title: %s') % item.name)


        # artist : album
        if info['artist']:
            textinfo.append( _('Artist: %s') % info['artist'] )
        if info['album']:
            textinfo.append( _('Album: %s') % info['album'] )


        textinfo.append(_('Duration: %02i:%02i') % (item.length / 60,
                                                    item.length % 60) )
        self.item = item

        return textinfo, image, item



class DetachbarAnimation(BaseAnimation):
    """
    Animation intended for the text on the detached audioplayer
    """
    def __init__(self, textobjects, textcanvas, item,
                       itemcanvas, el_font, fps=15):

        BaseAnimation.__init__(self, fps)

        self.fps          = fps
        self.pobj         = -1
        self.frame        = 0
        self.max_frames   = 0
        self.sleep_frames = fps
        self.canvas       = textcanvas
        self.objects      = textobjects

        self.elapsed_font = el_font
        self.item         = item
        self.itemcanvas   = itemcanvas
        self.last_elapsed = None


    def update(self, frame=None):
        """
        update the animation
        """
        if not audioplayer().running:
            # not running, stop
            # FIXME: maybe this is a Signal
            DETACH_AUDIO_STOP.post()

        self.frame += 1

        # goto next text object
        if self.frame > self.max_frames:
            # update the pointer
            self.pobj += 1
            if self.pobj == len(self.objects):
                self.pobj = 0

            # set animation frames boundries
            f = self.objects[self.pobj].get_size()[0]
            self.max_frames = f + self.sleep_frames
            self.frame = 0

        obj    = self.objects[self.pobj]
        srcpos = (0,0)

        if self.frame > self.sleep_frames:
            srcpos = (self.frame - self.sleep_frames, 0)

        # clear the current image and blit the textobject
        self.canvas.image.clear()
        self.canvas.draw_image(obj, src_pos=srcpos)

        # update the time elapsed
        if self.item.elapsed != self.last_elapsed:
            self.last_elapsed = self.item.elapsed
            elapsed = u'%02i:%02i' % (self.item.elapsed / 60,
                                      self.item.elapsed % 60)

            size = ( self.elapsed_font.stringsize(elapsed),
                     self.elapsed_font.height )

            # create the text image
            txt = gui.widgets.Text(elapsed, (0, 0), size, self.elapsed_font)

            # blit text to the itemcanvas
            self.itemcanvas.set_image(txt)
