# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# gui - GUI Subsystem
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2008-2011 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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

__all__ = []

# Note: nothing in this module does import anything from freevo

import os
import kaa.utils

from stage import Stage, config

# import all widgets
for name, module in kaa.utils.get_plugins(group='freevo.gui', location=__file__).items():
    if isinstance(module, Exception):
        raise ImportError('error importing %s: %s' % (name, module))
    for widget in module.__all__:
        __all__.append(widget)
        globals()[widget] = getattr(module, widget)

stage = None
signals = None
active = False

def show_window(cfg, sharedir):
    config.load(cfg, sharedir)
    global stage, signals, active
    stage = Stage()
    signals = stage.signals
    active = True

def set_active(state):
    global active
    stage.set_active(state)
    active = state

def show_application(application, fullscreen, context):
    return stage.show_application(application, fullscreen, context)

def show_widget(name, context=None):
    return stage.show_widget(name, context)

def destroy_application(layer):
    return stage.destroy_application(layer)

def load_theme(theme=None):
    return stage.load_theme(theme)
