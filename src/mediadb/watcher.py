# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# watcher - Watch/Scan directories and notify on changes
# -----------------------------------------------------------------------------
# $Id$
#
# FIXME: stop everything when dir is not shown
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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

# python imports
import os
import stat
import logging
import notifier

# get logging object
log = logging.getLogger('mediadb')

# mediadb imports
from globals import *

class Watcher(object):

    def __init__(self):
        self.listing = ''
        self.notifier_scan = None
        self.notifier_check = None
        self.callback = None


    def cwd(self, listing, callback=None):
        self.callback = callback
        self.listing = listing
        if not listing:
            if self.notifier_scan:
                log.info('remove scanner')
                notifier.removeTimer(self.notifier_scan)
                self.notifier_scan = None
            if self.notifier_check:
                notifier.removeTimer(self.notifier_check)
            return

        num_changes = listing.cache.num_changes()
        if num_changes:
            log.info('%s changes in dir' % num_changes)
        if not num_changes:
            if self.notifier_scan:
                log.info('remove scanner')
                notifier.removeTimer(self.notifier_scan)
                self.notifier_scan = None
        else:
            if not self.notifier_scan:
                log.info('add scanner')
                self.notifier_scan = notifier.addTimer(0, self.scan)
        if not self.notifier_check:
            self.notifier_check = notifier.addTimer(1000, self.check)
        return num_changes
    

    def scan(self):
        if self.listing.cache.parse_next():
            return True
        log.info('remove scanner')
        self.listing.cache.save()
        self.notifier_scan = None
        if self.callback:
            self.callback()
        return False


    def check(self):
        # check dir modification time
        cache = self.listing.cache
        if os.stat(cache.dirname)[stat.ST_MTIME] != \
               cache.data[ITEMS_MTIME]:
            if self.callback:
                log.info('directory changed')
                self.callback()
            return True
        try:
            if os.stat(cache.overlay_dir)[stat.ST_MTIME] != \
                   cache.data[OVERLAY_MTIME]:
                if self.callback:
                    log.info('overlay changed')
                    self.callback()
                return True
        except OSError:
            # no overlay
            pass
        if self.notifier_scan:
            # scanning in progress, do not check changes
            return True

        # FIXME: now check all items modification time
        # or maybe only fxd files
        return True
