#if 0 /*
# -----------------------------------------------------------------------
# item.py - Template for an item
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.6  2003/02/12 06:33:21  krister
# Cosmetic changes.
#
# Revision 1.5  2002/12/11 16:04:32  dischi
# make an item callable (actions()[0][0])
#
# Revision 1.4  2002/11/27 20:22:19  dischi
# Fixed some playlist problems. Sometimes the playlist stopped playing
# after one item is finished. By playling a playlist again, it will start
# with the first item again.
#
# Revision 1.3  2002/11/26 20:57:04  dischi
# Moved video specific stuff to videoitem
#
# Revision 1.2  2002/11/24 15:15:31  dischi
# skin.xml support re-added
#
# Revision 1.1  2002/11/24 13:58:44  dischi
# code cleanup
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


from menu import MenuItem

import rc
import menu

rc         = rc.get_singleton()

TRUE  = 1
FALSE = 0


#
# Item class. Inherits from MenuItem and is a template for other info items
# like VideoItem, AudioItem and ImageItem
#
class Item(MenuItem):
    def __init__(self, parent = None):
        self.name = None                # name in menu
        self.image = None               # imagefile
        
        self.type   = None              # type: e.g. video, audio, dir, playlist
        self.icon     = None
        self.parent   = parent          # parent item to pass unmapped event
        self.xml_file = None            # skin informationes etc.

        # possible variables for an item.
        # some or only needed for video or image or audio
        # these variables are copied by the copy function

        self.handle_type = None         # handle item in skin as video, audio, image
                                        # e.g. a directory has all video info like
                                        # directories of a cdrom

        self.mplayer_options = ''

        self.url     = ''
        self.genre   = ''
        self.tagline = ''
        self.plot    = ''
        self.runtime = ''
        self.year    = ''
        self.rating  = ''

        self.rom_id    = []
        self.rom_label = []
        self.media = None

        # interactive stuff for video, parsed by mplayer
        self.elapsed = 0

        if parent:
            self.image = parent.image
            self.handle_type = parent.handle_type
            self.xml_file = parent.xml_file


    def copy(self, obj):
        if not self.image:
            self.image = obj.image
        if not self.name:
            self.name = obj.name
            
        self.xml_file = obj.xml_file
        self.handle_type = obj.handle_type
        self.mplayer_options = obj.mplayer_options

        self.url     = obj.url
        self.genre   = obj.genre
        self.tagline = obj.tagline
        self.plot    = obj.plot
        self.runtime = obj.runtime
        self.year    = obj.year
        self.rating  = obj.rating

        self.rom_id    = obj.rom_id
        self.rom_label = obj.rom_label
        self.media     = obj.media

        self.elapsed = obj.elapsed
        

    # returns a list of possible actions on this item. The first
    # one is autoselected by pressing SELECT
    def actions(self):
        return None

    def __call__(self, arg=None, menuw=None):
        if self.actions():
            return self.actions()[0][0](arg=arg, menuw=menuw)
        
    # eventhandler for this item
    def eventhandler(self, event, menuw=None):
        if event == rc.EJECT and self.media and menuw and \
           menuw.menustack[1] == menuw.menustack[-1]:
            self.media.move_tray(dir='toggle')
            return TRUE

        # give the event to the next eventhandler in the list
        if self.parent:
            return self.parent.eventhandler(event, menuw)

        else:
            if event == rc.PLAY_END:
                menuwidget = menu.get_singleton()
                menuwidget.refresh()
                return TRUE

        print 'no eventhandler for event %s menuw %s' % (event, menuw)
        return FALSE

        
