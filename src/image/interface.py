# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# interface.py - interface between mediamenu and image
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines the PluginInterface for the image module of
# Freevo. It is loaded by __init__.py and will activate the mediamenu
# for images.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2006 Dirk Meyer, et al.
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

# only export 'PluginInterface' to the outside. This will be used
# with plugin.activate('image') and everything else should be handled
# by using plugin.mimetype()
__all__ = [ 'PluginInterface' ]

# freevo imports
from freevo.ui import config
from freevo.ui import plugin
from freevo.ui import fxditem

# ImageItem
from imageitem import ImageItem

# fxdhandler for <slideshow> tags
from fxdhandler import fxdhandler

class PluginInterface(plugin.MimetypePlugin):
    """
    Plugin to handle all kinds of image items
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)
        self.display_type = [ 'image' ]

        # register the callbacks
        fxditem.add_parser(['image'], 'slideshow', fxdhandler)

        # activate the mediamenu for image
        level = plugin.is_active('image')[2]
        args = _('Image Main Menu'), 'image'
        plugin.activate('mediamenu', level=level, args=args)


    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return [ 'beacon:image' ] + config.IMAGE_SUFFIX


    def get(self, parent, listing):
        """
        return a list of items based on the files
        """
        items = []
        for suffix in self.suffix():
            for file in listing.get(suffix):
                items.append(ImageItem(file, parent))
        return items
