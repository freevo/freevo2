# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# idlebar.py - IdleBar plugin
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.33  2004/11/20 18:23:03  dischi
# use python logger module for debug
#
# Revision 1.32  2004/10/12 13:55:23  dischi
# fix plugin position handling
#
# Revision 1.31  2004/10/07 14:02:48  dischi
# fix redraw when one plugin changes the width
#
# Revision 1.30  2004/09/14 14:00:39  dischi
# move plugins intro seperate files
#
# Revision 1.29  2004/09/08 08:33:13  dischi
# patch from Viggo Fredriksen to reactivate the plugins
#
# Revision 1.28  2004/08/27 14:27:54  dischi
# change to new animation class name
#
# Revision 1.27  2004/08/24 16:42:42  dischi
# Made the fxdsettings in gui the theme engine and made a better
# integration for it. There is also an event now to let the plugins
# know that the theme is changed.
#
# Revision 1.26  2004/08/23 20:41:47  dischi
# fade support
#
# Revision 1.25  2004/08/23 15:53:41  dischi
# do not remove from display, only hide
#
# Revision 1.24  2004/08/22 20:10:38  dischi
# changes to new mevas based gui code
#
# Revision 1.23  2004/08/05 17:39:34  dischi
# remove skin dep
#
# Revision 1.22  2004/08/01 10:48:21  dischi
# Move idlebar to new gui code:
# o it is not drawn inside the area (a.k.a skin) code anymore
# o it updates/removes itself if needed
#
# Some plugins are not changed to the new draw interface of the
# idlebar. They are deactivated. Feel free to send an updated version.
#
# Revision 1.21  2004/07/25 18:22:27  dischi
# changes to reflect gui update
#
# Revision 1.20  2004/07/24 17:49:48  dischi
# rename or deactivate some stuff for gui update
#
# Revision 1.19  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.18  2004/06/24 08:37:20  dischi
# add speed warning
#
# Revision 1.17  2004/05/31 10:43:20  dischi
# redraw not only in main, redraw when skin is active
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al.
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
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
# ----------------------------------------------------------------------- */

# python modules
import time
import locale

# freevo modules
import config
import plugin
import gui
import eventhandler
from event import *

import logging
log = logging.getLogger()

class PluginInterface(plugin.DaemonPlugin):
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
        plugin.DaemonPlugin.__init__(self)
        plugin.register(self, 'idlebar')
        eventhandler.register(self, SCREEN_CONTENT_CHANGE)
        eventhandler.register(self, THEME_CHANGE)
        self.poll_interval  = 300
        self.poll_menu_only = False
        self.plugins        = None
        self.visible        = False
        self.bar            = None
        self.barfile        = ''
        self.background     = None
        self.container      = gui.CanvasContainer()
        self.container.set_zindex(10)
        gui.display.add_child(self.container)

        # Getting current LOCALE
        try:
            locale.resetlocale()
        except:
            pass


    def update(self):
        """
        draw a background and all idlebar plugins
        """
        screen  = gui.get_display()
        changed = False

        w = screen.width
        h = config.OSD_OVERSCAN_Y + 60

        f = gui.get_image('idlebar')

        if self.barfile != f:
            if self.bar:
                self.container.remove_child(self.bar)
            self.barfile = f
            self.bar = gui.Image(self.barfile, (0,0), (w, h))
            self.container.add_child(self.bar)
            changed = True

        x1 = config.OSD_OVERSCAN_X
        y1 = config.OSD_OVERSCAN_Y
        x2 = screen.width - config.OSD_OVERSCAN_X
        y2 = h

        for p in plugin.get('idlebar'):
            width = p.draw(x2 - x1, y2 - y1)
            if width == p.NO_CHANGE:
                if p.align == 'left':
                    if changed:
                        p.set_pos((x1, y1))
                    x1 = x1 + p.width
                else:
                    if changed:
                        p.set_pos((x2 - width, y1))
                    x2 = x2 - p.width
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
            gui.get_display().update()


    def hide(self, update=True, fade=0):
        if not self.visible:
            return
        gui.animation.FadeAnimation([self.container], fade, 255, 0).start()
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
            self.background = gui.imagelib.load('background', (s.width, s.height))
            if self.background:
                size = (s.width, config.OSD_OVERSCAN_Y + 60)
                self.background.crop((0,0), size)
                self.background = gui.Image(self.background, (0,0))
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


    def eventhandler(self, event, menuw=None):
        """
        catch the IDENTIFY_MEDIA event to redraw the skin (maybe the cd status
        plugin wants to redraw). Also catch SCREEN_CONTENT_CHANGE in case we
        need to hide/show the bar.
        """
        if event == SCREEN_CONTENT_CHANGE:
            # react on toggle fullscreen, hide or show the bar, but not update
            # the screen itself, this is done by the app later
            app, fullscreen, fade = event.arg
            if fade:
                fade = config.OSD_FADE_STEPS
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
                self.update()
            return

        if not self.visible:
            return False

        if event == THEME_CHANGE:
            self.update()
        if plugin.isevent(event) == 'IDENTIFY_MEDIA':
            if self.update():
                gui.get_display().update()
        return False


    def poll(self):
        """
        update the idlebar every 30 secs even if nothing happens
        """
        if not self.visible:
            return
        if self.update():
            gui.get_display().update()



class IdleBarPlugin(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)
        self._type     = 'idlebar'
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
