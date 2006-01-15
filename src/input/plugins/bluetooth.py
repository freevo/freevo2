# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# bluetooth.py - A simple bluetooth interface
# -----------------------------------------------------------------------------
# $Id$
#
# First draft of a bluetooth plugin, the keymap handling needs to be much
# better, right now we use numbers to navigate, so when Freevo needs numbers
# we can't provide them.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2006 Krister Lagerstrom, Dirk Meyer, et al.
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

# kaa imports
from kaa.input.bluetooth import Bluetooth

# freevo imports
from event import OSD_MESSAGE

# freevo input plugin core
from input.interface import InputPlugin

class PluginInterface(InputPlugin):
    """
    Input plugin for bluetooth. Parameters are device and a name with device
    a list of hardware address and channel for the serial service.
    """

    KEYMAP = {
        '1' : 'EXIT',
        '2' : 'UP',
        '3' : 'ENTER',
        '4' : 'LEFT',
        '5' : 'SELECT',
        '6' : 'RIGHT',
        '8' : 'DOWN' }

    def __init__(self, device, name):
        """
        Init the plugin by connecting to the device and register the
        callback.
        """
        InputPlugin.__init__(self)
        self.btname = name
        self.bt = Bluetooth(device)
        self.bt.signals['key'].connect(self.handle)
        self.bt.signals['connected'].connect(self.connected)
        self.bt.signals['disconnected'].connect(self.disconnected)


    def handle(self, code):
        """
        Handle a key from the remote device.
        """
        if code in self.KEYMAP:
            self.post_key(self.KEYMAP[code])
        return True


    def connected(self):
        """
        Handle new connection.
        """
        OSD_MESSAGE.post('Found %s' % self.btname)
        

    def disconnected(self):
        """
        Handle new disconnection.
        """
        OSD_MESSAGE.post('Lost %s' % self.btname)
        

    def shutdown(self):
        """
        Shutdown plugin.
        """
        del self.bt
