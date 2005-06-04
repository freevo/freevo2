# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# display/__init__.py - Interface to the possible display backends
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
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

__all__ = [ 'get', 'set', 'remove', 'shutdown', 'active' ]

# python imports
import copy
import logging

# freevo imports
import config

# gui imports
import gui
from gui import animation

# get logging object
log = logging.getLogger('gui')

# Stack of the current active displays
display_stack  = []


def get():
    """
    return current display output or create the default one
    if no display is currently set
    """
    if display_stack:
        return display_stack[-1]
    exec('from %s import Display' % config.GUI_DISPLAY.lower())
    size = (config.CONF.width, config.CONF.height)
    display = Display(size, True)
    display_stack.append(display)
    animation.create(display)
    # set global gui width / height
    gui.width   = display.width
    gui.height  = display.height
    gui.display = display
    return display

# create a display (== get first one)
create = get

def set(name, size, *args, **kwargs):
    """
    set a new output display
    """
    animation.render().killall()
    old = display_stack[-1]

    # remove all children add update old display
    children = copy.copy(old.children)
    for c in children:
        if not hasattr(c, 'sticky') or not c.sticky:
            old.remove_child(c)
    old.update()
    old.hide()

    # create a new display
    exec('from %s import Display' % name.lower())
    display = Display(size, False, *args, **kwargs)
    display_stack.append(display)

    # move all children to new display
    for c in children:
        if not hasattr(c, 'sticky') or not c.sticky:
            display.add_child(c)
    display.update()

    animation.create(display)
    # set global gui width / height
    gui.width   = display.width
    gui.height  = display.height
    gui.display = display
    return display


def remove(screen):
    """
    remove the output display
    """
    global display_stack
    animation.render().killall()
    if screen != display_stack[-1]:
        log.error('removing screen not on top')
        print screen
        print display_stack
        raise AttributeError

    display_stack = display_stack[:-1]
    # move all active children to new display
    for c in copy.copy(screen.children):
        if not hasattr(c, 'sticky') or not c.sticky:
            screen.remove_child(c)
            display_stack[-1].add_child(c)

    # stop old display, reactivate new one
    # warning: no update() is called
    screen.stop()
    display = display_stack[-1]
    display.show()
    animation.create(display)
    # set global gui width / height
    gui.width   = display.width
    gui.height  = display.height
    gui.display = display
    return display


def shutdown():
    """
    shut down all running displays
    """
    global display_stack
    while display_stack:
        d = display_stack.pop()
        d.stop()
    # switch to none display
    from none import Display
    size = (config.CONF.width, config.CONF.height)
    display_stack = [ Display(size) ]


def active():
    """
    return True if at least one display is still
    active
    """
    return True
