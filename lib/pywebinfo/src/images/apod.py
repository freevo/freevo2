# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# apod.py - Grabber for Astronomic picture of the day
# -----------------------------------------------------------------------------
# $Id$
#
# TODO: Maybe add description?
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

# webinfo modules
import logging
from pywebinfo.grabber     import Grabber
from pywebinfo.grabberitem import GrabberItem
log = logging.getLogger('pywebinfo')

class ApodItem(GrabberItem):
    name = None
    url  = None
	


class ApodGrabber(Grabber):
    def __init__(self, cb_progress=None, cb_error=None,
                 cb_result=None, language='en-US'):

        Grabber.__init__(self, cb_progress, cb_error, cb_result, language)

        # regular expression mathces
        self.m_img  = re.compile('^<a href="(image[^"]+)">').match
        self.m_name = re.compile('^<b>[ ]+([^<]+)</b> <br>').match

        # base url
        self.base = 'http://antwrp.gsfc.nasa.gov/apod/%s'
        self.item = None


    def handle_line(self, url, line):
        """
        Handle one line of data
        """
        if not self.item:
            return
        
        if not self.item.url:
            m = self.m_img(line)
            if m:
                # found the image url
                self.item.url = self.base % m.group(1)
            return

        if not self.item.name:
            m = self.m_name(line)
            if m:
                # found the name
                self.item.name = m.group(1).strip()
                self.deliver_result(self.item)
                self.item = None


    def search(self):
        """
        Gets the current picture url.
        """
        self.item = ApodItem()

        self.get_url(self.base % 'index.html')

        # return the result according to profile
        return self.return_result()
