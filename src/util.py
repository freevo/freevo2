#if 0 /*
# -----------------------------------------------------------------------
# util.py - Some Utilities
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.14  2003/02/20 06:56:07  krister
# Bugfix for dot-files
#
# Revision 1.13  2003/02/17 21:00:24  dischi
# catch an error
#
# Revision 1.12  2003/02/13 07:47:25  krister
# Bugfixes for image errors.
#
# Revision 1.11  2003/02/12 10:38:51  dischi
# Added a patch to make the current menu system work with the new
# main1_image.py to have an extended menu for images
#
# Revision 1.10  2003/02/12 10:28:28  dischi
# Added new xml file support. The old xml files won't work, you need to
# convert them.
#
# Revision 1.9  2003/02/07 20:11:32  dischi
# bugfix
#
# Revision 1.8  2003/02/06 09:22:06  krister
# Added a python killall() function instead of the shell call.
#
# Revision 1.7  2003/02/04 16:28:37  outlyer
# Replaced proc_mount with os.ismount to be somewhat cross-platform.
#
# Revision 1.6  2003/01/31 19:24:41  outlyer
# Replaced proc_mount with python version from 'os' module. Currently
# commented out... can someone try it and make sure it works? I don't
# have a CDRom drive so I can't test it, but I can't imagine it not
# working.
#
# Revision 1.5  2002/12/07 11:32:59  dischi
# Added interface.py into video/audio/image/games. The file contains a
# function cwd to return the items for the list of files. games support
# is still missing
#
# Revision 1.4  2002/11/28 19:55:42  dischi
# add function to make a nice name from a filename
#
# Revision 1.3  2002/11/25 02:17:54  krister
# Minor bugfixes. Synced to changes made in the main tree.
#
# Revision 1.2  2002/11/24 17:00:15  dischi
# Copied the new transparent gif support to the code cleanup tree
#
# Revision 1.1  2002/11/24 13:58:44  dischi
# code cleanup
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
import commands
import Image # PIL

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


def find_matches(files, suffix_list):
    return [ fname for fname in files if match_suffix(fname, suffix_list) ]


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
# and return a default if and error occurs.
def pngsize(filename):
    if not os.path.isfile(filename):
        return (200, 200)

    try:
        image = Image.open(filename)
        width, height = image.size
        return (width, height)
    except IOError:
        print 'Cannot open image file "%s"' % filename
        return (200, 200)


def resize(filename, x0=25, y0=25):

    if not os.path.isfile(filename):
        return ''
        
    # Since the filenames are not unique we need
    # to cache them by content, not name.
    mythumb = (config.FREEVO_CACHEDIR + '/' +
               os.path.basename(md5file(filename)) + '-%s-%s.png' % (x0, y0))
    if os.path.isfile(mythumb):
        return mythumb
    else:
        try:
            im = Image.open(filename)
        except IOError:
            return ''
        try:
            im_res = im.resize((x0,y0), Image.BICUBIC)
            im_res.save(mythumb, 'PNG')
            return mythumb
        except IOError:
            print 'error resizing image %s' % filename
            return filename

def getExifThumbnail(file, x0=0, y0=0):
    import Image
    import cStringIO

    # EXIF parser
    from image import exif

    f=open(file, 'rb')
    tags=exif.process_file(f)
    
    if tags.has_key('JPEGThumbnail'):
        thumb_name='%s/image-viewer-thumb.jpg' % config.FREEVO_CACHEDIR
        image = Image.open(cStringIO.StringIO(tags['JPEGThumbnail']))
        if x0 >0 :
            image.resize((x0, y0), Image.BICUBIC)

        image.save(thumb_name)
        return thumb_name
        
    if tags.has_key('TIFFThumbnail'):
        print "TIFF thumbnail not supported yet"

    return None

    
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
                                if os.path.isfile(fullname) or \
                                   (return_folders and os.path.isdir(fullname)):
                                        result.append(fullname)
                                continue
                                
                # recursively scan other folders, appending results
                if recurse:
                        if os.path.isdir(fullname) and not os.path.islink(fullname):
                                result = result + recursefolders( fullname, recurse,
                                                                  pattern, return_folders )
                        
        return result


def umount(dir):
    if os.path.ismount(dir):
        os.system("umount %s" % dir)


def mount(dir):
    if not os.path.ismount(dir):
        os.system("mount %s 2>/dev/null" % dir)

def gzopen(file):
    import gzip
    m = open(file)
    magic = m.read(2)
    m.close
    if magic == '\037\213':
         f = gzip.open(file)
    else:
         f = open(file)
    return f

FILENAME_REGEXP = re.compile("^(.*?)_(.)(.*)$")

def getname(file):
    if not os.path.exists(file):
        return file
    name = os.path.splitext(os.path.basename(file))[0]

    if not name:
        # Bugfix for empty stem
        return os.path.basename(file)
    
    name = name[0].upper() + name[1:]
    while FILENAME_REGEXP.match(name):
        m = FILENAME_REGEXP.match(name)
        if m:
            name = m.group(1) + ' ' + m.group(2).upper() + m.group(3)
    if name[-1] == '_':
        name = name[:-1]
    return name


def killall(appname, sig=9):
    '''kills all applications with the string <appname> in their commandline.

    The <sig> parameter indicates the signal to use.
    This implementation uses the /proc filesystem, it might be Linux-dependent.
    '''

    cmdline_filenames = glob.glob('/proc/[0-9]*/cmdline')

    for cmdline_filename in cmdline_filenames:

        try:
            fd = open(cmdline_filename)
            cmdline = fd.read()
            fd.close()
        except IOError:
            continue

        cmdline_args = cmdline.split('\x00')

        for cmdline_arg in cmdline_args:
            if cmdline_arg.find(appname) != -1:
                # Found one, kill it
                pid = int(cmdline_filename.split('/')[2])
                if config.DEBUG:
                    a = sig, pid, ' '.join(cmdline_args)
                    print 'killall: Sending signal %s to pid %s ("%s")' % a
                os.kill(pid, sig)
                break # Done with this process, go on to the next one

    return


 
def resolve_media_mountdir(media_id, file):
    mountdir = None
    full_filename = file
    # Find on what media it is located
    for media in config.REMOVABLE_MEDIA:
        if media_id == media.id:
            # Then set the filename
            mountdir = media.mountdir
            full_filename = os.path.join(media.mountdir, file)
            break

    return mountdir, full_filename

def check_media(media_id):
    for media in config.REMOVABLE_MEDIA:
        if media_id == media.id:
            return media
    return None
