#if 0 /*
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# util/misc.py - Some Misc Utilities
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.17  2004/01/11 10:56:52  dischi
# Fixes in comingup:
# o do not crash when the recordserver is down
# o show a message when no schedules are set and not nothing
# o make arg optional (why is it there anyway?)
#
# Revision 1.16  2004/01/11 05:59:41  outlyer
# How overcomplicated could I have made something so simple? This is a little
# embarassing. I think this "algorithm" is less dumb.
#
# Revision 1.12  2004/01/01 16:18:11  dischi
# fix crash
#
# Revision 1.11  2003/12/31 16:43:49  dischi
# major speed enhancements
#
# Revision 1.10  2003/12/30 22:30:50  dischi
# major speedup in vfs using
#
# Revision 1.9  2003/12/29 22:31:56  dischi
# no need to check image
#
# Revision 1.8  2003/12/12 19:20:07  dischi
# check images
#
# Revision 1.7  2003/12/10 19:47:12  dischi
# remove unneeded imports
#
# Revision 1.6  2003/11/23 16:57:36  dischi
# move xml help stuff to new fxdparser
#
# Revision 1.5  2003/11/22 20:34:08  dischi
# use new vfs
#
# Revision 1.4  2003/11/08 23:15:42  outlyer
# Hyphenated words and abbreviations should be upper case in a title.
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
import os, sys
import string, re
import copy
import htmlentitydefs


# Configuration file. Determines where to look for AVI/MP3 files, etc
import config
from vfs import abspath as vfs_abspath

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


# Helper function for the md5 routine; we don't want to
# write filenames that aren't in lower ascii so we uhm,
# hexify them.
def hexify(str):
    """
    return the string 'str' as hex string
    """
    hexStr = string.hexdigits
    r = ''
    for ch in str:
        i = ord(ch)
        r = r + hexStr[(i >> 4) & 0xF] + hexStr[i & 0xF]
    return r


def escape(sql):
    """
    Escape a SQL query in a manner suitable for sqlite
    """
    if sql:
        sql = sql.replace('\'','\'\'')
        return sql
    else:
        return 'null'
    


FILENAME_REGEXP = re.compile("^(.*?)_(.)(.*)$")

def getimage(base, default=None):
    """
    return the image base+'.png' or base+'.jpg' if one of them exists.
    If not return the default
    """
    for suffix in ('.png', '.jpg', '.gif'):
        image = vfs_abspath(base+suffix)
        if image:
            return image
    return default


def getname(file):
    """
    make a nicer display name from file
    """
    if not os.path.exists(file):
        return file
    
    name = os.path.basename(file)
    name = name[:name.rfind('.')]
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

    unify_name = re.compile('[^A-Za-z0-9]').sub
    appname = unify_name('', appname)
    
    cmdline_filenames = glob.glob('/proc/[0-9]*/cmdline')

    for cmdline_filename in cmdline_filenames:

        try:
            fd = vfs.open(cmdline_filename)
            cmdline = fd.read()
            fd.close()
        except IOError:
            continue

        if unify_name('', cmdline).find(appname) != -1:
            # Found one, kill it
            pid = int(cmdline_filename.split('/')[2])
            if config.DEBUG:
                a = sig, pid, ' '.join(cmdline.split('\x00'))
                print 'killall: Sending signal %s to pid %s ("%s")' % a
            try:
                os.kill(pid, sig)
            except:
                pass
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
        if s and s[-1] == ' ' or s == '' or s[-1] == '-' or s[-1] == '.':
            s += string.upper(letter)
        elif letter == '_':
                s += ' '
        else:
            s += string.lower(letter)
    return s



 
def get_bookmarkfile(filename):
    myfile = vfs.basename(filename) 
    myfile = config.FREEVO_CACHEDIR + "/" + str(myfile) + '.bookmark'
    return myfile


def format_text(text):
    while len(text) and text[0] in (' ', '\t', '\n'):
        text = text[1:]
    text = re.sub('\n[\t *]', ' ', text)
    while len(text) and text[-1] in (' ', '\t', '\n'):
        text = text[:-1]
    return text


def list_usb_devices():
    devices = []
    fd = open('/proc/bus/usb/devices', 'r')
    for line in fd.readlines():
        if line[:2] == 'P:':
            devices.append('%s:%s' % (line[11:15], line[23:27]))
    fd.close()
    return devices


def smartsort(x,y): # A compare function for use in list.sort()
    """
    Compares strings after stripping off 'The' and 'A' to be 'smarter'
    Also obviously ignores the full path when looking for 'The' and 'A' 
    """
    m = os.path.basename(x)
    n = os.path.basename(y)
    
    for word in ('The', 'A'):
        word += ' '
        if m.find(word) == 0:
            m = m.replace(word, '', 1)
        if n.find(word) == 0:
            n = n.replace(word, '', 1)

    return cmp(m.upper(),n.upper()) # be case insensitive

def tagmp3 (filename, title=None, artist=None, album=None, track=None,
            tracktotal=None, year=None):
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


def encode(str, code):
    try:
        return str.encode(code)
    except UnicodeError:
        result = ''
        for ch in str:
            try:
                result += ch.encode(code)
            except UnicodeError:
                pass
        return result

def htmlenties2txt(string):
    e = copy.deepcopy(htmlentitydefs.entitydefs)
    e['ndash'] = "-";
    e['bull'] = "-";
    e['rsquo'] = "'";
    e['lsquo'] = "`";
    e['hellip'] = '...'

    string = string.encode(config.LOCALE, 'ignore').replace("&#039", "'").\
             replace("&#146;", "'")

    i = 0
    while i < len(string):
        amp = string.find("&", i) # find & as start of entity
        if amp == -1: # not found
            break
        i = amp + 1

        semicolon = string.find(";", amp) # find ; as end of entity
        if string[amp + 1] == "#": # numerical entity like "&#039;"
            entity = string[amp:semicolon+1]
            replacement = str(chr(int(entity[2:-1])))
        else:
            entity = string[amp:semicolon + 1]
            if semicolon - amp > 7:
                continue
            try:
                # the array has mappings like "Uuml" -> "ü"
                replacement = e[entity[1:-1]]
            except KeyError:
                continue
        string = string.replace(entity, replacement)
    #string = string.encode(config.LOCALE, 'ignore')
    return string


# 
# Coming Up for TV schedule
#

def comingup(items=None):
    import tv.record_client as ri
    import time
   
    result = ''

    cachefile = '%s/upsoon' % (config.FREEVO_CACHEDIR)
    if (os.path.exists(cachefile) and \
        (abs(time.time() - os.path.getmtime(cachefile)) < 3600)):
        cache = open(cachefile,'r')
        for a in cache.readlines():
            result = result + a
        cache.close()
        return result

    (status, recordings) = ri.getScheduledRecordings()

    if not status:
        result = _('The recordserver is down')
        return result

    progs = recordings.getProgramList()

    f = lambda a, b: cmp(a.start, b.start)
    progl = progs.values()
    progl.sort(f)

    today = []
    tomorrow = []
    later = []

    for what in progl:
        if time.localtime(what.start)[2] == time.localtime()[2]:
            today.append(what)
        if time.localtime(what.start)[2] == (time.localtime()[2] + 1):
            tomorrow.append(what)
        if time.localtime(what.start)[2] > (time.localtime()[2] + 1):
            later.append(what)


    if len(today) > 0:
        result = result + 'Today:\n'
        for m in today:
            sub_title = ''
            if m.sub_title:
                sub_title = ' "' + m.sub_title + '" '
            result = result + " " + str(m.title) + str(sub_title) + " at " + \
                str(time.strftime('%I:%M%p',time.localtime(m.start))) + '\n'

    if len(tomorrow) > 0:
        result = result + 'Tomorrow:\n'
        for m in tomorrow:
            sub_title = ''
            if m.sub_title:
                sub_title = ' "' + m.sub_title + '" '
            result = result + " " + str(m.title) + str(sub_title) + " at " + \
                str(time.strftime('%I:%M%p',time.localtime(m.start))) + '\n'
           
    if len(later) > 0:
        for m in later:
            sub_title = ''
            if m.sub_title:
                sub_title = ' "' + m.sub_title + '" '
            result = result + " " + str(m.title) + str(sub_title) + " at " + \
                str(time.strftime('%I:%M%p',time.localtime(m.start))) + '\n'

    if not result:
        result = _('No recordings are scheduled')
        
    cache = open(cachefile,'w')
    cache.write(result)
    cache.close()

    return result



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

