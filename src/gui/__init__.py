# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# gui - Interface to all gui functions and objects
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.21  2004/08/01 10:38:14  dischi
# better access to various submodules
#
# Revision 1.20  2004/07/27 11:15:52  dischi
# do not start the gui for helpers
#
# Revision 1.19  2004/07/25 18:17:09  dischi
# interface update
#
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

import copy

import config
import event
import eventhandler

# basic objects
from widgets.image import Image
from widgets.text import Text
from widgets.rectangle import Rectangle

_screen   = None
_skin     = None
_renderer = None
_keyboard = None

if hasattr(config, 'BMOVL_OSD_VIDEO'):
    import backends.bmovl
    backend = backends.bmovl
    default = 'bmovl'
else:
    import backends.sdl
    backend = backends.sdl
    default = 'sdl'

    
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
        _renderer = backend.get_renderer()
    return _renderer


def get_screen():
    """
    return the screen object
    """
    global _screen
    if not _screen:
        _screen = backend.get_screen(get_renderer())
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

    
def get_areas():
    """
    return the area object
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


def set_screen(name):
    """
    set a new screen backend
    """
    if name == 'default':
        global default
        name = default
        
    global _screen
    global _renderer
    global backend
    old_screen = get_screen()

    # import new backend
    module = 'backends.%s' % name
    exec('import %s' % module)
    backend = eval(module)

    _screen    = None
    _renderer  = None
    new_screen = get_screen()

    if old_screen != new_screen:
        _debug_('move all objects to new backend')
        for o in copy.copy(old_screen.get_objects()):
            print 'move %s (%s)' % (o, o.layer)
            old_screen.remove(o)
            new_screen.add(o)
        old_screen.update()



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
