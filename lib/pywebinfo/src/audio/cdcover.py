# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# cdcover.py - Fetches covers from amazon
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
from xml.dom import minidom
from cStringIO import StringIO


# webinfo modules
from pywebinfo.grabberitem import GrabberItem
from pywebinfo.grabber     import Grabber

# amazon module
import pywebinfo.lib.amazon as amazon


class CDCoverItem(GrabberItem):
    """
    Class representing the result
    """
    cover_large  = None
    cover_medium = None
    cover_small  = None
    release_date = None
    album        = None
    artist       = None
    tracks       = []



class CDCoverGrabber(Grabber):
    def __init__(self, amazon_license, cb_progress=None, cb_error=None,
                 cb_result=None, language='en-US'):

        Grabber.__init__(self, cb_progress, cb_error, cb_result, language)

        # configure the license
        self.license = amazon_license
        self.data = None
        self.url = None


    def handle_line(self, url, line):
        """
        Handle one line
        """
        # we need the whole data here
        self.data.write(line)
 

    def handle_finished(self, url):
        """
        Finished receiving results
        """
        self.data.seek(0)

        xmldoc = minidom.parse(self.data)


        data = amazon.unmarshal(xmldoc).ProductInfo

        # clean up
        xmldoc.unlink()
        self.data.close()

        if hasattr(data, 'ErrorMsg'):
            self.deliver_result(None)
        
        items = []

        for cover in data.Details:
            item = CDCoverItem()
            if hasattr(cover, 'ImageUrlLarge'):
                item.cover_large = cover.ImageUrlLarge
            if hasattr(cover, 'ImageUrlMedium'):
                item.cover_medium = cover.ImageUrlMedium
            if hasattr(cover, 'ImageUrlSmall'):
                item.cover_small = cover.ImageUrlSmall
            if hasattr(cover, 'ReleaseDate'):
                item.release_date = cover.ReleaseDate
            if hasattr(cover, 'ProductName'):
                item.album = cover.ProductName
            if hasattr(cover, 'Artists'):
                if isinstance(cover.Artists.Artist, list):
                    item.artist = u', '.join(cover.Artists.Artist)
                else:
                    item.artist = cover.Artists.Artist
                
            if hasattr(cover, 'Tracks'):
                item.tracks = cover.Tracks.Track

            item.to_unicode()
            items.append(item)

        self.deliver_result(items)


    def search(self, search):
        """
        Perform a keywordsearch on amazon
        """
        self.data = StringIO()
        self.url = amazon.buildURL('KeywordSearch', search,
                                   'music', 'heavy', 1,
                                   self.license)
        self.get_url(self.url)

        return self.return_result()

