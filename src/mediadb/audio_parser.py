# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# audio_parser.py - parser for audio metadata
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
import sys
import os
import stat
import md5

# mediadb imports
from listing import Listing, FileListing

#
# Interface
#

# internal version of the file
VERSION = 0.1

def cache(listing):
    """
    Function for the 'cache' helper.
    """
    print 'creating audio metadata...............................',
    sys.__stdout__.flush()
    for item in listing:
        check_info(item)
    print 'done'


def parse(filename, object, mminfo):
    """
    Add aditional audio based data.
    """
    pass


#
# Internal helper functions and classes
#

VARIOUS = u'__various__'

def check_info(dirinfo):
    """
    Parse additional information recursive over the given listing. The function
    will try to find 'length', 'artist', 'album' and 'year'.
    """
    listing = Listing(dirinfo.filename)
    if listing.num_changes:
        listing.update()

    # check if an update is needed
    for item in listing.get_dir():
        if os.path.islink(item.filename):
            # ignore softlinks
            continue
        if check_info(item):
            # yes, something changed
            break
    else:
        # no changes in all subdirs, looks good
        if dirinfo['length'] != None:
            # Since 'length' is not None and the info is stored with mtime,
            # no changes in here. Do not parse everything again
            return False

    # reset listing
    listing.reset()

    # variables to scan
    length = 0
    artist = ''
    album  = ''
    year   = ''

    # scan all subdirs
    for item in listing.get_dir():
        if os.path.islink(item.filename):
            # ignore softlinks
            continue
        check_info(item)
        for type in ('artist', 'album', 'year'):
            exec('%s = strcmp(item[type], %s)' % (type, type))
        length += item['length']

    use_tracks = True

    for item in listing:
        try:
            for type in ('artist', 'album'):
                exec('%s = strcmp(%s, item[type])' % (type, type))
            year = strcmp(year, item['date'])
            if item['length']:
                length += int(item['length'])
            use_tracks = use_tracks and item['trackno']
        except OSError:
            pass

    if use_tracks and (dirinfo['album'] or dirinfo['artist']):
        dirinfo.store_with_mtime('audio_advanced_sort', True)

    dirinfo.store_with_mtime('length', length)

    if not length:
        return True

    for type in ('artist', 'album', 'year'):
        if eval(type) not in ( '', VARIOUS ):
            dirinfo.store_with_mtime(type, eval(type))

    if not dirinfo['coverscan']:
        dirinfo.store_with_mtime('coverscan', True)
        extract_image(listing)
    return True


def strcmp(s1, s2):
    """
    Compare the given strings. If one is empty, return the other. If both are
    equal, return the string. If they are different, return VARIOUS.
    """
    if s1 != None:
        s1 = Unicode(s1)
    if s2 != None:
        s2 = Unicode(s2)

    if not s1 or not s2:
        return s1 or s2
    if s1 == VARIOUS or s2 == VARIOUS:
        return VARIOUS

    if s1.replace(u' ', u'').lower() == s2.replace(u' ', u'').lower():
        return s1
    return VARIOUS


def get_md5(obj):
    """
    Get md5 checksum of the given object (string or file)
    """
    m = md5.new()
    if isinstance(obj,file):
        for line in obj.readlines():
            m.update(line)
        return m.digest()
    else:
        m.update(obj)
        return m.digest()


def extract_image(listing):
    """
    Extract image from mp3 files in listing.
    """
    for item in listing.match_suffix(['mp3']):
        try:
            id3 = eyeD3.Mp3AudioFile( item.filename )
        except:
            continue
        myname = vfs.getoverlay(os.path.join(item.dirname, 'cover.jpg'))
        if id3.tag:
            images = id3.tag.getImages();
            for img in images:
                if os.path.isfile(myname) and \
                       (get_md5(vfs.open(myname,'rb')) == \
                        get_md5(img.imageData)):
                    # Image already there and has identical md5, skip
                    pass
                elif not os.path.isfile(myname):
                    f = open(myname, "wb")
                    f.write(img.imageData)
                    f.flush()
                    f.close()
                else:
                    # image exists, but sums are different, write a unique
                    # cover
                    iname = os.path.splitext(os.path.basename(i))[0]+'.jpg'
                    myname = vfs.getoverlay(os.path.join(item.dirname, iname))
                    f = open(myname, "wb")
                    f.write(img.imageData)
                    f.flush()
                    f.close()
