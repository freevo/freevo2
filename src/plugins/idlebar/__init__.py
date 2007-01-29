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
from freevo.ui import config
from freevo.ui import plugin
import gui
import gui.imagelib
import gui.widgets
import gui.animation
import gui.theme
import application
from freevo.ui.event import *

# get logging object
log = logging.getLogger()


class PluginInterface(plugin.Plugin):
    """
    To activate the idle bar, put the following in your local_conf.py:
        plugin.activate('idlebar')
    You can then add various plugins. Plugins inside the idlebar are
    sorted based on the level (except the clock, it's always on the
    right side). Use 'freevo plugins -l' to see all available plugins,
    and 'freevo plugins -i idlebar.<plugin>' for a specific plugin.
    """
    def __init__(self):
        """
        init the idlebar
        """
        plugin.Plugin.__init__(self)
        plugin.register(self, 'idlebar')

        # register for signals
        application.signals['changed'].connect(self._app_change)

        self.plugins        = None
        self.visible        = False
        self.bar            = None
        self.barfile        = ''
        self.background     = None

        self.container = gui.widgets.Container()
        self.container.set_zindex(10)
        gui.display.add_child(self.container)

        self._timer = kaa.notifier.Timer(self.poll)
        self._timer.start(30)

        # Getting current LOCALE
        try:
            locale.resetlocale()
        except:
            pass


    def update(self):
        """
        draw a background and all idlebar plugins
        """
        changed = False

        w = gui.display.width
        h = config.GUI_OVERSCAN_Y + 60

        x1 = config.GUI_OVERSCAN_X
        y1 = config.GUI_OVERSCAN_Y
        x2 = w - config.GUI_OVERSCAN_X
        y2 = h

        for p in plugin.get('idlebar'):
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
        gui.animation.FadeAnimation([self.container], fade, 0, 255).start()
        self.visible = True
        self.update()
        if update:
            gui.display.update()


    def hide(self, update=True, fade=0):
        if not self.visible:
            return
        gui.animation.FadeAnimation([self.container], fade, 255, 0).start()
        self.visible = False
        if update:
            gui.display.update()


    def add_background(self):
        """
        add a background behind the bar
        """
        if not self.background:
            # FIXME: respect fxd settings changes!!!
            s = gui.display
            size = (s.width, s.height)
            self.background = gui.imagelib.load('background', size)
            if self.background:
                size = (s.width, config.GUI_OVERSCAN_Y + 60)
                self.background.crop((0,0), size)
                self.background = gui.widgets.Image(self.background, (0,0))
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
        w = gui.display.width
        h = config.GUI_OVERSCAN_Y + 60

        f = gui.theme.image('idlebar')

        if self.barfile != f:
            if self.bar:
                self.container.remove_child(self.bar)
            self.barfile = f
            self.bar = gui.widgets.Image(self.barfile, (0,0), (w, h))
            self.container.add_child(self.bar)
        
        if fade:
            fade = config.GUI_FADE_STEPS
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
            gui.display.update()



class IdleBarPlugin(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)
        self._plugin_type = 'idlebar'
        self.objects   = []
        self.NO_CHANGE = -1
        self.align     = 'left'
        self.__x       = 0
        self.__y       = 0
        self.width     = 0


    def draw(self, width, height):
        return self.NO_CHANGE



    def clear(self):
        self.__x = 0
        self.__y = 0
        for o in self.objects:
            o.unparent()
        self.objects = []


    def set_pos(self, (x, y)):
        """
        move to x position
        """
        if x == self.__x and y == self.__y:
            return
        for o in self.objects:
            o.move_relative(((x - self.__x), (y - self.__y)))
        self.__x = x
        self.__y = y


    def update(self):
        """
        Force idlebar update.
        """
        bar = plugin.getbyname('idlebar')
        if bar:
            bar.poll()
