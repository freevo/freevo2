#if 0 /*
# -*- coding: iso-8859-1 -*-
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
# Revision 1.45  2003/08/23 18:33:29  dischi
# add default parameter to getimage
#
# Revision 1.44  2003/08/23 15:15:21  dischi
# add cover searcher
#
# Revision 1.43  2003/08/23 12:51:41  dischi
# removed some old CVS log messages
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


import glob
import os
import statvfs
import string, fnmatch, re
import md5
import Image # PIL
import copy
import cPickle, pickle # pickle because sometimes cPickle doesn't work

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
        # Try and use fchksum if installed
        try:
            import fchksum
            return fchksum.fmd5t(filename)[0]
        except ImportError:
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


def escape(sql):
    """
    Escape a SQL query in a manner suitable for sqlite
    """
    if sql:
        sql = sql.replace('\'','\'\'')
        return sql
    else:
        return 'null'
    
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


mounted_dirs = []

def umount(dir):
    global mounted_dirs
    if os.path.ismount(dir):
        os.system("umount %s" % dir)
        if not os.path.ismount(dir) and dir in mounted_dirs:
            mounted_dirs.remove(dir)


def mount(dir, force=0):
    global mounted_dirs
    if not os.path.ismount(dir):
        os.system("mount %s 2>/dev/null" % dir)
        if os.path.ismount(dir) and not dir in mounted_dirs:
            mounted_dirs.append(dir)
    if force and not dir in mounted_dirs:
        mounted_dirs.append(dir)
        
    
def umount_all():
    global mounted_dirs
    for d in copy.copy(mounted_dirs):
        umount(d)
        
            
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

def getimage(base, default=None):
    if os.path.isfile(base+'.png'):
        return base+'.png'
    if os.path.isfile(base+'.jpg'):
        return base+'.jpg'
    return default


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


def title_case(phrase):
    """
    Return a text string (i.e. from CDDB) with 
    the case normalized into title case.
    This is because people frequently put in ugly
    information, and we can avoid it here'
    """

    s = ''
    for letter in phrase:
        if s and s[-1] == ' ' or s == '':
            s += string.upper(letter)
        elif letter == '_':
                s += ' '
        else:
            s += string.lower(letter)
    return s



 
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

def get_bookmarkfile(filename):
    myfile = os.path.basename(filename) 
    myfile = config.FREEVO_CACHEDIR + "/" + str(myfile) + '.bookmark'
    return myfile


def format_text(text):
    while len(text) and text[0] in (' ', '\t', '\n'):
        text = text[1:]
    text = re.sub('\n[\t *]', ' ', text)
    while len(text) and text[-1] in (' ', '\t', '\n'):
        text = text[:-1]
    return text


def read_pickle(file):
    f = open(file, 'r')
    try:
        data = cPickle.load(f)
    except:
        data = pickle.load(f)
    f.close()
    return data


def save_pickle(data, file):
    f = open(file, 'w')
    cPickle.dump(data, f, 1)
    f.close()


def readfile(filename):
    fd = open(str(filename), 'r')
    ret = fd.readlines()
    fd.close()
    return ret


def list_usb_devices():
    devices = []
    lines = readfile('/proc/bus/usb/devices')
    for line in lines:
        if line[:2] == 'P:':
            devices.append('%s:%s' % (line[11:15], line[23:27]))
    return devices

def freespace(path):
    """
    freespace(path) -> integer
    Return the number of bytes available to the user on the file system
    pointed to by path.
    """
    s = os.statvfs(path)
    return s[statvfs.F_BAVAIL] * long(s[statvfs.F_BSIZE])
        
def smartsort(x,y): # A compare function for use in list.sort()
    """
    Compares strings after stripping off 'The' to be "smarter"
    Also obviously ignores the full path when looking for 'The' 
    """
    m = os.path.basename(x)
    n = os.path.basename(y)
    
    if m.find('The ') == 0:
        m = m.replace('The ','',1)
    if n.find('The ') == 0:
        n = n.replace('The ','',1)

    return cmp(m.upper(),n.upper()) # be case insensitive

def totalspace(path):
    """
    totalspace(path) -> integer
    Return the number of total bytes available on the file system
    pointed to by path.
    """
    s = os.statvfs(path)
    return s[statvfs.F_BLOCKS] * long(s[statvfs.F_BSIZE])
        

def tagmp3 (filename, title=None, artist=None, album=None, track=None, tracktotal=None, year=None):
    """
    use eyeD3 directly from inside mmpython to
    set the tag. We default to 2.3 since even
    though 2.4 is the accepted standard now, more
    players support 2.3
    """
    import mmpython.audio.eyeD3 as eyeD3   # Until mmpython has an interface for this.

    tag = eyeD3.Tag(filename)
    tag.header.setVersion(eyeD3.ID3_V2_3)
    if artist: tag.setArtist(artist)
    if album:  tag.setAlbum(album)
    if title:  tag.setTitle(title)
    if track:  tag.setTrackNum((track,tracktotal))   # eyed3 accepts None for tracktotal
    if year:   tag.setDate(year) 
    tag.update()
    return


def getdatadir(item):
    directory = item.dir
    if item.media:
        directory = directory[len(item.media.mountdir):]
        if len(directory) and directory[0] == '/':
            directory = directory[1:]
        return os.path.join(config.MOVIE_DATA_DIR, 'disc', item.media.id, directory)
    else:
        if len(directory) and directory[0] == '/':
            directory = directory[1:]
        return os.path.join(config.MOVIE_DATA_DIR, directory)

def touch(file):
    fd = open(file,'w+')
    fd.close()
    return 0

def rmrf(top=None):
    """
    Pure python version of 'rm -rf'
    """
    if not top == '/' and not top == '' and not top == ' ' and top:
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(top)

#
# synchronized objects and methods.
# By André Bjärby
# From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65202
# 
from types import *
def _get_method_names (obj):
    if type(obj) == InstanceType:
        return _get_method_names(obj.__class__)
    
    elif type(obj) == ClassType:
        result = []
        for name, func in obj.__dict__.items():
            if type(func) == FunctionType:
                result.append((name, func))

        for base in obj.__bases__:
            result.extend(_get_method_names(base))

        return result


class _SynchronizedMethod:

    def __init__ (self, method, obj, lock):
        self.__method = method
        self.__obj = obj
        self.__lock = lock

    def __call__ (self, *args, **kwargs):
        self.__lock.acquire()
        try:
            #print 'Calling method %s from obj %s' % (self.__method, self.__obj)
            return self.__method(self.__obj, *args, **kwargs)
        finally:
            self.__lock.release()


class SynchronizedObject:
    
    def __init__ (self, obj, ignore=[], lock=None):
        import threading

        self.__methods = {}
        self.__obj = obj
        lock = lock and lock or threading.RLock()
        for name, method in _get_method_names(obj):
            if not name in ignore:
                self.__methods[name] = _SynchronizedMethod(method, obj, lock)

    def __getattr__ (self, name):
        try:
            return self.__methods[name]
        except KeyError:
            return getattr(self.__obj, name)
