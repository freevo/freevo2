# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# gui - Interface to all gui functions and objects
# -----------------------------------------------------------------------------
# $Id$
#
# This file is the interface to the complete gui code of Freevo. It includes
# some basic get/set functions and also imports all parts from submodules that
# should be allowed to use.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
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

# The theme engine
from theme_engine import *

# Image library
import imagelib

# Basic widgets
from widgets import *

# Dialog boxes
from window   import Window
from popupbox import *

# The animation module
import animation


# -----------------------------------------------------------------------------
# Display engine control module. Based on the different display engines
# in the display subdirectory it is possible to change the display on
# runtime and get some basic display informations.
#
# provided functions:
#
# get_display()
#      Returns the current active display object
#
# set_display(name, size)
#      Create a display based on the display type name with the given size.
#      The new display will be returned. This will also create a new animation
#      render class for this display.
#
# remove_display(name)
#      Remove the display name and stop all animations for it. The function
#      will return the new active display.
# -----------------------------------------------------------------------------

import displays as _displays

get_display = _displays.get_display

def set_display(name, size, *args, **kwargs):
    """
    set a new output display
    """
    animation.render().killall()
    display = _displays.set_display(name, size, *args, **kwargs)
    width   = display.width
    height  = display.height
    animation.create(display)
    return display


def remove_display(name):
    """
    remove the output display
    """
    animation.render().killall()
    display = _displays.remove_display(name)
    width   = display.width
    height  = display.height
    animation.create(display)
    return display

import config as _config

if not _config.HELPER:
    # create default display and set gui width and height
    # in case some part of Freevo needs this
    display = get_display()
    width   = display.width
    height  = display.height
    animation.create(display)
else:
    # set width and height to fake values
    width   = 0
    height  = 0


# -----------------------------------------------------------------------------
# Area module.
#
# provided classes:
#
# AreaHandler(type, area_list)
#      AreaHandler based on the area/handler.py code. This is only a wrapper
#      class to give basic gui information to the subclass
#
# Area(name)
#      Template for an Area to add to the AreaHandler
# -----------------------------------------------------------------------------

from areas import AreaHandler as _AreaHandler
from areas import Area

class AreaHandler(_AreaHandler):
    """
    Create an AreaHandler
    """
    def __init__(self, type, area_list):
        _AreaHandler.__init__(self, type, area_list, get_theme,
                              get_display(), imagelib)
