#!/usr/bin/env python
#-----------------------------------------------------------------------
# GUI Exceptions - Various Exeptions for use with Freevo GUI.
#-----------------------------------------------------------------------
# $Id$
#
# Todo: o Make a ShowWhenVisibleError
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.1  2002/08/15 22:45:42  tfmalt
# o Inital commit of Freevo GUI library. Files are put in directory 'gui'
#   under Freevo.
# o At the moment the following classes are implemented (but still under
#   development):
#     Border, Color, Label, GUIObject, PopupBox, ZIndexRenderer.
# o These classes are fully workable, any testing and feedback will be
#   appreciated.
#
#-----------------------------------------------------------------------
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
"""
Various exceptions for use with Freevo GUI
"""
__date__    = "$Date$"
__version__ = "$Revision$" 
__author__  = """Thomas Malt <thomas@malt.no>"""


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

