# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# canvas.py - template for canvases
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Mevas - MeBox Canvas System
# Copyright (C) 2004-2005 Jason Tackaberry <tack@sault.org>
#
# First Edition: Jason Tackaberry <tack@sault.org>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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

__all__ = [ 'Canvas' ]

from util import *
from container import *

class Canvas(CanvasContainer):
    """
    Base class for all display canvases. This class is pretty much 'pure
    virtual' and defines a few new methods intended to be implemented by
    derived classes.
    """
    def __init__(self, size):
        CanvasContainer.__init__(self)
        self.set_size(size)
        self.canvas = make_weakref(self)

    def freeze(self):
        pass

    def thaw(self):
        pass

    def child_deleted(self, child):
        pass

    def child_reset(self, child):
        pass

    def child_paint(self, child):
        pass

    def rebuild(self):
        pass
