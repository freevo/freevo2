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
# Revision 1.18  2004/06/09 20:09:10  dischi
# cleanup
#
# Revision 1.17  2004/02/14 15:45:26  dischi
# do not include folder.fxd
#
# Revision 1.16  2004/02/05 19:26:42  dischi
# fix unicode handling
#
# Revision 1.15  2004/02/05 05:44:26  gsbarbieri
# Fixes some bugs related to handling unicode internally.
# NOTE: Many of the bugs are related to using str() everywhere, so please stop doing that.
#
# Revision 1.14  2004/02/05 02:52:26  gsbarbieri
# Handle filenames internally as unicode objects.
#
# This does *NOT* affect filenames that have only ASCII chars, since the
# translation ASCII -> Unicode is painless. However this *DOES* affect files with
# accents, like é (e acute, \xe9) and others.
#
# I tested with Video, Images and Music modules, but *NOT* with Games, so if you
# have the games modules, give it a try.
#
# It determines the encoding based on (in order) FREEVO_LOCALE, LANG and LC_ALL,
# which may have the form: "LANGUAGE_CODE.ENCODING", like "pt_BR.UTF-8", and others.
#
# Revision 1.13  2004/02/04 11:54:27  dischi
# check if directory is not overlay_dir
#
# Revision 1.12  2004/01/18 16:47:16  dischi
# more verbose
#
# Revision 1.11  2004/01/09 19:03:39  dischi
# make it possible to exclude dot files and overlay dir
#
# Revision 1.10  2004/01/06 19:25:46  dischi
# added mtime function using stat
#
# Revision 1.9  2004/01/05 17:39:22  dischi
# make overlay abspath before getting the dirname
#
# Revision 1.8  2004/01/03 17:38:17  dischi
# Freevo now needs the vfs active. OVERLAY_DIR is set to ~/.freevo/vfs as
# default value.
#
# Revision 1.7  2003/12/31 16:43:49  dischi
# major speed enhancements
#
# Revision 1.6  2003/12/30 22:30:50  dischi
# major speedup in vfs using
#
# Revision 1.5  2003/12/30 15:28:48  dischi
# remove old code
#
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
from stat import ST_MTIME


import config

def getoverlay(directory):
    if not directory.startswith('/'):
        directory = os.path.abspath(directory)
    if directory.startswith(config.OVERLAY_DIR):
        return directory
    for media in config.REMOVABLE_MEDIA:
        if directory.startswith(media.mountdir):
            directory = directory[len(media.mountdir):]
            return '%s/disc/%s%s' % (config.OVERLAY_DIR, media.id, directory)
    return config.OVERLAY_DIR + directory


def abspath(name):
    """
    return the complete filename (including OVERLAY_DIR)
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


def mtime(name):
    """
    Return the modification time of the file. If the files also exists
    in OVERLAY_DIR, return the max of both. If the file does not exist
    in the normal directory, OSError is raised.
    """
    t = os.stat(name)[ST_MTIME]
    try:
        return max(os.stat(getoverlay(name))[ST_MTIME], t)
    except (OSError, IOError):
        return t

    
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
        overlay = os.path.abspath(getoverlay(name))
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
    

def listdir(directory, handle_exception=True, include_dot_files=False,
            include_overlay=False):
    """
    get a directory listing (including OVERLAY_DIR)
    """
    try:
        if not directory.endswith('/'):
            directory = directory + '/'
            
        files = []

        if include_dot_files:
            for f in os.listdir(directory):
                if not f in ('CVS', '.xvpics', '.thumbnails', '.pics', 'folder.fxd'):
                    files.append(directory + f)
        else:
            for f in os.listdir(directory):
                if not f.startswith('.') and not f in ('CVS', 'folder.fxd'):
                    files.append(directory + f)

        if not include_overlay:
            return files

        overlay = getoverlay(directory)
        if overlay and overlay != directory and os.path.isdir(overlay):
            for fname in os.listdir(overlay):
                if fname.endswith('.raw') or fname.startswith('.') or \
                       fname == 'folder.fxd':
                    continue
                f = overlay + fname
                if not os.path.isdir(f):
                    files.append(f)
        return files
    
    except OSError:
        _debug_('Error in dir %s' % directory)
        traceback.print_exc()
        if not handle_exception:
            raise OSError
        return []


def isoverlay(name):
    """
    return if the name is in the overlay dir
    """
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

    
