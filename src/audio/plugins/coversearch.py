#if 0 /*
# -----------------------------------------------------------------------
# coverserarch.py - Plugin for album cover support
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This plugin will allow you to find album covers. At first, only
#        Amazon is supported. Someone could easily add allmusic.com support
#        which is more complete, but lacks a general interface like amazon's
#        web services.
#
#        You also need an Amazon developer key.
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2003/06/24 01:51:13  rshortt
# Made the license key into an activate argument.  Now you can have:
# plugin.activate('audio.coversearch', args=('my_key',))
#
# Revision 1.7  2003/06/23 19:28:32  dischi
# cover support for audio cds (only with installed mmpython)
#
# Revision 1.6  2003/06/20 20:51:42  outlyer
# Trap ParserErrors if Amazon sends bad xml
#
# Revision 1.5  2003/06/12 23:41:11  outlyer
# Don't crash if no matches are found...
# notify user and return.
#
# Revision 1.4  2003/06/12 17:12:32  outlyer
# Fallback to medium cover if it's available, only if that too is missing, give
# up.
#
# Revision 1.3  2003/06/12 16:47:04  outlyer
# Tried to make the Amazon search more intelligent.
#
# Problem:
#     If a cover is not available, Amazon returns an 807b GIF file instead
#     of saying so
#
# Solution:
#     What we do now is check the content length of the file
#     before downloading and remove those entries from the list.
#
# I've also removed the example, since the plugin itself works better.
#
# Revision 1.2  2003/06/10 13:13:55  outlyer
# Initial revision is complete, current main problem is that it only
# writes 'cover.jpg' someone could add a submenu to choose between
# per-file or per-directory images, but I have to go to class now.
#
# I've tested this, but please let me know if you find problems.
#
# Revision 1.1  2003/06/07 18:43:26  outlyer
# The beginnings of a cover search plugin to complement Dischi's IMDB plugin
# for video. Currently, it uses the ID3 tag to find the album cover from
# amazon and prints the url on the screen.
#
# It doesn't do anything with it yet, because I still need to add a submenu
# to allow the user to choose:
#
# 1. Write a per-song cover (i.e. song_filename.jpg)
# 2. Write a per-album/directory cover (i.e. cover.jpg)
#
# If you want to see it in action, you can do a:
#
# plugin.activate('audio.coversearch')
#
# This only uses Amazon now, but could easily be extended to use allmusic.com
# if someone writes something to interface with it. Amazon was dead-simple
# to use, so I did it first, though Amazon is pretty weak, selection-wise
# compared to allmusic.com
#
# Revision 1.7  2003/06/07 11:32:48  dischi
# reactivated the plugin
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

import os

import menu
import plugin
import re
import urllib2
import time
import config

from gui.PopupBox import PopupBox


class PluginInterface(plugin.ItemPlugin):
    def __init__(self, license=None):
        plugin.ItemPlugin.__init__(self)

	# You must get your own key!
	if license:
	    self.license = license
        else:
	    self.license = 'empty'


    def actions(self, item):
        self.item = item
        if item.type == 'audio' or item.type == 'audiocd':
            return [ ( self.cover_search_file, 'Find a cover for this music',
                       'cover_search') ]
        return []


    def cover_search_file(self, arg=None, menuw=None):
        """
        search imdb for this item
        """
        import amazon

        box = PopupBox(text='searching Amazon...')
        box.show()
        
        if self.item.type == 'audiocd':
            album = self.item.info['title']
            artist = self.item.info['artist']
        else:
            album = self.item.album
            artist = self.item.artist

        amazon.setLicense(self.license) 
        try:
            cover = amazon.searchByKeyword('%s %s' % (artist,album) , product_line="music")
        except amazon.AmazonError:
            box.destroy() 
            box = PopupBox(text='No matches for %s - %s' % (str(artist),str(album)))
            box.show()
            time.sleep(2)
            box.destroy()
            return
        except amazon.ParseError:
            box.destroy()
            box = PopupBox(text='The cover provider returned bad information.')
            box.show()
            time.sleep(2)
            box.destroy()
            return

        items = []
        
        # Check if they're valid before presenting the list to the user
        # Grrr I wish Amazon wouldn't return an empty gif (807b)

        for i in range(len(cover)):
            print "Checking Large Cover"
            m = urllib2.urlopen(cover[i].ImageUrlLarge)
            if not (m.info()['Content-Length'] == '807'):
                items += [ menu.MenuItem('%s' % cover[i].ProductName,
                                     self.cover_create, cover[i].ImageUrlLarge) ]
                m.close()
            else:
                m.close()
                # see if a small one is available
                print "No Large Cover, Checking Small Cover..."
                n = urllib2.urlopen(cover[i].ImageUrlMedium)
                if not (n.info()['Content-Length'] == '807'):
                    items += [ menu.MenuItem('%s [small]' % cover[i].ProductName,
                                    self.cover_create, cover[i].ImageUrlMedium) ]
                n.close()
       
        if items: 
            moviemenu = menu.Menu('Cover Results', items)
            box.destroy()
            menuw.pushmenu(moviemenu)
            return
        else:
            box = PopupBox(text='No covers available from Amazon')
            box.show()
            time.sleep(2)
            box.destroy()
            return


    def cover_create(self, arg=None, menuw=None):
        """
        create cover file for the item
        """
        import amazon
        import directory
        
        box = PopupBox(text='getting data...')
        box.show()
        
        #filename = os.path.splitext(self.item.filename)[0]
        if self.item.type == 'audiocd':
            filename = '%s/mmpython/disc/%s.jpg' % (config.FREEVO_CACHEDIR,
                                                    self.item.info['id'])
        else:
            filename = '%s/cover.jpg' % (os.path.dirname(self.item.filename))

        fp = urllib2.urlopen(str(arg))
        m = open(filename,'wb')
        m.write(fp.read())
        m.close()
        fp.close()

        if self.item.type == 'audiocd':
            self.item.image = filename
            
        # check if we have to go one menu back (called directly) or
        # two (called from the item menu)
        back = 1
        if menuw.menustack[-2].selected != self.item:
            back = 2
            
        # update the directory
        if directory.dirwatcher_thread:
            directory.dirwatcher_thread.scan()

        # go back in menustack
        for i in range(back):
            menuw.delete_menu()
        
        box.destroy()
