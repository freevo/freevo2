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
# Revision 1.23  2003/08/23 12:51:41  dischi
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


import event as em

TRUE  = 1
FALSE = 0


#
# Item class. Inherits from MenuItem and is a template for other info items
# like VideoItem, AudioItem and ImageItem
#
class Item:
    def __init__(self, parent = None, info = None):
        self.image = None               # imagefile
        
        self.type   = None              # type: e.g. video, audio, dir, playlist
        self.icon     = None
        self.parent   = parent          # parent item to pass unmapped event
        self.xml_file = None            # skin informationes etc.
        self.menuw    = None
        self.eventhandler_plugins = []

        if not info:
            self.info = {}
        else:
            self.info = info

        # name in menu
        try:
            self.name = info['title']
            
        except (TypeError, AttributeError, KeyError):
            self.name = None                
            
        # possible variables for an item.
        # some or only needed for video or image or audio
        # these variables are copied by the copy function

        self.handle_type = None         # handle item in skin as video, audio, image
                                        # e.g. a directory has all video info like
                                        # directories of a cdrom

        self.mplayer_options = ''

        self.rom_id    = []
        self.rom_label = []
        self.media = None

        # interactive stuff for video, parsed by mplayer
        self.elapsed = 0

        if parent:
            self.image = parent.image
            self.handle_type = parent.handle_type
            self.xml_file = parent.xml_file
            self.media = parent.media


    def copy(self, obj):
        if not self.image:
            self.image = obj.image
        if not self.name:
            self.name = obj.name
            
        self.xml_file = obj.xml_file
        self.handle_type = obj.handle_type
        self.mplayer_options = obj.mplayer_options

        self.rom_id    = obj.rom_id
        self.rom_label = obj.rom_label
        self.media     = obj.media

        self.elapsed   = obj.elapsed
        self.info      = obj.info
        

    # returns a list of possible actions on this item. The first
    # one is autoselected by pressing SELECT
    def actions(self):
        return None

    def __call__(self, arg=None, menuw=None):
        if self.actions():
            return self.actions()[0][0](arg=arg, menuw=menuw)
        
    # eventhandler for this item
    def eventhandler(self, event, menuw=None):
        if not menuw:
            menuw = self.menuw

        for p in self.eventhandler_plugins:
            if p(event, self, menuw):
                return TRUE
            
        # give the event to the next eventhandler in the list
        if self.parent:
            return self.parent.eventhandler(event, menuw)

        else:
            if event == em.PLAY_END or event == em.USER_END and menuw:
                if menuw.visible:
                    menuw.refresh()
                else:
                    menuw.show()
                return TRUE

        return FALSE

        
    def getattr(self, attr):
        """
        return the specific attribute as string or an empty string
        """
        if attr == 'length':
            try:
                length = int(self.info['length'])
            except ValueError:
                return self.info['length']
            except:
                try:
                    length = int(self.length)
                except:
                    return ''
            if length / 3600:
                return '%d:%02d:%02d' % ( length / 3600, (length % 3600) / 60, length % 60)
            else:
                return '%d:%02d' % (length / 60, length % 60)

        if attr[:4] == 'len(' and attr[-1] == ')':
            try:
                r = self.info[attr[4:-1]]
            except:
                try:
                    r = getattr(self,attr[4:-1])
                except:
                    return 0
                
            if r != None:
                return len(r)

        else:
            r = None
            try:
                r = self.info[attr]
            except:
                pass
            if not r:
                try:
                    r = getattr(self,attr)
                except:
                    pass
                
            if r != None and str(r):
                return str(r)

        return ''
