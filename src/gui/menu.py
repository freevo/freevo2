# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# menu - Menu Application
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2008-2011 Dirk Meyer, et al.
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

kaa.candy.Eventhandler.signatures['submenu-show'] = 'self, menu'
kaa.candy.Eventhandler.signatures['submenu-hide'] = 'self, menu'

class MenuWidget(kaa.candy.Group):
    """
    Menu implementation
    """
    candyxml_name = 'menu'


class MenuApplication(Application):
    """
    Menu application implementation
    """
    candyxml_style = 'menu'

    def __init__(self, widgets, background=None, context=None):
        super(MenuApplication, self).__init__(widgets, background, context)
        self.templates = self.theme.get('menu')
        name = context.get('menu').type
        if not name in self.templates:
            name = 'default'
        self.menu = self.templates.get(name)(context)
        self.menu.type = name
        self.menu.parent = self
        self.bgmenu = None

    @kaa.coroutine()
    def hide_submenu(self, submenu, menu):
        # FIXME: if a new menu is a different widget than the old one,
        # we are changing the old one back here while indepenent a new
        # menu comes in which does not know there was a submenu
        menu.freeze_context = False
        submenu.freeze_context = True
        hiding = submenu.emit('submenu-hide', submenu, menu)
        if isinstance(hiding, kaa.InProgress):
            yield hiding
        submenu.parent = None

    def sync_context(self):
        name = self.context.get('menu').type
        if not name in self.templates:
            name = 'default'
        if self.menu.type == name:
            return super(MenuApplication, self).sync_context()
        template = self.templates.get(name)
        if template == self.menu.__template__:
            # same template, just update the existing one
            self.menu.type = name
            return super(MenuApplication, self).sync_context()
        if name != 'submenu' and self.bgmenu:
            # we switched away from a submenu. Remove the submenu from
            # the stack and do the function call again.
            self.hide_submenu(self.menu, self.bgmenu)
            self.menu = self.bgmenu
            self.bgmenu = None
            return self.sync_context()
        new = template(self.context)
        new.type = name
        if name == 'submenu':
            # switch to submenu
            self.bgmenu = self.menu
            self.bgmenu.freeze_context = True
            self.menu = new
            self.menu.parent = self
            self.menu.emit('submenu-show', self.menu, self.bgmenu)
        else:
            # normal menu switch
            self.replace(self.menu, new)
            self.menu = new
        super(MenuApplication, self).sync_context()
