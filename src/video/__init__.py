# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# __init__.py
# -----------------------------------------------------------------------
# $Id$
#
# This file imports everything needed to use this video module.
# There is  only one class provided for video files, the PluginInterface
# from interface.py. It is a MimetypePlugin that can be accessed
# from plugin.mimetype(). It will also register an fxd handler for the
# <movie> and <disc-set> tags.
#
# Video plugins are also allowed to use VideoItem to create a new VideoItem
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.36  2004/09/14 20:05:19  dischi
# split __init__ into interface.py and database.py
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
# ----------------------------------------------------------------------- */

from interface import *

# special database imports (please fix)
from database import *

# used by video plugins
from videoitem import VideoItem
