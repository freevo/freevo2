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
# Revision 1.9  2003/12/09 20:32:29  dischi
# fix plugin to match the new player structure
#
# Revision 1.8  2003/09/20 09:42:32  dischi
# cleanup
#
# Revision 1.7  2003/09/19 22:10:11  dischi
# check self.player before using it
#
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


import config
import plugin
import menu
import rc
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


    def detach(self):
        gui  = audio.player.get()

        # hide the player and show the menu
        gui.hide()
        gui.menuw.show()

        # set all menuw's to None to prevent the next title to be
        # visible again
        gui.menuw = None
        gui.item.menuw = None
        if gui.item.parent:
            gui.item.parent.menuw = None
        

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


    def eventhandler(self, event, menuw=None):
        gui = audio.player.get()
        if gui and gui.player.is_playing() and event == AUDIO_PLAY_END:
            self.player.eventhandler(event=event)
            return True
        return False
