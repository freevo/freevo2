# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# usb-storage.py - Special handling for usb storage devices
# -----------------------------------------------------------------------
# $Id$
#
# Notes: 
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2004/10/29 18:17:20  dischi
# moved usb util functions to this file
#
# Revision 1.3  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.2  2004/01/31 13:15:26  dischi
# fixed doc
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


import plugin
import util

from directory import DirItem

class PluginInterface(plugin.MainMenuPlugin):
    """
    Plugin for usb storage devices.
    Parameter: name and mountpoint..
    You should also activate the usb plugin so that the menu will change
    when you plugin in or remove the usb storage device.
    
    Example:
    plugin.activate('usb')
    plugin.activate('usbstorage', type='video', args=('USB Key', '/mnt/hd'))
    plugin.activate('usbstorage', type='audio', args=('USB Key', '/mnt/hd'))
    plugin.activate('usbstorage', type='image', args=('USB Key', '/mnt/hd'))
    """
    def __init__(self, name, mountpoint):
        plugin.MainMenuPlugin.__init__(self)
        self.name       = name
        self.mountpoint = mountpoint

    def is_usb_storage_device(self):
        fd = open('/proc/bus/usb/devices', 'r')
        for line in fd.readlines():
            if line.lower().find('storage') != -1:
                fd.close()
                return 0
        fd.close()
        return -1


    def items(self, parent):
        if self.is_usb_storage_device() != -1:
            d = DirItem(self.mountpoint, parent, self.name, display_type='image')
            d.mountpoint = self.mountpoint
            return [ d ]
        return []
        
