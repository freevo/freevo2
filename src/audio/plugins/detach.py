# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# detach.py - Detach plugin for the audio player
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.23  2004/10/12 11:31:57  dischi
# make animation frame selection timer based
#
# Revision 1.22  2004/09/15 20:46:08  dischi
# fix audio stop hide() bug
#
# Revision 1.21  2004/09/15 19:36:15  dischi
# new detach plugin from Viggo
#
# Revision 1.20  2004/09/13 19:35:36  dischi
# replace player.get_singleton() with audioplayer()
#
# Revision 1.19  2004/08/01 10:42:23  dischi
# update to new application/eventhandler code
#
# Revision 1.18  2004/07/26 18:10:17  dischi
# move global event handling to eventhandler.py
#
# Revision 1.17  2004/07/10 12:33:37  dischi
# header cleanup
#
# Revision 1.16  2004/04/25 11:23:58  dischi
# Added support for animations. Most of the code is from Viggo Fredriksen
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

# python modules
import os
import mevas.image

# freevo modules
import gui
import plugin
import config
import eventhandler

from gui.animation.base import BaseAnimation
from plugins.idlebar    import IdleBarPlugin
from audio.player       import audioplayer
from audio.audioitem    import AudioItem
from controlpanel       import *
from event              import *

DETACH_AUDIO_STOP = Event('DETACH_AUDIO_STOP')

class PluginInterface(IdleBarPlugin):
    """
    A detached audioplayer view for freevo
    """
    def __init__(self, show_detachbar=True):
        """
        init the idlebar
        """
        IdleBarPlugin.__init__(self)
        config.EVENTS['audio']['DISPLAY'] = Event(FUNCTION_CALL, arg=self.detach)
        plugin.register(self, 'audio.detach')

        # XXX add support for theme changes?
        # eventhandler.register(self, THEME_CHANGE)
        # XXX that doesn't work, PLAY_END doesn't send the stopped item
        # XXX as argument
        # eventhandler.register(self, PLAY_END)
        eventhandler.register(self, PLAY_START)
        eventhandler.register(self, DETACH_AUDIO_STOP)
        
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
        our boundries for now
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
        p = audioplayer()
        # hide the detached player show the player
        if self.visible:
            self.hide()
            p.show()
            self.detached = False

            #p.item.parent.menuw.show()

        # hide the audioplayer and show the itemmenu
        else:
            p.hide()
            #p.item.parent.menuw.show()
            self.detached = True

            # show the detachbar
            # XXX FIXME: add config-var here
            self.show()


    def show(self):

        if self.visible:
            return


        # set up a controlbar
        # XXX FIXME: Add config-var for this
        path = os.path.join(config.ICON_DIR, 'misc','audio_')
        handlers = [('Prev',  '%sprev.png' % path,  audioplayer().eventhandler, PLAYLIST_PREV),
                    ('Rew',   '%srew.png'  % path,  audioplayer().eventhandler, Event(SEEK, arg=-10)),
                    ('Pause', '%spause.png'% path,  audioplayer().eventhandler, PAUSE ),
                    ('Play',  '%splay.png' % path,  audioplayer().eventhandler, PLAY ),
                    ('Stop',  '%sstop.png' % path,  self.eventhandler, STOP ),
                    ('FFwd',  '%sffwd.png' % path,  audioplayer().eventhandler, Event(SEEK, arg=10)),
                    ('Next',  '%snext.png' % path,  audioplayer().eventhandler, PLAYLIST_NEXT),
                    ('Show Player',  '%sshow.png' % path,  self.detach, None) ]


        self.controlbar = ButtonPanel(handlers, default_action=3)
        controlpanel().register(self.controlbar)

        self.w       = self.max_width
        self.visible = True

        # do not show the detached view if not configured
        if not self.show_detachbar:
            return

        width  = self.max_width  - 4
        height = self.max_height - 4

        y1 = self.y1
        x1 = 2

        textinfo, image, item = self.format_info()

        ft  = gui.get_font('detached player time')
        fi  = gui.get_font('detached player info')
        fth = ft.height
        fih = fi.height

        # Draw coverimage
        # FIXME: Find a more suitable default image?
        if not image:
            image = os.path.join(config.IMAGE_DIR, 'gant', 'music.png')
        cover = gui.Image(gui.imagelib.load(image, (None, height)),(x1, y1))
        iw,ih = cover.get_size()
        self.objects.append(cover)

        # create a marquee for showing item info
        info = mevas.image.CanvasImage((width-iw-6, fih))
        info.set_pos((x1+iw+4, y1+ih-fih-2))

        # create text objects to be shown as
        # iteminfo on the detachbar
        tobjs = []
        for string in textinfo:
            tobjs.append(gui.Text(string, (0,0),
                                    (fi.stringsize(string), fih),
                                    fi, align_v='top', align_h='left'))

        self.objects.append(info)

        # create canvas for showing elapsed time
        w = ft.stringsize('00:00')
        elapsed = mevas.image.CanvasImage((w, fth))
        elapsed.set_pos((x1+width-w, y1))
        self.objects.append(elapsed)

        self.animation = DetachbarAnimation(tobjs, info, item, elapsed, ft)
        self.animation.start()

        plugin.getbyname('idlebar').update()


    def hide(self):
        if not self.visible:
            return

        if self.controlbar:
            controlpanel().unregister(self.controlbar)
            self.controlbar = None

        # Stop the scroller
        if self.animation and self.animation.running():
            self.animation.finish()

        self.clear()
        self.w         = 0
        self.visible   = False


    def eventhandler(self, event, menuw=None):
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
            plugin.getbyname('idlebar').update()
            gui.get_display().update()
            return True
        
        elif event == PLAY_START and isinstance(event.arg, AudioItem) and self.detached:
            # An audio item has started playing and we are in detached mode. This is our
            # item and we should show ourself
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
            textinfo.append( 'Title: %s - %s' % (info['trackno'], info['title'] ) )
        elif info['title']:
            textinfo.append( 'Title: %s' % info['title'] )
        else:
            textinfo.append( 'Title: %s' % item.name)


        # artist : album
        if info['artist']:
            textinfo.append( 'Artist: %s' % info['artist'] )
        if info['album']:
            textinfo.append( 'Album: %s' % info['album'] )


        textinfo.append('Duration: %02i:%02i' % (item.length/60, item.length%60) )

        self.item = item

        return textinfo, image, item



class DetachbarAnimation(BaseAnimation):
    """
    Animation intended for the text on the detached audioplayer
    """
    def __init__(self, textobjects, textcanvas, item, itemcanvas, el_font, fps=15):
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
            eventhandler.post(DETACH_AUDIO_STOP)
            
        self.frame += 1

        # goto next text object
        if self.frame > self.max_frames:
            # update the pointer
            self.pobj += 1
            if self.pobj == len(self.objects):
                self.pobj = 0

            self.max_frames = self.objects[self.pobj].get_size()[0] + self.sleep_frames
            self.frame = 0

        obj    = self.objects[self.pobj]
        srcpos = (0,0)

        if self.frame > self.sleep_frames:
            srcpos = (self.frame - self.sleep_frames, 0)

        # clear the current image and blit the textobject
        self.canvas.image.clear()
        # XXX FIXME!! Causes "Fatal python error: Deallocating None"
        #             after a while!
        self.canvas.draw_image(obj, src_pos=srcpos)

        # update the time elapsed
        if self.item.elapsed != self.last_elapsed:
            self.last_elapsed = self.item.elapsed
            elapsed = '%02i:%02i' % (self.item.elapsed / 60, self.item.elapsed % 60)
            size    = (self.elapsed_font.stringsize(elapsed), self.elapsed_font.height)

            # XXX FIXME!! Causes "Fatal python error: Deallocating None"
            #             after a while!
            self.itemcanvas.set_image(gui.Text(elapsed, (0,0), size, self.elapsed_font))

