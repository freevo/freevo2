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
# FIXME: remove global import
from theme_engine import *

# Image library
# FIXME: remove global import
import imagelib

# Basic widgets
# FIXME: remove global import
from widgets import *

# Windows / PopupBoxes
# FIXME: remove global import
from windows import *

# The animation module
# import animation

# -----------------------------------------------------------------------------
# Display engine control module. Based on the different display engines
# in the display subdirectory it is possible to change the display on
# runtime and get some basic display informations.
# import gui.displays
#
# get()
#      Returns the current active display object
#
# create()
#      Create initial display
#
# set(name, size)
#      Create a display based on the display type name with the given size.
#      The new display will be returned. This will also create a new animation
#      render class for this display.
#
# remove(name)
#      Remove the display name and stop all animations for it. The function
#      will return the new active display.
# -----------------------------------------------------------------------------


# set width, height and display to fake values
# Call gui.displays.create() to setup the display
width   = 0
height  = 0
display = None

# -----------------------------------------------------------------------------
# Area module.
# import gui.areas
#
# provided classes:
#
# Handler(type, area_list)
#      Create an area handler with areas
#
# Area(name)
#      Template for an Area to add to the AreaHandler
# -----------------------------------------------------------------------------
