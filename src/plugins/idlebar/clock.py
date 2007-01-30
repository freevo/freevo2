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

from freevo.ui import gui
from freevo.ui.gui import theme, widgets
from plugins.idlebar import IdleBarPlugin

class PluginInterface(IdleBarPlugin):
    """
    Shows the current time.

    Activate with:
    plugin.activate('idlebar.clock',   level=50)
    Note: The clock will always be displayed on the right side of
    the idlebar.
    """
    def __init__(self, format=''):
        IdleBarPlugin.__init__(self)
        if format == '': # No overiding of the default value
            if time.strftime('%P') =='':
                format ='%a %H:%M'
            else:
                format ='%a %I:%M %P'

        self.format = format
        self.object = None
        self.align  = 'right'
        self.width  = 0
        self.text   = ''

    def draw(self, width, height):
        clock  = time.strftime(self.format)

        if self.objects and self.text == clock:
            return self.NO_CHANGE

        self.clear()

        font  = theme.font('clock')
        width = min(width, font.stringsize(clock))

        txt = widgets.Text(clock, (0, 0), (width, height), font,
                           align_v='center', align_h='right')
        self.objects.append(txt)
        self.text = clock
        return width
