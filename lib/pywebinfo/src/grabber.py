# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# grabber.py - Template for grabbers
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
import logging
from cStringIO import StringIO
from types import StringTypes

# pywebinfo modules
from pywebinfo.httpreader import HTTPReader

log = logging.getLogger('pywebinfo')

# notifier to keep main loop alive
try:
    import notifier
    if notifier.loop == None:
        notifier.init()
except ImportError:
    notifier = None



class Grabber(object):
    """
    Basic grabber template
    """
    def __init__(self, cb_progress=None, cb_error=None, cb_result=None,
                 language='en-US'):
        """
        @param cb_progress: A callback for reporting approximate
                            progress status (0-100). Should be
                            used for keeping the main loop alive
                            if using notifier.
        @param cb_result:   A callback for receiving the result
                            from the query.
        @param cb_error:    A callback for receiving errors in the query.

        @param language:    Accept-Language.
        """
        self.cb_result      = cb_result
        self.cb_progress    = cb_progress
        self.cb_error       = cb_error
        self.language       = language
        self.delivered      = False
        self.d_progress     = {}
        self.bytes_total    = 0
        self.bytes_fetched  = 0
        self.bytes_progress = 0

        self.__result       = None


    def handle_header(self, url, header):
        """
        Handle the initial header
        """
        pass
    	

    def handle_line(self, url, line):
        """
        Handle one line of data
        """
        pass


    def handle_finished(self, url):
        """
        Marker sent when an url has finished
        processing by the httpreader
        """
        pass


    def handle_error(self, url, reason):
        """
        Callback for error handling. Classes overriding this should
        call cb_error if it exists. By default this sets results
        to None and delivers this to the waiting caller.
        """
        log.warning('Failed fetching %s:%s' % (url, reason))

        if self.cb_error:
            # deliver error to receiver
            self.cb_error(url, reason)

        # deliver an empty result
        self.deliver_result(None)

    def handle_progress(self, url, fetched=None, length=None):
        """
        Calculate overall progress status.
        TODO: The calculations could probably be done better.
        """
        if not self.cb_progress or self.delivered:
            # not interesting
            return

        if fetched:
            self.bytes_fetched += fetched

        if length and not self.d_progress.has_key(url):
            self.d_progress[url] = length
            self.bytes_total    += length

        if self.bytes_total == 0:
            perc = 0
        else:
            perc = float(self.bytes_fetched*100) / float(self.bytes_total)
            perc = min( int(perc), 100 )

        self.bytes_progress = perc

        # callback the percentage done.
        self.cb_progress(perc)


    def deliver_result(self, result):
        """
        Deliver result to the registered callback
        """
        self.delivered = True

        if self.cb_result:
            # deliver via callback
            self.cb_result(result)
        else:
            # deliver via loop
            self.__result = result


    def return_result(self):
        """
        Helper for methods which can return a result
        when the grabber is configured to not use callback
        for the result.
        """
        if self.cb_result:
            # This grabber uses callbacks to deliver
            # results.
            return
        
        while not self.delivered:
            # step until finished
            notifier.step(False, False)

        self.delivered = False

        # return the result
        return self.__result


    def get_image(self, url_or_urls):
        """
        Special function allowing fetching of images
        from the web and printing copyright info to
        the logger.
        """
        if isinstance(url_or_urls, StringTypes):
            url_or_urls = [url_or_urls]


        _ImageGrabber(self, url_or_urls, self.language)

        log.info('Downloading images from:')
        log.info('\n'.join(url_or_urls))
        log.info('Freevo knows nothing of the copyright')
        log.info('status of this/these image(s). Refer to')
        log.info('the above source(s) for more information')
        log.info('about private use.')

        return self.return_result()
    	


    def get_url(self, url_or_urls):
        """
        This makes it possible to retrieve several
        urls at once.
        """
        if isinstance(url_or_urls, StringTypes):
            url_or_urls = [url_or_urls]

        for url in url_or_urls:
            # create the readers for the urls
            HTTPReader(url, self, self.language)


class _ImageGrabber(object):
    """
    Generic image grabber, do not use directly. This is used
    by the Grabber.get_image() method.
    """
    def __init__(self, parent, urls, language):
        self.image_data = {}

        for url in urls:
            self.image_data[url] = StringIO()

        self.num_images = len(urls)
        self.num_finished = 0
        self.parent = parent

        for url in urls:
            # create the readers for the urls
            HTTPReader(url, self, language)


    def handle_header(self, url, header):
        """
        Handle header
        """
        pass
    	

    def handle_line(self, url, line):
        """
        Handle one line of data
        """
        self.image_data[url].write(line)


    def handle_finished(self, url):
        """
        Count finished items
        """
        self.num_finished += 1
        self.image_data[url].seek(0)

        if self.num_images == self.num_finished:
            self.parent.deliver_result(self.image_data)


    def handle_progress(self, url, fetched=None, length=None):
        """
        Handle progress
        """
        self.parent.handle_progress(url, fetched, length)
    	