#if 0
# -----------------------------------------------------------------------
# skin_dischi1.py - Test Skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:   My test skin
# Todo:    Identical with main1 except it uses the gui classes for the
#          popup box
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.10  2002/09/22 09:52:44  dischi
# Cleanup. Inherits from main1 and only contains the difference.
##
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
# -----------------------------------------------------------------------
#endif



# Configuration file. Determines where to look for AVI/MP3 files, etc
# Logging is initialized here, so it should be imported first
import config

import sys, socket, random, time, os, copy, re

# Various utilities
import util

# The mixer class, controls the volumes for playback and recording
import mixer

# The OSD class, used to communicate with the OSD daemon
import osd

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# XML parser for skin informations
sys.path.append('skins/xml/type1')
import xml_skin

sys.path.append('skins/main1')
import skin_main1

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0


PADDING=5   # Padding/spacing between items

###############################################################################

# Set up the mixer
mixer = mixer.get_singleton()

# Create the remote control object
rc = rc.get_singleton()

# Create the OSD object
osd = osd.get_singleton()

import gui   # Gui library.


###############################################################################
# Skin main functions
###############################################################################

class Skin(skin_main1.Skin):

    def PopupBox(self, text=None, icon=None):
        """
        text  STring to display

        Draw a popupbox with an optional icon and a text.
        
        Notes: Should maybe be named print_message or show_message.
               Maybe I should use one common box item.
        """
        left   = (osd.width/2)-180
        top    = (osd.height/2)-30
        width  = 360
        height = 60
        icn    = icon
        bd_w   = 2
        bg_c   = gui.Color(osd.default_bg_color)
        fg_c   = gui.Color(osd.default_fg_color)

        bg_c.set_alpha(192)

        pb = gui.PopupBox(left, top, width, height, icon=icn, bg_color=bg_c,
                          fg_color=fg_c, border='flat', bd_width=bd_w)

        pb.set_text(text)
        pb.set_h_align(gui.Label.CENTER)
        pb.set_font('skins/fonts/bluehigh.ttf', 24)
        pb.show()
        
        osd.update()
