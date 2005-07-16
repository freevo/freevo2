# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# controlpanel.py - Freevo control management
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains a basic control manager. With this manager one can add
# on-screen controls which is toggled by the TOGGLE_CONTROL event. Plugins
# can add panels to this manager and therefore show it to the user.
#  - See audio.plugins.detach and See audio.plugins.mplayervis for an examples
#    on usage.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Viggo Fredriksen <viggo@katatonic.org>
# Maintainer:    Viggo Fredriksen <viggo@katatonic.org>
#
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
# -----------------------------------------------------------------------------

import kaa.notifier

import gui
import gui.widgets
import gui.theme

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


class ControlManager(object):
    """
    A class for showing different controlpanels
    on the screen.

    Use ButtonPanel as basis for creating own panels.
    Register it to this manager with the register() and
    unregister() methods. See audio.plugins.detach for
    an example on usage.

    TODO: Needs clean-up and nice graphics!
    """
    def __init__(self):
        self.plugins = []
        self.p_ctrl          = -1

        self.container = gui.widgets.Container()
        self.container.set_zindex(80)

        gui.display.add_child(self.container)

        # listen for TOGGLE_CONTROL events
        kaa.notifier.EventHandler(self.eventhandler).register(TOGGLE_CONTROL)


    def register(self, controlbar):
        """
        Register a control widget
        """
        self.plugins.append(controlbar)


    def unregister(self, controlbar):
        """
        Unregister a control widget
        """
        if controlbar not in self.plugins:
            return

        # hide if visible
        if controlbar.visible:
            self.hide()
            self.p_ctrl = -1

        self.plugins.remove(controlbar)



    def show(self):
        """
        Shows the currently selected control widget
        """
        display = gui.display
        control = self.plugins[self.p_ctrl]

        # add controlmanager as a window
        eventhandler.add_window(self)

        # clear the container and set it visible
        self.container.clear()
        self.container.show()


        # draw the control
        w, h = control.draw((5, 5))
        w += 10
        h += 10

        # add a background
        bg = gui.widgets.Rectangle((0, 0), (w, h), (0,0,0,100), 1,
                                   (255,255,255,100), 4)
        bg.set_zindex(-1)
        self.container.add_child(bg)


        # add objects from the control in the container
        for o in control.objects:
            self.container.add_child(o)

        # center the container at bottom
        x = (display.width - 2*config.GUI_OVERSCAN_X - w) / 2
        y = display.height - config.GUI_OVERSCAN_Y - h

        self.container.set_pos((x,y))

        # update the display
        display.update()


    def hide(self):
        """
        Hides the currently selected control widget
        """
        # remove controlmanager as a window
        eventhandler.remove_window(self)

        # clear the objects and update the display
        self.container.hide()
        gui.display.update()
        self.container.clear()
        self.plugins[self.p_ctrl].clear()


    def eventhandler(self, event):
        """
        Catch events for the controlmanager and
        its associated controls.
        """

        # Focus logic
        if event == TOGGLE_CONTROL:

            if len(self.plugins) < 1:
                return True

            last = self.p_ctrl
            next = self.p_ctrl + 1

            # destroy the current control
            if self.plugins[last].visible:
                self.hide()

            if next >= len(self.plugins):
                # out of bounds
                self.p_ctrl = -1
                return True

            # show if it's different
            if last != next:
                self.p_ctrl = next
                self.show()

            return True

        # pass events to selected plugin
        plugin = self.plugins[self.p_ctrl]

        if plugin and plugin.visible:
            # okay, visible -- check event

            if event == INPUT_EXIT:
                # hide the plugin
                self.hide()
                self.p_ctrl = -1
                gui.display.update()
                return True

            # pass the event to the plugin
            elif plugin.eventhandler(event):
                gui.display.update()
                return True

        return False


    def get_eventmap(self):
        """
        Return event mapping for ControlManager.
        """
        return 'input'


class ButtonPanel(object):
    """
    This is an example ControlBar widget, it simply shows
    a buttonpanel on the screen.
    """
    def __init__(self, name, handlers=[], button_size=(32,32),
                 button_spacing=2, default_action=0,
                 hide_when_run=False):

        self.name          = name
        self.p_action      = default_action
        self.handlers      = handlers
        self.button_size   = button_size
        self.spacing       = button_spacing
        self.hide_when_run = hide_when_run

        self.objects       = []
        self.buttons       = []
        self.visible       = False



    def eventhandler(self, event):
        """
        Handle events on the buttonpanel
        """

        if event in [INPUT_LEFT, INPUT_RIGHT]:
            # move right or left on the panel
            desel = -1
            hlen = len(self.handlers) - 1

            if event == INPUT_LEFT and self.p_action > 0:
                # move left
                desel = self.p_action
                self.p_action -= 1

            elif event == INPUT_RIGHT and self.p_action < hlen:
                # move right
                desel = self.p_action
                self.p_action += 1

            if desel != -1:
                # change the selected button
                self.buttons[desel].deselect()
                self.buttons[self.p_action].select()

                # show what was selected
                OSD_MESSAGE.post(self.handlers[self.p_action][0])

            return True


        elif event == INPUT_ENTER:
            # run the associated handle
            self.buttons[self.p_action].handle()

            if self.hide_when_run:
                # hide the control if configured
                TOGGLE_CONTROL.post()

            return True

        return False


    def draw(self, pos):
        """
        Draws the buttonpanel
        return the size of the bar
        """
        if self.visible:
            return

        self.visible     = True

        w, h = self.button_size

        # total width of the buttons
        hl = len(self.handlers)
        t_w = (w * hl) + (self.spacing * (hl-1))

        # width of the description test
        font = gui.theme.font('small0')
        txt_w = font.stringsize(self.name)

        # final width of the bar
        w = max(t_w, txt_w)

        # calculate x, y for the buttons
        x = (w - t_w) / 2 + pos[0]
        y = pos[1]

        
        # add control description text (centered)
        t_x = (w - txt_w) / 2 + pos[0]

        descr = gui.widgets.Text(self.name, (t_x, y),
                                 (txt_w, font.height),
                                 font, dim=False)
        descr.set_zindex(1)
        self.objects.append(descr)

        # add spacings
        h += font.height + self.spacing
        y += font.height + self.spacing

        # create the controlbuttons
        for (descr, icon, action, arg) in self.handlers:
            i = ControlButton(icon, (action, arg), self.button_size, (x, y))
            x += self.spacing + self.button_size[0]
            self.objects.append(i)
            self.buttons.append(i)

        self.buttons[self.p_action].select()

        return (w, h)


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
        self.visible     = False



class ControlButton(gui.widgets.Image):
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

            gui.widgets.Image.__init__(self, self.icon, self.pos, self.size)

        def select(self):
            """
            Select the button
            """
            i = gui.widgets.Image(self.icon, self.sel_pos, self.sel_size)
            self.set_image(i)
            self.set_pos(self.sel_pos)


        def deselect(self):
            """
            Deselect the button
            """
            self.set_image(gui.widgets.Image(self.icon, self.pos, self.size))
            self.set_pos(self.pos)


        def handle(self):
            """
            Run the callback associated with the button
            """
            try:
                # FIXME: what about handlers without arg?
                #        Take a look at the rc.callback methods
                #        to do this properly
                self.handler[0](self.handler[1])
            except Exception, e:
                # XXX Maybe use a WaitBox here?
                print 'Handling failed on the controlbutton:'
                print e
