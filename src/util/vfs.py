# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# vfs.py - virtual filesystem
# -----------------------------------------------------------------------------
# $Id$
#
# This is a virtual filesystem for Freevo. It uses the structure in
# sysconfig.VFS_DIR to store files that should be in the normal directory,
# but the user has no write access to it. It's meant to store fxd and image
# files (covers).
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
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

# python imports
import os
import codecs
import logging
from stat import ST_MTIME

import sysconfig

# the logging object
log = logging.getLogger('vfs')

# vfs directory on disc
BASE = sysconfig.VFS_DIR

# list of mount points
mountpoints = []

class Mountpoint(object):
    """
    Base object for a mount point.
    """
    def __init__(self, mountdir, devicename, type, id=""):
        self.mountdir = mountdir
        self.devicename = devicename
        self.type = type

        self.set_id(id)
        
        # add to global list
        mountpoints.append(self)

        
    def set_id(self, id):
        """
        Set media id. May be called more than once when the
        id changes (e.g. rom drives)
        """
        self.id = id
        self.cache = os.path.join(BASE, 'disc/metadata/%s.db' % id)
        vfs = os.path.join(BASE, 'disc', id)
        self.mediadb = os.path.join(vfs, '.metadata')
        self.thumbnails = os.path.join(vfs, '.thumbnails')
        

    def get_overlay(self, filename):
        """
        Get overlay for filename.
        """
        filename = filename[len(self.mountdir):]
        return '%s/disc/%s%s' % (BASE, self.id, filename)


    def get_root(self):
        """
        Get root dir for the vfs.
        """
        return '%s/disc/%s' % (BASE, self.id)


    def get_relative_path(self, filename):
        """
        Get relative path for filename at this mountpoint.
        """
        return filename[len(self.mountdir)+1:]
        

    def mount(self):
        """
        Mount the media
        """
        if not os.path.ismount(self.mountdir):
            log.info('Mounting %s' % self.mountdir)
            os.system('mount "%s"' % self.mountdir)
        return


    def umount(self):
        """
        Mount the media
        """
        if os.path.ismount(self.mountdir):
            log.info('Unmounting %s' % self.mountdir)
            os.system('umount "%s"' % self.mountdir)


    def is_mounted(self):
        """
        Check if the media is mounted
        """
        return os.path.ismount(self.mountdir)



def get_mountpoint(filename):
    if not filename.startswith('/'):
        filename = os.path.abspath(filename)
    for media in mountpoints:
        if filename.startswith(media.mountdir):
            return media
    return None


def get_mountpoint_by_id(id):
    for mp in mountpoints:
        if id == mp.id:
            return mp
    return None
    
    
def getoverlay(directory):
    if not directory.startswith('/'):
        directory = os.path.abspath(directory)
    if directory.startswith(BASE):
        return directory
    for media in mountpoints:
        if directory.startswith(media.mountdir):
            directory = directory[len(media.mountdir):]
            return '%s/disc/%s%s' % (BASE, media.id, directory)
    return BASE + directory


def abspath(name):
    """
    return the complete filename (including vfs.BASE)
    """
    if os.path.exists(name):
        if not name.startswith('/'):
            return os.path.abspath(name)
        return name
    overlay = getoverlay(name)
    if overlay and os.path.isfile(overlay):
        return overlay
    return ''


def isfile(name):
    """
    return if the given name is a file
    """
    if os.path.isfile(name):
        return True
    overlay = getoverlay(name)
    return overlay and os.path.isfile(overlay)


def open(name, mode='r'):
    """
    open the file
    """
    try:
        return file(name, mode)
    except:
        overlay = os.path.abspath(getoverlay(name))
        if not overlay:
            raise OSError
        try:
            if not os.path.isdir(os.path.dirname(overlay)):
                os.makedirs(os.path.dirname(overlay), mode=04775)
        except IOError:
            log.error('vfs.open: error creating dir %s' % \
                      os.path.dirname(overlay))
            raise IOError
        try:
            return file(overlay, mode)
        except IOError:
            log.error('vfs.open: error opening file %s' % overlay)
            raise IOError


def codecs_open(name, mode, encoding):
    """
    use codecs.open to open the file
    """
    try:
        return codecs.open(name, mode, encoding=encoding)
    except:
        overlay = os.path.abspath(getoverlay(name))
        if not overlay:
            raise OSError
        try:
            if not os.path.isdir(os.path.dirname(overlay)):
                os.makedirs(os.path.dirname(overlay))
        except IOError:
            log.error('vfs.codecs_open: error creating dir %s' % \
                      os.path.dirname(overlay))
            raise IOError
        try:
            return codecs.open(overlay, mode, encoding=encoding)
        except IOError, e:
            log.error('vfs.codecs_open: error opening file %s' % overlay)
            raise IOError, e


# Init VFS

# Make sure BASE doesn't ends with a slash
# With that, we don't need to use os.path.join, normal string
# concat is much faster
if BASE.endswith('/'):
    BASE = BASE[:-1]

# Check if BASE is valid
if BASE == '/':
    print
    print 'ERROR: bad VFS dir.'
    print 'Set vfs dir it to a directory on the local filesystem.'
    print 'Make sure this partition has about 100 MB free space'
    sys.exit(0)

# create VFS dirs
if not os.path.isdir(BASE):
    os.makedirs(BASE)

if not os.path.isdir(BASE + '/disc'):
    os.makedirs(BASE + '/disc')

if not os.path.isdir(BASE + '/disc/metadata'):
    os.makedirs(BASE + '/disc/metadata')

if not os.path.isdir(BASE + '/disc-set'):
    os.makedirs(BASE + '/disc-set')
