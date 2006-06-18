# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mplayer_select_aspectratio.py - Choose mplayer aspect ratio
# -----------------------------------------------------------------------------
# $Id: mplayer.py 8142 2006-04-07 19:29:23Z dmeyer $
#
# Notes: Changes the aspect ratio of a movie
#
# This plugin allows to override the aspect ratio of a movie
#
# Activate: 
#
#   plugin.activate('mplayer_select_aspectratio')
#
#   The first element selects the default ratio of the movie
#   you can add the aspect ratios you find useful
#   MPLAYER_ASPECT_RATIOS =  ('Def', '16:9', '2.35:1', '4:3')
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Gorka Olaizola <gorka@escomposlinux.org>
# Maintainer:    Gorka Olaizola <gorka@escomposlinux.org>
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
# ----------------------------------------------------------------------- */

# python imports
import logging

# kaa imports
from kaa.notifier import Callback

from menu import Action, ActionItem

import config
import plugin

# get logging object
log = logging.getLogger()

class PluginInterface(plugin.ItemPlugin):
    """
    Changes the aspect ratio of a Movie

    plugin.activate('mplayer_aspectratio')

    """

    def __init__(self):
        plugin.ItemPlugin.__init__(self)

        self.plugin_name = 'mplayer_aspectratio.item'

        if hasattr(config, 'MPLAYER_ASPECT_RATIOS'):
            self.ratios = config.MPLAYER_ASPECT_RATIOS
        else:
            self.ratios = ('Def', '16:9', '2.35:1', '4:3')

        self.ratio = self.ratios[0]

        self.title_def = _('Aspect Ratio - %s')

        self.default_str = _('Default')


    def change_aspect(self, item):
        
        item['cnt'] = (item['cnt'] + 1) % len(self.ratios)
        self.ratio = self.ratios[ item['cnt'] ]

        if self.ratio == self.ratios[0]:
            item.mplayer_options = ''
        else:
            item.mplayer_options = ' -aspect ' + self.ratio
        log.debug('Aspect command string for mplayer:  %s' % item.mplayer_options)
        if self.ratio == self.ratios[0]:
            str = self.default_str
        else:
            str = self.ratio

        item['item_title'] = self.title_def % str

        menustack = item.get_menustack()

        newaction = ActionItem(item['item_title'], item, self.change_aspect)
        menuitem = menustack.get_selected()
        menuitem.replace( newaction )

        menustack.refresh()


    def actions(self, item):
        
        myactions = []
        desc = _("Changes the movie aspect ratio. It's useful for movies that have incorrect aspect ratio in the headers.")

        if item.type == 'video':

            setattr(item, 'cnt', 0)
            setattr(item, 'item_title', self.title_def % self.default_str)

            a = Action(item['item_title'], self.change_aspect, 'mplayer_aspect_change', desc)

            myactions.append(a)

        return myactions

    
