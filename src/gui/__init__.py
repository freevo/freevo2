# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# gui - Freevo GUI subsystem
# -----------------------------------------------------------------------------
# $Id$
#
# The only variables that can be access by gui.variable are width and height
# of the current display and the display itself. The variables may change
# when the current activate display changes
#
# Submodule:    import gui.font
# Dependencies: mevas, freevo config
# Content:      get
# Description:  This module makes it possible to load a font from disc and
#               provides some basic drawing functions. It should not be used
#               directly, better use the theme module to get fonts by aliases
#               defined by the current theme
#
# Submodule:    import gui.theme
# Dependencies: freevo, gui.font
# Content:      get, set, font, image, icon, set_base_fxd
# Description:  This module reads theme fxd files and provides an interface to
#               the objects defined in the theme
#
# Submodule:    import gui.imagelib
# Dependencies: PIL, mevas, freevo config and util, gui.theme
# Content:      rotate, scale, load, item_image
# Description:  This module can read images based on filenames or theme
#               definitions. In most cases this module is not needed and the
#               Image widget can be used.
#
# Submodule:    import gui.widgets
# Dependencies: mevas, imagelib
# Content:      The different widgets
# Description:  Basic widgets that can be drawn on the display. Use this module
#               and not mevas directly.
#
# Submodule:    import gui.animation
# Dependencies: notifier
# Content:      The different animation modules
# Description:  Animation classes in this module can be used to animate gui
#               widgets
#
# Submodule:    import gui.displays
# Dependencies: mevas displays, freevo config, util and plugin, gui.animation
# Content:      get, set, remove, shutdown, active
# Description:  Display engine control module. Based on the different display
#               engines in the display subdirectory it is possible to change
#               the display on runtime and get some basic display informations.
#
# Submodule:    import gui.windows
# Dependencies: freevo config, event and eventhandler, gui.widgets
# Content:      The different windows and popup boxes
# Description:  This module includes different popup boxes and a basic window
#
# Submodule:    import gui.areas
# Dependencies: freevo config, util and recoord, gui.widgets, gui.animation,
#               gui.imagelib
# Content:      Handler, Area (for defining areas outside the gui system)
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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

width   = 0
height  = 0
display = None

# ugly compat code until the new gui is ready
from compat import *
