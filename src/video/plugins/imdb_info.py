#if 0 /*
# -----------------------------------------------------------------------
# info.py - Plugin for displaying movieinfo
# -----------------------------------------------------------------------
# $Id$
#
# Notes: Info plugin.
#        You can show IMDB informations for video items with this plugin.
#        Activate with: plugin.activate('video.imdb_info')
#        You can also bind it to a key (in this case key 2):
#        EVENTS['menu']['2'] = Event(MENU_CALL_ITEM_ACTION, arg='info_show')
#
# Todo:  - Scaling and nice graphics
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.12  2003/11/24 19:21:04  dischi
# do not depend on xml_parser, the item has all infos in it
#
# Revision 1.11  2003/11/16 17:41:05  dischi
# i18n patch from David Sagnol
#
# Revision 1.10  2003/09/23 21:15:14  dischi
# show info not only for files
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

import menu
import config
import plugin
import re
import time

from gui.AlertBox import AlertBox

class PluginInterface(plugin.ItemPlugin):        

    def actions(self, item):
        self.item = item
        if item.type == 'video' and item.info:
            return [ ( self.info_showdata, _('Show info for this file'),
                       'info_show') ]
        return []


            
    def info_showdata(self, arg=None, menuw=None):
        """
        show info for this item
        """
        if not self.item.xml_file:
            box = AlertBox(text=_('There is no IMDB information for this file.'))
            box.show()
            return

        info = self.item

        box = AlertBox(icon=info.image, width=550, height=400, text=_('%s\n \n \n  %s\n \n \n----\n Year: %s\n Genre: %s\n Rating: %s\n Runtime: %s') % (info.name,info.info['plot'],info.info['year'],info.info['genre'],info.info['rating'],info.info['length']))
        box.show()

