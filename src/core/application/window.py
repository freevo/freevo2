# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# window.py - Popup Windows known by Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007-2009 Dirk Meyer, et al.
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

__all__ = [ 'TextWindow', 'MessageWindow', 'ConfirmWindow' ]

# kaa imports
import kaa
from kaa.utils import property

# freevo imports
from ... import gui
from .. import api as freevo

# application imports
from handler import handler
from base import WidgetContext as BaseWidgetContext

class TextWindow(object):
    """
    A basic empty window, not very usefull on its own.
    """
    class WidgetContext(BaseWidgetContext):
        """
        Context link between Window and view
        """
        def show(self):
            """
            Render and show the widget
            """
            self._app = gui.show_widget('popup', context=self._ctx)
            kaa.signals['step'].disconnect(self.sync)

        def hide(self):
            """
            Hide the widget
            """
            if self._app:
                self._app.unparent()
            self._app = None


    def __init__(self, text):
        self.__eventmap = 'input'
        self.__visible = False
        self.gui_context = TextWindow.WidgetContext('popup')
        self.gui_context.text = text

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
        Eventhandler for the window, this window has nothing to do
        """
        return False

    @property
    def eventmap(self):
        """
        Return the eventmap for the window
        """
        return self.__eventmap

    @eventmap.setter
    def eventmap(self, eventmap):
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
        super(Button, self).__init__()
        self.name = name
        self.selected = selected


class MessageWindow(TextWindow):
    """
    A simple window showing a text. The window will hide on input
    events. It is used as small information.
    """
    def __init__(self, text, button=_('OK')):
        super(MessageWindow, self).__init__(text)
        self.button = Button(button)
        self.gui_context.buttons = [ self.button ]

    def eventhandler(self, event):
        """
        Eventhandler to close the box on INPUT_ENTER or INPUT_EXIT
        """
        if event in (freevo.INPUT_ENTER, freevo.INPUT_EXIT):
            self.hide()
            if event == freevo.INPUT_ENTER:
                self.button.emit()
            return True
        return False


class ConfirmWindow(TextWindow):
    """
    A simple window showing a text and two buttons for the user to choose
    from. In most cases this window is used to ask the user if an action
    should really be performed.
    """
    def __init__(self, text, buttons=(_('Yes'), _('No')), default_choice=0):
        super(ConfirmWindow, self).__init__(text)
        self.buttons = []
        for text in buttons:
            self.buttons.append(Button(text, len(self.buttons) == default_choice))
        self.gui_context.buttons = self.buttons
        self.selected = self.buttons[default_choice]

    def eventhandler(self, event):
        """
        Eventhandler to toggle the selection or press the button
        """
        if event in (freevo.INPUT_LEFT, freevo.INPUT_RIGHT):
            # Toggle selection
            self.selected.selected = False
            index = self.buttons.index(self.selected)
            if event == freevo.INPUT_LEFT:
                index = (index + 1) % len(self.buttons)
            elif index == 0:
                index = len(self.buttons) - 1
            else:
                index = index - 1
            self.selected = self.buttons[index]
            self.selected.selected = True
            self.gui_context.sync()
            return True
        elif event == freevo.INPUT_ENTER:
            self.selected.emit()
            self.hide()
            return True
        return False
