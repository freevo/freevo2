# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# GUI Exceptions - Various Exeptions for use with Freevo GUI.
# -----------------------------------------------------------------------
# $Id$
#
# Todo: o Make a ShowWhenVisibleError
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/22 21:12:35  dischi
# move all widget into subdir, code needs update later
#
# Revision 1.3  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.2  2004/02/18 21:52:04  dischi
# Major GUI update:
# o started converting left/right to x/y
# o added Window class as basic for all popup windows which respects the
#   skin settings for background
# o cleanup on the rendering, not finished right now
# o removed unneeded files/functions/variables/parameter
# o added special button skin settings
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


class BadColorException(StandardError):
    """
    An exception for color handling.

    This is my first attempt at creating an exception. Any hints or
    feedback on the preferred way to do that is welcome
    """
    def __init__(self, value):
        value = 'Nobody expects the BadColorException: ' + str(value)
        StandardError.__init__(self, value)
        

class LabelException(StandardError):
    """
    An exception regarding Labels.
    """
    def __init__(self, value):
        StandardError.__init__(self, value)


class ParentException(StandardError):
    """
    An exception which is raised if no parent is present when a parent
    should be.
    """
    def __init__(self, value):
        StandardError.__init__(self, 'No parent is present: ' + str(value))
