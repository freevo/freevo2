# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# ivtv_fb.py - Display for the IVTV OSD interface.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/12/31 11:57:41  dischi
# renamed SKIN_* and OSD_* variables to GUI_*
#
# Revision 1.2  2004/10/06 18:59:52  dischi
# remove import rc
#
# Revision 1.1  2004/09/25 05:26:03  rshortt
# Move ivtv_osd to ivtv_fb to avoid confusion with other OSD interfaces.
#
# Revision 1.2  2004/09/02 00:05:26  rshortt
# *** empty log message ***
#
# Revision 1.1  2004/09/01 23:39:53  rshortt
# Initial support for using IvtvCanvas which will display over the ivtv osd
# interface.  This is called ivtv_osd because it is also possible to display
# through the ivtv decoder (MPEG and perhaps YUV)... maybe someone would like
# another module for that.
#
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
from mevas.displays.ivtvcanvas import IvtvCanvas

# Freevo imports
import config


class Display(IvtvCanvas):
    """
    Display class for OSD output
    """
    def __init__(self, size, default=False):
        IvtvCanvas.__init__(self, size)
        self.running = True
        # TODO: someone please see if we can do animations here.
        self.animation_possible = False

        
    def hide(self):
        """
        Hide the output display. In most cases this does nothing since
        a simple window doesn't matter. If GUI_STOP_WHEN_PLAYING the
        display will be shut down.
        """
        if config.GUI_STOP_WHEN_PLAYING:
            self.stop()


    def show(self):
        """
        Show the output window again if it is not visible
        """
        if config.GUI_STOP_WHEN_PLAYING:
            self.restart()


    def stop(self):
        """
        Stop the display
        """
        if self.running:
            self.freeze()
            self.running = False

        
    def restart(self):
        """
        Restart the display if it is currently stopped
        """
        if not self.running:
            self.thaw()
            self.running = True

        
