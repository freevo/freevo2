# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# util.py - some utils for mevas
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

__all__ = [ 'make_weakref', 'check_weakref' ]

import weakref

def make_weakref(object, callback = None):
    """
    Create a weak reference.
    """
    if type(object) == weakref.ReferenceType or not object:
        return object
    if callback:
        return weakref.ref(object, callback)
    else:
        return weakref.ref(object)


def check_weakref(object):
    """
    Check weak reference and return the object behind it.
    """
    if not object or not object():
        return None
    return object
