# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# lcd.py - use PyLCD to display menus and players
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
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
# ----------------------------------------------------------------------- */

import re

from kaa.strutils import unicode_to_str
import kaa.notifier

from freevo.ui import plugin, application
from freevo.ui.event import *

import logging
log = logging.getLogger()

import kaa.display

varreg = re.compile('%%.*?%%')

# This is the config for a display layout. Right now only 16x2 displays
# are supported (and higher). Do not send patches for other lcd resolutions,
# this code is only for testing. LCD should be part of the gui as second
# screen. I will do that once the gui is rewritten for kaa.candy.
layouts = { 2:
            { 16:
              {
                "menu":
                [ ( 'scroller', 1, 1, '%%self.width%%', 1, 'm', 3,
                    '%%menu.heading%%' ),
                  ( 'scroller', 1, 2, '%%self.width%%', 2, 'm', 3,
                    '%%menu.selected.name%%' )],

                "audioplayer"  :
                [ ( 'scroller', 1, 1, '%%self.width%%', 1, 'm', 3,
                    '%%item["artist"]%% - %%item["title"]%% - ' ),
                  ( 'string', 1, 2, '%%item["elapsed"]%%'),
                  ( 'string', 8, 2, '%%item["length"]%%')],

                "videoplayer":
                [ ( 'string', 1, 1, '%%item["title"]%%' ),
                  ( 'string', 1, 2, '%%item["elapsed"]%%'),
                  ( 'string', 9, 2, '%%item["length"]%%')
                ]
              }
            }
}

class PluginInterface( plugin.Plugin ):
    """
    Display context info in LCD using lcdproc daemon.
    """

    def __init__( self ):
        """
        init the lcd
        """
        plugin.Plugin.__init__( self )
        self.lcd = kaa.display.LCD()
        self.lcd.signals['connected'].connect_once(self._connected)
        self.running = False
        self.current = []
        self.timer = kaa.notifier.Timer(self.update)


    def _connected(self, width, height):
        self.running = True

        self.height = height
        self.width = width
        self.playitem = None

        self.screens = None
        l = self.height
        while not self.screens:
            try:
                layouts[ l ]
                c = self.width
                while True:
                    try:
                        self.screens = layouts[ l ][ c ]
                        break
                    except KeyError:
                        c -= 1
                        if c < 1:
                            raise KeyError
            except KeyError:
                l -= 1
                if l < 1:
                    return False
        self.lines = l
        self.columns = c
        plugin.register( self, "lcd" )

        kaa.notifier.EventHandler(self.eventhandler).register()
        application.signals['changed'].connect(self.set_application)
        self.set_application(application.get_active())


    def set_application(self, app):
        name = str(app)
        widgets = self.screens.get(name)
        if not widgets:
            log.error('no lcd screen for %s %s' % (name, self.screens.keys()))
            self.current = []
            return
        self.current = [ app, self.lcd.create_screen(name) ]
        for widget in widgets:
            w = self.current[1].widget_add(widget[0])
            self.current.append([w, widget[1:], []])
        self.update()


    def update(self):

        def replace(obj, l):
            try:
                r = eval(obj.group()[2:-2], l)
                if r == None:
                    return ''
                if isinstance(r, unicode):
                    return unicode_to_str(r)
                return str(r)
            except (SystemExit, KeyboardInterrupt):
                raise SystemExit
            except Exception, e:
                return ''

        if not self.current:
            return

        menu = None
        if hasattr(self.current[0], 'get_menu'):
            menu = self.current[0].get_menu()

        item = self.playitem

        cb = kaa.notifier.Callback(replace, locals())

        for w in self.current[2:]:
            args = []
            for a in w[1]:
                if isinstance(a, unicode):
                    a = unicode_to_str(a)
                if isinstance(a, str) and a.find('%%') >= 0:
                    a = varreg.subn(cb, a)[0]
                args.append(a)
            if w[2] != args:
                w[0].set(*args)
                w[2] = args


    def eventhandler(self, event):
        self.update()
        if event == PLAY_START:
            if self.running:
                self.timer.start(0.2)
            self.playitem = event.arg
        elif event == PLAY_END or event == STOP:
            self.playitem = None
            self.timer.stop()
        return True
