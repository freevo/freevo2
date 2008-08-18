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
import core

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
        kwargs = super(MenuType, cls).candyxml_parse(element)
        return dict(widgets=kwargs['widgets'])


class MenuApplication(core.Application):
    """
    Menu application implementation, style simple
    """
    __application__ = 'menu'
    candyxml_style = 'simple'

    def __init__(self, widgets, context=None):
        super(MenuApplication, self).__init__(widgets, context)
        self.__current = None
        self.templates = self.theme.get('menu')
        self.set_menu(context)

    def set_menu(self, context):
        name = context.get('menu').type
        if not name in self.templates:
            name = 'default'
        if not self.__current or self.__current.type != name:
            if self.__current:
                # FIXME: handle animations here
                self.__current.parent = None
            self.__current = self.templates.get(name)(context)
            self.__current.parent = self
            self.__current.type = name

    def set_context(self, context):
        self.set_menu(context)
        super(MenuApplication, self).set_context(context)
        
core.register(MenuApplication)
core.register(MenuType)
