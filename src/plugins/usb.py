#if 0 /*
# -----------------------------------------------------------------------
# usb.py - the Freevo usb plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This plugin sends an event if an usb device is added
#        or removed
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/09/14 20:09:37  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.3  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
#
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
#endif

import plugin
import util
import rc

class PluginInterface(plugin.DaemonPlugin):
    """
    This Plugin to scan for usb devices. You should activate this
    plugin if you use mainmenu plugins for special usb devices
    like camera.py.
    """
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.devices = util.list_usb_devices()
        self.poll_interval = 10

    def poll(self, menuw=None, arg=None):
        """
        poll to check for devices
        """

        changes = FALSE

        current_devices = util.list_usb_devices()
        for d in current_devices:
            try:
                self.devices.remove(d)
            except ValueError:
                changes = TRUE
                print 'usb.py: new device %s' %d

        for d in self.devices:
            changes = TRUE
            print 'usb.py: removed device %s' % d

        if changes:
            rc.post_event(plugin.event('USB'))
            
        self.devices = current_devices
