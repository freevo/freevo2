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
# Revision 1.20  2003/07/09 20:36:49  gsbarbieri
# anged Item.getattr() behaviour, now "len(attr)" returns an integer.
# There should be no problems here since it's only used in info_area
#
# Revision 1.19  2003/06/29 20:45:14  dischi
# mmpython support
#
# Revision 1.18  2003/06/22 20:48:45  dischi
# special len() support for new info_area
#
# Revision 1.17  2003/06/20 19:52:59  dischi
# Oops
#
# Revision 1.16  2003/06/20 19:38:31  dischi
# moved getattr to item.py
#
# Revision 1.15  2003/05/27 17:53:33  dischi
# Added new event handler module
#
# Revision 1.14  2003/04/24 19:55:46  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.13  2003/04/20 12:43:32  dischi
# make the rc events global in rc.py to avoid get_singleton. There is now
# a function app() to get/set the app. Also the events should be passed to
# the daemon plugins when there is no handler for them before. Please test
# it, especialy the mixer functions.
#
# Revision 1.12  2003/04/20 10:55:39  dischi
# mixer is now a plugin, too
#
# Revision 1.11  2003/04/19 21:28:39  dischi
# identifymedia.py is now a plugin and handles everything related to
# rom drives (init, autostarter, items in menus)
#
# Revision 1.10  2003/04/15 20:00:17  dischi
# make MenuItem inherit from Item
#
# Revision 1.9  2003/04/06 21:12:55  dischi
# o Switched to the new main skin
# o some cleanups (removed unneeded inports)
#
# Revision 1.8  2003/03/16 19:28:03  dischi
# Item has a function getattr to get the attribute as string
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

        self.elapsed = obj.elapsed
        self.info     = obj.info
        

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
                    return ''
                
            if r != None:
                #return str(len(r))
                return len(r)

        else:
            try:
                r = self.info[attr]
            except:
                try:
                    r = getattr(self,attr)
                except:
                    return ''
                
            if r != None and str(r):
                return str(r)

        return ''
