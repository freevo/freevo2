# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# idlebar.py - IdleBar plugin
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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


# python imports
import time
import locale
import logging

import kaa.notifier

# freevo imports
from freevo.plugin import Plugin
from freevo.ui import gui, application
from freevo.ui import config
from freevo.ui.gui import theme, imagelib, widgets, animation
from freevo.ui.event import *

from plugin import IdleBarPlugin

# get logging object
log = logging.getLogger()

# get gui config object
guicfg = config.gui

class PluginInterface(Plugin):
    """
    """
    def plugin_activate(self, level):
        """
        init the idlebar
        """
        # register for signals
        application.signals['changed'].connect(self._app_change)

        self.plugins        = None
        self.visible        = False
        self.bar            = None
        self.barfile        = ''
        self.background     = None

        self.container = widgets.Container()
        self.container.set_zindex(10)
        gui.get_display().add_child(self.container)

        self._timer = kaa.notifier.Timer(self.poll)
        self._timer.start(30)


    def update(self):
        """
        draw a background and all idlebar plugins
        """
        changed = False

        w = gui.get_display().width
        h = guicfg.display.overscan.y + 60

        x1 = guicfg.display.overscan.x
        y1 = guicfg.display.overscan.y
        x2 = w - guicfg.display.overscan.x
        y2 = h

        for p in IdleBarPlugin.plugins():
            width = p.draw(x2 - x1, y2 - y1)
            if width == p.NO_CHANGE:
                if p.align == 'left':
                    if changed:
                        p.set_pos((x1, y1))
                    x1 = x1 + p.width
                else:
                    x2 = x2 - p.width
                    if changed:
                        p.set_pos((x2, y1))
                continue

            if width > x2 - x1:
                # FIXME
                continue

            if p.align == 'left':
                p.set_pos((x1, y1))
                for o in p.objects:
                    self.container.add_child(o)
                x1 = x1 + width
            else:
                p.set_pos((x2 - width, y1))
                for o in p.objects:
                    self.container.add_child(o)
                x2 = x2 - width
            p.width = width
            changed = True

        return changed


    def show(self, update=True, fade=0):
        if self.visible:
            return
        animation.FadeAnimation([self.container], fade, 0, 255).start()
        self.visible = True
        self.update()
        if update:
            gui.get_display().update()


    def hide(self, update=True, fade=0):
        if not self.visible:
            return
        animation.FadeAnimation([self.container], fade, 255, 0).start()
        self.visible = False
        if update:
            gui.get_display().update()


    def add_background(self):
        """
        add a background behind the bar
        """
        if not self.background:
            # FIXME: respect fxd settings changes!!!
            s = gui.get_display()
            size = (s.width, s.height)
            self.background = imagelib.load('background', size)
            if self.background:
                size = (s.width, guicfg.display.overscan.y + 60)
                self.background.crop((0,0), size)
                self.background = widgets.Image(self.background, (0,0))
                self.background.set_alpha(230)
                self.background.set_zindex(-1)
                self.container.add_child(self.background)
        else:
            self.background.show()


    def remove_background(self):
        """
        remove the background behind the bar
        """
        if self.background:
            self.background.hide()


    def _app_change(self, app):
        fullscreen = app.has_capability(application.CAPABILITY_FULLSCREEN)
        fade = True
        
        # get gui informations
        w = gui.get_display().width
        h = guicfg.display.overscan.y + 60

        f = theme.image('idlebar')

        if self.barfile != f:
            if self.bar:
                self.container.remove_child(self.bar)
            self.barfile = f
            self.bar = widgets.Image(self.barfile, (0,0), (w, h))
            self.container.add_child(self.bar)
        
        if fade:
            fade = guicfg.theme.fadestep
        else:
            fade = 0
        if fullscreen:
            # add the background behind the bar
            self.add_background()
        else:
            # remove the background again, it's done by the
            # 'not in fullscreen' app.
            self.remove_background()
        if fullscreen == self.visible:
            log.info('set visible %s' % (not fullscreen))
            if not self.visible:
                self.show(False, fade=fade)
            else:
                self.hide(False, fade=fade)
        return True


    def poll(self):
        """
        update the idlebar every 30 secs even if nothing happens
        """
        if not self.visible:
            return
        if self.update():
            gui.get_display().update()
