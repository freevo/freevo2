# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# dfbevents.py - An input plugin to get events from DirectFB.
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rob@tvcentric.com>
# Maintainer:    Rob Shortt <rob@tvcentric.com>
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
import logging
import traceback

# pynotifier
import kaa.notifier

# pydirectfb
import directfb

# Freevo imports
import config
import gui.displays
from event import *
from input.interface import InputPlugin

log = logging.getLogger('input')


class PluginInterface(InputPlugin):

    def __init__(self):
        InputPlugin.__init__(self)

        self.plugin_name = 'DirectFB Input'

        if config.GUI_DISPLAY.lower() == 'dfb':
            self.dfb = gui.displays.get().dfb
        else:
            self.dfb = directfb.DirectFB()
     
        try:
            self.event_buffer = \
                 self.dfb.createInputEventBuffer(directfb.DICAPS_ALL, 1)
            self.fd = self.event_buffer.createFileDescriptor()
        except:
            log.error('Unable to open file descriptor for DirectFB events, ' \
                      'exiting.')
            traceback.print_exc()
            raise RuntimeError

        log.info('Using DirectFB input.')

        self.keymap = {}
        for key in config.KEYBOARD_MAP:
            if hasattr(directfb, 'DIKS_%s' % key):
                code = getattr(directfb, 'DIKS_%s' % key)
                self.keymap[code] = config.KEYBOARD_MAP[key]
        for key in config.REMOTE_MAP:
            if hasattr(directfb, 'DIKS_%s' % key):
                code = getattr(directfb, 'DIKS_%s' % key)
                self.keymap[code] = config.REMOTE_MAP[key]

        log.debug(self.keymap)
        log.debug(self.fd)

        kaa.notifier.SocketDispatcher(self.handle).register(self.fd)


    def handle(self):
        log.info('handling DFBEvent')
        dfbevent = self.event_buffer.getEventFromFD()

        if not dfbevent or dfbevent.type != directfb.DIET_KEYPRESS: 
            return True

        print 'DFBEvent: %s' % dfbevent
        print 'DFBEvent: %s' % dir(dfbevent)
        print 'DFBEvent: button=%s' % dfbevent.button
        print 'DFBEvent: buttons=%s' % dfbevent.buttons
        #print 'DFBEvent: device_id=%s' % dfbevent.device_id
        #print 'DFBEvent: flags=%s' % dfbevent.flags
        #print 'DFBEvent: key_code=%s' % dfbevent.key_code
        print 'DFBEvent: key_id=%s' % dfbevent.key_id
        #print 'DFBEvent: key_symbol=%s' % dfbevent.key_symbol
        #print 'DFBEvent: locks=%s' % dfbevent.locks
        #print 'DFBEvent: modifiers=%s' % dfbevent.modifiers
        #print 'DFBEvent: type=%s' % dfbevent.type
                
        key = self.keymap.get(dfbevent.key_symbol)
        if not key :
            log.warning('unmapped key_symbol=%s' % dfbevent.key_symbol)
            return True

        log.debug('posting key: %s' % key)
        self.post_key(key)

        return True
