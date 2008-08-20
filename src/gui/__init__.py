# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# gui - GUI Subsystem
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2008 Dirk Meyer, et al.
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

# Note: nothing in this module does import anything from freevo

from stage import *
from window import Window
from config import config
from widgets import *

window = None
signals = None

def configure(cfg, sharedir):
    config.load(cfg, sharedir)
    global window, signals
    window = Window()
    signals = window.signals

def show_application(application, context=None):
    return window.show_application(application, context)

def show_widget(name, context=None):
    return window.render(name, context)

def load_theme(theme=None):
    return window.load_theme(theme)
