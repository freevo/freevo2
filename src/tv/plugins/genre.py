# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# genre.py - Browse EPG by Genre
# -----------------------------------------------------------------------------
# $Id$
#
# This plugin lists all the available genres found in the TV guide. Selecting
# a genre will show a program list of that genre.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
#
# First Edition: Jose Taza <jose4freevo@chello.nl>
# Maintainer:    Jose Taza <jose4freevo@chello.nl>
#
# Please see the file AUTHORS for a complete list of authors.
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
# -----------------------------------------------------------------------------

# python imports
import logging
import time
import sys

# kaa imports
import kaa.notifier
import kaa.epg

# freevo imports
from freevo.ui.mainmenu import MainMenuPlugin
from freevo.ui.menu import Item, Action, ActionItem, Menu
from freevo.ui.tv.program import ProgramItem
from freevo.ui.application import MessageWindow

# get logging object
log = logging.getLogger('tv')

EXCLUDE_GENRES = ('unknown', 'none', '', None)
ALL_GENRE = _('All Genre')
ALL_CAT = _('All Categories')

class GenreItem(Item):
    """
    Item for the TV genre
    """
    def __init__(self, parent, name, category=None):
        Item.__init__(self, parent)
        self.name = name
        self.cat = category


    def actions(self):
        return [ Action(_('Browse list'), self.browse) ]


    @kaa.notifier.yield_execution()
    def browse(self):
        """
        Find all the programs with this genre
        """
        if not kaa.epg.is_connected():
            MessageWindow(_('TVServer not running')).show()
            return
        items = []
        # time tuple representing the future
        future = (int(time.time()), sys.maxint)
        # query epg in background
        if self.cat:
            if self.name==ALL_GENRE:
                query_data = kaa.epg.search(category=self.cat, time=future)
            else:
                query_data = kaa.epg.search(genre=self.name, 
                                            category=self.cat,
                                            time=future)
        else:
            query_data = kaa.epg.search(genre=self.name, time=future)
        yield query_data
        # fetch epg data from InProgress object
        query_data = query_data()
        for prg in query_data:
            items.append(ProgramItem(prg, self))
        # create menu for programs
        menu = Menu(self.name, items, type='tv program menu')
        self.get_menustack().pushmenu(menu)


class CategoryItem(Item):
    """
    Item for a TV category
    """
    def __init__(self, parent, name):
        Item.__init__(self, parent)
        self.name = name
        self.parent = parent


    def actions(self):
        return [ Action(_('Browse list'), self.browse)]
        
   
    @kaa.notifier.yield_execution()
    def browse(self):
        """ 
        Find all genres that are in this category
        """
        if not kaa.epg.is_connected():
            MessageWindow(_('TVServer not running')).show()
            return
        items = []
         
        if self.name==ALL_CAT:
            # query epg in background for all genres
            query_data = kaa.epg.search(attrs=['genre'], distinct=True)
        else: 
            # query epg in background for a specific category
            query_data = kaa.epg.search(attrs=['genre'], category=self.name, 
                                        distinct=True)
        
        yield query_data
        # fetch epg data from InProgress object
        query_data = query_data()
        query_data.sort()
        if not self.name == ALL_CAT:
            items.append(GenreItem(self.parent, ALL_GENRE, self.name))
        for genre, in query_data:
            if genre not in EXCLUDE_GENRES:
                if self.name==ALL_CAT:
                    items.append(GenreItem(self.parent, genre))
                else:    
                    items.append(GenreItem(self.parent, genre, self.name)) 
        # create menu
        menu = Menu(self.name, items, type='tv listing')
        self.get_menustack().pushmenu(menu)
    


#
# the plugin is defined here
#

class PluginInterface(MainMenuPlugin):
    """
    Add 'Browse by Genre' to the TV menu.
    """

    @kaa.notifier.yield_execution()
    def category(self, parent):
        """
        Show all category.
        """
        if not kaa.epg.is_connected():
            MessageWindow(_('TVServer not running')).show()
            return
        items = []
               
        # look if there is category data in the epg data
        query_data = kaa.epg.search(attrs=['category'], distinct=True)
        yield query_data
        # fetch epg data from InProgress object
        query_data = query_data()
        query_data.sort()
        if len(query_data) > 1:
            items.append(CategoryItem(parent, ALL_CAT))
            # there is category data in the epg
            for cat, in query_data:
                if cat not in EXCLUDE_GENRES:
                    items.append(CategoryItem(parent, cat))
        else:
            # maybe there is only genre data in the epg
            query_data = kaa.epg.search(attrs=['genre'], distinct=True)
            yield query_data
            # fetch epg data from InProgress object
            query_data = query_data()
            query_data.sort()
            for genre, in query_data:
                if genre not in EXCLUDE_GENRES:
                    items.append(GenreItem(parent, genre))
        
        # create menu
        parent.get_menustack().pushmenu(Menu(_('Genre'), items, type='tv listing'))


    def items(self, parent):
        """
        Return the main menu item.
        """
        return [ ActionItem(_('Browse by Genre'), parent, self.category) ]
