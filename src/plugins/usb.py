# -*- coding: iso-8859-1 -*-
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
# Revision 1.22  2005/08/07 13:00:22  dischi
# remove all menuw in eventhandler and remove fallback for old code in menu
#
# Revision 1.21  2005/08/07 10:17:56  dischi
# poll has no parameters
#
# Revision 1.20  2005/08/06 14:50:32  dischi
# adjust to kaa.notifier.Timer.start now using seconds
#
# Revision 1.19  2005/07/16 15:00:41  dischi
# more eventhandler cleanups
#
# Revision 1.18  2005/07/16 11:40:28  dischi
# remove poll_menu_only
#
# Revision 1.17  2005/07/16 10:07:25  dischi
# move eventhandler.py into applications subdir
#
# Revision 1.16  2005/07/16 09:48:24  dischi
# adjust to new event interface
#
# Revision 1.15  2005/06/04 17:18:13  dischi
# adjust to gui changes
#
# Revision 1.14  2004/11/20 18:23:03  dischi
# use python logger module for debug
#
# Revision 1.13  2004/11/01 20:15:41  dischi
# fix debug
#
# Revision 1.12  2004/10/29 18:17:20  dischi
# moved usb util functions to this file
#
# Revision 1.11  2004/10/08 20:19:55  dischi
# fix poll intervall
#
# Revision 1.10  2004/10/03 15:55:25  dischi
# adjust to new popup code
#
# Revision 1.9  2004/07/26 18:10:18  dischi
# move global event handling to eventhandler.py
#
# Revision 1.8  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.7  2004/05/31 10:42:50  dischi
# change poll intervall
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


import os

import config
import plugin
import util
from gui.windows import WaitBox
import application

import logging
log = logging.getLogger()

class PluginInterface(plugin.DaemonPlugin):
    """
    This Plugin to scan for usb devices. You should activate this
    plugin if you use mainmenu plugins for special usb devices
    like camera.py.

    You can also set USB_HOTPLUG in your local_config.py to call
    an external program when a device is added. USB_HOTPLUG is a
    list with actions. Each action is also a list of device, message
    and program to call. Limitation: this works only when Freevo shows
    the menu and is not running a video.
    
    Example:
    call pilot-xfer when a pda with the id 082d:0100 is pluged in:
    USB_HOTPLUG = [ ('082d:0100', 'Synchronizing',
                     '/usr/bin/pilot-xfer -t -u /local/visor/current') ]
    """
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.devices = self.list_usb_devices()
        self.poll_interval = 1


    def config(self):
        return [( 'USB_HOTPLUG', [], 'action list when a devices comes up' )]

    
    def list_usb_devices(self):
        devices = []
        fd = open('/proc/bus/usb/devices', 'r')
        for line in fd.readlines():
            if line[:2] == 'P:':
                devices.append('%s:%s' % (line[11:15], line[23:27]))
        fd.close()
        return devices

    def poll(self):
        """
        poll to check for devices
        """
        app = application.get_active()
        if not app or app.get_name() != 'menu':
            return False

        changes = False

        current_devices = self.list_usb_devices()
        for d in current_devices:
            try:
                self.devices.remove(d)
            except ValueError:
                log.error('new device %s' %d)
                for device, message, action in config.USB_HOTPLUG:
                    if d == device:
                        pop = WaitBox(message)
                        pop.show()
                        os.system(action)
                        pop.destroy()
                        break
                else:
                    changes = True
                        
        for d in self.devices:
            changes = True
            log.warning('removed device %s' % d)

        if changes:
            plugin.event('USB').post()
            
        self.devices = current_devices
