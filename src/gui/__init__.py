# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# gui - Interface to all gui functions and objects
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.27  2004/08/24 19:23:37  dischi
# more theme updates and design cleanups
#
# Revision 1.26  2004/08/24 16:42:40  dischi
# Made the fxdsettings in gui the theme engine and made a better
# integration for it. There is also an event now to let the plugins
# know that the theme is changed.
#
# Revision 1.25  2004/08/23 14:28:21  dischi
# fix animation support when changing displays
#
# Revision 1.24  2004/08/23 12:37:36  dischi
# better display handling
#
# Revision 1.23  2004/08/22 20:06:16  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.22  2004/08/14 15:08:21  dischi
# new area handling code
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

import copy
import config

# basic objects
from widgets.image import Image
from widgets.text import Text
from widgets.textbox import Textbox
from widgets.infotext import InfoText
from widgets.rectangle import Rectangle

# Container for widgets
from mevas import CanvasContainer

# Display engine control module
import displays

# Image load library
import imagelib

# The animation module
import animation

def get_display():
    """
    return current display output or create the default one
    if no display is currently set
    """
    return displays.get_display()


def set_display(name, size):
    """
    set a new output display
    """
    global display
    animation.render().killall()
    display = displays.set_display(name, size)
    width   = display.width
    height  = display.height
    animation.create(display)
    return display


def remove_display(name):
    """
    remove the output display
    """
    global display
    animation.render().killall()
    display = displays.remove_display(name)
    width   = display.width
    height  = display.height
    animation.create(display)
    return display


# create default display and set gui width and height
# in case some part of Freevo needs this
if not config.HELPER:
    display = get_display()
    width   = display.width
    height  = display.height
    animation.create(display)
else:
    display = None
    width   = 0
    height  = 0


from areas import AreaHandler as _AreaHandler

def AreaHandler(type, area_list):
    """
    return the area object
    """
    return _AreaHandler(type, area_list, get_theme, display, imagelib)


from theme_engine import *



# High level widgets
from widgets.label             import Label
from widgets.button            import Button
from widgets.progressbar       import Progressbar

# dialog boxes
from widgets.Window            import Window
from widgets.PopupBox          import PopupBox

# broken boxes
from widgets.AlertBox          import AlertBox
from widgets.ConfirmBox        import ConfirmBox
from widgets.ProgressBox       import ProgressBox
from widgets.InputBox          import InputBox
from widgets.ListBox           import ListBox

# from widgets.LetterBoxGroup    import *
# from widgets.RegionScroller    import *
# from widgets.Scrollbar         import *
# from widgets.LayoutManagers    import *
# from widgets.exceptions        import *
