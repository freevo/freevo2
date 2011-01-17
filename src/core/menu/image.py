# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# image.py - Images for Items
# -----------------------------------------------------------------------------
# $Id: $
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2011 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
import hashlib

# kaa imports
import kaa
import kaa.net

# freevo imports
from .. import api as freevo

class Image(object):

    _downloads = {}

    PRIORITY_HIGH = PRIORITY_NORMAL = PRIORITY_HIGH = None

    def __init__(self, image):
        self.image = None
        self.failed = False
        self.needs_update = False
        self.cachefile = None
        if image.startswith('http://'):
            self.base = hashlib.md5(image).hexdigest() + os.path.splitext(image)[1]
            if not os.path.exists(os.path.join(freevo.FREEVO_DATA_DIR, 'webcache')):
                os.mkdir(os.path.join(freevo.FREEVO_DATA_DIR, 'webcache'))
            self.cachefile = os.path.join(freevo.FREEVO_DATA_DIR, 'webcache', self.base)
            if not os.path.isfile(self.cachefile):
                self.needs_update = True
                self.url = image
            else:
                self.image = self.cachefile
        else:
            self.image = image

    def create(self, priority):
        if not self.cachefile:
            return
        if not self.cachefile in self._downloads:
            tmpfile = kaa.tempfile('freevo-cache/' + self.base)
            c = kaa.net.url.fetch(self.url, self.cachefile, self.cachefile + '.part')
            self._downloads[self.cachefile] = c
            self._downloads[self.cachefile].connect_weak_once(self._fetched)
        return self._downloads[self.cachefile]

    def _fetched(self, status):
        """
        Callback for HTTP GET result. The image should be in the cachefile.
        """
        if self.cachefile in self._downloads:
            del self._downloads[self.cachefile]
        self.image = self.cachefile
        self.needs_update = False
