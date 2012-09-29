# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# freevo.ui
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2009 Dirk Meyer, et al.
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

import kaa
import api as __api__
import event as __event__
for obj in dir(__event__):
    if obj.upper() == obj or obj == 'Event':
        __api__.__all__.append(obj)
        setattr(__api__, obj, getattr(__event__, obj))
for module in ('menu', 'taskmanager', 'application', 'window', 'playlist', 'directory', 'mainmenu', 'mediamenu', 'player'):
    exec('import %s as module' % module)
    for obj in module.__all__:
        if obj == 'signals':
            for name, signal in module.signals.items():
                __api__.signals[name] = signal
        else:
            __api__.__all__.append(obj)
            setattr(__api__, obj, getattr(module, obj))
from api import *
__all__ = __api__.__all__

@kaa.coroutine()
def init():
    yield beacon.connect()
