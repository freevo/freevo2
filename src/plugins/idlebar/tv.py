# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# tv.py - IdleBarPlugin for information about XMLTV-listings
# -----------------------------------------------------------------------
# $Id:
#
# -----------------------------------------------------------------------
# $Log:
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------- */
import os
import time

import gui
import config
import util.tv_util as tv_util
from plugins.idlebar import IdleBarPlugin


class PluginInterface(IdleBarPlugin):
    """
    Informs you, when the xmltv-listings expires.

    Activate with:
    plugin.activate('idlebar.tv', level=20, args=(listings_threshold,))
    listings_threshold must be a number in hours.  For example if you put
    args=(12, ) then 12 hours befor your xmltv listings run out the tv icon
    will present a warning.  Once your xmltv data is expired it will present
    a more severe warning.  If no args are given then no warnings will be
    given.
    """
    def __init__(self, listings_threshold=-1):
        IdleBarPlugin.__init__(self)

        self.listings_threshold = listings_threshold
        self.next_guide_check   = 0
        self.listings_expire    = 0
        self.tvlockfile         = config.FREEVO_CACHEDIR + '/record'
        self.status             = None

        self.TVLOCKED     = 'television_active.png'
        self.TVFREE       = 'television_inactive.png'
        self.NEAR_EXPIRED = 'television_near_expired.png'
        self.EXPIRED      = 'television_expired.png'


    def clear(self):
        IdleBarPlugin.clear(self)
        self.status = None


    def checktv(self):
        if os.path.exists(self.tvlockfile):
            return 1
        return 0


    def draw(self, width, height):
        status = 'inactive'
        if self.checktv() == 1:
            status = 'active'

        if self.listings_threshold != -1:
            now = time.time()

            if now > self.next_guide_check:
                self.listings_expire = tv_util.when_listings_expire()
                # check again in 10 minutes
                self.next_guide_check = now + 10*60

            if self.listings_expire <= self.listings_threshold:
                status = 'near_expired'

            if self.listings_expire == 0:
                status = 'expired'

        if self.status == status:
            return self.NO_CHANGE

        self.clear()
        self.status = status
        icon = gui.get_icon('status/television_%s' % status)
        i = gui.imagelib.load(icon, (None, None))


        self.objects.append(gui.Image(i, (0, (height-i.height)/2)))
        return i.width
