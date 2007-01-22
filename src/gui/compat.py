# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
#
# This file does some ugly stuff to deal with the new application subsystem.
# We need a rewrite for this, but we will wait for kaa.candy before doing it.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Krister Lagerstrom, Dirk Meyer, et al.
#
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


class BaseApplication(object):
    visible = None
    
    def __init__(self):
        from areas import Handler
        import config
        self.GUI_FADE_STEPS = config.GUI_FADE_STEPS
        self.engine = Handler(self.name, self.areas)

    def show(self):
        if BaseApplication.visible and BaseApplication.visible != self:
            BaseApplication.visible.hide(self.GUI_FADE_STEPS)
        BaseApplication.visible = self
        self.engine.show(self.GUI_FADE_STEPS)

    def hide(self, fade=0):
        if BaseApplication.visible == self:
            BaseApplication.visible = None
        self.engine.hide(fade)
    

class _Menu(BaseApplication):
    name = 'menu'
    areas = ('screen', 'title', 'subtitle', 'view', 'listing', 'info')

    def __init__(self):
        from areas import Handler
        BaseApplication.__init__(self)
        self.menuengine = self.engine
        tv = ('screen', 'title', 'subtitle', 'view', 'tvlisting', 'info')
        self.tvengine = Handler('tv', tv)
        self.intv = False
        self.drawing = False
        self.waiting = None
        
    def update(self, menu):
        if self.drawing:
            self.waiting = menu
            return
        self.drawing = True
        
        if menu.type == 'tvgrid' and not self.intv:
            self.tvengine.show()
            self.engine.hide()
            self.engine = self.tvengine
            self.intv = True
        if menu.type != 'tvgrid' and self.intv:
            self.menuengine.show()
            self.engine.hide()
            self.engine = self.menuengine
            self.intv = False

        if menu.type != 'tvgrid' or menu.selected:
            # FIXME: tvguide is async
            self.engine.draw(menu)

        self.drawing = False
        if self.waiting:
            menu = self.waiting
            self.waiting = None
            self.update(menu)

class _Audioplayer(BaseApplication):
    name = 'player'
    areas = ('screen', 'title', 'view', 'info')
    
    def set_item(self, item):
        self.item = item
        
    def update(self):
        self.engine.draw(self.item)


class _Imageviewer(BaseApplication):
    name = 'viewer'
    areas = ()

    def update(self):
        self.engine.canvas.update()
        
        
class _Videoplayer(BaseApplication):
    name = 'video'
    areas = ()


    def set_item(self, item):
        self.item = item
        
    def update(self):
        pass

    def get_window(self):
        return self.engine.canvas._window
    
    
def Application(name):
    return eval('_' + name.capitalize())()

    
class Window(object):
    def __init__(self, name):
        import windows
        self.engine_class = getattr(windows, name.capitalize() + 'Box')

    def update(self):
        self.engine.update()
    
    def show(self, x):
        self.engine = self.engine_class(x)
        self.engine.show()

    def hide(self):
        self.engine.destroy()

