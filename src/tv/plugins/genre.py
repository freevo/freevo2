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

# kaa imports
import kaa.epg

# freevo imports
from freevo.ui.plugin import MainMenuPlugin
from freevo.ui.mainmenu import MainMenuItem
from freevo.ui.menu import Item, Action, ActionItem, Menu
from freevo.ui.tv.program import ProgramItem

# get logging object
log = logging.getLogger('tv')


class GenreItem(Item):
    """
    Item for the TV genre
    """
    def __init__(self, parent, name):
        Item.__init__(self, parent)
        self.name = name


    def actions(self):
        return [ Action(_('Browse list'), self.browse) ]


    def browse(self):
        """
        Find all the programs with this genre
        """
        items = []
        for prg in kaa.epg.search():
            if prg.genre == self.name:
                items.append(ProgramItem(prg, self))
        self.get_menustack().pushmenu(Menu(self.name, items, type='tv program menu'))


#
# the plugin is defined here
#

EXCLUDE_GENRES = ('unknown', 'none', '')

class PluginInterface(MainMenuPlugin):
    """
    Add 'Browse by Genre' to the TV menu.
    """

    def category(self, parent):
        """
        Show all category.
        """
        items = []
        genres = []
        # find the available category/genre
        # find a better way to do this via sqlDB ???... Because this is very intensive
        for prg in kaa.epg.search():
            genre = str(prg.genre).strip()
            if prg.genre not in genres and genre.lower() not in EXCLUDE_GENRES:
                genres.append(prg.genre)
                items.append(GenreItem(parent, prg.genre))
        parent.pushmenu(Menu(_('Genre'), items, type='tv listing'))


    def items(self, parent):
        """
        Return the main menu item.
        """
        return [ ActionItem(_('Browse by genre'), parent, self.category) ]
