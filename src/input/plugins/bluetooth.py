# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# bluetooth.py - A simple bluetooth interface
# -----------------------------------------------------------------------------
# $Id$
#
# Just testing, needs doc
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2006 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Based on the bluetooth plugin for Freevo 1.5.x from Erik "ikea" Pettersson
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
import os
import fcntl
import re
import logging

# kaa imports
import kaa
import kaa.notifier

# freevo input plugin core
from input.interface import InputPlugin

# get logging object
log = logging.getLogger('bt')

class BlueTooth(object):
    """
    A class handling the bluetooth serial connection.
    """
    def __init__(self):
        self.fd = 0
        self.signals = { 'key': kaa.notifier.Signal() }

        # regexp for keys
        self.regexp = re.compile(r"\+CKEV:\s+(\w+,\w+)")


    def connect(self, device):
        """
        Connect to the device. This is handled in a thread because the
        connection will take some time and will block the system.
        """
        kaa.notifier.Thread(self._connect, device).start()


    def _connect(self, device):
        """
        Thread handling all the stuff needed to connect to a device.
        """
        log.info('connecting to %s', device)
        self.fd = os.open(device, os.O_RDWR | os.O_NONBLOCK)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, os.O_NONBLOCK)
        os.write(self.fd, "AT+CMER=3,2,0,0,0\r")
        kaa.notifier.SocketDispatcher(self._read).register(self.fd)
        log.info('connected')


    def _read(self):
        """
        Read data from the remote device.
        """
        data = os.read(self.fd, 1024)
        if self.regexp.search(data):
            key = self.regexp.search(data).groups()[0]
            if key.endswith(',0'):
                return
            self.signals['key'].emit(key.split(',')[0])
        return True


    def disconnect(self):
        """
        Disconnect the device.
        """
        if not self.fd:
            return
        os.write(self.fd, "AT+CMER=0,0,0,0\r")
        self.fd = 0


    def __del__(self):
        """
        Disconnect on __del__.
        """
        self.disconnect()



class PluginInterface(InputPlugin):
    """
    Input plugin for bluetooth
    """

    KEYMAP = {
        '1' : 'EXIT',
        '2' : 'UP',
        '3' : 'ENTER',
        '4' : 'LEFT',
        '5' : 'SELECT',
        '6' : 'RIGHT',
        '8' : 'DOWN' }

    def __init__(self, device):
        """
        Init the plugin by connecting to the device and register the
        callback.
        """
        InputPlugin.__init__(self)
        self.bt = BlueTooth()
        self.bt.signals['key'].connect(self.handle)
        self.bt.connect(device)


    def handle(self, code):
        """
        Handle a key from the remote device.
        """
        if code in self.KEYMAP:
            self.post_key(self.KEYMAP[code])
        return True


    def shutdown(self):
        """
        Shutdown plugin.
        """
        self.bt.disconnect()
