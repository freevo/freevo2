#if 0 /*
# -----------------------------------------------------------------------
# util.py - This file contains utility functions for Freevo
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.47  2002/11/23 19:32:27  dischi
# We don't need that
#
# Revision 1.46  2002/11/15 03:39:20  krister
# Fixed a bug in autoslideshows.
#
# Revision 1.45  2002/11/14 03:16:47  krister
# Bigfixes for VCD playing.
#
# Revision 1.44  2002/11/13 14:34:21  krister
# Fixed a bug in music playing (the file type was mistaken for video for songs without an absolute path) by changing the way file suffixes are handled. The format of suffixes in freevo_config.py changed, local_conf.py must be updated!
#
# Revision 1.43  2002/11/06 03:24:31  krister
# Added fileheader
#
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

import sys
import socket, glob
import random
import termios, tty, time, os
import string, popen2, fcntl, select, struct, fnmatch,re, operator
import time
import threading
import fcntl
import md5

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52560
def unique(s):
    """Return a list of the elements in s, but without duplicates.

    For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
    unique("abcabc") some permutation of ["a", "b", "c"], and
    unique(([1, 2], [2, 3], [1, 2])) some permutation of
    [[2, 3], [1, 2]].

    For best speed, all sequence elements should be hashable.  Then
    unique() will usually work in linear time.

    If not possible, the sequence elements should enjoy a total
    ordering, and if list(s).sort() doesn't raise TypeError it's
    assumed that they do enjoy a total ordering.  Then unique() will
    usually work in O(N*log2(N)) time.

    If that's not possible either, the sequence elements must support
    equality-testing.  Then unique() will usually work in quadratic
    time.
    """

    n = len(s)
    if n == 0:
        return []

    # Try using a dict first, as that's the fastest and will usually
    # work.  If it doesn't work, it will usually fail quickly, so it
    # usually doesn't cost much to *try* it.  It requires that all the
    # sequence elements be hashable, and support equality comparison.
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        del u  # move on to the next method
    else:
        return u.keys()

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = list(s)
        t.sort()
    except TypeError:
        del t  # move on to the next method
    else:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti += 1
            i += 1
        return t[:lasti]

    # Brute force is all that's left.
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u


def getdirnames(dirname):
    '''Get all subdirectories in the given directory.
    Returns a list that is case insensitive sorted.'''

    try:
        dirnames = [ os.path.join(dirname, dname) for dname in os.listdir(dirname)
                     if os.path.isdir(os.path.join(dirname, dname)) ]
    except OSError:
        return []
    
    dirnames.sort(lambda l, o: cmp(l.upper(), o.upper()))
    
    return dirnames


def match_suffix(filename, suffixlist):
    '''Check if a filename ends in a given suffix, case is ignored.'''

    fsuffix = os.path.splitext(filename)[1].lower()[1:]

    for suffix in suffixlist:
        if fsuffix == suffix:
            return 1

    return 0


def match_files(dirname, suffix_list):
    '''Find all files in a directory that has matches a list of suffixes.
    Returns a list that is case insensitive sorted.'''

    try:
        files = [ os.path.join(dirname, fname) for fname in os.listdir(dirname) if
                  os.path.isfile(os.path.join(dirname, fname)) ]
    except OSError:
        print 'util:match_files(): Got error on dir = "%s"' % dirname
        return []

    matches = [ fname for fname in files if match_suffix(fname, suffix_list) ]
        
    matches.sort(lambda l, o: cmp(l.upper(), o.upper()))
    
    return matches

    
def match_files_recursively_helper(result, dirname, names):
    for name in names:
	fullpath = os.path.join(dirname, name)
	result.append(fullpath)
    return result


def match_files_recursively(dir, suffix_list):
    all_files = []
    os.path.walk(dir, match_files_recursively_helper, all_files)

    matches = unique([f for f in all_files if match_suffix(f, suffix_list) ])

    matches.sort(lambda l, o: cmp(l.upper(), o.upper()))
    
    return matches


# Helper function for the md5 routine; we don't want to
# write filenames that aren't in lower ascii so we uhm,
# hexify them.
def hexify(str):
        hexStr = string.hexdigits
        r = ''
        for ch in str:
                i = ord(ch)
                r = r + hexStr[(i >> 4) & 0xF] + hexStr[i & 0xF]
        return r


# Python's bundled MD5 class only acts on strings, so
# we have to calculate it in this loop
def md5file(filename):
        m = md5.new()
        try:
            f = open(filename, 'r')
        except IOError:
            print 'Cannot find file "%s"!' % filename
            return ''
        for line in f.readlines():
                m.update(line)
        f.close()
        return hexify(m.digest())
    

# Simple Python Imaging routine to return image size
# and return a default if the Imaging library is not
# installed.
def pngsize(file):
    if not os.path.isfile(file):
        return 200,200
    import Image
    image = Image.open(file)
    width, height = image.size
    return width,height


def resize(file, x0=25, y0=25):
        import Image

        if not os.path.isfile(file):
            return ''
        
        # Since the filenames are not unique we need
        # to cache them by content, not name.
        mythumb = (config.FREEVO_CACHEDIR + '/' +
                   os.path.basename(md5file(file)) + '-%s-%s.png' % (x0, y0))
        if os.path.isfile(mythumb):
                return mythumb
        else:
                im = Image.open(file)
                im_res = im.resize((x0,y0), Image.BICUBIC)
                im_res.save(mythumb,'PNG')
                return mythumb

def getExifThumbnail(file, x0=0, y0=0):
    import Image

    # EXIF parser
    import exif

    f=open(file, 'rb')
    tags=exif.process_file(f)
    
    if tags.has_key('JPEGThumbnail'):
        thumb_name='%s/image-viewer-thumb.jpg' % config.FREEVO_CACHEDIR
        open(thumb_name, 'wb').write(tags['JPEGThumbnail'])
        if x0 >0 :
            return resize(thumb_name, x0, y0)
        return thumb_name
        
    if tags.has_key('TIFFThumbnail'):
        print "TIFF thumbnail not supported yet"

    
def recursefolders(root, recurse=0, pattern='*', return_folders=0):
        # Before anyone asks why I didn't use os.path.walk; it's simple, 
        # os.path.walk is difficult, clunky and doesn't work right in my
        # mind. 
        #
        # Here's how you use this function:
        #
        # songs = recursefolders('/media/Music/Guttermouth',1,'*.mp3',1):
        # for song in songs:
        #       print song      
        #
        # Should be easy to add to the mp3.py app.

        # initialize
        result = []

        # must have at least root folder
        try:
                names = os.listdir(root)
        except os.error:
                return result

        # expand pattern
        pattern = pattern or '*'
        pat_list = string.splitfields( pattern , ';' )
        
        # check each file
        for name in names:
                fullname = os.path.normpath(os.path.join(root, name))

                # grab if it matches our pattern and entry type
                for pat in pat_list:
                        if fnmatch.fnmatch(name, pat):
                                if os.path.isfile(fullname) or (return_folders and os.path.isdir(fullname)):
                                        result.append(fullname)
                                continue
                                
                # recursively scan other folders, appending results
                if recurse:
                        if os.path.isdir(fullname) and not os.path.islink(fullname):
                                result = result + recursefolders( fullname, recurse, pattern, return_folders )
                        
        return result


PROC_MOUNT_REGEXP = re.compile("^([^ ]*) ([^ ]*) .*$").match

def proc_mount(dir):
    f = open('/proc/mounts')
    l = f.readline()
    while(l):
        m = PROC_MOUNT_REGEXP(l)
        if m:
            if m.group(2) == dir and m.group(1).encode() != 'none':
                f.close()
                return m.group(1).encode()
        l = f.readline()
    f.close()
    return None


def umount(dir):
    if proc_mount(dir):
        os.system("umount %s" % dir)


def mount(dir):
    if not proc_mount(dir):
        os.system("mount %s 2>/dev/null" % dir)
