# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# thumbnail.py - Thumbnail functions
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines some helper functions for creating thumbnails for faster
# image access. The thumbnails are stored in the vfs and have a max size
# of 255x255 pixel. 
#
# TODO: move this file and it's logic into kaa.thumb
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

__all__ = ( 'create', 'get_name', 'load' )

# python imports
import os
import logging
import stat

# kaa import
import kaa.mevas
import kaa.thumb
import kaa.notifier

# freevo utils
import fileops
import vfs

# the logging object
log = logging.getLogger('util')

# list for thumbnails to create in bg
_create_jobs = []

class Queue(kaa.notifier.Timer):
    """
    Timer handling the thumbaniling in a queue.
    """
    def __init__(self):
        kaa.notifier.Timer.__init__(self, self.create)
        self.jobs = []
        self.restart_when_active = False

    def append(self, filename, callback):
        for j, c in self.jobs:
            if j == filename:
                if callback:
                    c.append(callback)
                return
        self.jobs.append((filename, [ callback ]))
        if not self.active():
            self.start(10)
            
    def handle(self, filename):
        for job in self.jobs:
            if job[0] == filename:
                self.jobs.remove(job)
                return job[1]
        return []

    def create(self):
        log.info(self.jobs[0][0])
        create(self.jobs[0][0])
        if self.jobs:
            return True
        else:
            return False


# internal queue
_queue = Queue()

def get_name(filename):
    """
    Returns the filename of the thumbnail if it exists. None if not or
    False if it is impossible to create one.
    """
    # use ~/.thumbnails
    mp = vfs.get_mountpoint(filename)
    if mp:
        return kaa.thumb.check(filename, kaa.thumb.LARGE, mp.thumbnails)
    else:
        return kaa.thumb.check(filename, kaa.thumb.LARGE)


def create(filename):
    """
    Create a thumbnail for the given filename in the vfs.
    """
    callbacks = _queue.handle(filename)
    log.debug('create %s', filename)

    type, thumb = get_name(filename)

    if type == kaa.thumb.FAILED:
        # unable to create thumbnail
        return None

    if type != kaa.thumb.LARGE:
        # create a large thumbnail
        mp = vfs.get_mountpoint(filename)
        if mp:
            thumb = kaa.thumb.create(filename, kaa.thumb.LARGE, mp.thumbnails)
        else:
            thumb = kaa.thumb.create(filename, kaa.thumb.LARGE)

    if thumb:
        thumb = kaa.mevas.imagelib.open(thumb)

    # call all callbacks when the thumbnail is done and a valid
    # one is loaded.
    if thumb and callbacks:
        for c in callbacks:
            c(filename, thumb)
    return thumb


def need_thumbnailing(filename, bg=False):
    """
    Return True if it could be possible to create a thumbnail.
    """
    type, thumb = get_name(filename)
    return type in (kaa.thumb.MISSING, kaa.thumb.FAILED)

    
def load(filename, bg=False, callback=None):
    """
    Return the thumbnail. Create one, if it doesn't exists.
    """
    type, thumb = get_name(filename)
    if type == kaa.thumb.FAILED:
        # unable to create thumbnail
        return None
    if type == kaa.thumb.LARGE:
        # load image and return
        return kaa.mevas.imagelib.open(thumb)

    if not bg:
        # create thumbnail now
        return create(filename)

    # add thumbnail to background queue
    _queue.append(filename, callback)

    # If type is NORMAL, we have a thumbnail but want a better one.
    # But still, for now, a small one is better than nothing
    if type == kaa.thumb.NORMAL:
        # load image and return
        return kaa.mevas.imagelib.open(thumb)

    # no image
    return None
