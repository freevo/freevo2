# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# rss.py - Rss parser
# -----------------------------------------------------------------------------
# $Id$
#
# Notes:
#    Uses feedparser by Mark Pilgrim <http://diveintomark.org/>
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
from cStringIO import StringIO

# webinfo module
from pywebinfo.grabber     import Grabber
from pywebinfo.lib.feedparser import parse


class RssGrabber(Grabber):
    """
    This is just a thin layer above the feedparser to accommodate
    our needs for notifying the main loop. It does not return an
    item, only the raw dicts from feedparser. For more information
    on how to use it, ckeck lib/feedparser.
    """
    def __init__(self, cb_progress=None, cb_error=None,
                 cb_result=None, language='en-US'):

        Grabber.__init__(self, cb_progress, cb_error, cb_result, language)
        self.data = None


    def handle_line(self, url, line):
        """
        Handle one line of data
        """
        self.data.write(line)


    def handle_finished(self, url):
        # Use feedparser to parse the results.
        # PS: This seems to take a lot of time
        # (~1.3s on my 2800+), if anyone knows
        # a good implementation which takes as
        # many formats as feedparser, but is
        # quicker, please let me know.
        self.data.seek(0)
        feed = parse(self.data)
        self.data.close()
        self.deliver_result(feed)


    def search(self, rss_url):
        """
        Gets an RSS feed.
        """
        self.data = StringIO()
        self.get_url(rss_url)

        return self.return_result()
