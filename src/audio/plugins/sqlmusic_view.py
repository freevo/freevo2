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

import os

import menu
import config
import plugin
import re
import time
import sqlite

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
               ' WHERE path = \'%s\' and filename = \'%s\'' % (os.path.dirname(file), 
               os.path.basename(file))
        cursor.execute(sql)
        md5,last_play,play_count,rating = cursor.fetchone()
       
        box = AlertBox(width=550, height=400, text='MD5: %s\nLast Play: %s\nPlay Count: %s\nRating: %s\n' 
            % (str(md5),str(last_play),str(play_count),str(rating)))
        box.show()
        db.close()
        return

