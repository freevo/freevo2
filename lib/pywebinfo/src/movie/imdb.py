# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# imdb.py - grabber for imdb information
# -----------------------------------------------------------------------------
# $Id$
#
# This grabber collects movie information from imdb.
#
# Notes: The grabber does not parse with handle_line, but
#        keeps its own buffer until complete. This should
#        not be a problem, as the parsing is pretty fast.
#        (albeit it uses more memory)
#
# Todo: Support for other images than std. (/poster/ /dvd/)
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
from cStringIO import StringIO


# webinfo modules
from pywebinfo.grabberitem import GrabberItem
from pywebinfo.grabber     import Grabber


# some definitions
URL_SEARCH = 'http://%s.imdb.com/find?q=%s&restrict=Movies+and+TV'
URL_TITLE  = 'http://%s.imdb.com/title/tt%s/'


class ImdbItem(GrabberItem):
    """
    Class representing an imdb result
    """
    # imdb info
    imdbid   = -1
    rating   = None
    votes    = None
    cover    = None

    # movie info
    title    = None
    year     = None
    tagline  = None
    runtime  = None
    plot     = None
    mpaa     = None
    genres   = []

    # cast info
    director = None
    cast   = []

    # internal
    complete = False

class ImdbPerson(GrabberItem):
    """
    Class representing actors
    """
    name = None
    role = None


class ImdbGrabber(Grabber):
    """
    Grabber for imdb
    @site: either 'us' or 'uk'
    """
    # section searches
    s_sect = re.compile('<b>\w*?\s*Titles[^<]*</b>[^<]+<ol><li>.*?</ol>').search
    m_type = re.compile('<b>Titles \((\w+) Matches\)</b>').match

    def __init__(self, site='us', cb_progress=None, cb_error=None,
                 cb_result=None, language='en-US'):

        Grabber.__init__(self, cb_progress, cb_error, cb_result, language)

        if site not in ('us', 'uk'):
            # only these sites are valid
            site = 'us'
        
        self.site       = site
        self.url        = None
        self.data       = None
        self.state      = 'search'
        self.imdbid     = -1
        self.single_hit = False


    def handle_header(self, url, header):
        """
        Handle header data
        """
        if self.state == 'search' and header.has_key('location'):
            # redirected to single item hit
            self.url   = header['location']
            self.data  = StringIO()
            self.state = 'hit'
            m_id = re.compile('.*/title/tt(\d+)/.*').match(self.url)
            if m_id:
                # imdbid in ref
                self.imdbid = m_id.group(1)
            self.single_hit = True
            self.get_url(self.url)


    def handle_line(self, url, line):
        """
        Handle one line of data
        """
        if url == self.url:
            # write one line of data
            self.data.write(line)
    	

    def handle_finished(self, url):
        """
        Handle finished get
        """
        if url != self.url:
            # not interesting
            return
        
        if self.state == 'search':
            # parsing searchpage
            result = self.__parse_searchpage(self.data.getvalue())
            self.data.close()
            self.deliver_result(result)

        elif self.state == 'hit':
            # parsing imdb item page
            result = self.__parse_imdbitem(self.data.getvalue(), self.imdbid)
            self.data.close()
            if self.single_hit:
                # single hit
                self.single_hit = False
                result = [result]
            
            self.deliver_result(result)
        

    def search(self, search=''):
        """
        Perform a textual search on imdb.
        """
        self.url  = URL_SEARCH % (self.site, urllib.quote(search))
        self.data  = StringIO()
        self.state = 'search'
        self.search = search
        self.get_url(self.url)

        return self.return_result()


    def select(self, imdbItem):
        """
        Get the imdb info corresponding to imdbid
        """
        if imdbItem.complete:
            # the information on this item is already complete
            self.deliver_result(imdbItem)
            return self.return_result()
        
        self.url   = URL_TITLE % (self.site, imdbItem.imdbid)

        self.data  = StringIO()
        self.state = 'hit'
        self.imdbid = imdbItem.imdbid
        self.get_url(self.url)

        return self.return_result()
    	

    def __parse_searchpage(self, data):
        """
        Parse the searchpage.
        """
        # matches found
        popular = []
        partial = []
        exact   = []
        ids     = []
        
        # one item in a match section
        item   = '<li>[ ]+<a href="/title/tt(\d+)/.*?">([^<]+)</a> ' \
               + '\((\w+)\).*?</li>'
        r_item = re.compile(item)

        m = self.__get_next_section(data, 0)
        while m:
            # iterate through all
            # sections of interest
            (start, stop, type) = m
            
            section_items = r_item.finditer(data[start:stop])
            for section_item in section_items:
                # Iterate through all items 
                # in this section
                imdbid = section_item.group(1)

                if imdbid in ids:
                    # don't add duplicate imdbids
                    continue

                ids.append(imdbid)

                # create the result item
                item        = ImdbItem()
                item.imdbid = imdbid
                item.title  = urllib.unquote(section_item.group(2))
                item.year   = section_item.group(3)
                item.to_unicode()

                # add it to the correct match-set
                if type == 'Popular':
                    popular.append(item)
                elif type == 'Partial':
                    partial.append(item)
                elif type == 'Exact':
                    exact.append(item)

            # get the next section
            m = self.__get_next_section(data, stop)
      
        # FIXME: Find a better way to utilize the fact that we
        #   have divided popular/exact/partial matches.
        if (len(popular) + len(exact) + len(partial)) > 20:
            # The result set seem to large,
            # try to weed out some of them
            words     = []
            new_found = []            

            # Create a filtered list of searchwords
            for p in re.split('[\._ -]', self.search):
                if p and not p[0] in '0123456789':
                    words.append(p.lower())
            
            # iterate through the found imdbitems
            # don't add that doesn't contain our
            # updated search words
            for result in partial:
                for word in words:
                    title = result.title.lower()
                    if title.find(word) != -1:
                        # accept the result
                        new_found.append(result)
                        break

            # replace the result set
            partial = new_found

        popular.extend(exact)
        popular.extend(partial)

        return popular


    def __parse_imdbitem(self, data='', imdbid=-1):
        """
        Parse data from imdb
        
        Structure of the page
         1. title and year 2. cover 3. director 4. genre
         5. tagline 6. plot 7. rating 8. cast 9. mpaa
         10. rating
        """
        # the item
        item          = ImdbItem()
        item.imdbid   = imdbid
        item.complete = True

        # this is where the parsing should begin,
        # we also harvest the title and year from
        # this.
        r_begin = '<h1><strong class="title">([^<]+)<small>' \
                + '\(<a href="[^"]+">(\d+)</a>\)'
        s_begin = re.compile(r_begin).search(data)


        if not s_begin:
            # did not find anything
            return None

        # set title and year
        (start, stop) = s_begin.span()
        item.title    = urllib.unquote(s_begin.group(1))
        item.year     = s_begin.group(2)


        # find the cover url
        r_cover = '<img border="0" alt="cover" src="([^"]+)"'
        s_cover = re.compile(r_cover).search(data, stop)
        if s_cover:
            (start, stop) = s_cover.span()
            item.cover    = s_cover.group(1)

        # find the director
        r_dir = '<b class="blackcatheader">Directed by</b><br>\n' \
              + '<a href="/name/nm[^>]+>([^<]+)'
        s_dir = re.compile(r_dir, re.MULTILINE).search(data, stop)
        if s_dir:
            (start, stop) = s_dir.span()
            item.director = s_dir.group(1)
        
        # find the genres
        r_genres = '<a href="/Sections/Genres/[^>]+>([^<]+)'
        i_genres = re.compile(r_genres).finditer(data, stop)

        for genre in i_genres:
            # iterate through the results
            (start, stop) = genre.span()
            item.genres.append(genre.group(1))
        
        # find the tagline
        r_tag = '<b class="ch">Tagline:</b> ([^<]+)'
        s_tag = re.compile(r_tag).search(data, stop)

        if s_tag:
            (start, stop) = s_tag.span()
            item.tagline  = urllib.unquote(s_tag.group(1))

        # find the plot
        r_plot = '<b class="ch">Plot [\w]{7}:</b>([^<]+)'
        s_plot = re.compile(r_plot).search(data, stop)

        if s_plot:
            (start, stop) = s_plot.span()
            item.plot     = urllib.unquote(s_plot.group(1))

        # find the rating
        r_rate = '<b>([0-9\.]*)/10</b> \(([0-9,]+) votes\)'
        s_rate = re.compile(r_rate).search(data, stop)

        if s_rate:
            (start, stop) = s_rate.span()
            item.rating   = float(s_rate.group(1))
            item.votes    = int(s_rate.group(2).replace(',',''))

        # find the cast
        r_cast = '<a href="/name/nm[^"]+">([^<]+)</a></td>'\
               + '<td[^>]+>[ \.]+</td><td[^>]+>([^<]+)'
        i_cast = re.compile(r_cast).finditer(data, stop)

        if i_cast:
            for actor in i_cast:
                # append all the found casts
                person        = ImdbPerson()
                person.name   = actor.group(1)
                person.role   = actor.group(2)
                (start, stop) = actor.span()

                # append the actor
                person.to_unicode()
                item.cast.append(person)

        # find MPAA status
        r_mpaa = '<b class="ch"><a href="/mpaa">MPAA</a>:</b> ([^<]+)<br>'
        s_mpaa = re.compile(r_mpaa).search(data, stop)

        if s_mpaa:
            (start, stop) = s_mpaa.span()
            item.mpaa     = urllib.unquote(s_mpaa.group(1))
        
        # find the runtime
        # backup, the other may not be good enough
        #   r_run = '^<b class="ch">Runtime:</b>\n(\d+) min'
        r_run = '^(\d+) min $'
        s_run = re.compile(r_run, re.MULTILINE).search(data, stop)

        if s_run:
            (start, stop) = s_run.span()
            item.runtime  = int(s_run.group(1))

        item.to_unicode()

        return item


    def __get_next_section(self, stack, start):
        """
        Get the next section in the multiple title page
        """
        # Interesting sections:
        # <b>Popular Titles</b>
        # <b>Titles (Exact Matches)</b>
        # <b>Titles (Partial Matches)</b>

        # search for the next section
        search_section = self.s_sect(stack, start)

        if not search_section:
            # no match
            return False

        # the bounds of this section
        (start, stop) =  search_section.span()

        # match the section type
        match_type = self.m_type(stack[start:stop])

        if match_type:
            # partial or exact matches
            type = match_type.group(1)
        else:
            # popular matches
            type = 'Popular'

        return (start, stop, type)

