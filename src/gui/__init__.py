# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# gui - Interface to all gui functions and objects
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.18  2004/07/24 12:21:05  dischi
# move renderer into backend subdir
#
# Revision 1.17  2004/07/23 19:43:30  dischi
# move most of the settings code out of the skin engine
#
# Revision 1.16  2004/07/22 21:16:01  dischi
# add first draft of new gui code
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

import config

# the objects that can be drawn
from base import Image, Rectangle, Text

_screen   = None
_skin     = None
_renderer = None
_keyboard = None

if hasattr(config, 'BMOVL_OSD_VIDEO'):
    import backends.bmovl
    backend = backends.bmovl
else:
    import backends.sdl
    backend = backends.sdl

    
def get_keyboard():
    """
    return the screen object
    """
    global _keyboard
    if not _keyboard:
        _keyboard = backend.Keyboard()
        print _keyboard
    return _keyboard


def get_renderer():
    """
    return the screen object
    """
    global _renderer
    if not _renderer:
        _renderer = backend.Renderer()
    return _renderer


def get_screen():
    """
    return the screen object
    """
    global _screen
    if not _screen:
        _screen = backend.Screen(get_renderer())
    return _screen


def get_skin():
    """
    return the skin object
    """
    global _skin
    if not _skin:
        import areas
        _skin = areas.AreaHandler(get_settings())
        _skin.set_screen(get_screen())
    return _skin

    

def get_settings():
    """
    get current fxd settings
    """
    return settings.settings



# Bad interface into settings based on current
# skin interface.
# FIXME: needs cleanup where used!

def set_base_fxd(file):
    return settings.set_base_fxd(file)


def load_settings(filename, copy_content = 1):
    return settings.load(filename, copy_content)


def get_font(name):
    return settings.settings.get_font(name)


def get_image(name):
    return settings.settings.get_image(name)


def get_icon(name):
    return settings.settings.get_icon(name)


import fxdparser
settings = fxdparser.Settings()


# include all the widgets
# FIXME: needs cleanup!

from widgets.Border            import *
from widgets.Color             import *
from widgets.GUIObject         import *
from widgets.Container         import *
from widgets.PopupBox          import *
from widgets.AlertBox          import *
from widgets.ConfirmBox        import *
from widgets.Label             import *
from widgets.Button            import *
from widgets.LetterBoxGroup    import *
from widgets.RegionScroller    import *
from widgets.Scrollbar         import *
from widgets.InputBox          import *
from widgets.LayoutManagers    import *
from widgets.exceptions        import *
from widgets.ProgressBox       import *
from widgets.ListBox           import *

