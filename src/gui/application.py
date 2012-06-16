# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# application - application widget
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

__all__ = [ 'Application', 'ApplicationStyles' ]

# gui imports
import kaa.candy

from widget import Widget, WidgetStyles

class ApplicationStyles(WidgetStyles):
    """
    Dict to store the different application classes
    """
    candyxml_name = 'application'


class OSD(object):
    def __init__(self, template):
        self.template = template
        self.widget = None

    @kaa.coroutine()
    def toggle(self, parent):
        if self.widget and self.widget.visible:
            res = self.hide()
        else:
            res = self.show(parent)
        if isinstance(res, kaa.InProgress):
            yield res
        
    def show(self, parent):
        if not self.widget:
            self.widget = self.template(context=parent.context)
            self.widget.parent = parent
        return self.widget.show()

    @kaa.coroutine()
    def hide(self):
        res = self.widget.hide()
        if isinstance(res, kaa.InProgress):
            yield res
        if not self.widget.visible:
            self.widget.destroy()
            self.widget = None
        
        
class Application(Widget):
    """
    Application base class.
    """
    candyxml_name = 'application'

    def __init__(self, widgets, background=None, context=None, **osd_templates):
        if kaa.candy.is_template(background):
            background = background(context=context)
        self.background = background
        self.osd_widgets = {}
        for key, template in osd_templates.items():
            self.osd_widgets[key] = OSD(template)
        super(Application, self).__init__(None, None, widgets, context=context)

    def osd_show(self, name):
        """
        Show the OSD with the given name
        """
        widget = self.osd_widgets.get(name)
        if widget:
            return widget.show(self)

    def osd_hide(self, name):
        """
        Hide the OSD with the given name
        """
        widget = self.osd_widgets.get(name)
        if widget:
            return widget.hide()

    def osd_toggle(self, name):
        """
        Toggle the OSD with the given name
        """
        widget = self.osd_widgets.get(name)
        if widget:
            return widget.toggle(self)

    def sync_context(self):
        """
        Adjust to a new context
        """
        super(Application, self).sync_context()
        if not self.background:
            return
        if not self.background.supports_context(self.context):
            new = self.background.__template__(context=self.context)
            self.background.parent.replace(self.background, new)
            self.background = new
        else:
            self.background.context = self.context

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the XML element for parameter to create the widget.
        """
        attrs = super(Application, cls).candyxml_parse(element).remove('pos', 'size')
        return kaa.candy.XMLdict(**attrs)
