# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Application widget
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

__all__ = [ 'Application', 'ApplicationStyles' ]

import kaa.candy

from widget import Widget, WidgetStyles

# register xml eventhandler
kaa.candy.Eventhandler.signatures['system'] = 'widget,event'


class ApplicationStyles(WidgetStyles):
    """
    Dict to store the different application classes
    """
    candyxml_name = 'application'


class Application(kaa.candy.Layer):
    """
    Application base class.
    """
    candyxml_name = 'application'

    class OSDWrapper(object):
        """
        Wrapper around the actual OSD widget in case it is not
        available. This class uses simpler method names; instead of
        osd_show() it is just show(). The actual widget cannot use
        these names but they are reserved by kaa.candy.
        """
        layer = None

        def show(self, name, autohide=None):
            """
            Show the OSD with the given name
            """
            if self.layer:
                return self.layer.osd_show(name, autohide)

        def hide(self, name):
            """
            Hide the OSD with the given name
            """
            if self.layer:
                return self.layer.osd_hide(name)

        def toggle(self, name):
            """
            Toggle the OSD with the given name
            """
            if self.layer:
                return self.layer.osd_toggle(name)

        def is_visible(self, name):
            """
            Return if the OSD with the given name is visible
            """
            if self.layer:
                return self.layer.osd_visible(name)
            return False

        @property
        def scale(self):
            if self.layer:
                return self.layer.scale_x, self.layer.scale_y
            return 1.0, 1.0

    class __template__(kaa.candy.AbstractGroup.__template__):
        @classmethod
        def candyxml_get_class(cls, element):
            return kaa.candy.candyxml.get_class(element.node, element.name)

    def __init__(self, size, widgets, background=None, context=None):
        """
        Constructor for the application widget
        """
        if kaa.candy.is_template(background):
            background = background(context=context)
        self.osd = Application.OSDWrapper()
        self.timer = None
        self.background = background
        super(Application, self).__init__(size, widgets, context)
        for child in self.children:
            # connect to OSD widget
            if child.candyxml_name == 'osd':
                self.osd.layer = child

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

    def eventhandler(self, event):
        """
        Hook into all Freevo events to react on them in the GUI.
        """
        self.emit('system', self, event)
