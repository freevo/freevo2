# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# freevo-rendezvous.py - rendezvous support
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/07/10 12:33:40  dischi
# header cleanup
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


import socket
from util import Rendezvous
import time
import plugin
from freevo.version import __version__
import config

class PluginInterface(plugin.DaemonPlugin):
    """
    Rendezvous Broadcaster Plugin
    See: http://www.porchdogsoft.com/products/howl/ (Win32 Plugin/Linux/FreeBSD)

    This plugin has been tested with 
       * Safari on Mac OS X Panther
       * IE6 + Howl on Windows XP

    To enable this plugin, add 
        plugin.activate('freevo-rendezvous')
    to your local_conf.py
    """

    r = RendezVous.Rendezvous()

    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        desc = {'version':__version__}
        myip = self.my_ipaddr('localhost')
        info = Rendezvous.ServiceInfo("_http._tcp.local.", "Freevo Web._http._tcp.local.", address=socket.inet_aton(myip), 
            port=config.WWW_PORT, weight=0, priority=0, properties=desc, server=socket.gethostname)
        r.registerService(info)

    def my_ipaddr(self,interface_hostname=None):
        # give the hostname of the interface you want the ipaddr of
        hostname = interface_hostname or socket.gethostname()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((hostname, 0))
        ipaddr, port = s.getsockname()
        s.close()
        return ipaddr  # returns 'nnn.nnn.nnn.nnn' (StringType)

    def shutdown(self):
        r.unregisterService(info)
        r.close()





