# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# freedb.py - grabber for freedb information.
# -----------------------------------------------------------------------------
# $Id$
#
# This grabber collects CDDB data from freedb servers. It uses the freedb.org
# websearch to get discids for textual searches. This should be removed when
# freedb supports in another way.
#
# Notes:
#    Originally based on CDDB.py by Ben Gertzfield <che@debian.org>
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Viggo Fredriksen <viggo@katatonic.org>
# Maintainer:    Viggo Fredriksen <viggo@katatonic.org>
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


# python modules
import os
import re
import urllib
import socket

# webinfo modules
from pywebinfo.grabberitem import GrabberItem
from pywebinfo.grabber     import Grabber


class FreedbItem(GrabberItem):
    discid = None
    artist = None
    album = None
    year = None
    length = None
    tracks = []
    offsets = []
    revision = None

    def set(self, key, value):
        """
        Set items
        """
        if key == 'DTITLE':
            # artist and album match
            (self.artist, self.album) = value.split('/')

        elif key == 'DYEAR':
            # year
            self.year = value
        elif key == 'DGENRE':
            # genre
            self.genre = value
        elif key == 'DISCID':
            # discid
            self.discid = value
        elif key.startswith('TTITLE'):
            # track title
            self.tracks.append(String(value))


class FreedbGrabber(Grabber):
    """
    Grabber for freedb information

    Note: This is a little hackish, and should probably not be
    done. This grabber gets information from the freedb html
    web frontend. If a discid is known, it is therefore best
    to create a new Freedbitem with the given discid, and pass
    it directly to the select method. The select method does in
    turn use the real freedb protocol.
    """
    def __init__(self, server='http://freedb.freedb.org/~cddb/cddb.cgi',
                 cb_progress=None, cb_error=None, cb_result=None,
                 language='en-US'):

        Grabber.__init__(self, cb_progress, cb_error, cb_result, language)

        self.data    = None
        self.client  = 'Freevo'
        self.version = 2.0
        self.server  = server
        self.proto   = 6
        self.host    = socket.gethostname() or 'host'

        if os.environ.has_key('EMAIL'):
            (self.user, self.host) = os.environ['EMAIL'].split('@')
        else:
            try:
                self.user = os.geteuid() or os.environ['USER'] or 'user'
            except:
                self.user = 'user'

        # Regular expressions
        R_IT  = '^<tr><td><a href=".*/freedb_search_fmt\.php' \
              + '.*\&id\=([^&^"]+)">(.*?) / ([^<]+)</a>.*'

        self.m_item = re.compile(R_IT).match
        self.m_cat  = re.compile('^<h2>(.*)</h2>').match

        self.url  = None
        self.surl = None
        self.s_items = None
        self.item = None
        self.last_genre = None


        # regular expressions
        self.m_len = re.compile(r'#\s*Disc length:\s*(\d+)\s*seconds').match
        self.m_revis = re.compile(r'#\s*Revision:\s*(\d+)').match
        self.m_keyword = re.compile(r'([^=]+)=(.*)').match
        self.m_offset = re.compile(r'#[\t](\d+)').match


    def handle_line(self, url, line):
        """
        Handle one line of data
        """
        if url == self.url:
            # parsing web search

            m = self.m_cat(line)
            if m:
                # genre match
                self.last_genre = m.groups()[0]
                return

            m = self.m_item(line)
            if m:
                # item match
                item        = FreedbItem()
                item.discid = m.group(1)
                item.arist  = m.group(2)
                item.album  = m.group(3)
                item.genre  = self.last_genre
                self.s_items.append(item)
            return

        if url == self.surl:
            # parsing freedb

            m = self.m_keyword(line)
            if m:
                (keyword, data) = m.groups()
                self.item.set(keyword, data)
                return

            m = self.m_offset(line)
            if m:
                # track offset
                self.item.offsets.append(int(m.group(1)))
                return

            m = self.m_len(line)
            if m:
                # the total length of the album
                self.item.length = int(m.group(1))
                return

            m = self.m_revis(line)
            if m:
                # The revision of this entry
                self.item.revision = int(m.group(1))
                return



    def handle_finished(self, url):
        """
        Handle finished
        """
        if url == self.url:
            # deliver search results
            self.deliver_result(self.s_items)
            self.s_items = None

        elif url == self.surl:
            # deliver select item result
            self.deliver_result(self.item)
            self.item = None

	
    def search(self, search):
        """
        Keywordsearch

        Note: This will only do a simple textual search of the freedb webpage.
        Returned are simple items with artist/album and discid information.
        """
        search = urllib.quote_plus(search)
        self.url = 'http://www.freedb.org/freedb_search.php?words='\
                 + '%s&grouping=cats' % search

        self.s_items    = []
        self.last_genre = 'none'
        self.get_url(self.url)
        
        # return the result according to profile
        return self.return_result()


    def select(self, item):
        """
        Selects an item and returns a complete item
        if available. The item needs to atleast have
        an discid and a category.
        """

        self.surl = "%s?cmd=cddb+read+%s+%s&hello=%s+%s+%s+%s&proto=%i" % \
          (self.server, item.genre, item.discid, self.user, self.host,
           self.client, self.version, self.proto)

        self.item = FreedbItem()
        self.get_url(self.surl)
        
        # return the result according to profile
        return self.return_result()
