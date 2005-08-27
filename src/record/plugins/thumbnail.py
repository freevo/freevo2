# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# thumbnail.py - Plugin to generated thumbnails for recordings
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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

# kaa imports
import kaa.thumb

# freevo imports
from record.plugins import Plugin
from record.record_types import *

class PluginInterface(Plugin):
    """
    Plugin to generated thumbnails for recordings.
    """
    def stop_recording(self, recording):
        """
        Create a thumbnail for the recording
        """
        if recording.status != SAVED:
            return
        if not recording.url.startswith('file:'):
            return
        filename = recording.url[5:]
        kaa.thumb.videothumb(filename)
