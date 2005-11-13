# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# widgets/__init__.py - Widgets for Freevo
# -----------------------------------------------------------------------
# $Id$
#
# This file imports all widgets freevo can use. All widgets can be put
# on a display or in a container.
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2005/06/26 17:04:19  dischi
# adjust to mevas - kaa.mevas move
#
# Revision 1.4  2005/06/04 17:17:16  dischi
# Clean import for gui system. There are no gui imports in the __init__
# anymore because this caused recursive imports: gui imports e.g.
# windows and in windows gui is imported again to get to the widgets.
#
# So if a gui module like windows or widgets is needed, the correct
# submodule needs to be imported. This is also needed for simple modules
# like theme (renamed from theme_engine) and imagelib.
#
# The only variables still direct in gui are width, weight and display, I
# don't know were else to put them.
#
# Revision 1.3  2004/10/09 16:22:24  dischi
# create Container class inside widgets
#
# Revision 1.2  2004/10/05 19:50:55  dischi
# Cleanup gui/widgets:
# o remove unneeded widgets
# o move window and boxes to the gui main level
# o merge all popup boxes into one file
# o rename popup boxes
#
#
# -----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
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

# Container for widgets
import kaa.mevas

class Container(kaa.mevas.CanvasContainer):
    """
    A CanvasContainer with an optional name for debugging
    """
    def __init__(self, name=''):
        kaa.mevas.CanvasContainer.__init__(self)
        self.__name = name

    def __str__(self):
        return 'Container %s' % self.__name


# Simple widgets
from image       import Image
from text        import Text
from textbox     import Textbox
from infotext    import InfoText
from rectangle   import Rectangle

# High level widgets
from button      import Button
from progressbar import Progressbar
