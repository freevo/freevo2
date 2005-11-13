# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# cdstatus.py - IdleBarPlugin for showing cd status
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: ? <?@?>
# Maintainer:    Viggo Fredriksen <viggo@katatonic.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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

import os
import gui.widgets
import gui.imagelib
import config

from plugins.idlebar import IdleBarPlugin

class PluginInterface(IdleBarPlugin):
    """
    Show the status of all rom drives.

    Activate with:
    plugin.activate('idlebar.cdstatus')
     or
    plugin.activate('idlebar.cdstatus', args=(draw_empty_rom,)

    Where draw_empty_rom is either of
     True   : draw empty cdroms.   (default)
     False  : do not draw empty cdroms.
    """
    def __init__(self, args=(True,)):

        IdleBarPlugin.__init__(self)
        icondir = os.path.join(config.ICON_DIR, 'status')
        self.cdimages ={}
        self.cdimages ['audiocd']     = os.path.join(icondir, 'cd_audio.png')
        self.cdimages ['empty_cdrom'] = os.path.join(icondir, 'cd_inactive.png')
        self.cdimages ['images']      = os.path.join(icondir, 'cd_photo.png')
        self.cdimages ['video']       = os.path.join(icondir, 'cd_video.png')
        self.cdimages ['dvd']         = os.path.join(icondir, 'cd_video.png')
        self.cdimages ['burn']        = os.path.join(icondir, 'cd_burn.png')
        self.cdimages ['cdrip']       = os.path.join(icondir, 'cd_rip.png')
        self.cdimages ['mixed']       = os.path.join(icondir, 'cd_mixed.png')

        self.draw_empty = args
        self.init       = True
        self.rem_media  = []

        # collect all the media types
        for media in vfs.mountpoints:
            self.rem_media.append(media.type)

    def draw(self, width, height):
        """
        Draws the removable media.
        """

        changed = False
        i       = 0

        for media in vfs.mountpoints:
            # check if there has been any changes
            if media.type != self.rem_media[i] or self.init:
                self.rem_media[i] = media.type
                changed           = True
            i += 1

        if not changed:
            # no changes registered
            return self.NO_CHANGE

        # clear previous images
        self.clear()

        self.init = False
        w         = 0
        x0        = 5

        # iterate through the removable medias
        for media in vfs.mountpoints:

            if media.type == 'empty_cdrom' and not self.draw_empty:
                # don't draw empty if configured
                continue

            if media.type and self.cdimages.has_key(media.type):
                # search for a specific media type
                image = gui.imagelib.load(self.cdimages[media.type],(None,None))
            else:
                # no specific type, use mixed icon
                image = gui.imagelib.load(self.cdimages['mixed'], (None, None))

            y0 = int((height-image.height)/2)
            self.objects.append(gui.widgets.Image(image, (x0, y0)))

            w  += image.width + 10
            x0 += image.width + 5

        if w >= 10:
            w -= 10

        return w
