# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# group - group widgets
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2012 Dirk Meyer, et al.
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

__all__ = [ 'ScaledGroup', 'Freevo', 'Content' ]

import kaa.candy

from stage import config

class ScaledGroup(kaa.candy.Group):
    """
    Group with XML theme scaling
    """
    candyxml_name = 'group'
    candyxml_style = 'scaled'

    __screen_width = None
    __screen_height = None

    @property
    def screen_width(self):
        return self.__screen_width

    @screen_width.setter
    def screen_width(self, value):
        self.__screen_width = int(value)
        self.scale_x = float(self.ssize[0] - ( 2 * config.display.overscan.x)) / int(value)

    @property
    def screen_height(self):
        return self.__screen_height

    @screen_height.setter
    def screen_height(self, value):
        self.__screen_height = int(value)
        self.scale_y = float(self.ssize[1] - ( 2 * config.display.overscan.y)) / int(value)


class Freevo(ScaledGroup):
    """
    Base Freevo widget
    """
    candyxml_name = 'freevo'
    candyxml_style = None

    def __init__(self, pos=None, size=None, widgets=[], context=None):
        super(ScaledGroup, self).__init__(pos, size, [], context)
        self.children = widgets


class Content(ScaledGroup):
    """
    Base Freevo widget
    """
    candyxml_name = 'content'
    candyxml_style = None


class Layer(ScaledGroup):

    candyxml_name = 'layer'
    candyxml_style = None

    _candy_layer_status = 0     # 0 new, 1 active, 2 destroyed

    def __init__(self, pos=None, size=None, ssize=None, widgets=[], context=None):
        if not size:
            size = ssize
        size = (size[0] or ssize[0], size[1] or ssize[1])
        self.screen_width, self.screen_height = size
        super(Layer, self).__init__(pos, size, widgets, context)

    @property
    def parent(self):
        return self.stage



class OSD(ScaledGroup):

    candyxml_name = 'osd'
    candyxml_style = None

    class WidgetWrapper(object):
        def __init__(self, template):
            self.template = template
            self.widget = None
            self.__visible = False

        def toggle(self, parent, application):
            if self.visible:
                return self.hide()
            return self.show(parent, application)

        def show(self, parent, application):
            if self.__visible:
                return None
            if not self.widget:
                self.widget = self.template(context=parent.context)
                self.widget.parent = parent.master
                self.widget.application = kaa.weakref.weakref(application)
            self.__visible = True
            return self.widget.show()

        @property
        def visible(self):
            return self.__visible

        @kaa.coroutine()
        def hide(self):
            if not self.__visible or not self.widget:
                yield None
            self.__visible = False
            hiding = self.widget.hide()
            if isinstance(hiding, kaa.InProgress):
                yield hiding
            if not self.widget.visible and not self.__visible:
                self.widget.destroy()
                self.widget = None


    def __init__(self, pos=None, size=None, widgets=[], context=None, **osd_templates):
        super(OSD, self).__init__(pos, size, widgets, context)
        self.master = kaa.candy.Group((0,0), context=context)
        self.master.parent = self
        self.clone = None
        self.timer = None
        self.osd_widgets = {}
        self.stereo = None
        for key, template in osd_templates.items():
            self.osd_widgets[key] = OSD.WidgetWrapper(template)

    def sync_context(self):
        super(OSD, self).sync_context()
        if self.context.stereo != self.stereo:
            if not self.context.stereo and self.clone:
                self.clone = None
            elif not self.clone:
                self.clone = kaa.candy.Clone((0,0), master=self.master)
                self.clone.parent = self
            
    def sync_layout(self, (width, height)):
        if self.stereo != self.context.stereo:
            self.master.clip = (0,0), (self.screen_width, self.screen_height)
            if not self.context.stereo and not self.clone:
                self.master.scale_x = 1.0
                self.stereo = self.context.stereo
            elif self.context.stereo and self.clone:
                if self.context.stereo.startswith('side'):
                    self.master.scale_x = 0.5
                    self.clone.scale_x = 0.5
                    self.clone.x = self.screen_width / 2
                else:
                    self.master.scale_y = 0.5
                    self.clone.scale_y = 0.5
                    self.clone.y = self.screen_height / 2
                self.stereo = self.context.stereo
        super(OSD, self).sync_layout((width, height))
        
    def osd_show(self, name, autohide=None):
        """
        Show the OSD with the given name
        """
        if self.timer:
            self.timer.stop()
            self.timer = None
        if autohide:
            self.timer = kaa.WeakOneShotTimer(self.osd_hide, name)
            self.timer.start(autohide)
        widget = self.osd_widgets.get(name)
        if widget:
            return widget.show(self, self.parent)

    def osd_hide(self, name):
        """
        Hide the OSD with the given name
        """
        if self.timer:
            self.timer.stop()
            self.timer = None
        widget = self.osd_widgets.get(name)
        if widget:
            return widget.hide()

    def osd_toggle(self, name):
        """
        Toggle the OSD with the given name
        """
        widget = self.osd_widgets.get(name)
        if widget:
            return widget.toggle(self, self.parent)

    def osd_visible(self, name):
        """
        Return if the OSD with the given name is visible
        """
        widget = self.osd_widgets.get(name)
        return widget and widget.visible
