# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Misc image widgets
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2009-2013 Dirk Meyer, et al.
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

__all__ = [ 'Image', 'Thumbnail' ]

import os

import kaa.beacon
import kaa.candy


class Image(kaa.candy.Image):
    """
    Basic image widget from kaa.candy with changed cache
    """
    candyxml_style = None

    def get_cachefile(self, url):
        """
        Return the cache filename for the given url
        """
        return kaa.beacon.md5url(url, 'images')


class Thumbnail(kaa.candy.Thumbnail):
    """
    Thumbnail image with mimetype icons as fallback
    """
    candyxml_style = 'mimetype'

    __item = __item_eval = None

    def __init__(self, pos, size, item, context=None):
        super(Thumbnail,self).__init__(pos, size, context=context)
        self.item = item

    def _candy_context_sync(self, context):
        """
        Sync the kaa.candy context
        """
        super(Thumbnail, self)._candy_context_sync(context)
        self.item = self.__item

    @property
    def item(self):
        """
        Get associated item
        """
        return self.__item_eval

    @item.setter
    def item(self, item):
        """
        Set associated item and load the thumbnail
        """
        self.__item = item
        if isinstance(item, (str, unicode)):
            if self.context:
                item = self.context.get(item)
            else:
                item = None
        if self.__item_eval == item:
            return
        self.__item_eval = item
        if not item:
            return
        self.set_thumbnail(item.get('thumbnail'))
        if not self.image:
            # find matching mimetype icon
            # TODO: cache the results
            # TODO: rotate if required
            if item.type == 'directory':
                if self._try_mimetype('folder_%s' % item.media_type):
                    return
                return self._try_mimetype('folder')
            if item.type == 'playlist':
                if item.parent and self._try_mimetype('playlist_%s' % item.parent.media_type):
                    return
                return self._try_mimetype('playlist')
            try:
                if self._try_mimetype(item.info['mime'].replace('/', '_')):
                    return
            except:
                pass
            if item.type and self._try_mimetype(item.type):
                return
            if self._try_mimetype('unknown'):
                return

    def _try_mimetype(self, name):
        """
        Try the given mimetype. Set self.image and return True if it is found
        """
        for ext in ('.png', '.jpg'):
            fname = os.path.join(self.theme.icons, 'mimetypes', name + ext)
            if os.path.isfile(fname):
                self.image = fname
                return True
        return False

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the candyxml element for parameter to create the widget.
        """
        return kaa.candy.Widget.candyxml_parse(element).update(
            item=element.item)
