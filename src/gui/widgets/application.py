# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# core - Application Core
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

# display config
from .. import config

class ApplicationStyles(dict):
    """
    Dict to store the different application classes based on the
    freevo_appname (name) and the style.
    """
    candyxml_name = 'application'

    def get(self, name):
        """
        Get the given application class or return the default.
        """
        if not name in self:
            name = 'default'
        return super(ApplicationStyles, self).get(name)

    def candyxml_parse(self, element):
        """
        Parse and return the class based on the given xml element.
        """
        for key in ('%s:%s' % (element.name, element.style), element.name, 'default'):
            if key in self:
                return self.get(key)

# register this as application
kaa.candy.candyxml.register(ApplicationStyles(), kaa.candy.candyxml.STYLE_HANDLER)

class Application(kaa.candy.Container):
    """
    Application base class.
    """
    class __template__(kaa.candy.Container.__template__):
        @classmethod
        def candyxml_get_class(cls, element):
            name = element.name
            if element.style:
                name += ':%s' % element.style
            return kaa.candy.candyxml.get_class(element.node, name)

    candyxml_name = 'application'
    freevo_appname = 'default'

    def __init__(self, widgets, context=None):
        super(Application, self).__init__(None, None, widgets, context=context)

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the XML element for parameter to create the widget.
        """
        guicfg = config.stage
        for c in element:
            if c.ignore_overscan:
                # adjust direct children that want to ignore the overscan
                c._attrs['x'] = c._attrs.get('x', 0) - guicfg.overscan_x
                c._attrs['y'] = c._attrs.get('y', 0) - guicfg.overscan_y
                value = float(c._attrs.get('width', guicfg.width))
                factor = value / guicfg.width
                c._attrs['width'] = int(value + factor * 2 * guicfg.overscan_x)
                value = float(c._attrs.get('height', guicfg.height))
                factor = value / guicfg.height
                c._attrs['height'] = int(value + factor * 2 * guicfg.overscan_y)
        kwargs = super(Application, cls).candyxml_parse(element)
        return dict(widgets=kwargs['widgets'])

    @classmethod
    def candyxml_register(cls):
        name = cls.freevo_appname
        if hasattr(cls, 'candyxml_style'):
            name += ':%s' % cls.candyxml_style
        kaa.candy.candyxml.register(cls, name)

# register default application
Application.candyxml_register()
