# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# input - Input Submodule
# -----------------------------------------------------------------------------
# $Id$
#
# This module does not import anything from Freevo, plugins do. This module
# is very ugly. The EVENTMAP should not be defined here in one big file, each
# application should define it's own list of events. This means the video, dvd
# and vcd eventmap should be defined in the video submodule.
# The global eventmap variable could be in application. But application needs
# menu right now and menu needs the eventmap for menu mapping. This needs to
# be made clean.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2005-2007 Dirk Meyer, et al.
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

from keymap import KEYBOARD_MAP, REMOTE_MAP, DIRECTFB_MAP
from eventmap import EVENTMAP
