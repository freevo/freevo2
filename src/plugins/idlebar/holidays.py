# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# holidays.py - IdleBarPlugin for displaying holidays
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

import os
import time

import gui.widgets
import gui.imagelib
import config
from plugins.idlebar import IdleBarPlugin

class PluginInterface(IdleBarPlugin):
    """
    Display some holidays in the idlebar

    This plugin checks if the current date is a holiday and will
    display a specified icon for that holiday. If no holiday is found,
    nothing will be displayed. If you use the idlebar, you should activate
    this plugin, most of the time you won't see it.

    You can customize the list of holidays with the variable HOLIDAYS in
    local_config.py. The default value is:

    [ ('01-01',  'newyear.png'),
      ('02-14',  'valentine.png'),
      ('05-07',  'freevo_bday.png'),
      ('07-03',  'usa_flag.png'),
      ('07-04',  'usa_flag.png'),
      ('10-30',  'ghost.png'),
      ('10-31',  'pumpkin.png'),
      ('12-21',  'snowman.png'),
      ('12-25',  'christmas.png')]
    """
    def __init__(self):
        IdleBarPlugin.__init__(self)
        self.icon = ''

    def config(self):
        return [ ('HOLIDAYS', [ ('01-01',  'newyear.png'),
                                ('02-14',  'valentine.png'),
                                ('05-07',  'freevo_bday.png'),
                                ('07-03',  'usa_flag.png'),
                                ('07-04',  'usa_flag.png'),
                                ('10-30',  'ghost.png'),
                                ('10-31',  'pumpkin.png'),
                                ('12-21',  'snowman.png'),
                                ('12-25',  'christmas.png')],
                  'list of holidays this plugin knows') ]

    def get_holiday_icon(self):
        # Creates a string which looks like "07-04" meaning July 04
        todays_date = time.strftime('%m-%d')

        for i in config.HOLIDAYS:
            holiday, icon = i
            if todays_date == holiday:
                return os.path.join(config.ICON_DIR, 'holidays', icon)


    def draw(self, width, height):
        icon = self.get_holiday_icon()

        if icon == self.icon:
            return self.NO_CHANGE

        if icon:
            self.icon = icon
            self.clear()
            i = gui.imagelib.load(icon, (None, None))
            self.objects.append(gui.widgets.Image(i, (0, (height-i.height)/2)))

            return i.width

        return 0
