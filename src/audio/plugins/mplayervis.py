# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mplayervis.py - Freevo MPlayer Audio Visualization Plugin using libvisual
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains the mplayer visualization plugin. This plugin is dependant
# of libvisual (http://libvisual.sf.net) and pylibvisual which is located in
# the freevo/lib directory.
#
# Notes: -This plugin could also be used with alsa as input plugin, but this
#         does not seem to work for me ( ice1712 ).
#
#        -Some visualizations leaks memory, this may not be a problem with this
#         plugin or pylibvisual -- rather the libvisual-plugin. This is
#         hopefully fixed in later versions.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Viggo Fredriksen <viggo@katatonic.org>
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

REASON = None
try:
    from libvisual import bin
except ImportError:
    REASON = 'libvisual not available'

# python modules
import os

import kaa.notifier

# freevo modules
import plugin
import config
import gui
import gui.widgets
import gui.theme

from event import *
from audio.player import *
from gui.animation.base import BaseAnimation
from kaa.mevas.image import CanvasImage
from kaa.mevas.imagelib import *
from controlpanel import *

import logging
log = logging.getLogger('audio')

# Visualization events
AUDIO_VISUAL_SHOW = Event('AUDIO_VISUAL_SHOW')
AUDIO_VISUAL_HIDE = Event('AUDIO_VISUAL_HIDE')


class PluginInterface(plugin.Plugin):
    """
    Audio visualization for Freevo based on libvisual.

    Activate with:
     plugin.activate('audio.mplayervis')
    """
    def __init__(self):

        # error when libvisual is not available
        if REASON:
            self.reason = REASON
            return

        plugin.Plugin.__init__(self)
        self.app_mode = 'audio'
        self.poll_menu_only = False
        self.visual = None
        self.plugin_name = 'audio.mplayervis'
        self.running = False
        self.state = None
        self.should_start = False
        self.controlbar = None
 
        plugin.register(self, self.plugin_name)

        # register for events
        handler = kaa.notifier.EventHandler(self.eventhandler)
        handler.register((AUDIO_VISUAL_SHOW, AUDIO_VISUAL_HIDE))


    def play( self, command, player ):
        """
        This method is run by mplayer when it is started
        """
        return command + [ "-af", "export" ]


    def eventhandler(self, event):
        """
        Eventhandler for catching audio events
        """

        if event == AUDIO_VISUAL_HIDE and self.running:
            # attached, should hide
            self.hide()
            return True

        elif event == AUDIO_VISUAL_SHOW and not self.running:
            # detached, should show
            self.start()
            return True

        return False


    def change_visualization(self, move):
        """
        Changes the visualization to the next in list
        """
        self.visual.change_actor(move)


    def dock(self):
        """
        Get the rect to draw in from the theme
        """
        # calculate pos and size
        # FIXME: does this work for all skins?
        t = gui.theme.get()
        view = t.sets['player'].areas['view']

        x = view.x
        y = view.y
        w = view.width
        h = view.height

        # update the visualization
        self.visual.set_pos(x, y, w, h)


    def start(self):
        """
        Starts the new visualization
        """
        detach = plugin.getbyname('audio.detach')

        if self.running or (detach and detach.detached) \
           or not self.should_start:
            # player is detached or vis allready started
            return

        if self.state:
            s = self.state
            self.visual = LibvisualAnimation(s['pos'],    s['size'],
                                             s['actor'],  s['p_actor'],
                                             s['actors'], s['input'])
        else:
            self.visual = LibvisualAnimation()

        self.dock()
        self.visual.start()
        self.running = True

        # set up a controlbar for the visualization
        path = os.path.join(config.ICON_DIR, 'misc','audio_')

        handlers = [ ( _('Prev visualization'), '%sprev.png' % path,
                       self.change_visualization,-1),
                     ( _('Stop visualization'), '%sstop.png' % path,
                       self.change_visualization, 0),
                     ( _('Next visualization'), '%snext.png' % path,
                       self.change_visualization, 1) ]

        self.controlbar = ButtonPanel( _('Visualization'),
                                       handlers,
                                       default_action=2)
        controlpanel().register(self.controlbar)


    def hide(self):
        """
        Stops and hides the current visualization
        """

        if not self.running:
            # not running
            return

        # finish the animation
        self.running = False
        self.state = self.visual.finish()
        self.visual = None

        if self.controlbar:
            controlpanel().unregister(self.controlbar)
            self.controlbar = None


    def stop(self):
        """
        Called by audio.mplayer trying to stop the plugin.
        We don't want that!
        """
        self.should_start = False
    	

    def stdout(self, line):
        """
        get information from mplayer stdout

        It should be safe to do call start() from here
        since this is now a callback from main.
        """
        if self.running:
            return

        if line.find( "[export] Memory mapped to file: " ) == 0:
            log.info("Detected MPlayer 'export' audio filter!")
            self.should_start = True
            self.start()


class LibvisualAnimation(BaseAnimation):
    """
    This is the animation which shows the images produced by libvisual.
    """
    def __init__(self, pos=(0, 0), size=(100, 100), actor='oinksie',
                 p_actor=0, actors=None, input='mplayer'):

        try:
           fps = config.AUDIO_VISUALIZATION_FPS
        except:
           fps = 15

        BaseAnimation.__init__(self, fps=fps)

        self.started = False
        self.hidden = False
        self.actor = actor
        self.possible_actors = actors
        self.p_actor = p_actor
        self.pos = pos
        self.size = size
        self.input = input


    def start(self):
        """
        Starts the visualization
        """

        if self.started:
            # allready started
            return
        
        width, height = self.size

        # initialize libvisual
        import time
        t0 = time.time()
        self.bin = bin()
        # set log verboseness from libvisual
        self.bin.set_log_verboseness(0)

        self.bin.set_size(width, height)
        self.bin.set_input(self.input)

        
        if not self.possible_actors:
            # a list of possible actors from libvisual
            self.possible_actors = self.bin.get_actors()

            # these don't work well here
            self.possible_actors.remove('gdkpixbuf')

        # set the actor
        self.bin.set_actor(self.possible_actors[self.p_actor])

        # sync the settings
        self.bin.sync()
        
        # this is the image we are drawing to
        self.image  = gui.widgets.Image(CanvasImage(self.size), self.pos)
        self.image.draw_rectangle((0, 0), self.size,(0,0,0,255), 1)

        # add it to the display
        self.image.set_zindex(1)
        gui.display.add_child(self.image)

        # start baseanimation
        BaseAnimation.start(self)
        self.started = True
        log.info('Libvisual started')


    def set_pos(self, x, y, width, height):
        """
        Set the pos and size of the visualization
        """
        self.size = (width, height)
        self.pos  = (x, y)

        if not self.started:
            # don't do anything if we're not started
            return

        # set the new size in libvisual
        self.bin.set_size(width, height)
        self.bin.sync()

        # scale and place the image
        self.image.scale(self.size)
        self.image.set_pos(self.pos)

        # update the drawing
        self.update()


    def change_actor(self, move):
        """
        Changes the actor
         -1: previous in list
          0: hide
          1: next in list
        """

        if move == 0:
            # should not draw
            # remove from gui
            gui.display.remove_child(self.image)
            self.hidden = True
            return

        elif self.hidden:
            # should draw
            # add to gui
            gui.display.add_child(self.image)


        self.hidden = False

        # update the actor pointer
        self.p_actor += move
        l_a = len(self.possible_actors)

        if self.p_actor >= l_a:
            self.p_actor = 0
        
        elif self.p_actor < 0:
            self.p_actor = l_a - 1
        	
        actor = self.possible_actors[self.p_actor]

        # set the new actor
        self.bin.set_actor(actor)
        self.bin.sync()

        # send osd notification
        OSD_MESSAGE.post(_('Visualization: %s') % actor)


    def finish(self):
        """
        Finish the animation
        """
        BaseAnimation.finish(self)
        gui.display.remove_child(self.image)
        self.started = False

        # delete stuff that uses mem.    
        if self.bin:
            del self.bin
            self.bin = None

        if self.image:
            del self.image
            self.image = None

        # create a state object for use with new
        # visualizations
        state = {}
        state['actor'] = self.actor
        state['actors'] = self.possible_actors
        state['p_actor'] = self.p_actor
        state['pos'] = self.pos
        state['size'] = self.size
        state['input'] = self.input
        log.info('Libvisual stopped')

        return state


    def update(self, frame=None):
        """
        Update the animation

        FIXME: Better way of doing this?
        """
        if not self.started or self.hidden:
            return
        
        # get the current backend
        backend = get_backend(get_current_backend())
        
        # create the new image
        img = backend.new(self.size, self.bin.get_frame(), 'RGB')

        # set the image
        self.image.set_image(img)

