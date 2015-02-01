# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Clutter Stage and basic groups
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

__all__ = [ 'Stage' ]

# python imports
import os
import logging

# kaa imports
import kaa.candy

# gui imports
from core import config
from application import Application

# get logging object
log = logging.getLogger('gui')

class Stage(kaa.candy.Stage):
    """
    Freevo main window
    """

    __kaasignals__ = {
        'reset':
            '''
            Emitted when the backend process closed its socket, most
            likely due to a crash. The stage and all its processes are
            now invalid.
            ''',
    }

    def __init__(self):
        size = (int(config.display.width), int(config.display.height))
        super(Stage, self).__init__(size, 'freevo2', os.path.expanduser('~/.freevo/log/candy'))
        self.theme_prefix = ''
        self.width, self.height = self.size
        self.applications = []
        self.destroy_layer(0)

    def load_theme(self, name=None, part=''):
        if name == None:
            name = config.theme
        if self.theme_prefix:
            for path in kaa.candy.config.imagepath[:]:
                if path.startswith(self.theme_prefix):
                    kaa.candy.config.imagepath.remove(path)
        self.theme_prefix = os.path.join(config.sharedir, 'themes', name)
        kaa.candy.config.imagepath.append(self.theme_prefix)
        attr, self.theme = self.candyxml(self.theme_prefix + '/' + part)
        self.theme.icons = os.path.join(self.theme_prefix, 'icons')
        # reference theme in all widgets
        # NOTE: this bounds all widgets created from this point to the
        # same theme. Two displays with different themes are not possible.
        # On the other hand setting a theme this way is fast and simple.
        kaa.candy.Widget.theme = self.theme
        kaa.candy.Widget.screen_width, kaa.candy.Widget.screen_height = self.size
        # Create the defined layers
        self.applications_idx = None
        for c in self.theme.get('freevo')[None]().children[:]:
            c = c()
            if c.name == 'application':
                self.applications_idx = self.layer[-1]
                continue
            self.add_layer(c)

    def __reset__(self):
        self.signals['reset'].emit()

    def show_application(self, application, fullscreen, context):
        """
        Render <application> widget with the given name and the given context.
        """
        if isinstance(application, (str, unicode)):
            tmp = self.theme.application.get(application)
            if not tmp:
                return log.error('no application named %s', application)
            application = tmp(size=self.size, context=context)
            self.add_layer(application, sibling=self.applications_idx)
        elif application is None:
            application = Application(self.size, [], context=context)
            self.add_layer(application, sibling=self.applications_idx)
        else:
            application.visible = True
            self.applications.remove(application)
        # TODO: add show/hide/remove/unparent/whatever here
        for l in self.layer:
            l.visible = not fullscreen
            if l == self.applications_idx:
                break
        if self.applications:
            self.applications[-1].visible = False
        self.applications.append(application)
        return application

    def show_widget(self, name, context=None):
        """
        Render widget with the given name
        """
        try:
            widget = self.theme.get('widget')[name](context=context)
            for c in self.layer:
                if c.name == widget.layer:
                    c.add(widget)
                    return widget
            log.error('widget %s has no valid layer %s' % (widget, widget.layer))
        except TypeError:
            log.error('widget %s not defined in theme', name)

    def destroy_application(self, app):
        """
        """
        self.destroy_layer(app)
        self.applications.remove(app)
