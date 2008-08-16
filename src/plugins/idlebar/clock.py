# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# clock.py - IdleBar clock
# -----------------------------------------------------------------------
# $Id:
#
# -----------------------------------------------------------------------
# $Log:
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
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
# ----------------------------------------------------------------------- */

import time
import kaa
import kaa.candy

from plugin import IdleBarPlugin

class PluginInterface(IdleBarPlugin):
    """
    Shows the current time.
    """
    def __init__(self, format=''):
        IdleBarPlugin.__init__(self)
        if format == '':
            if time.strftime('%P') =='':
                format ='%a %H:%M'
            else:
                format ='%a %I:%M %P'
        self.format = format
        self.widget = kaa.candy.Label((580,20), (200, 30), 'Vera', '0xffffff', '')
        self.widget.xalign=self.widget.ALIGN_RIGHT
        self.current = ''
        self.update()
        kaa.Timer(self.update).start(10)
        
    def update(self):
        clock = time.strftime(self.format)
        if clock == self.current:
            return
        self.widget.text = clock
