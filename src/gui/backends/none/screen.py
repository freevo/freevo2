# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# screen.py - dummy screen if drawing is not possible
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/08/01 10:34:19  dischi
# dummy backend 'none' is case drawing on the screen is not possible
# right now (e.g. xine is playing a video)
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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
# -----------------------------------------------------------------------

class Screen:
    """
    The screen implementation
    """
    def __init__(self, renderer):
        self.renderer = renderer
        self.width    = self.renderer.width
        self.height   = self.renderer.height
        self.objects  = []


    def add(self, object):
        """
        Add object to the screen
        """
        self.objects.append(object)
        object.screen = self
            

    def remove(self, object):
        """
        Remove an object from the screen
        """
        self.objects.remove(object)
        object.screen = None


    def get_objects(self):
        """
        Return current 'visible' objects
        """
        return self.objects


    def update(self):
        """
        Show the screen using pygame
        """
        pass
