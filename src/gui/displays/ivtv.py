# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# ivtv.py - Display for the IVTV OSD interface.
# -----------------------------------------------------------------------------
# $Id$
#
# Support for using IvtvCanvas which will display over the ivtv osd
# interface.  his is called ivtv_osd because it is also possible to display
# through the ivtv decoder (MPEG and perhaps YUV)... maybe someone would like
# another module for that.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rshortt@users.sf.net>
# Maintainer:    Rob Shortt <rshortt@users.sf.net>
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

__all__ = [ 'Display' ]

# mevas imports
from kaa.mevas.displays.ivtvcanvas import IvtvCanvas

# display imports
from display import Display as Base


class Display(IvtvCanvas, Base):
    """
    Display class for OSD output
    """
    def __init__(self, size, default=False):
        IvtvCanvas.__init__(self, size)
        Base.__init__(self)

        # TODO: someone please see if we can do animations here.
        self.animation_possible = False
