# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# detach.py - Detach plugin for the audio player
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.18  2004/07/26 18:10:17  dischi
# move global event handling to eventhandler.py
#
# Revision 1.17  2004/07/10 12:33:37  dischi
# header cleanup
#
# Revision 1.16  2004/04/25 11:23:58  dischi
# Added support for animations. Most of the code is from Viggo Fredriksen
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


import config
import plugin
import menu
import eventhandler
import audio.player

from event import *

class PluginInterface(plugin.MainMenuPlugin):
    """
    plugin to detach the audio player to e.g. view pictures while listening
    to music
    """
    def __init__(self):
        plugin.MainMenuPlugin.__init__(self)
        config.EVENTS['audio']['DISPLAY'] = Event(FUNCTION_CALL, arg=self.detach)
        self.show_item = menu.MenuItem(_('Show player'), action=self.show)
        self.show_item.type = 'detached_player'


    def detach(self):
        gui  = audio.player.get()

        # hide the player and show the menu
        mpav = plugin.getbyname( 'audio.mpav' )
        if mpav:
            mpav.stop_mpav()

        mplvis = plugin.getbyname( 'audio.mplayervis' )
        if mplvis:
            mplvis.stop_visual()

        gui.hide()
        gui.menuw.show()

        # set all menuw's to None to prevent the next title to be
        # visible again
        gui.menuw = None
        gui.item.menuw = None
        if gui.item.parent:
            gui.item.parent.menuw = None
        eventhandler.post(plugin.event('DETACH'))
        

    def items(self, parent):
        gui = audio.player.get()
        if gui and gui.player.is_playing():
            self.show_item.parent = parent
            return [ self.show_item ]
        return []


    def show(self, arg=None, menuw=None):
        gui = audio.player.get()

        # restore the menuw's
        gui.menuw = menuw
        gui.item.menuw = menuw
        if gui.item.parent:
            gui.item.parent.menuw = menuw

        # hide the menu and show the player
        menuw.hide()
        gui.show()
        mpav = plugin.getbyname( 'audio.mpav' )
        if mpav:
            mpav.start_mpav()

        mplvis = plugin.getbyname( 'audio.mplayervis' )
        if mplvis:
            mplvis.stop_visual()
            mplvis.start_visual()
