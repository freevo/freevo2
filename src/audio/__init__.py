#if 0 /*
# -----------------------------------------------------------------------
# __init__.py - interface between mediamenu and audio
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2003/06/06 21:41:54  dischi
# Set AUDIO_CACHE_VERSION to 2 to audio-rebuild the cache if the
# audio cache is from older versions to avoid crash and manual
# removal of the cache files
#
# Revision 1.2  2003/04/21 18:17:50  dischi
# Moved the code from interface.py for video/audio/image/games to __init__.py
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

import config
import util

import cPickle as pickle
import md5
import os


from audioitem import AudioItem

AUDIO_CACHE_VERSION = 2

def cwd(parent, files):
    """
    return a list of items based on the files
    """
    items = []

    if parent and parent.type == 'dir':
        cache_file = '%s/audio/%s' % (config.FREEVO_CACHEDIR,
                                      util.hexify(md5.new(parent.dir).digest()))
    else:
        cache_file = None
        
    if cache_file and os.path.isfile(cache_file):
        version, cache = pickle.load(open(cache_file, 'r'))
        if version != AUDIO_CACHE_VERSION:
            print 'cache file has a wrong version'
            cache = {}
    else:
        cache = {}


    new_cache = {}

    for file in util.find_matches(files, config.SUFFIX_AUDIO_FILES):
        try:
            data = cache[file]
            items += [ AudioItem(file, parent, data) ]
            new_cache[file] = data
        except KeyError:
            item = AudioItem(file, parent)
            new_cache[file] = item.dump()
            items += [ item ]
            
        files.remove(file)


    if cache_file:
        pickle.dump((AUDIO_CACHE_VERSION, new_cache), open(cache_file, 'w'))

    return items



def update(parent, new_files, del_files, new_items, del_items, current_items):
    """
    update a directory. Add items to del_items if they had to be removed based on
    del_files or add them to new_items based on new_files
    """
    for item in current_items:
        for file in util.find_matches(del_files, config.SUFFIX_AUDIO_FILES):
            if item.type == 'audio' and item.filename == file:
                del_items += [ item ]
                del_files.remove(file)

    new_items += cwd(parent, new_files)
