# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# window.py - Popup Windows known by Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007-2008 Dirk Meyer, et al.
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

__all__ = [ 'TextWindow', 'MessageWindow', 'ConfirmWindow']

# kaa imports
import kaa
from kaa.utils import property

# freevo imports
from freevo import view
from freevo.ui.event import *

# application imports
from handler import handler
from base import WidgetContext as BaseWidgetContext

class WidgetContext(BaseWidgetContext):
    """
    Context link between Window and view
    """
    def show(self):
        """
        Render and show the widget
        """
        if 0: # no support in the view yet
            self._app = view.show_window(self._name, self._ctx)
            self._app.show()

    def hide(self):
        """
        Hide the widget
        """
        if self._app:
            self._app.hide()
        self._app = None


class Window(object):
    """
    A basic empty window, not very usefull on its own.
    """
    type = None

    def __init__(self):
        self.__eventmap = 'input'
        self.__visible = False
        self.gui_context = WidgetContext(self.name)

    def show(self):
        """
        Show the window on the screen.
        """
        if self.__visible:
            return
        self.__visible = True
        handler.add_window(self)
        self.gui_context.show()

    def hide(self):
        """
        Hide the window.
        """
        if not self.__visible:
            return
        self.__visible = False
        handler.remove_window(self)
        self.gui_context.hide()

    def eventhandler(self, event):
        """
        Eventhandler for the window, this raw window has nothing to do
        """
        return False

    @property
    def eventmap(self):
        """
        Return the eventmap for the window
        """
        return self.__eventmap

    @eventmap.setter
    def eventmap(self):
        """
        Set the eventmap for the window
        """
        self.__eventmap = eventmap
        handler.set_focus()


class Button(kaa.Signal):
    """
    A button used in some windows.
    """
    def __init__(self, name, selected=True):
        self.name = name
        self.selected = selected
        kaa.Signal.__init__(self)


class TextWindow(Window):
    """
    A simple window without eventhandler showing a text.
    """
    type = 'text'

    def __init__(self, text):
        Window.__init__(self)
        # FIXME: update gui_context
        self.text = text


class MessageWindow(Window):
    """
    A simple window showing a text. The window will hide on input
    events. It is used as small information.
    """
    type = 'message'

    def __init__(self, text, button=_('OK')):
        Window.__init__(self)
        self.text = text
        self.button = Button(button)

    def eventhandler(self, event):
        """
        Eventhandler to close the box on INPUT_ENTER or INPUT_EXIT
        """
        if event in (INPUT_ENTER, INPUT_EXIT):
            self.hide()
            if event == INPUT_ENTER:
                # FIXME: update gui_context
                self.button.emit()
            return True
        return False


class ConfirmWindow(Window):
    """
    A simple window showing a text and two buttons for the user to choose
    from. In most cases this window is used to ask the user if an action
    should really be performed.
    """
    type = 'confirm'

    def __init__(self, text, buttons=(_('Yes'), _('No')), default_choice=0):
        Window.__init__(self)
        self.text = text
        self.buttons = []
        for text in buttons:
            self.buttons.append(Button(text, len(self.buttons) == default_choice))
        self.selected = self.buttons[default_choice]

    def eventhandler(self, event):
        """
        Eventhandler to toggle the selection or press the button
        """
        # FIXME: update gui_context
        if event in (INPUT_LEFT, INPUT_RIGHT):
            # Toggle selection
            self.selected.selected = False
            index = self.buttons.index(self.selected)
            if event == INPUT_LEFT:
                index = (index + 1) % len(self.buttons)
            elif index == 0:
                index = len(self.buttons) - 1
            else:
                index = index - 1
            self.selected = self.buttons[index]
            self.selected.selected = True
            self.engine.update()
            return True
        elif event == INPUT_ENTER:
            self.selected.emit()
            self.hide()
            return True
        return False
