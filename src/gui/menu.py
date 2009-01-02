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

# kaa imports
import kaa
import kaa.candy

# gui imports
from application import Application

class MenuType(kaa.candy.Container):
    """
    Menu implementation, style default
    """
    candyxml_name = 'menu'
    candyxml_style = 'default'

    def __init__(self, widgets, context=None):
        super(MenuType, self).__init__(None, None, widgets, context=context)
        self.cid = context.get('menu').id

    def _candy_context_prepare(self, context):
        """
        Try if the widget is capable of handling the context.

        @param context: context dict
        """
        if self.cid != context.get('menu').id:
            # print 'menu change', self.context.get('menu').pos, context.get('menu').pos
            self.cid = context.get('menu').id
        return super(MenuType, self)._candy_context_prepare(context)

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

    def __del__(self):
        print 'del', self.context.get('type')

class MenuApplication(Application):
    """
    Menu application implementation, style simple
    """
    candyxml_style = 'menu:simple'

    def __init__(self, widgets, context=None):
        super(MenuApplication, self).__init__(widgets, context)
        self.templates = self.theme.get('menu')
        name = context.get('menu').type
        if not name in self.templates:
            name = 'default'
        self.__template = self.templates.get(name)
        self.menu = self.__template(context)
        self.menu.type = name
        self.add(self.menu)

    def _candy_context_prepare(self, context):
        """
        Try if the widget is capable of handling the context. This does not
        modify any internal variables and is thread safe.

        @param context: context dict
        """
        if not super(MenuApplication, self)._candy_context_prepare(context):
            return False
        name = context.get('menu').type
        if not name in self.templates:
            name = 'default'
        if self.menu.type == name:
            return True
        template = self.templates.get(name)
        if template == self.__template:
            # same template, just update the existing one
            self.menu.type = name
            return True
        self.__template = template
        menu = template(context)
        menu.type = name
        menu.prepare(self)
        self.menu.userdata['context:replace'] = menu
        return True

    def _candy_replace_child(self, child, replace, context):
        """
        Replace child with a new one.
        """
        if child == self.menu:
            self.menu = replace
        return super(MenuApplication, self)._candy_replace_child(child, replace, context)
