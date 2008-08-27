# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# menu - Menu Application
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

# gui imports
import kaa.candy
from application import Application

class MenuType(kaa.candy.Container):
    """
    Menu implementation, style default
    """
    candyxml_name = 'menu'
    candyxml_style = 'default'

    def __init__(self, widgets, context=None):
        super(MenuType, self).__init__(None, None, widgets, context=context)

    def set_context(self, context):
        # FIXME: handle animations here
        # context.get('menu').pos
        super(MenuType, self).set_context(context)

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the XML element for parameter to create the widget.
        """
        widgets = []
        for inherit in element.get_children('inherit'):
            element.remove(inherit)
            theme = element
            while getattr(theme, '_parent', None):
                theme = theme._parent
            kwargs = theme._elements.get(element.node)[inherit.name]._kwargs
            widgets.extend(kwargs.get('widgets'))
        widgets.extend(super(MenuType, cls).candyxml_parse(element).get('widgets'))
        return dict(widgets=widgets)


class MenuApplication(Application):
    """
    Menu application implementation, style simple
    """
    freevo_appname = 'menu'
    candyxml_style = 'simple'

    def __init__(self, widgets, context=None):
        super(MenuApplication, self).__init__(widgets, context)
        self.templates = self.theme.get('menu')
        name = context.get('menu').type
        if not name in self.templates:
            name = 'default'
        self.__menu = self.templates.get(name)(context)
        self.__menu.type = name
        self.__menu.parent = self

    def try_context(self, context):
        if not super(MenuApplication, self).try_context(context):
            return False
        name = context.get('menu').type
        if not name in self.templates:
            name = 'default'
        if self.__menu.type != name:
            menu = self.templates.get(name)(context)
            menu.type = name
            menu._prepare_sync_with_parent(self)
            self._queue_replace_children(self.__menu, menu)
        return True

    def _child_replace(self, old, new):
        """
        Replace child with a new one.
        """
        if old != self.__menu:
            return super(MenuApplication, self)._child_replace(old, new)
        # FIXME: add some nice animations here
        old.parent = None
        self.__menu = new
        self.__menu.parent = self

MenuApplication.candyxml_register()
MenuType.candyxml_register()
