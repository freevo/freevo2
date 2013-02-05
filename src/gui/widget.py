# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Generic widgets for menu and osd
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2009-2013 Dirk Meyer, et al.
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

__all__ = [ 'Widget', 'WidgetStyles' ]

import kaa.candy

kaa.candy.Eventhandler.signatures['widget-show'] = 'self'
kaa.candy.Eventhandler.signatures['widget-hide'] = 'self'

class WidgetStyles(kaa.candy.candyxml.Styles):
    """
    """
    candyxml_name = 'widget'

    def get(self, name):
        """
        Get the given widget class or return the default.
        """
        if not name in self:
            name = None
        return super(WidgetStyles, self).get(name)

    def candyxml_parse(self, element):
        """
        Parse and return the class based on the given xml element.
        """
        return self.get(element.name)


class Widget(kaa.candy.Group):
    candyxml_name = 'widget'

    # This variable can be False (not visible), True (visible) and
    # 'showing' and 'hiding' for the transitions. The later translate
    # to True in the visible property to make sure kaa.candy does not
    # delete the item because the flag is False and we need a way to
    # determain if we are about to be visible or hidden.
    __visible = False

    class __template__(kaa.candy.AbstractGroup.__template__):
        @classmethod
        def candyxml_get_class(cls, element):
            return kaa.candy.candyxml.get_class(element.node, element.name)

    def __init__(self, pos=None, size=None, widgets=[], layer=None, context=None):
        super(Widget, self).__init__(pos, size, widgets, context)
        self.layer = layer

    @property
    def status(self):
        if self.__visible == True:
            return 'visible'
        if self.__visible == False:
            return 'hidden'
        return self.__visible

    @property
    def visible(self):
        return bool(self.__visible)

    @visible.setter
    def visible(self, visible):
        if bool(self.__visible) == visible:
            return
        if visible:
            self.show()
        else:
            self.hide()

    @kaa.coroutine()
    def show(self):
        if self.__visible in ('showing', True):
            yield None
        self.__visible = 'showing'
        showing = self.emit('widget-show', self)
        if isinstance(showing, kaa.InProgress):
            yield showing
        if self.__visible == 'showing':
            self.__visible = True

    @kaa.coroutine()
    def hide(self):
        if self.__visible in ('hiding', False):
            yield None
        self.__visible = 'hiding'
        hiding = self.emit('widget-hide', self)
        if isinstance(hiding, kaa.InProgress):
            yield hiding
        if self.__visible == 'hiding':
            self.__visible = False

    @kaa.coroutine()
    def destroy(self):
        hiding = self.hide()
        if isinstance(hiding, kaa.InProgress):
            yield hiding
        self.parent = None

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the candyxml element for parameter to create the widget.
        """
        return super(Widget, cls).candyxml_parse(element).update(layer=element.layer)
