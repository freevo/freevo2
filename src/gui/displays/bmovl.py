# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# bmovl.py - Bmovl output display over mplayer
# -----------------------------------------------------------------------
# $Id$
#
# Note: This output plugin is work in progress
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2004/10/06 19:14:36  dischi
# use new childapp interface
#
# Revision 1.4  2004/08/23 20:33:39  dischi
# smaller bugfixes, restart has some problems
#
# Revision 1.3  2004/08/23 14:29:46  dischi
# displays have information about animation support now
#
# Revision 1.2  2004/08/23 12:36:50  dischi
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

# python imports
import os

# mevas imports
import mevas
from mevas.displays.bmovlcanvas import BmovlCanvas

# freevo imports
import config

class Display(BmovlCanvas):
    """
    Display class for bmovl output over mplayer
    """
    def __init__(self, size, default=False):
        self.animation_possible = False
        self.start_video = default
        if default:
            print
            print 'Activating skin bmovl output'
            print 'THIS IS A TEST, DO NOT USE ANYTHING EXCEPT MENUS'
            print
            self.mplayer_args = "-subfont-text-scale 15 -sws 2 -vf scale=%s:-2,"\
                                "expand=%s:%s,bmovl=1:0:/tmp/bmovl "\
                                "-loop 0 -font /usr/share/mplayer/fonts/"\
                                "font-arial-28-iso-8859-2/font.desc" % \
                                ( config.CONF.width, config.CONF.width,
                                  config.CONF.height )
            self.child = None
            self.restart()
        BmovlCanvas.__init__(self, size)


    def restart(self):
        """
        Restart the display. This will restart the background video to
        make the canvas work.
        """
        if self.start_video and not self.child:
            import childapp
            arg = [config.MPLAYER_CMD] + self.mplayer_args.split(' ') + \
                  [config.OSD_BACKGROUND_VIDEO]
            self.child = childapp.Instance( arg, stop_osd = 0 )
            if hasattr(self, 'fifo') and not self.fifo:
                self.fifo = os.open('/tmp/bmovl', os.O_WRONLY)
                _debug_('rebuild bmovl')
                self.rebuild()

    def stop(self):
        """
        Stop the mplayer process
        """
        if self.start_video and self.child:
            self.child.stop('quit')
            self.child = None
        if not self.fifo:
            return
        try:
            os.close(self.fifo)
        except (IOError, OSError):
            print 'IOError on bmovl.fifo'
        self.fifo = None
        
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


