#if 0 /*
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# util/vfs.py - virtual filesystem
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# This is a virtual filesystem for Freevo. It uses the structure in
# config.OVERLAY_DIR to store files that should be in the normal
# directory, but the user has no write access to it. It's meant to
# store fxd and image files (covers).
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/12/18 18:21:33  outlyer
# I'm assuming these were supposed to be debug messages.
#
# Revision 1.3  2003/12/07 11:06:45  dischi
# small bugfix
#
# Revision 1.2  2003/11/23 16:57:08  dischi
# small fixes
#
# Revision 1.1  2003/11/22 20:33:53  dischi
# new vfs
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
#endif
            

import os
import copy
import traceback
import codecs

import config

def getoverlay(item):
    if not config.OVERLAY_DIR:
        return ''

    if isinstance(item, str) or isinstance(item, unicode):
        # it's a directory, return it
        directory = os.path.abspath(item)
        for media in config.REMOVABLE_MEDIA:
            if directory.startswith(media.mountdir):
                directory = directory[len(media.mountdir):]
                return os.path.join(config.OVERLAY_DIR, 'disc', media.id + directory)
        return os.path.join(config.OVERLAY_DIR, directory[1:])
        
    directory = item.dir
    
    if item.media:
        directory = directory[len(item.media.mountdir):]
        if len(directory) and directory[0] == '/':
            directory = directory[1:]
        return os.path.join(config.OVERLAY_DIR, 'disc', item.media.id, directory)
    else:
        if len(directory) and directory[0] == '/':
            directory = directory[1:]
        return os.path.join(config.OVERLAY_DIR, directory)


def abspath(name):
    """
    return the complete filename (including OVERLAY_DIR)
    """
    if os.path.exists(name):
        return os.path.abspath(name)
    overlay = getoverlay(name)
    if overlay and os.path.isfile(overlay):
        return overlay
    return ''


def isfile(name):
    """
    return if the given name is a file
    """
    return os.path.isfile(abspath(name))


def unlink(name):
    absname = abspath(name)
    if not absname:
        raise IOError, 'file %s not found' % name
    os.unlink(absname)


def stat(name):
    absname = abspath(name)
    if not absname:
        raise IOError, 'file %s not found' % name
    return os.stat(absname)

    
def open(name, mode='r'):
    """
    open the file
    """
    try:
        return file(name, mode)
    except:
        overlay = getoverlay(name)
        if not overlay:
            raise OSError
        try:
            if not os.path.isdir(os.path.dirname(overlay)):
                os.makedirs(os.path.dirname(overlay))
        except IOError:
            print 'error creating dir %s' % os.path.dirname(overlay)
            raise IOError
        try:
            return file(overlay, mode)
        except IOError:
            print 'error opening file %s' % overlay
            raise IOError


def codecs_open(name, mode, encoding):
    """
    use codecs.open to open the file
    """
    try:
        return codecs.open(name, mode, encoding=encoding)
    except:
        overlay = getoverlay(name)
        if not overlay:
            raise OSError
        try:
            if not os.path.isdir(os.path.dirname(overlay)):
                os.makedirs(os.path.dirname(overlay))
        except IOError:
            print 'error creating dir %s' % os.path.dirname(overlay)
            raise IOError
        try:
            return codecs.open(overlay, mode, encoding=encoding)
        except IOError, e:
            print 'error opening file %s' % overlay
            raise IOError, e
    

def listdir(directory, handle_exception=True):
    """
    get a directory listing (including OVERLAY_DIR)
    """
    try:
        files = ([ os.path.join(directory, fname)
                   for fname in os.listdir(directory) ])
        overlay = getoverlay(directory)
        if overlay and os.path.isdir(overlay):
            for f in ([ os.path.join(overlay, fname)
                        for fname in os.listdir(overlay) ]):
                if not os.path.isdir(f):
                    files.append(f)

        # remove unwanted directories
        for f in copy.copy(files):
            if vfs.basename(f) in ('CVS', '.xvpics', '.thumbnails', '.pics', '.', '..'):
                files.remove(f)
        return files
    
    except OSError:
        _debug_('Error in dir')
        if not handle_exception:
            raise OSError
        return []


def isoverlay(name):
    """
    return if the name is in the overlay dir
    """
    if not config.OVERLAY_DIR:
        return False
    return name.startswith(config.OVERLAY_DIR)


def normalize(name):
    """
    remove OVERLAY_DIR if it's in the path
    """
    if isoverlay(name):
        name = name[len(config.OVERLAY_DIR):]
        if name.startswith('disc-set'):
            # revert it, disc-sets have no real dir
            return os.path.join(config.OVERLAY_DIR, name)
        if name.startswith('disc'):
            name = name[5:]
            id = name[:name.find('/')]
            name = name[name.find('/')+1:]
            for media in config.REMOVABLE_MEDIA:
                if media.id == id:
                    name = os.path.join(media.mountdir, name)
        return name
    return name


# some other os functions (you don't need to use them)
basename = os.path.basename
join     = os.path.join
splitext = os.path.splitext
basename = os.path.basename
dirname  = os.path.dirname
exists   = os.path.exists
isdir    = os.path.isdir
islink   = os.path.islink

if not config.OVERLAY_DIR:
    _debug_('OVERLAY_DIR not set, virtual filesystem won\'t work',1)
else:
    _debug_('Virtual filesystem activated',1)
    
