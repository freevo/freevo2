#!/usr/bin/env python
#-----------------------------------------------------------------------
# gui - First attempt at a freevo gui library
#-----------------------------------------------------------------------
# $Id$
#
# The goal is to make a OO GUI library for use with freevo. The main
# idea is that skins can use or inherit from this class and override
# when needed.
#
# Todo:  o Implement "listbox" for selections with different styles
#          for showing what is selected (glow, bg_color, etc)
#             ListItem -> Label -> Text
#        o Make GraphBar class.
#        o Make more excpetions.
#
# Done:  * Find a way to do Z-index handling.
#        * Split classes into separate files.
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.10  2003/11/29 11:41:35  dischi
# do not import from gui, this object _is_ gui
#
# Revision 1.9  2003/10/12 10:56:19  dischi
# change debug to use _debug_ and set level to 2
#
# Revision 1.8  2003/05/02 01:09:03  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.7  2003/04/24 19:56:29  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.6  2003/03/30 17:21:20  rshortt
# New classes: PasswordInputBox, PasswordLetterBox.
# PasswordLetterBox is a subclass of Letterbox, PasswordInputBox does not
# extend InputBox but instead is also a subclass of PopupBox.  LetterBoxGroup
# has a new constructor argument called 'type' which when set to 'password'
# will make a LetterBoxGroup of PasswordLetterBox's rather than Letterbox's.
#
# Revision 1.5  2003/02/24 11:58:28  rshortt
# Adding OptionBox and optiondemo.  Also some minor cleaning in a few other
# objects.
#
# Revision 1.4  2003/02/23 18:21:50  rshortt
# Some code cleanup, better OOP, influenced by creating a subclass of
# RegionScroller called ListBox.
#
# Revision 1.3  2003/02/19 00:58:18  rshortt
# Added scrolldemo.py for a better demonstration.  Use my audioitem.py
# to test.
#
# Revision 1.2  2003/02/18 13:40:53  rshortt
# Reviving the src/gui code, allso adding some new GUI objects.  Event
# handling will not work untill I make some minor modifications to main.py,
# osd.py, and menu.py.
#
#-----------------------------------------------------------------------
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
"""
A Object Oriented GUI Widget library for Freevo

This is aimed at being a general library for GUI programming with Freevo.
It is built directly on top of SDL with pygame, and it's aimed at being
fairly fast.

Event though the library is built from the ground the design is heavy
influenced by other GUI toolkits, such as Java JDK and QT.

Currently not many classes are in place, but hopefully we will add more
in time.
"""
__date__    = "$Date$"
__version__ = "$Revision$" 
__author__  = """Thomas Malt <thomas@malt.no>"""


import sys
import os.path
import config

from Border            import *
from Color             import *
from GUIObject         import *
from Container         import *
from PopupBox          import *
from AlertBox          import *
from ConfirmBox        import *
from Label             import *
from Button            import *
from LetterBox         import *
from PasswordLetterBox import *
from LetterBoxGroup    import *
from RegionScroller    import *
from Scrollbar         import *
from InputBox          import *
from PasswordInputBox  import *
from LayoutManagers    import *
from exceptions        import *
from scrolldemo        import *
from listboxdemo       import *
from optiondemo        import *


if config.DEBUG > 1:
    from debug import *
