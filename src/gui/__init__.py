# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# gui - First attempt at a freevo gui library
# -----------------------------------------------------------------------
# $Id$
#
# The goal is to make a OO GUI library for use with freevo. The main
# idea is that skins can use or inherit from this class and override
# when needed.
#
# A Object Oriented GUI Widget library for Freevo
# 
# This is aimed at being a general library for GUI programming with Freevo.
# It is built directly on top of SDL with pygame, and it's aimed at being
# fairly fast.
# 
# Event though the library is built from the ground the design is heavy
# influenced by other GUI toolkits, such as Java JDK and QT.
# 
# Currently not many classes are in place, but hopefully we will add more
# in time.
#
# Initial version: Thomas Malt <thomas@malt.no>
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.15  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.14  2004/02/23 19:15:46  dischi
# remove import of debug
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

from Border            import *
from Color             import *
from GUIObject         import *
from Container         import *
from PopupBox          import *
from AlertBox          import *
from ConfirmBox        import *
from Label             import *
from Button            import *
from LetterBoxGroup    import *
from RegionScroller    import *
from Scrollbar         import *
from InputBox          import *
from LayoutManagers    import *
from exceptions        import *
from ProgressBox       import *

