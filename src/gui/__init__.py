# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# gui - Interface to all gui functions and objects
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
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

from mevas import CanvasContainer

_display  = []
_skin     = None
_renderer = None
_keyboard = None

def get_keyboard():
    """
    return the screen object
    """
    global _keyboard
    if not _keyboard:
        import backends.sdl
        _keyboard = backends.sdl.Keyboard()
        print _keyboard
    return _keyboard


import displays

def get_display():
    """
    return the screen object
    """
    if not _display:
        _display.append(displays.default())
    return _display[-1]


def set_display(display, size):
    """
    set a new screen
    """
    old = _display[-1]

    # remove all children add update old display
    children = copy.copy(old.children)
    for c in children:
        old.remove_child(c)
    old.update()
    old.hide()

    # create a new display
    new = displays.new(display, size)
    _display.append(new)

    # move all children to new display
    for c in children:
        new.add_child(c)
    new.update()
    return _display[-1]


def remove_display(screen):
    """
    remove screen
    """
    global _display
    if screen != _display[-1]:
        _debug_('FIXME: removing screen not on top')
        return

    _display = _display[:-1]
    # move all active children to new display
    for c in copy.copy(screen.children):
        screen.remove_child(c)
        _display[-1].add_child(c)

    # stop old display, reactivate new one
    # warning: no update() is called
    screen.stop()
    _display[-1].show()
    
    
def AreaHandler(type, area_list):
    """
    return the area object
    """
    import areas
    import imagelib
    return areas.AreaHandler(type, area_list, get_settings(), get_display(), imagelib)

    
def get_settings():
    """
    get current fxd settings
    """
    return settings.settings




# Bad interface into settings based on current
# skin interface.
# FIXME: needs cleanup where used!

if not config.HELPER:
    import fxdparser
    settings = fxdparser.Settings()


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



# High level widgets
from widgets.label             import Label
from widgets.button            import Button
from widgets.progressbar       import Progressbar


# dialog boxes
from widgets.Window            import Window
from widgets.PopupBox          import PopupBox
from widgets.AlertBox          import AlertBox
from widgets.ConfirmBox        import ConfirmBox
from widgets.ProgressBox       import ProgressBox

# broken boxes
from widgets.InputBox          import InputBox
from widgets.ListBox           import ListBox

# from widgets.LetterBoxGroup    import *
# from widgets.RegionScroller    import *
# from widgets.Scrollbar         import *
# from widgets.LayoutManagers    import *
# from widgets.exceptions        import *
