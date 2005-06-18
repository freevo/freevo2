# -*- coding: iso-8859-1 -*-
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
# Revision 1.41  2005/06/18 12:07:02  dischi
# use new menu memeber function
#
# Revision 1.40  2005/06/04 17:18:11  dischi
# adjust to gui changes
#
# Revision 1.39  2005/05/01 17:36:41  dischi
# remove some vfs calls were they are not needed
#
# Revision 1.38  2005/01/02 11:49:05  dischi
# use fthread to be non blocking
#
# Revision 1.37  2004/11/20 18:23:00  dischi
# use python logger module for debug
#
# Revision 1.36  2004/10/02 11:44:09  dischi
# reactivate plugin
#
# Revision 1.35  2004/08/01 10:41:03  dischi
# deactivate plugin
#
# Revision 1.34  2004/07/22 21:21:47  dischi
# small fixes to fit the new gui code
#
# Revision 1.33  2004/07/10 12:33:37  dischi
# header cleanup
#
# Revision 1.32  2004/07/09 11:09:56  dischi
# use vfs.open to make sure we can write the image
#
# Revision 1.31  2004/05/15 18:01:13  outlyer
# Trap a potential crash if the "guessed" filename doesn't exist.
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


import os

import menu
import plugin
import re
import urllib2
import time
import config
import Image
import cStringIO
from xml.dom import minidom # ParseError used by amazon module

from gui.windows import WaitBox

from util import amazon
import util.fthread as fthread

import logging
log = logging.getLogger('audio')


class PluginInterface(plugin.ItemPlugin):
    """
    This plugin will allow you to search for CD Covers for your albums. To do
    that just go in an audio item and press 'e' (on your keyboard) or 'ENTER'
    on your remote control. That will present you a list of options with Find a
    cover for this music as one item, just select it press 'enter' (on your
    keyboard) or 'SELECT' on your remote control and then it will search the
    cover in amazon.com.

    Please Notice that this plugin use the Amazon.com web services and you will
    need an Amazon developer key. You can get your at:
    http://www.amazon.com/webservices, get that key and put it in a file named
    ~/.amazonkey or passe it as an argument to this plugin.

    To activate this plugin, put the following in your local_conf.py.

    If you have the key in ~/.amazonkey
    plugin.activate( 'audio.coversearch' ) 

    Or this one if you want to pass the key to the plugin directly:
    plugin.activate( 'audio.coversearch', args=('YOUR_KEY',) ) 
    """
    def __init__(self, license=None):
        if not config.USE_NETWORK:
            self.reason = 'no network'
            return
        
        if license:
            amazon.setLicense(license)
        try:
            amazon.getLicense()
        except amazon.NoLicenseKey:
            print String(_( 'To search for covers you need an Amazon.com Web' \
                            'Services\nlicense key. You can get it from:\n'))
            print 'https://associates.amazon.com/exec/panama/associates/join/'\
                  'developer/application.html'
            self.reason = 'no amazon key'
            return
            
        plugin.ItemPlugin.__init__(self)


    def actions(self, item):
        self.item = item
        # don't allow this for items on an audio cd, only on the disc itself
        if item.type == 'audio' and item.parent.type == 'audiocd':
            return []

        # don't allow this for items in a playlist
        if item.type == 'audio' and item.parent.type == 'playlist':
            return []

        # do don't call this when we have an image
        if item.type == 'audiocd' and item.image:
            return []

        # do don't call this when we have an image
        if item.type == 'audio' and item.filename and \
           vfs.isfile(os.path.join(os.path.dirname(item.filename), 'cover.jpg')):
            return []
        
        if item.type in ('audio', 'audiocd', 'dir'):
            try:
                # use title for audicds and album for normal data
                if self.item.getattr('artist') and \
                   ((self.item.getattr('album') and \
                     item.type in ('audio', 'dir')) or \
                    (self.item.getattr('title') and item.type == 'audiocd')):
                    return [ ( self.cover_search_file,
                               _( 'Find a cover for this music' ),
                               'imdb_search_or_cover_search') ]
                else:
                    log.info('no artist or album')
            except KeyError:
                log.warning('no artist or album')
            except AttributeError:
                log.warning('unknown disc')
        return []


    def cover_search_file(self, arg=None, menuw=None):
        """
        search imdb for this item
        """
        box = WaitBox(text=_( 'searching Amazon...' ) )
        box.show()

        album = self.item.getattr('album')
        if not album:
            album = self.item.getattr('title')

        artist = self.item.getattr('artist')
        search_string = '%s %s' % (String(artist), String(album))
        search_string = re.sub('[\(\[].*[\)\]]', '', search_string)
        try:
            cover = fthread.call(amazon.searchByKeyword, search_string,
                                 product_line="music")
        except amazon.AmazonError:
            box.destroy()
            dict_tmp = { "artist": String(artist), "album": String(album) }
            box = WaitBox(text=_('No matches for %(artist)s - %(album)s') \
                           % dict_tmp )
            box.show()
            time.sleep(2)
            box.destroy()
            return

        except:
            box.destroy()
            box = WaitBox(text=_( 'Unknown error while searching.' ) )
            box.show()
            time.sleep(2)
            box.destroy()
            return

        items = []
        
        # Check if they're valid before presenting the list to the user
        # Grrr I wish Amazon wouldn't return an empty gif (807b)

        MissingFile = False
        m = None
        n = None

        for i in range(len(cover)):
            try:
                m = fthread.call(urllib2.urlopen, cover[i].ImageUrlLarge)
            except urllib2.HTTPError:
                # Amazon returned a 404
                MissingFile = True
            if not MissingFile and not (m.info()['Content-Length'] == '807'):
                image = Image.open(cStringIO.StringIO(m.read()))
                items += [ menu.MenuItem('%s' % cover[i].ProductName,
                                         self.cover_create,
                                         cover[i].ImageUrlLarge,
                                         image=image) ]
                m.close()
            else:
                if m: m.close()
                MissingFile = False
                # see if a small one is available
                try:
                    n = fthread.call(urllib2.urlopen, cover[i].ImageUrlMedium)
                except urllib2.HTTPError:
                    MissingFile = True
                if not MissingFile and \
                       not (n.info()['Content-Length'] == '807'):
                    image = Image.open(cStringIO.StringIO(n.read()))
                    items.append(menu.MenuItem(('%s [' + _( 'small' ) + ']')%\
                                               cover[i].ProductName,
                                               self.cover_create,
                                               cover[i].ImageUrlMedium))
                    n.close()
                else:
                    if n: n.close()
                    # maybe the url is wrong, try to change '.01.' to '.03.'
                    large = cover[i].ImageUrlLarge.replace('.01.', '.03.')
                    cover[i].ImageUrlLarge = large
                    try:
                        n = fthread.call(urllib2.urlopen, cover[i].ImageUrlLarge)

                        if not (n.info()['Content-Length'] == '807'):
                            image = Image.open(cStringIO.StringIO(n.read()))
                            name = ('%s [' + _( 'small' ) + ']' ) % \
                                   cover[i].ProductName
                            items.append(menu.MenuItem(name, self.cover_create,
                                                       cover[i].ImageUrlLarge))
                        n.close()
                    except urllib2.HTTPError:
                        pass

        box.destroy()
        if len(items) == 1:
            self.cover_create(arg=items[0].arg, menuw=menuw)
            return
        if items: 
            moviemenu = menu.Menu( _( 'Cover Search Results' ), items)
            menuw.pushmenu(moviemenu)
            return

        box = WaitBox(text= _( 'No covers available from Amazon' ) )
        box.show()
        time.sleep(2)
        box.destroy()
        return


    def cover_create(self, arg=None, menuw=None):
        """
        create cover file for the item
        """
        import directory
        
        box = WaitBox(text= _( 'getting data...' ) )
        box.show()
        
        #filename = os.path.splitext(self.item.filename)[0]
        if self.item.type == 'audiocd':
            filename = '%s/disc/metadata/%s.jpg' % (config.OVERLAY_DIR,
                                                    self.item.info['id'])
        elif self.item.type == 'dir':
            filename = os.path.join(self.item.dir, 'cover.jpg')
        else:
            filename = '%s/cover.jpg' % (os.path.dirname(self.item.filename))

        fp = fthread.call(urllib2.urlopen, str(arg))
        m = vfs.open(filename,'wb')
        m.write(fp.read())
        m.close()
        fp.close()

        # try to crop the image to avoid ugly borders
        try:
            import Image
            image = Image.open(filename)
            width, height = image.size
            image.crop((2,2,width-4, height-4)).save(filename)
        except:
            pass

        if self.item.type in ('audiocd', 'dir'):
            self.item.image = filename
        elif self.item.parent.type == 'dir':
            # set the new cover to all items
            self.item.parent.image = filename
            for i in self.item.parent.menu.choices:
                i.image = filename

        # check if we have to go one menu back (called directly) or
        # two (called from the item menu)
        back = 1
        if menuw.menustack[-2].selected != self.item:
            back = 2

        # maybe we called the function directly because there was only one
        # cover and we called it with an event
        if menuw.menustack[-1].selected == self.item:
            back = 0
            
        # update the directory
        if directory.dirwatcher:
            directory.dirwatcher.scan()

        # go back in menustack
        for i in range(back):
            menuw.back_one_menu(False)

        box.destroy()
        menuw.refresh()
