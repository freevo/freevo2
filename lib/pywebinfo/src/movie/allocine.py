# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# allocine.py - Grabber for allocine information
# -----------------------------------------------------------------------------
# $Id$
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
import re
import urllib

# webinfo modules
from pywebinfo.grabber     import Grabber

from imdb import ImdbItem, ImdbPerson


class AllocineGrabber(Grabber):
    SEARCH_URL = 'http://www.allocine.fr/recherche/?motcle=%s&rub=%s'
    ITEM_URL   = 'http://www.allocine.fr/film/fichefilm_gen_cfilm=%s.html'

    # search regular expressions
    m_idmovie = re.compile('^<h4><a href=".*?/film/fichefilm_gen_cfilm='\
                          +'([0-9]+)\.html"[^>]*>(.*?)</a>.*').match
    m_iddate = re.compile('^<h4 style="[^>]+>[^\(]*'\
                         +'\(([0-9]+)\)</h4>.*').match

    # item regular expressions
    m_director = re.compile('^<h4>Réalisé par <a[^>]+>([^<]+)</a></h4>').match
    m_genre = re.compile('^<h4>Genre : ([^<]+)</h4>').match
    m_runtime = re.compile('^<h4>Durée : ([0-9]+h ){0,1}([0-9]+)'\
                          +'min\.</h4>\&nbsp;').match
    m_plot = re.compile('^[ \t]+<td valign="top" style="padding:10 0 0 0"><d'\
                       +'iv align="justify"><h4>([^<]+)</h4></div></td>').match
    m_rating = re.compile('^[ \t]+<td valign="top" style=[^>]+><h4><a [^>]+>'\
                         +'Spectateurs</a> <img .*/etoile_([0-4]).gif.*').match
    m_cover = re.compile('^[ \t]+<td valign="top" style="padding:0 0 5 0" wi'\
                        +'dth="100%"><img src="([^"]+)".*').match
    m_cast = re.compile('^<h4>Avec (.*?)</h4><br />').match
    i_cast = re.compile('<a[^>]+>([^<]+)</a>[,]?[ ]?').finditer
    
    def __init__(self, cb_progress=None, cb_error=None,
                 cb_result=None, language='en-US'):

        Grabber.__init__(self, cb_progress, cb_error, cb_result, language)

        self.url  = None
        self.surl = None

        self.search_items = []
        self.item = None


    def handle_line(self, url, line):
        """
        Handle one line of data
        """
        if url == self.url:
            # handle search data
            m = self.m_idmovie(line)

            if m:
                # found match for id
                if self.item:
                    # no date
                    self.item.year = _('Unknown')
                    self.search_items.append(self.item)

                sub_tag              = re.compile('<[^>]+>')
                self.item            = ImdbItem()
                self.item.imdbid = m.group(1)
                self.item.title      = re.sub(sub_tag, '', m.group(2))
                self.item.to_unicode()
                return


            if not self.item:
                # no use searching for date
                # if there is no item
                return
            
            m = self.m_iddate(line)
            if m:
                # found match for year
                self.item.year = m.group(1)
                self.search_items.append(self.item)
                self.item = None
                return

        elif url == self.surl:
            # handle parsing of a selected page
            self.__parse_page(line)
            return


    def handle_finished(self, url):
        """
        Handle finished data
        """
        if url == self.surl:
            # select finished
            self.item.to_unicode()
            self.deliver_result(self.item)

            self.surl = None
            self.item = None

        elif url == self.url:
            # search finished
            self.deliver_result(self.search_items)

            self.item = None
            self.url  = None
            self.search_items = []


    def search(self, search, type=1):
        """
        Search for allocine movies
        """

        self.url = self.SEARCH_URL % (urllib.quote(search), type)
        self.get_url(self.url)

        return self.return_result()


    def select(self, allocineItem):
        """
        Get complete information about an item
        """

        self.surl = self.ITEM_URL % allocineItem.imdbid
        self.item = allocineItem
        self.get_url(self.surl)

        return self.return_result()


    def __parse_page(self, line):
        """
        Parses a complete page for allocine data,
        one line at the time.
        """
        if not self.item.cover:
            # match cover
            m = self.m_cover(line)
            if m:
                if not m.group(1).endswith('AffichetteAllocine.gif'):
                    # real cover
                    self.item.cover = m.group(1)
                return
        
        if not self.item.director:
            # match director
            m = self.m_director(line)
            if m:
                self.item.director = m.group(1)
                return

        if len(self.item.cast) == 0:
            # match cast
            m = self.m_cast(line)
            if m:
                castiter = self.i_cast(m.group(1))
                if castiter:
                    for cast in castiter:
                        p = ImdbPerson()
                        p.name = cast.group(1)
                        p.to_unicode()
                        self.item.cast.append(p)
                return

        
        if len(self.item.genres) == 0:
            # match genre
            m = self.m_genre(line)
            if m:
                self.item.genres.append(m.group(1))
                return

        if not self.item.runtime:
            # match runtime
            m = self.m_runtime(line)
            if m:
                runtime = 0
                if m.group(1):
                    # remove 'h '
                    runtime += int(m.group(1)[:-2])*60

                self.item.runtime = runtime + int(m.group(2))
                return
            
        if not self.item.rating:
            # match raring
            m = self.m_rating(line)
            if m:
                self.item.rating = m.group(1)
                return
            
        if not self.item.plot:
            # match plot
            m = self.m_plot(line)
            if m:
                self.item.plot = m.group(1)
