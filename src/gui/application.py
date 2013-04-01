# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Application widget including OSD
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

__all__ = [ 'OSD', 'Application', 'ApplicationStyles' ]

import kaa.candy

from widget import Widget, WidgetStyles
from stage import ScaledGroup

# register xml eventhandler
kaa.candy.Eventhandler.signatures['system'] = 'widget,event'


class OSD(ScaledGroup):
    """
    On Screen Display for Application Widgets
    """
    candyxml_name = 'osd'
    candyxml_style = None

    class WidgetWrapper(object):
        """
        Wraper around a template to create a widget on demand
        """
        def __init__(self, template):
            self.template = template
            self.widget = None
            self.visible = False
            self.timer = None

    def __init__(self, pos=None, size=None, widgets=[], context=None, **osd_templates):
        super(OSD, self).__init__(pos, size, widgets, context)
        self.master = kaa.candy.Group((0,0), context=context)
        self.master.parent = self
        self.clone = None
        self.__children = {}
        self.stereo = None
        for key, template in osd_templates.items():
            self.__children[key] = OSD.WidgetWrapper(template)

    def sync_context(self):
        """
        Internal kaa.candy function before sync
        """
        super(OSD, self).sync_context()
        if 'stereo' in self.context and self.context.stereo != self.stereo:
            if not self.context.stereo and self.clone:
                self.clone = None
            elif not self.clone:
                self.clone = kaa.candy.Clone((0,0), master=self.master)
                self.clone.parent = self

    def sync_layout(self, (width, height)):
        """
        Internal kaa.candy function before sync
        """
        if 'stereo' in self.context and self.stereo != self.context.stereo:
            self.master.clip = (0,0), (self.width, self.height)
            if not self.context.stereo and not self.clone:
                self.master.scale_x = 1.0
                self.stereo = self.context.stereo
            elif self.context.stereo and self.clone:
                if self.context.stereo.startswith('side'):
                    self.master.scale_x = 0.5
                    self.clone.scale_x = 0.5
                    self.clone.x = self.width / 2
                else:
                    self.master.scale_y = 0.5
                    self.clone.scale_y = 0.5
                    self.clone.y = self.height / 2
                self.stereo = self.context.stereo
        super(OSD, self).sync_layout((width, height))

    def osd_show(self, name, autohide=None):
        """
        Show the OSD widget with the given name
        """
        obj = self.__children.get(name)
        if not obj:
            return None
        if obj.timer:
            obj.timer.stop()
            obj.timer = None
        if autohide:
            obj.timer = kaa.WeakOneShotTimer(self.osd_hide, name)
            obj.timer.start(autohide)
        if obj.visible:
            return None
        if not obj.widget:
            obj.widget = obj.template(context=self.context)
            obj.widget.parent = self.master
            obj.widget.application = kaa.weakref.weakref(self.parent)
        obj.visible = True
        return obj.widget.show()

    @kaa.coroutine()
    def osd_hide(self, name):
        """
        Hide the OSD widget with the given name
        """
        obj = self.__children.get(name)
        if not obj:
            yield None
        if obj.timer:
            obj.timer.stop()
            obj.timer = None
        if not obj.visible or not obj.widget:
            yield None
        obj.visible = False
        hiding = obj.widget.hide()
        if isinstance(hiding, kaa.InProgress):
            yield hiding
        if not obj.widget.visible and not obj.visible:
            obj.widget.destroy()
            obj.widget = None

    def osd_toggle(self, name):
        """
        Toggle the OSD widget with the given name
        """
        obj = self.__children.get(name)
        if obj:
            if obj.visible:
                return self.osd_hide(name)
            return self.osd_show(name)

    def osd_visible(self, name):
        """
        Return if the OSD with the given name is visible
        """
        widget = self.__children.get(name)
        return widget and widget.visible


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
    def scale_x(self):
        if self.layer:
            return self.layer.scale_x
        return 1.0

    @property
    def scale_y(self):
        if self.layer:
            return self.layer.scale_y
        return 1.0


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
        self.osd = OSDWrapper()
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
