#if 0 /*
# -----------------------------------------------------------------------
# interface.py - interface between mediamenu and audio
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2003/03/15 10:19:34  dischi
# use extra audio cache dir
#
# Revision 1.4  2003/01/12 17:10:37  dischi
# Add cache for the id tags to avoid reloading known mp3/ogg tags. This will
# speed up displaying a directory.
#
# Revision 1.3  2003/01/12 13:51:51  dischi
# Added the feature to remove items for videos, too. For that the interface
# was modified (update instead of remove).
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

AUDIO_CACHE_VERSION = 1

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
