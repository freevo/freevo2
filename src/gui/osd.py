# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# osd.py - OSD Widget
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2008 Dirk Meyer, et al.
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

# kaa imports
from kaa.utils import property
import kaa.candy

class OSD(kaa.candy.Label):
    """
    This OSD widget is a label and it fades in and out
    """
    candyxml_name = 'osd'

    @property
    def message(self):
        return self.text

    @message.setter
    def message(self, message):
        self.text = message

    def hide(self):
        self.animate('0.2', unparent=True).behave('opacity', 255, 0)

    def show(self):
        self.opacity = 0
        self.animate('0.2').behave('opacity', 0, 255)
