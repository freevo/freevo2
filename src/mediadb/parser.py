# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# parser.py - parsing functions to get informations about a file
# -----------------------------------------------------------------------------
# $Id$
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
import time
import kaa.metadata
import kaa.metadata.version
import pickle
import cPickle
import re

# freevo imports
import config
import util.vfs as vfs
import util

# mediadb imports
import db
from globals import *

# list of external parser
_parser = []

# internal version of the file
VERSION = 0.1

def init():
    """
    Init the parser module
    """
    global VERSION
    VERSION += kaa.metadata.version.CHANGED
    for f in os.listdir(os.path.dirname(__file__)):
        if f.endswith('_parser.py'):
            exec('import %s' % f[:-3])
            _parser.append(eval(f[:-3]))
            VERSION += eval(f[:-3]).VERSION


def simplify(object):
    """
    Kaa.metadata has huge objects to cache, we don't need them.
    This function simplifies them to be only string, integer, dict or
    list of one of those above. This makes the caching much faster
    """
    ret = {}
    for k in object.keys:
        if not k in [ 'thumbnail', URL ] and getattr(object,k) != None:
            value = getattr(object,k)
            if isinstance(value, (str, unicode)):
                value = Unicode(value.replace('\0', '').lstrip().rstrip())
            if value:
                ret[k] = value

    for k in  ( 'video', 'audio'):
        # if it's an AVCORE object, also simplify video and audio
        # lists to string and it
        if hasattr(object, k) and getattr(object, k):
            ret[k] = []
            for o in getattr(object, k):
                ret[k].append(simplify(o))

    if hasattr(object, 'tracks') and object.tracks:
        # read track informations for dvd
        ret['tracks'] = []
        for o in object.tracks:
            track = simplify(o)
            if not track.has_key('audio'):
                track['audio'] = []
            if not track.has_key('subtitles'):
                track['subtitles'] = []
            ret['tracks'].append(track)

    for k in ('subtitles', 'chapters', 'mime', 'id' ):
        if hasattr(object, k) and getattr(object, k):
            ret[k] = getattr(object, k)

    return ret

# regexp for filenames used in getname
_FILENAME_REGEXP = re.compile("^(.*?)_(.)(.*)$")

def getname(file, keep_ext):
    """
    make a nicer display name from file
    """
    if len(file) < 2:
        return Unicode(file)

    # basename without ext
    if not keep_ext and file.rfind('/') < file.rfind('.'):
        name = file[file.rfind('/')+1:file.rfind('.')]
    else:
        name = file[file.rfind('/')+1:]
    if not name:
        # Strange, it is a dot file, return the complete
        # filename, I don't know what to do here. This should
        # never happen
        return Unicode(file)

    name = name[0].upper() + name[1:]
    # check which char is the space
    if name.count('_') == 0 and name.count(' ') == 0:
        if name.count('.') > 4:
            # looks like '.' is the space here
            name = name.replace('.', '_')
        elif name.count('-') > 4:
            # looks like '-' is the space here
            name = name.replace('-', '_')
    while name.find('_') != -1 and _FILENAME_REGEXP.match(name):
        m = _FILENAME_REGEXP.match(name)
        if m:
            name = m.group(1) + ' ' + m.group(2).upper() + m.group(3)
    if name.endswith('_'):
        name = name[:-1]
    return Unicode(name)


def cover_filter(x):
    """
    Filter function to get valid cover names
    """
    return re.search(config.AUDIO_COVER_REGEXP, x, re.IGNORECASE)



def parse(basename, filename, object, cache, listing):
    """
    Add additional informations to filename, object.
    """
    for key in object[MTIME_DEP]:
        del object[key]
    object[MTIME_DEP] = []

    for key in [ URL, TYPE, NEEDS_UPDATE ]:
        if object.has_key(key):
            del object[key]

    if object.has_key(NEW_FILE):
        added = True
        del object[NEW_FILE]
    else:
        added = False
        
    mminfo = None
    ext = object[EXTENTION]
    if not ext in [ 'xml', 'fxd' ]:
        mminfo = kaa.metadata.parse(filename)

    is_dir = os.path.isdir(filename)
    title = getname(filename, is_dir)
    object[FILETITLE] = title

    if mminfo:
        # store kaa.metadata data as pickle for faster loading
        object[MMINFO] = cPickle.dumps(simplify(mminfo),
                                         pickle.HIGHEST_PROTOCOL)
        if hasattr(mminfo, TITLE) and mminfo.title:
            object[TITLE] = mminfo.title.replace('\0', '').strip()
        else:
            object[TITLE] = title
    elif object.has_key(MMINFO):
        del object[MMINFO]
        object[TITLE] = title
    else:
        object[TITLE] = title

    if is_dir:
        object[ISDIR] = True
        if vfs.abspath(filename + '/' + basename + '.fxd'):
            # directory is covering a fxd file
            object[TYPE] = 'fxd'

        # Create a simple (fast) cache of subdirs to get some basic idea
        # about the files inside the directory
        c = db.Cache(filename)
        if c.num_changes():
            c.parse(None, True)

        listing = c.keys()

        # get directory cover
        for fname in listing:
            if fname in ( 'cover.png', 'cover.jpg', 'cover.gif'):
                object[COVER] = c.filename(fname)
                object[EXTRA_COVER] = c.filename(fname)
                break
        else:
            object[COVER] = ''
            object[EXTRA_COVER] = ''
            files = util.find_matches(listing, COVER_EXT)
            if len(files) == 1:
                object[EXTRA_COVER] = files[0]
            elif len(files) > 1 and len(files) < 10:
                files = filter(cover_filter, files)
                if files:
                    object[EXTRA_COVER] = files[0]

        # get folder fxd
        for fname in listing:
            if fname == 'folder.fxd':
                object[FXD] = c.filename(fname)
                break
        else:
            if object.has_key(FXD):
                del object[FXD]
            
        # save directory overlay mtime
        overlay = vfs.getoverlay(filename)
        if os.path.isdir(overlay):
            mtime = os.stat(overlay)[stat.ST_MTIME]
            object[OVERLAY_MTIME] = mtime
        else:
            object[OVERLAY_MTIME] = 0
    else:
        if object.has_key(ISDIR):
            del object[ISDIR]

        if ext in COVER_EXT:
            # find items that could have this file as cover
            splitext = basename[:-len(ext)]
            for key, value in listing:
                if key.startswith(splitext) and \
                       not value[EXTENTION] in COVER_EXT:
                    value[COVER] = filename
        else:
            # search for a cover for this file
            object[COVER] = ''
            splitext = basename[:-len(ext)]
            for key, value in listing:
                if key.startswith(splitext) and value[EXTENTION] in COVER_EXT:
                    object[COVER] = cache.filename(key)
    

    # call external parser
    for p in _parser:
        p.parse(filename, object, mminfo)


def cache(listing):
    """
    Function for the 'cache' helper.
    """
    for p in _parser:
        p.cache(listing)
