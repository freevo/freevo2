# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# GUI subsystem based on kaa.candy
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2009-2013 Dirk Meyer, et al.
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
signals = kaa.Signals('reset', 'key-press')
active = False

def init(cfg, sharedir):
    """
    Initialize the GUI subsystem
    """
    config.init(cfg, sharedir)
    # expose methods and variables from stage to the gui subsystem
    global stage, active, show_application, destroy_application, show_widget, load_theme
    stage = Stage()
    for key in stage.signals:
        stage.signals[key].connect(signals[key].emit)
    show_application = stage.show_application
    destroy_application = stage.destroy_application
    show_widget = stage.show_widget
    load_theme = stage.load_theme
    active = True

def set_active(state):
    """
    Set the gui active/inactive in case Freevo takes too long
    """
    global active
    stage.set_active(state)
    active = state
