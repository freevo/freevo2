#if 0 /*
# -----------------------------------------------------------------------
# sqlmusic_view.py - Plugin for displaying information stored in sqlite
# -----------------------------------------------------------------------
#
# Notes: Info plugin.
#        You can show music information from the sqlite database.
#        Activate with: plugin.activate('audio.sqlmusic_view')
#        You can also bind it to a key (in this case key 2):
#        EVENTS['menu']['2'] = Event(MENU_CALL_ITEM_ACTION, arg='sqlmusic_view')
#
# Currently, this serves little purpose unless you want to work on the sql
# music stuff, in which case it's a convenient way to make sure stuff is working.
#
# -----------------------------------------------------------------------
# $Log
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
import sqlite,util

from gui.AlertBox import AlertBox


class PluginInterface(plugin.ItemPlugin):        

    def actions(self, item):
        self.item = item
        if item.type == 'audio':
            return [ ( self.info_show, 'Show database information for this file',
                           'info_showdata') ]
        return []


            
    def info_show(self, arg=None, menuw=None):
        """
        show info for this item
        """

        file = self.item.filename
        db = sqlite.connect('%s/freevo.sqlite' % (config.FREEVO_CACHEDIR))
        cursor = db.cursor() 



        sql = 'SELECT md5, last_play,play_count,rating FROM music' + \
               ' WHERE path = \'%s\' and filename = \'%s\'' % (util.escape(os.path.dirname(file)), 
               util.escape(os.path.basename(file)))
         
        cursor.execute(sql)
        md5,last_play,play_count,rating = cursor.fetchone()

        if last_play != 0:
            last = str(time.strftime("%a, %d %b %Y %I:%M:%P", time.localtime(last_play)))
        else:
            last = 'Never'

        box = AlertBox(width=550, height=400, text='MD5: %s\nLast Play: %s\nPlay Count: %s\nRating: %s\n' 
            % (str(md5),last,str(play_count),str(rating)))
        box.show()
        db.close()
        return

