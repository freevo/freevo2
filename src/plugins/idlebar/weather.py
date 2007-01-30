# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# weather.py - idlebarplugin for showing weather information
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# Maintainer:    Viggo Fredriksen <viggo@katatonic.org>
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

# python modules
import os
import time

# freevo modules
from freevo.ui.gui import theme, widgets
from freevo.ui import config, plugin, gui
from plugins.idlebar import IdleBarPlugin

# grabber module
from pywebinfo.weather import WeatherGrabber

class PluginInterface(IdleBarPlugin):
    """
    Shows the current weather on the idlebar.

    Activate with:
    plugin.activate('idlebar.weather', level=30,
                    args=('4-letter code', metric))

    For weather station codes check:
    http://www.msnbc.com/news/WEA_Front.asp?cp1=1
    You can also set the metric to True if you want metric units (celcius).
    """
    def __init__(self, zone='GMXX0014', metric=False):
        IdleBarPlugin.__init__(self)

        self.metric    = metric
        self.metarcode = zone
        self.active    = False

        # check every 10 minutes
        self.cache_keep  = 60*10

        self.cache_icon  = None
        self.cache_temp  = None
        self.cache_check = -1

        self.new_icon  = None
        self.new_temp  = None



    def cb_weather(self, result):
        """
        Result callback from the weather grabber.
        """
        if not result:
            # not a valid result
            return

        if self.cache_temp == result.temp and \
              self.cache_icon == result.icon:
            # valid result, but equal to old
            return

        # update on next pass
        self.new_temp = result.temp
        self.new_icon = result.icon

        # update the idlebar
        self.update()


    def draw(self, width, height):
        """
        Draw the information on the idlebar
        """
        if self.new_temp or self.new_icon:
            # new results are available, we know these
            # are different then before, so there is
            # a point in re-drawing it on the screen.
            self.cache_icon = self.new_icon
            self.cache_temp = self.new_temp
            self.new_temp   = None
            self.new_icon   = None

            self.clear()

            if not self.cache_icon:
                # no icon available
                self.cache_icon = 'unknown.png'

            if not self.cache_temp:
                # no temperature available
                self.cache_temp = _('na')

            icon = os.path.join(config.IMAGE_DIR, 'weather', self.cache_icon)
            font = theme.font('small0')
            temp = unicode('%s\xb0' % self.cache_temp)

            # icon object
            img = widgets.Image(icon, pos=(5, 5))
            (iw, ih) = img.get_size()

            # scale it to fit
            height = 50 - 10
            width  = int( (float(iw)/float(ih)) * float(height) )
            img.scale((width, height))

            # text object
            txt_size = (width, 50)
            txt_pos  = (5, 0)
            txt = widgets.Text(temp, txt_pos, txt_size, font, 'center', 'center')

            (tw, th) = img.get_size()

            # add to objects
            self.objects.append(img)
            self.objects.append(txt)

            return width

        if (time.time() - self.cache_check) < self.cache_keep:
            # don't check for changes
            return self.NO_CHANGE


        # Fetch the information we want with the grabber.
        self.cache_check = time.time()
        grabber          = WeatherGrabber(cb_result=self.cb_weather)
        grabber.search(self.metarcode, self.metric, False)
        return self.NO_CHANGE
