#if 0 /*
# -----------------------------------------------------------------------
# camera.py - Special handling for digi cams who are storage devices
# -----------------------------------------------------------------------
# $Id$
#
# Notes: 
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/04/26 15:23:04  dischi
# this file now covers camera support _without_ gphoto
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

from directory import DirItem

class PluginInterface(plugin.MainMenuPlugin):
    """
    Plugin for digi cams who are usb storage devices.
    Parameter: name, usb id and mountpoint. You can get the usb id with lsusb.
    You should also activate the usb plugin so that the menu will change
    when you plugin in or remove the camera.
    
    Example for a Fujifilm Finepix:
    plugin.activate('usb')
    plugin.activate('image.camera', args=('Finepix', '04cb:0100', '/mnt/camera'))
    """
    def __init__(self, name, usb_id, mountpoint):
        plugin.MainMenuPlugin.__init__(self)
        self.name       = name
        self.usb_id     = usb_id
        self.mountpoint = mountpoint

    def items(self, parent):
        if self.usb_id in util.list_usb_devices():
            d = DirItem(self.mountpoint, parent, self.name, display_type='image')
            d.mountpoint = self.mountpoint
            return [ d ]
        return []
        
