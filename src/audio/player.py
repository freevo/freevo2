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
# Revision 1.11  2003/12/03 21:51:31  dischi
# register to the skin and rename some skin function calls
#
# Revision 1.10  2003/11/22 15:30:55  dischi
# support more than one player
#
# Revision 1.9  2003/11/08 13:19:06  dischi
# add AUDIOCD as plugin type
#
# Revision 1.8  2003/10/12 11:01:19  dischi
# Don't show black screen between selecting and playing an audio file
#
# Revision 1.7  2003/09/20 09:44:23  dischi
# cleanup
#
# Revision 1.6  2003/09/15 20:06:02  dischi
# error handling when mplayer does not start
#
# Revision 1.5  2003/08/27 15:27:08  mikeruelle
# Start of Radio Support
#
# Revision 1.4  2003/04/24 19:56:01  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.3  2003/04/22 11:56:45  dischi
# fixed bug that shows the player again after stopping it
#
# Revision 1.2  2003/04/21 18:40:32  dischi
# use plugin name structure to find the real player
#
# Revision 1.1  2003/04/21 13:27:48  dischi
# o make it possible to hide() the audio player
# o mplayer is now a plugin, controlled by the PlayerGUI
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

import config
import skin
import rc
import plugin
import event

skin = skin.get_singleton()

skin.register('player', ('screen', 'title', 'subtitle', 'view', 'info'))


class PlayerGUI(GUIObject):
    def __init__(self, item, menuw):
        GUIObject.__init__(self)
        if menuw:
            self.visible = True
        else:
            self.visible = False

        self.menuw = menuw
        self.item = item

        self.player  = None
        self.running = False

        
    def play(self, player=None):

        if self.player and self.player.is_playing():
            self.stop()
            
        if player:
            self.player = player
        else:
            self.possible_player = []
            for p in plugin.getbyname(plugin.AUDIO_PLAYER, True):
                rating = p.rate(self.item) * 10
                if config.AUDIO_PREFERED_PLAYER == p.name:
                    rating += 1
                self.possible_player.append((rating, p))
            self.possible_player.sort(lambda l, o: -cmp(l[0], o[0]))
            self.player = self.possible_player[0][1]
        
        if self.menuw and self.menuw.visible:
            self.menuw.hide(clear=False)

        self.running = True
        error = self.player.play(self.item, self)
        if error:
            print error
            self.running = False
            if self.visible:
                rc.app(None)
            self.item.eventhandler(event.PLAY_END)
            
        else:
            if self.visible:
                rc.app(self.player)
            self.refresh()

    def try_next_player(self):
        self.stop()
        _debug_('error, try next player')
        player = None
        next   = False
        for r, p in self.possible_player:
            if next:
                player = p
                break
            if p == self.player:
                next = True

        if player:
            self.play(player=player)
            return 1
        _debug_('no more players found')
        return 0
        
    def stop(self):
        self.player.stop()
        self.running = False
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

        if not self.running:
            return
        
        # Calculate some new values
        if not self.item.length:
            self.item.remain = 0
        else:
            self.item.remain = self.item.length - self.item.elapsed
        skin.draw(('player', self.item))
        return
