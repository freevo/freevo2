#if 0 /*
# -----------------------------------------------------------------------
# icecastchanger.py - Example item plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This is a plpugin to change the current icecast m3u
#
# Activate: 
#   plugin.activate('icecastchanger')
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2003/10/16 17:45:19  mikeruelle
# put our only i18n change
#
# Revision 1.2  2003/09/22 20:28:46  mikeruelle
# adding help document strings for the web interface
#
# Revision 1.1  2003/08/30 15:17:10  mikeruelle
# We can now change icecast playlists from inside freevo
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


import os
import plugin
import config
import rc
import event as em

class PluginInterface(plugin.ItemPlugin):
    """
    This plugin is automatically included by the icecast plugin. There
    should be no need to activate it yourself. It's purpose is to add
    the extra action to m3u files to use them as playlists for icecast. 
    """
    def __init__(self):
        plugin.ItemPlugin.__init__(self)

    def change2m3u(self, arg=None, menuw=None):
        myfile = file(os.path.join(config.FREEVO_CACHEDIR, 'changem3u.txt'), 'wb')
        myfile.write(self.item.filename)
        myfile.flush()
        myfile.close()
        rc.post_event(em.MENU_BACK_ONE_MENU)
        
    def actions(self, item):
        self.item = item
        if item.type == 'playlist':
            fsuffix = os.path.splitext(item.filename)[1].lower()[1:]
            if fsuffix == 'm3u':
                return [ (self.change2m3u,
                          _('Set as icecast playlist')) ]
        return []

