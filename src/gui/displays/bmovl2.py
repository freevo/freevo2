# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# bmovl2.py - Bmovl2 output display over mplayer
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines a Freevo display using mplayer and the bmovl2 filter.
# It is based on bmovl2 and mplayercanvas from mevas and adds the basic
# functions Freevo needs. When used as primary display, a background mplayer
# will be started.
#
# Note: this display may not work right now
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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

__all__ = [ 'Display' ]

# python imports
import time
import logging

# mevas imports
import mevas
from mevas.displays.mplayercanvas import MPlayerCanvas
from mevas.bmovl2 import MPlayerOverlay

# Freevo imports
import config

# display imports
from display import Display as Base

# the logging object
log = logging.getLogger('gui')


class Display(MPlayerCanvas, Base):
    """
    Display class for bmovl2 output over mplayer
    """
    def __init__(self, size, default=False):
        Base.__init__(self)
        self.start_video = default
        self.animation_possible = True
        MPlayerCanvas.__init__(self, size)
        if default:
            print
            print 'Activating bmovl2 output'
            print 'THIS IS A TEST, DO NOT USE ANYTHING EXCEPT MENUS'
            print
            self.mplayer_overlay = MPlayerOverlay()
            self.mplayer_args = "-sws 2 -vf scale=%s:-2,"\
                                "expand=%s:%s,bmovl2=%s "\
                                "-loop 0 -font /usr/share/mplayer/fonts/"\
                                "font-arial-28-iso-8859-2/font.desc" % \
                                ( config.CONF.width, config.CONF.width,
                                  config.CONF.height,
                                  self.mplayer_overlay.fifo_fname )
            self.child = None
            self.show()


    def restart(self):
        """
        Restart the display. This will restart the background video to
        make the canvas work.
        """
        log.info('restart bmovl2')
        if self.start_video and not self.child:
            import childapp
            arg = [config.MPLAYER_CMD] + self.mplayer_args.split(' ') + \
                  [config.GUI_BACKGROUND_VIDEO]
            self.child = childapp.Instance( arg, stop_osd = 0 )
            time.sleep(2)
            self.mplayer_overlay.set_can_write(True)
            while 1:
                if self.mplayer_overlay.can_write():
                    break
            self.set_overlay(self.mplayer_overlay)
            self.rebuild()


    def stop(self):
        """
        Stop the mplayer process
        """
        log.info('stop bmovl2')
        if self.start_video and self.child:
            self.child.stop('quit')
            self.child = None


    def hide(self):
        """
        Hide the display. This results in shutting down the
        background video
        """
        log.info('hide bmovl2')
        self.stop()


    def show(self):
        """
        Show the display. This results in starting the background
        video again.
        """
        log.info('show bmovl2')
        self.restart()

