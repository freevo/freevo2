# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# mplayervis.py - Native Freevo MPlayer Audio Visualization Plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: - This is a demonstrator only atm.
# Todo:  - Much
# -----------------------------------------------------------------------
# $Log$
# Revision 1.13  2004/10/12 11:31:57  dischi
# make animation frame selection timer based
#
# Revision 1.12  2004/10/02 11:38:00  dischi
# update to libvisual
#
# Revision 1.11  2004/08/23 12:40:54  dischi
# remove osd.py dep
#
# Revision 1.10  2004/08/05 17:33:31  dischi
# fix skin imports
#
# Revision 1.9  2004/08/01 10:41:03  dischi
# deactivate plugin
#
# Revision 1.8  2004/07/24 12:23:38  dischi
# deactivate plugin
#
# Revision 1.7  2004/07/22 21:21:47  dischi
# small fixes to fit the new gui code
#
# Revision 1.6  2004/07/10 12:33:38  dischi
# header cleanup
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

REASON = None
try:
    from libvisual import bin
except:
    REASON = '[audio.mplayervis]: libvisual not available'



# freevo modules
import plugin
import config
import gui

from event import *
from audio.player import *
from gui.animation.base import BaseAnimation
from mevas.image import CanvasImage
from mevas.imagelib import *
#from controlpanel import *

class PluginInterface(plugin.Plugin):
    """
    Audio visualization for Freevo based on libvisual.

    Activate with:
     plugin.activate('audio.mplayervis')

    When activated one can change between visualizations
    with the 0 (zero) button.
    """
    def __init__(self):
        if REASON:
            self.reason = REASON
            return

        self.reason = 'needs more work'
        return
        plugin.Plugin.__init__(self)
        self._type    = 'mplayer_audio'
        self.app_mode = 'audio'
        self.visual   = None

        # Event for changing between viewmodes
        config.EVENTS['audio']['0'] = Event(FUNCTION_CALL, arg=self.change_vis)

        self.plugin_name = 'audio.mplayervis'
        plugin.register(self, self.plugin_name)


    def play( self, command, player ):
        """
        This method is run by mplayer when it is started
        """
        return command + [ "-af", "export" ]

    def eventhandler(self, event, arg=None):
        return False

    def change_vis(self):
        """
        Changes the visualization to the next in list
        """
        self.visual.next()

    def dock(self):
        """
        Get the rect to draw in from the theme_engine
        """
        # calculate pos and size
        # todo: add content spacing?
        t = gui.theme_engine.get_theme()
        view = t._sets['player'].areas['view']
        x = view.x
        y = view.y
        w = view.width
        h = view.height

        # update the visualization
        self.visual.set_pos(x, y, w, h)


    def start(self):
        """
        Starts a new visualization
        """
        if self.visual:
            return
        try:
            self.visual = libvisualAnimation(300, 300, 150, 150)
            self.visual.start()
            self.dock()
        except Exception, e:
            print e

    def stop(self):
        """
        Stops the current visualization
        """
        if self.visual:
            # finish the animation
            self.visual.finish()
            self.visual = None


    def stdout(self, line):
        """
        get information from mplayer stdout

        It should be safe to do call start() from here
        since this is now a callback from main.
        """
        if self.visual:
            return

        if line.find( "[export] Memory mapped to file: " ) == 0:
            _debug_("Detected MPlayer 'export' audio filter! Using libvisual.")
            self.start()


class libvisualAnimation(BaseAnimation):
    """
    This is the animation which shows the images produced by libvisual.
    """
    def __init__(self, x, y, width, height, actor='oinksie', input='mplayer'):
        BaseAnimation.__init__(self, fps=15)

        # initialize libvisual with the default oinksie actor,
        # use mplayer as input plugin.
        self.bin = bin("oinksie", (300,300), 'mplayer')
            
        width, height = 300, 300
        #self.bin = bin(actor, (width,height), input)

        # this is the image we are drawing to
        self.image  = gui.Image(CanvasImage((width,height)), (x,y))
        self.image.draw_rectangle((0, 0), (width, height), (0,0,0,255), 1)
        # a list of possible actors from libvisual
        self.possible_actors = self.bin.get_actors()

        # these don't work well here
        self.possible_actors.remove('gdkpixbuf')
        self.possible_actors.remove('lv_analyzer')

        self.actor_p = 0
        self.pos     = (x, y)
        self.size    = (width, height)

        # add image to the display
        self.image.set_zindex(1)
        gui.get_display().add_child(self.image)

        
    def set_pos(self, x, y, width, height):
        """
        Set the pos and size of the visualization
        """
        # set the new size in libvisual
        self.bin.set_size(width, height)

        # scale and place the image
        self.image.scale((width,height))
        self.image.set_pos((x, y))

        self.size = (width, height)
        self.pos  = (x, y)
        self.update()

    def next(self):
        """
        Changes to next actor in list
        """
        # set the new actor
        self.bin.set_actor(self.possible_actors[self.actor_p])

        # update the pointer
        self.actor_p += 1
        if self.actor_p >= len(self.possible_actors):
            self.actor_p = 0


    def finish(self):
        """
        Run to finish the animation
        """
        del self.bin
        BaseAnimation.finish(self)
        gui.get_display().remove_child(self.image)


    def update(self, frame=None):
        """
        Update the animation
        """
        try:
            # get the current backend
            b = get_current_backend()
            i = get_backend(b).new(self.size, self.bin.run(), 'RGB')

            # set the image
            self.image.set_image(i)
        except Exception,e:
            print e

"""
class VisPanel(ButtonPanel):

TODO: perhaps add a panel for controling the visualizations
"""


