# -----------------------------------------------------------------------
# info.py - Plugin for displaying movieinfo
# -----------------------------------------------------------------------
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

import os

import menu
import config
import plugin
import re
import time

from video import xml_parser
from gui.AlertBox import AlertBox


class PluginInterface(plugin.ItemPlugin):        

    def actions(self, item):
        self.item = item
        if item.type == 'video' and item.info:
            if item.mode == 'file':
                return [ ( self.info_showdata, 'Show info for this file',
                           'info_show') ]
        return []


            
    def info_showdata(self, arg=None, menuw=None):
        """
        show info for this item
        """

        file = self.item.xml_file
        
        if not file:
            box = AlertBox(text='There is no IMDB information for this file.')
            box.show()
            return

        infolist = xml_parser.save_parseMovieFile(file, os.path.dirname(file),[])
        for info in infolist:
            box = AlertBox(icon=info.image, width=550, height=400, text='%s\n \n \n  %s\n \n \n----\n Year: %s\n Genre: %s\n Rating: %s\n Runtime: %s' % (info.name,info.info['plot'],info.info['year'],info.info['genre'],info.info['rating'],info.info['length']))
            box.show()
        return

