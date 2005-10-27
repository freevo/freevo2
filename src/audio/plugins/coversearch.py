# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# coverserarch.py - Plugin for album cover support
# -----------------------------------------------------------------------------
# $Id$
#
# This plugin will allow you to find album covers. At first, only Amazon is
# supported. Someone could easily add allmusic.com support which is more
# complete, but lacks a general interface like amazon's web services.
#
# You also need an Amazon developer key.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Aubin Paul <aubin@outlyer.org>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

# python imports
import os
import re
import urllib2
import time
import logging

# kaa imports
import kaa.imlib2
import kaa.notifier

# freevo imports
import sysconfig
import plugin
import config

from menu import ItemPlugin, Action, ActionItem, Menu
from gui.windows import WaitBox, MessageBox
from util import amazon

# get logging object
log = logging.getLogger('audio')

# shortcut for the actions
SHORTCUT = 'imdb_search_or_cover_search'

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

    You can also specify the amazon locale. Possible settings are us, uk,
    de and jp. This is a limitation from the Amazon web service. Default is
    us.
    """
    def __init__(self, license=None, locale='us'):
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

        self.locales = [ 'us', 'uk' ]
        if locale in self.locales:
            self.locales.remove(locale)
        self.locales = [ locale ] + self.locales
        plugin.ItemPlugin.__init__(self)


    def actions(self, item):
        """
        Return possible actions for the item.
        """
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
        c = os.path.dirname(item.filename)
        if item.type == 'audio' and item.filename and \
           vfs.isfile(os.path.join(c, 'cover.jpg')):
            return []
        
        if item.type in ('audio', 'audiocd', 'dir'):
            try:
                # use title for audicds and album for normal data
                if (item['artist'] and item['album'] and \
                    item.type in ('audio', 'dir') or \
                    (item['title'] and item.type == 'audiocd')):

                    return [ Action(_( 'Find a cover for this music' ),
                                    self.search, SHORTCUT) ]
                else:
                    log.info('no artist or album')
            except KeyError:
                log.warning('no artist or album')
            except AttributeError, e:
                log.exception('coversearch')
        return []


    def handle_exception(self, exception, item, box):
        """
        Exception while getting data.
        """
        box.destroy()
        if isinstance(exception, amazon.AmazonError):
            text = _('No matches for %s - %s') % \
                   (item['artist'], item['album'])
        else:
            text = _('Unknown error: %s' % exception)
        MessageBox(text).show()
        item.show_menu()


    def __get_data_thread(self, search):
        """
        Get the cover data in a thread.
        """
        for locale in self.locales:
            log.info('trying amazon locale %s' % locale)
            amazon.setLocale(locale)
            try:
                cover = amazon.searchByKeyword(search, product_line="music")
                # there are results, break from the loop
                break
            except AmazonError:
                # nothing found
                pass
        else:
            raise AmazonError('No results found')
        
        results = []
        
        # Check if they're valid before presenting the list to the user
        # Grrr I wish Amazon wouldn't return an empty gif (807b)
        for c in cover:
            for url in c.ImageUrlLarge, c.ImageUrlMedium, \
                    c.ImageUrlLarge.replace('.01.', '.03.'):
                try:
                    data = urllib2.urlopen(url)
                    if data.info()['Content-Length'] == '807':
                        continue
                    image = kaa.imlib2.open_from_memory(data.read())
                    image = image.crop((2,2), (image.width-4, image.height-4))
                    break
                except urllib2.HTTPError:
                    # Amazon returned a 404 or bad image
                    pass
                except:
                    # Bad image
                    log.exception('create image data')
                    
            else:
                # no image found
                log.info('No image for %s' % c.ProductName)
                continue

            name = Unicode(c.ProductName)
            if url == c.ImageUrlMedium:
                name += _('[small]')
            results.append((name, image))
            
        # end of thread
        return results


    def search(self, item):
        """
        Search for the cover.
        """
        box = WaitBox(text=_( 'searching Amazon...' ) )
        box.show()

        album = item['album']
        if not album:
            album = item['title']

        artist = item['artist']
        search_string = '%s %s' % (String(artist), String(album))
        search_string = re.sub('[\(\[].*[\)\]]', '', search_string)

        log.info('searching for \'%s\'' % search_string)
        thread = kaa.notifier.Thread(self.__get_data_thread, search_string)
        thread.signals['completed'].connect(self.cover_menu, item, box)
        thread.signals['exception'].connect(self.handle_exception, item, box)
        thread.start()


    def cover_menu(self, cover, item, box):
        """
        Show cover images. 
        """
        box.destroy()
        items = []
        for name, image in cover:
            a = ActionItem(name, item, self.save)
            a.image = image
            a.parameter(image)
            items.append(a)
        item.pushmenu(Menu( _( 'Cover Search Results' ), items))


    def save(self, item, image):
        """
        create cover file for the item
        """
        if item.type == 'audiocd':
            filename = '%s/disc/metadata/%s.jpg' % (vfs.BASE, item.info['id'])
        elif item.type == 'dir':
            filename = os.path.join(item.dir, 'cover.jpg')
        else:
            filename = '%s/cover.jpg' % (os.path.dirname(item.filename))

        log.info('save to cover to %s' % filename)
        image.save(filename)
        item.show_menu()
