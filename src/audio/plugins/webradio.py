#if 0 /*
# -----------------------------------------------------------------------
# webradio.py - webradio plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:       Proof-of-concept
#
# Todo:        We need our own mediamarks file with _working_ entries
#              and maybe more meta informations
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
#
# Revision 1.1  2003/08/17 17:17:34  dischi
# Webradio plugin. Right now it uses the mediamarks from WIP/Dischi, but
# most of them are broken (with mplayer and xine). We need our own
# collection.
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
from item import Item
from audio.audioitem import AudioItem
import config
import event as em
from xml.utils import qp_xml
import os

import menu

TRUE  = 1
FALSE = 0

class EntryList(Item):
    def __init__(self, mediamarks, parent):
        Item.__init__(self, parent)
        self.name = mediamarks.attrs[('', 'NAME')]
        self.mediamarks = mediamarks.children
        
    def actions(self):
        return [ ( self.cwd, 'Browse entries' ) ]

    def cwd(self, arg=None, menuw=None):
        items = []
        for entry in self.mediamarks:
            title = ''
            url   = ''
            for info in entry.children:
                if info.name == u'TITLE':
                    title = info.textof()
                if info.name == u'REF':
                    url = info.attrs[('', 'HREF')]
            if title and url:
                items.append(AudioItem(url, self, title, scan=FALSE))
                
        menuw.pushmenu(menu.Menu(self.name, items))

class GenreList(Item):
    def __init__(self, mediamarks, parent):
        Item.__init__(self, parent)
        self.name = 'Webradio'
        self.type = 'webradio'
        self.mediamarks = mediamarks
        
    def actions(self):
        return [ ( self.cwd, 'Browse genre list' ) ]

    def cwd(self, arg=None, menuw=None):
        items = []
        for child in self.mediamarks.children:
            try:
                items.append(EntryList(child, self))
            except KeyError:
                pass
        menuw.pushmenu(menu.Menu('Webradio Genre List', items))


class PluginInterface(plugin.MainMenuPlugin):
    """
    plugin to detach the audio player to e.g. view pictures while listening
    to music
    """
    def __init__(self, mediamarks='./WIP/Dischi/gxine-mediamarks'):
        plugin.MainMenuPlugin.__init__(self)
        if os.path.isfile(mediamarks):
            parser = qp_xml.Parser()
            f = open(mediamarks)
            self.mediamarks = parser.parse(f.read())
            f.close()
        else:
            print '%s: file not found, webradio plugin deactivated' % mediamarks
            self.mediamarks = None

            
    def items(self, parent):
        if self.mediamarks:
            return [ GenreList(self.mediamarks, parent) ]
        return ()
