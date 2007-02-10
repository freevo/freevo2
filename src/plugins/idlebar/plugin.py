# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# idlebar/plugin.py - Basic Idlebar plugin
# -----------------------------------------------------------------------------
# $Id: mainmenu.py 9193 2007-02-10 19:34:15Z dmeyer $
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2005-2007 Dirk Meyer, et al.
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

from freevo.ui import plugin

class IdleBarPlugin(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)
        self._plugin_type = 'idlebar'
        self.objects   = []
        self.NO_CHANGE = -1
        self.align     = 'left'
        self.__x       = 0
        self.__y       = 0
        self.width     = 0
        if not plugin.getbyname('idlebar'):
            plugin.activate('idlebar')


    def draw(self, width, height):
        return self.NO_CHANGE



    def clear(self):
        self.__x = 0
        self.__y = 0
        for o in self.objects:
            o.unparent()
        self.objects = []


    def set_pos(self, (x, y)):
        """
        move to x position
        """
        if x == self.__x and y == self.__y:
            return
        for o in self.objects:
            o.move_relative(((x - self.__x), (y - self.__y)))
        self.__x = x
        self.__y = y


    def update(self):
        """
        Force idlebar update.
        """
        plugin.getbyname('idlebar').poll()


    def plugins():
        """
        Static function to return all IdlebarPlugins.
        """
        return plugin.get('idlebar')

    plugins = staticmethod(plugins)
