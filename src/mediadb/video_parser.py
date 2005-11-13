# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# video_parser.py - parsing functions for video files
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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

# internal version of the file
VERSION = 0.1

# python imports
import os

# mediadb imports
from globals import *

def parse(filename, object, mminfo):
    """
    Parse additional data for video files.
    """
    if mminfo and mminfo.type == 'DVD':
        if os.path.isfile(filename) or os.path.isdir(filename):
            # a real file / dir
            object[URL]  = 'dvd://' + filename
        else:
            # a device
            object[URL]  = 'dvd://'
        object[TYPE] = 'dvd'


def cache(listing):
    """
    Function for the 'cache' helper.
    """
    pass
