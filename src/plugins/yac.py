# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# yac.py - Support for YAC (Caller ID)
# -----------------------------------------------------------------------
# $Id: yac.py,v
#
# Notes:
#    To activate, put the following line in local_conf.py:
#       plugin.activate('yac')
#
# This plugin supports the "YAC" protocol as documented here:
#       http://www.sunflowerhead.com/software/yac/
#
# It allows you to use a "YAC Server" to send messages; the yac 
# server can run on Windows, and there is also a Linux version
# available: http://bah.org/tivo/ and clients for Windows and
# Linux. 
#
# -----------------------------------------------------------------------
# $Log: yac.py,v
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


import socket, time, sys
import plugin
from event import *
import eventhandler

class PluginInterface (plugin.DaemonPlugin):
    """
    Listen on the default YAC port (10629) for messages from a YAC server
    and then display them using OSD_MESSAGE. Anything can be sent, though
    it was originally designed to show Caller ID information on a TIVO.
    """
    def __init__ ( self):
        port = 10629
        host = ''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host,port))
        self.sock.listen(5)
        self.sock.setblocking(0)
        plugin.DaemonPlugin.__init__( self )
        plugin.register( self, "yac")

    def poll(self):
        try:
            conn,addr = self.sock.accept()
            data = conn.recv(300)               # 300 is max in specification
            if data:
                if data[:5] == '@CALL':
                    eventhandler.post(Event(OSD_MESSAGE, arg=_('Call: %s') % data[5:-1]))
                else:
                    eventhandler.post(Event(OSD_MESSAGE, arg=_('Message: %s') % data[:-1]))
            conn.close()
        except:
            pass

    def shutdown(self):
        self.sock = None 
