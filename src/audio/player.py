#if 0 /*
# -----------------------------------------------------------------------
# player.py - the Freevo audio player GUI
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/04/21 13:27:48  dischi
# o make it possible to hide() the audio player
# o mplayer is now a plugin, controlled by the PlayerGUI
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

from gui.GUIObject import GUIObject

import skin
import config
import rc

skin = skin.get_singleton()

TRUE  = 1
FALSE = 0

class PlayerGUI(GUIObject):
    def __init__(self, item, menuw):
        GUIObject.__init__(self)
        if menuw:
            self.visible = TRUE
        else:
            self.visible = FALSE

        self.menuw = menuw
        self.item = item
        self.player = config.AUDIO_PLAYER
        
    def play(self):
        if self.player.is_playing():
            self.stop()
            
        if self.menuw and self.menuw.visible:
            self.menuw.hide()

        self.player.play(self.item, self)
        if self.visible:
            rc.app(self.player)
        self.refresh()

    def stop(self):
        self.player.stop()
        if self.visible:
            rc.app(None)
        
    def show(self):
        if not self.visible:
            self.visible = 1
            self.refresh()
            rc.app(self.player)
            
    def hide(self):
        if self.visible:
            self.visible = 0
            skin.clear()
            rc.app(None)
            
    def refresh(self):
        """
        Give information to the skin..
        """
        if not self.visible:
            return
        
        # Calculate some new values
        if not self.item.length:
            self.item.remain = 0
        else:
            self.item.remain = self.item.length - self.item.elapsed
        skin.draw(('player', self.item))
        return
