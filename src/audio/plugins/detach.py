#if 0 /*
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
# Revision 1.2  2003/04/24 19:56:04  dischi
# comment cleanup for 1.3.2-pre4
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
import config
import rc

import menu

TRUE  = 1
FALSE = 0

class PluginInterface(plugin.MainMenuPlugin):
    """
    plugin to detach the audio player to e.g. view pictures while listening
    to music
    """
    def __init__(self):
        plugin.MainMenuPlugin.__init__(self)
        config.RC_MPLAYER_AUDIO_CMDS['DISPLAY'] = ( self.detach, 'detach player' )
        self.player = None
        self.show_item = menu.MenuItem('Show player', action=self.show)
        
    def detach(self, player):
        gui   = player.playerGUI

        # hide the player and show the menu
        gui.hide()
        gui.menuw.show()

        # set all menuw's to None to prevent the next title to be
        # visible again
        gui.menuw = None
        gui.item.menuw = None
        if gui.item.parent:
            gui.item.parent.menuw = None
        self.player = gui.player
        

    def items(self, parent):
        if self.player and self.player.is_playing():
            self.show_item.parent = parent
            return [ self.show_item ]
        return ()


    def show(self, arg=None, menuw=None):
        gui = self.player.playerGUI

        # restore the menuw's
        gui.menuw = menuw
        gui.item.menuw = menuw
        if gui.item.parent:
            gui.item.parent.menuw = menuw

        # hide the menu and show the player
        menuw.hide()
        gui.show()


    def eventhandler(self, event, menuw=None):
        if event == 'AUDIO_PLAY_END':
            self.player.eventhandler(event=event)
            return TRUE
        return FALSE
