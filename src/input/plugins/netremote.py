# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# netremote.py - A network remote control plugin for Freevo.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/10/06 19:24:02  dischi
# switch from rc.py to pyNotifier
#
# Revision 1.2  2004/09/27 18:40:35  dischi
# reworked input handling again
#
# Revision 1.1  2004/09/25 04:40:03  rshortt
# A network remote control plugin for freevo:
# plugin.activate('input.netremote') - untested.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

import notifier

import socket

import config
import eventhandler


class PluginInterface(plugin.Plugin):

    def __init__(self):
        plugin.Plugin.__init__(self)
        self.plugin_name = 'NETREMOTE'

        self.port = config.NETREMOTE_PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(0)
        self.sock.bind(('', self.port))


    def config(self):
        return [
                ('NETREMOTE_PORT', 16310, 'Network port to listen on.'),
               ]


    def poll(self):
        """
        return next event
        """
        try:
            return self.sock.recv(100)
        except:
            # No data available
            return None


