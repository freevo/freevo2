# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# progressbox.py - popup box with progressbar
# -----------------------------------------------------------------------------
# $Id$
#
# A box showing a progress bar. There is no wait for the user to close the
# box, this has to be done from the outside.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
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

__all__ = [ 'ProgressBox' ]

# python imports
import notifier
import logging

# gui imports
from gui.widgets.progressbar import Progressbar

# windows imports
from waitbox import WaitBox

# get logging object
log = logging.getLogger()


class ProgressBox(WaitBox):
    """
    A box showing a progress bar. There is no wait for the user to close the
    box, this has to be done from the outside.
    """
    def __init__(self, text, full=0):
        WaitBox.__init__(self, text)

        h = 25
        y = self.add_row(h)
        x = self.get_content_pos()[0]
        style = self.widget_normal.rectangle
        self.bar = Progressbar((x, y), (self.get_content_size()[0], h),
                               2, style.color, style.bgcolor, 0, None,
                               self.widget_selected.rectangle.bgcolor, 0, full)
        self.add_child(self.bar)


    def tick(self):
        """
        increase the bar position
        """
        notifier.step( False, False )
        self.bar.tick()
        self.update()
