# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# controlpanel.py - Controlmanager
# -----------------------------------------------------------------------
# $Id:
#
# -----------------------------------------------------------------------
# $Log:
#
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

import gui
import plugin
import eventhandler
import config

from event import *

_cpmgr_ = None

def controlpanel():
    global _cpmgr_
    if not _cpmgr_:
        _cpmgr_ = ControlManager()

    return _cpmgr_


class ControlManager:
    """
    A class for showing different controlpanels
    on the screen.

    Use ControlPanel as basis for creating own panels.
    Register it to this manager with the register() and
    unregister() methods.
    """
    def __init__(self):
        self.plugins = []
        self.p_ctrl          = -1
        self.event_context   = 'input'

        self.container       = gui.CanvasContainer()
        self.container.set_zindex(80)

        gui.get_display().add_child(self.container)
        eventhandler.register(self, TOGGLE_CONTROL)


    def register(self, controlbar):
        """
        Register a controlbar
        """
        self.plugins.append(controlbar)

    def unregister(self, controlbar):
        """
        Unregister a controlbar
        """
        if controlbar not in self.plugins:
            return

        # hide if visible
        if controlbar.visible:
            self.hide()
            self.p_ctrl = -1

        self.plugins.remove(controlbar)



    def show(self):

        display = gui.get_display()
        control = self.plugins[self.p_ctrl]

        eventhandler.add_window(self)

        self.container.clear()
        self.container.show()

        # draw the control
        w, h = control.draw()

        # add a background
        bg = gui.Rectangle((0,0), (w, h+5), (0,0,0,100), 1,
                           (255,255,255,100), 4)
        bg.set_zindex(-1)
        self.container.add_child(bg)


        for o in control.objects:
            self.container.add_child(o)

        # TODO: support different placements
        x = config.GUI_OVERSCAN_X + 10
        y = display.height - config.GUI_OVERSCAN_Y - h

        self.container.set_pos((x,y))

        fade = config.GUI_FADE_STEPS
        if fade:
            gui.animation.FadeAnimation([self.container],fade, 0, 255).start()

        gui.get_display().update()


    def hide(self):
        eventhandler.remove_window(self)
        self.container.hide()
        gui.get_display().update()
        self.container.clear()
        self.plugins[self.p_ctrl].clear()


    def eventhandler(self, event):
        # Focus logic
        if event == TOGGLE_CONTROL:

            if len(self.plugins) < 1:
                return True

            last = self.p_ctrl
            next = self.p_ctrl + 1

            # destroy the current control
            if self.plugins[last].visible:
                self.hide()

                # if handler is run, stop here
                if self.plugins[last].handler_run:
                    self.p_ctrl = -1
                    return True

            # boundry check
            if next >= len(self.plugins):
                self.p_ctrl = -1
                return True

            # show if it's different
            if last != next:
                self.p_ctrl = next
                self.show()

            return True

        # Pass event to control
        elif event.context == self.event_context:
            if self.plugins[self.p_ctrl] and self.plugins[self.p_ctrl].visible:
                if event == INPUT_EXIT:
                    self.hide()
                    gui.get_display().update()
                    return True
                elif self.plugins[self.p_ctrl].eventhandler(event):
                    gui.get_display().update()
                    return True

        return False



class ButtonPanel:
    """
    This is an example ControlBar widget, it simply shows
    a buttonpanel on the screen.

    TODO: Add text describing each action
    """
    def __init__(self, handlers=[], button_size=(32,32), button_spacing=2, default_action=0):
        self.p_action      = default_action
        self.handlers      = handlers
        self.button_size   = button_size
        self.spacing       = button_spacing

        self.objects       = []
        self.buttons       = []
        self.visible       = False
        self.handler_run   = False


    def eventhandler(self, event):
        """
        The default eventhandler for a flat
        controlbar
        """
        if event == INPUT_LEFT:
            if self.p_action >= 1:
                self.buttons[self.p_action].deselect()
                self.p_action -= 1
                self.buttons[self.p_action].select()
                eventhandler.post(Event(OSD_MESSAGE, arg=self.handlers[self.p_action][0]))
            return True

        elif event == INPUT_RIGHT:
            if self.p_action < len(self.handlers)-1:
                self.buttons[self.p_action].deselect()
                self.p_action += 1
                self.buttons[self.p_action].select()
                eventhandler.post(Event(OSD_MESSAGE, arg=self.handlers[self.p_action][0]))
            return True

        elif event == INPUT_ENTER:
            self.buttons[self.p_action].handle()
            self.handler_run = True
            return True

        return False


    def draw(self):
        """
        Draws the controlbar

        return the size of the bar
        """
        if self.visible:
            return

        self.visible     = True

        w, h = self.button_size
        x    = self.spacing
        y    = self.spacing

        # create the controlbuttons
        for (descr, icon, action, arg) in self.handlers:
            i = ControlButton(icon, (action, arg), self.button_size, (x, y) )
            x += self.spacing + w
            self.objects.append(i)
            self.buttons.append(i)

        self.buttons[self.p_action].select()

        return (x, h+2*self.spacing)


    def clear(self):
        """
        Cleanup
        """
        if not self.visible:
            return

        for o in self.objects:
            o.unparent()

        self.objects     = []
        self.buttons     = []
        self.handler_run = False
        self.visible     = False



class ControlButton(gui.Image):
        """
        A simple icon-based button which can be selected or deselected.
        @icon    : Image or filename to an image
        @handler : A tuple of (method, argument), run by handle()
        @size    : size of the button (w,h)
        @pos     : position of the button
        @scale   : scalefactor for selected buttons
        """
        def __init__(self, icon, handler, size, pos, selected_zoom=1.3):
            self.handler = handler

            # calculate sizes and positions
            w, h = size
            x, y = pos
            sh = int(h*selected_zoom)
            sw = int(w*selected_zoom)
            sx = x + int((w-sw)/2)
            sy = y + int((h-sh)/2)

            self.icon     = icon
            self.pos      = pos
            self.size     = size
            self.sel_pos  = (sx, sy)
            self.sel_size = (sh, sw)

            gui.Image.__init__(self, self.icon, self.pos, self.size)

        def select(self):
            self.set_image(gui.Image(self.icon, self.sel_pos, self.sel_size))
            self.set_pos(self.sel_pos)

        def deselect(self):
            self.set_image(gui.Image(self.icon, self.pos, self.size))
            self.set_pos(self.pos)

        def handle(self):
            try:
                # FIXME: what about handlers without arg?
                #        Take a look at the rc.callback methods
                #        to do this properly
                self.handler[0](self.handler[1])
            except Exception, e:
                # XXX Maybe use a PopupBox here?
                print 'Handling failed on the controlbutton:'
                print e
