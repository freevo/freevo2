# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# bmovl.py - Bmovl output display over mplayer
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines a Freevo display using mplayer and the bmovl filter.
# It is based on bmovlcanvas from mevas and adds the basic functions Freevo
# needs. When used as primary display, a background mplayer will be started.
# The fifo communication is wrapped around a non blocking version for
# pyNotifier.
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
import logging

# mevas imports
from kaa.mevas.displays.bmovlcanvas import BmovlCanvas

# freevo imports
import config
import util.popen
import util.fsocket

# display imports
from display import Display as Base

# the logging object
log = logging.getLogger('gui')


class Display(BmovlCanvas, Base):
    """
    Display class for bmovl output over mplayer
    """
    def __init__(self, size, default=False, fifo = None):
        Base.__init__(self)
        self.animation_possible = False
        self.start_video = default

        if default:
            self.cmd = [ config.MPLAYER_CMD, "-loop", "0", "-vf",
                         "scale=%s:-2,expand=%s:%s,bmovl=1:0:%s"\
                         % ( config.CONF.width, config.CONF.width,
                             config.CONF.height, self.get_fname() ),
                         '-vo', config.MPLAYER_VO_DEV, '-ao', 'null',
                         config.GUI_BACKGROUND_VIDEO ]
            self.child = None
            self.restart()
        BmovlCanvas.__init__(self, size, fifo)


    def restart(self):
        """
        Restart the display. This will restart the background video to
        make the canvas work.
        """
        Base.restart(self)
        if self.start_video and not self.child:
            self.child = util.popen.Process( self.cmd )
            self.child.stdout.close()
            self.child.stderr.close()
            if hasattr(self, 'fifo') and not self.fifo:
                # this is a previous working display
		self.open_fifo()
                log.info('rebuild bmovl')
                self.rebuild()


    def open_fifo(self):
        """
        Create and open the fifo and create notifier aware fd wrapper
        """
        BmovlCanvas.open_fifo(self)
        self.nbsocket = util.fsocket.Socket(self.fifo)
        self.send = self.nbsocket.write


    def close_fifo(self):
        """
        Close and remove the fifo
        """
        if self.nbsocket:
            self.nbsocket.close()
            self.nbsocket = None
            self.send = None
            self.fifo = None
        BmovlCanvas.close_fifo(self)


    def stop(self):
        """
        Stop the mplayer process
        """
        if self.start_video and self.child:
            self.child.stop('quit')
            self.child = None
        self.close_fifo()
        Base.stop(self)


    def hide(self):
        """
        Hide the display. This results in shutting down the
        background video
        """
        self.stop()


    def show(self):
        """
        Show the display. This results in starting the background
        video again.
        """
        self.restart()
