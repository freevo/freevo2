# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# config.py
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2008 Dirk Meyer, et al.
#
# First edition: Dirk Meyer <dischi@freevo.org>
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

# FIXME, read this information from the theme file. That is not that
# simple as it sounds because the theme parser need this information
# and we get it after the theme is parsed.
aspect = 4,3

class Stage(object):
    """
    Special config for the gui geometry based on overscan and aspect
    ratio fixes.
    """
    def __init__(self, guicfg):
        self.scale = 1.0
        self.x = guicfg.display.overscan.x
        self.y = guicfg.display.overscan.y
        self.width = guicfg.display.width - 2 * self.x
        self.height = guicfg.display.height - 2 * self.y
        # check aspect ratio based on the smaller overscan based
        # sizes. They must match the theme aspect
        if self.width * aspect[1] != self.height * aspect[0]:
            # adjust height based on width and aspect and scale
            # based on the difference we just added
            original = self.height
            self.height = self.width * aspect[1] / aspect[0]
            self.scale = float(original) / self.height
        self.overscan_x = self.x
        self.overscan_y = int(self.y / self.scale)

class Config(object):

    def load(self, config, sharedir):
        self.stage = Stage(config.gui)
        self.freevo = config
        self.sharedir = sharedir

    def __getattr__(self, attr):
        return getattr(self.freevo.gui, attr)
    
# create config object
config = Config()
