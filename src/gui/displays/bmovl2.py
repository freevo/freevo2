# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# bmovl2.py - Bmovl2 output display over mplayer
# -----------------------------------------------------------------------
# $Id$
#
# Note: This output plugin is work in progress
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2004/08/23 14:29:46  dischi
# displays have information about animation support now
#
# Revision 1.4  2004/08/23 12:36:50  dischi
# cleanup, add doc
#
#
# -----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------

# basic python imports
import time

# mevas imports
import mevas
from mevas.displays.mplayercanvas import MPlayerCanvas
from mevas.bmovl2 import MPlayerOverlay

# Freevo imports
import config

class Display(MPlayerCanvas):
    """
    Display class for bmovl2 output over mplayer
    """
    def __init__(self, size, default=False):
        self.start_video = default
        self.animation_possible = True
        MPlayerCanvas.__init__(self, size)
        if default:
            print
            print 'Activating bmovl2 output'
            print 'THIS IS A TEST, DO NOT USE ANYTHING EXCEPT MENUS'
            print
            self.mplayer_overlay = MPlayerOverlay()
            self.mplayer_args = "-subfont-text-scale 15 -sws 2 -vf scale=%s:-2,"\
                                "expand=%s:%s,bmovl2=%s "\
                                "-loop 0 -font /usr/share/mplayer/fonts/"\
                                "font-arial-28-iso-8859-2/font.desc" % \
                                ( config.CONF.width, config.CONF.width,
                                  config.CONF.height, self.mplayer_overlay.fifo_fname )
            self.child = None
            self.show()

    def restart(self):
        """
        Restart the display. This will restart the background video to
        make the canvas work.
        """
        _debug_('restart bmovl2')
        if self.start_video and not self.child:
            import childapp
            arg = [config.MPLAYER_CMD] + self.mplayer_args.split(' ') + \
                  [config.OSD_BACKGROUND_VIDEO]
            self.child = childapp.ChildApp2(arg)
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
        _debug_('stop bmovl2')
        if self.start_video and self.child:
            self.child.stop('quit')
            self.child = None
            
    def hide(self):
        """
        Hide the display. This results in shutting down the
        background video
        """
        _debug_('hide bmovl2')
        self.stop()


    def show(self):
        """
        Show the display. This results in starting the background
        video again.
        """
        _debug_('show bmovl2')
        self.restart()

