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
# Revision 1.6  2003/09/13 10:08:22  dischi
# i18n support
#
# Revision 1.5  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
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
import event as em

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
        config.EVENTS['audio']['DISPLAY'] = em.Event(em.FUNCTION_CALL, arg=self.detach)
        self.player = None
        self.show_item = menu.MenuItem(_('Show player'), action=self.show)
        
    def detach(self):
        gui   = plugin.getbyname(plugin.AUDIO_PLAYER).playerGUI

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
        if event == em.AUDIO_PLAY_END:
            self.player.eventhandler(event=event)
            return TRUE
        return FALSE
