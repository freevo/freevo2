#if 0 /*
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# extendedmeta.py - Extended Metadata Reader/Cacher
# -----------------------------------------------------------------------
# $Id: extendedmeta.py,v #
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/01/16 17:15:29  dischi
# Many improvements to AudioParser
# o try to detect if we should overwrite an existing fxd file
# o Various is not included anymore, the value is not set in the fxd
#   Aubin: the skin now doesn't need to check for 'Various', it needs
#   to write 'Various' if Album/Artist is not set
# o make it much faster by comparing timestamps to avoid rechecking
#
# Warning: I made the changes to mp3info which was removed while I was
# working. I hope I didn't forgot something to copy
#
# Also made the db optional
#
# Revision 1.2  2004/01/16 14:40:33  outlyer
# (Don't you love it when your neighbours make enough noise to wake you up
# early on your day off)
#
# Just some fixes from the code I commited last night.
#
# o Use the proper db instead of my test db
# o use md5
# o Remove some unnecessary 'print'
# o remove mp3.py and smartimage.py as they are both merged into extendedmeta
# o Remove musicsqlimport as it's all being done in extendedadd.py now.
#
# Revision 1.1  2004/01/16 08:14:04  outlyer
# Forgot to commit this earlier. This is:
#
# extendedmeta: Parser for embedded covers, folder cache, and sqlite scoring
# dbutil:       Helper class for dealing with the sqlite db
# extendedadd:  A tool which calls the extendedmeta functions on a path, an
#               example of how to add all three types of data from the
#               command-line. Since the data is already used in blurr2, and
#               the info skins, it's nice to have.
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

# The basics
import os,string,fnmatch,sys,md5,stat

# Metadata tools
import mmpython
import config, util
import util.fxdparser

try:
    # The DB stuff
    import sqlite

    from util.dbutil import *
    has_db = True
except ImportError:
    has_db = False
    
from mmpython.audio import eyeD3
from util import recursefolders

mmcache = '%s/mmpython' % ('/var/cache/freevo')
mmpython.use_cache(mmcache)

if mmpython.object_cache and hasattr(mmpython.object_cache, 'md5_cachedir'):
    mmpython.object_cache.md5_cachedir = False
    mmpython.object_cache.cachedir     = config.OVERLAY_DIR

##### Database

dbschema = """CREATE TABLE music (id INTEGER PRIMARY KEY, dirtitle VARCHAR(255), path VARCHAR(255), 
        filename VARCHAR(255), type VARCHAR(3), artist VARCHAR(255), title VARCHAR(255), album VARCHAR(255), 
        year VARCHAR(255), track NUMERIC(3), track_total NUMERIC(3), bpm NUMERIC(3), last_play float, 
        play_count NUMERIC, start_time NUMERIC, end_time NUMERIC, rating NUMERIC, eq  VARCHAR)"""

def make_query(filename,dirtitle):
    if not os.path.exists(filename):
        print "File %s does not exist" % (filename)
        return None

    mmpython.cache_dir(os.path.dirname(filename))

    a = mmpython.parse(filename)
    t = tracknum(a['trackno'])

    VALUES = "(null,\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',%i,%i,%i,\'%s\',%f,%i,\'%s\',\'%s\',%i,\'%s\')" \
        % (util.escape(dirtitle),util.escape(os.path.dirname(filename)),util.escape(os.path.basename(filename)), \
           'mp3',util.escape(a['artist']),util.escape(a['title']),util.escape(a['album']),inti(a['date']),t[0], \
           t[1], 100,0,0,'0',inti(a['length']),0,'null')

    SQL = 'INSERT OR IGNORE INTO music VALUES ' + VALUES
    return SQL

def addPathDB(path='/media/Music',dirtitle=config.AUDIO_ITEMS[0][0],type='*.mp3'):

    # Get some stuff ready
    count = 0
    db = MetaDatabase();
    if not db.checkTable('music'): 
        db.runQuery(dbschema)

    # Compare and contrast the db to the disc
    songs = util.recursefolders(path,1,type,1)
    for row in db.runQuery('SELECT path, filename FROM music'):
        try:
            songs.remove(os.path.join(row['path'],row['filename']))
            count = count + 1
        except ValueError:
            # Why doesn't it just give a return code
            pass
  
    if count > 0: print "Skipped %i songs already in the database..." % (count)

    for song in songs:
        db.runQuery(make_query(song,dirtitle))
    db.close()


##### Images

def get_md5(obj):
    m = md5.new()
    if isinstance(obj,file):     # file
        for line in obj.readlines():
            m.update(line)
        return m.digest()
    else:                        # str
        m.update(obj)
        return m.digest()

def extract_image(path):
    songs = util.recursefolders(path, pattern='*.mp3',recurse=0)
    name = 'cover.jpg'
    for i in songs:
        id3 = eyeD3.Mp3AudioFile( i )
        path = os.path.dirname(i)
        myname = os.path.join(path,name)
        if id3.tag:
            images = id3.tag.getImages();
            for img in images:
                if vfs.isfile(myname) and (get_md5(vfs.open(myname,'rb')) == get_md5(img.imageData)):
                    # Image already there and has identical md5, skip
                    pass 
                elif not vfs.isfile(myname):
                    f = vfs.open(myname, "wb")
                    f.write(img.imageData)
                    f.flush()
                    f.close()
                else:
                    # image exists, but sums are different, write a unique cover
                    myname = os.path.join(path,os.path.splitext(os.path.basename(i))[0]+'.jpg')
                    f = vfs.open(myname, "wb")
                    f.write(img.imageData)
                    f.flush()
                    f.close()
     

##### Audio Folder Information

various = '__various__'

class AudioParser:

    def __init__(self, dirname, force=False):

        self.artist  = ''
        self.album   = ''
        self.year    = ''
        self.length  = 0
        self.changed = False
        self.force   = force
        
        fxdfile      = os.path.join(dirname, 'folder.fxd')
        fname        = vfs.abspath(fxdfile)
        if fname:
            fxdfile  = fname
        subdirs      = util.getdirnames(dirname, softlinks=False)
        filelist     = None

        for subdir in subdirs:
            d = AudioParser(subdir)
            if d.changed:
                break

        else:
            # no changes in all subdirs, looks good
            if fname:
                if os.stat(dirname)[stat.ST_MTIME] <= os.stat(fname)[stat.ST_MTIME]:
                    # and no changes in here. Do not parse everything again
                    if force:
                        # forces? We need to load our current values
                        fxd = util.fxdparser.FXD(fxdfile)
                        fxd.set_handler('folder', self.fxd_read)
                        fxd.parse()
                        if self.length:
                            # set the stuff to various if not set
                            for type in ('artist', 'album', 'year'):
                                if not getattr(self, type):
                                    setattr(self, type, various)
                    return
            else:
                filelist = util.match_files(dirname, config.AUDIO_SUFFIX)
                if not filelist:
                    # no files in here, great
                    return

        if not filelist:
            filelist = util.match_files(dirname, config.AUDIO_SUFFIX)
            
        # ok, something changed here, too bad :-(
        self.changed = True
        self.force   = False

        # scan all subdirs
        for subdir in subdirs:
            d = AudioParser(subdir, force=True)
            for type in ('artist', 'album', 'year'):
                setattr(self, type, self.strcmp(getattr(self, type), getattr(d, type)))
            self.length += d.length

        # cache dir first
        mmpython.cache_dir(dirname)

        for song in filelist:
            try:
                data = mmpython.parse(song)
                for type in ('artist', 'album'):
                    setattr(self, type, self.strcmp(getattr(self, type), data[type]))
                self.year = self.strcmp(self.year, data['date'])
                if data['length']:
                    self.length += int(data['length'])
            except:
                pass

        if not self.length:
            return
        
        fxd = util.fxdparser.FXD(fxdfile)
        fxd.set_handler('folder', self.fxd_read)
        fxd.parse()

        if config.DEBUG:
            print dirname
            if self.artist:
                print self.artist
            if self.album:
                print self.album
            if self.year:
                print self.year
            if self.length > 3600:
                print '%i:%0.2i:%0.2i' % (int(self.length/3600),
                                          int((self.length%3600)/60),
                                          int(self.length%60))
            else:
                print '%i:%0.2i' % (int(self.length/60), int(self.length%60))
            print

        fxd.set_handler('folder', self.fxd_callback, mode='w', force=True)
        try:
            fxd.save()
        except IOError, e:
            print e


    def strcmp(self, s1, s2):
        if not s1 or not s2:
            return s1 or s2
        if s1 == various or s2 == various:
            return various
        # print 'cmp: %s %s ' % ( s1, s2)
        if s1.replace(' ', '').lower() == s2.replace(' ', '').lower():
            return s1
        return various


    def fxd_read(self, fxd, node):
        info = []
        for child in fxd.get_children(node, 'info'):
            info += child.children

        overwrite = True
        for child in info:
            if child.name == 'length':
                if self.force:
                    # in force mode
                    self.length = int(fxd.gettext(child))
                elif str(fxd.gettext(child)) == str(self.length):
                    overwrite = False

        for child in info:
            if child.name in ('artist', 'album', 'year'):
                var = fxd.gettext(child)
                # if the var is not set, continue
                if not var:
                    continue
                # fxd value is set, let's see what we have here now:
                # 1. not overwrite, return fxd value
                # 2. current value is various, return various
                # 3. current value is nothing, return fxd value
                # 4. current and fxd value are something, return fxd value
                if not (overwrite and getattr(self, child.name) == various):
                    setattr(self, child.name, var)


    def fxd_callback(self, fxd, node):
        info = fxd.get_or_create_child(node, 'info')

        for var in ('artist', 'album', 'length', 'year'):
            if getattr(self, var) and str(getattr(self, var)) != various:
                fxd.get_or_create_child(info, var).first_cdata = str(getattr(self, var))
            else:
                for child in info.children:
                    if child.name == var:
                        info.children.remove(child)

    

##### Helper to do all of them

def AddExtendedMeta(path):
    AudioParser(path)
    extract_image(path)
    if has_db:
        addPathDB(path)
