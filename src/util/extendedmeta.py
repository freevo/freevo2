#if 0 /*
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# extendedmeta.py - database wrapper
# -----------------------------------------------------------------------
# $Id: extendedmeta.py,v #
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
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
import os,string,fnmatch,sys

# The DB stuff
import sqlite

# Metadata tools
import mmpython
import config, util
import util.fxdparser

from util.dbutil import *
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

    print "Adding %s to %s ..." % (path, dirtitle)

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

class AudioParser:
    def __init__(self, dirname):

        # cache dir first
        mmpython.cache_dir(dirname)

        self.artist = ''
        self.album  = ''
        self.year   = ''
        self.length = 0
        for subdir in util.getdirnames(dirname):
            d = AudioParser(subdir)
            if d.artist:
                if self.artist and d.artist != self.artist:
                    self.artist = 'Various'
                elif not self.artist:
                    self.artist = d.artist
            if d.album:
                if self.album and d.album != self.album:
                    self.album = 'Various'
                elif not self.album:
                    self.album = d.album
            if d.year:
                if self.year and d.year != self.year:
                    self.year = 'Various'
                elif not self.year:
                    self.year = d.year
            self.length += d.length

        for song in util.match_files(dirname, config.AUDIO_SUFFIX):
            try:
                data = mmpython.parse(song)
                myartist = data['artist']
                myalbum  = data['album']
                myyear   = data['date']
                if myartist:
                    if myartist != self.artist and self.artist:
                        self.artist = 'Various'
                    else:
                        self.artist = myartist

                if myyear:
                    if myyear != self.year and self.year:
                        self.year = 'Various'
                    else:
                        self.year = myyear


                if myalbum:
                    if myalbum != self.album and self.album:
                        self.album = 'Various'
                    else:
                        self.album = myalbum

                self.length += data['length']
            except:
                pass

        if not self.length:
            return
        
        if config.DEBUG:
            print dirname
            if self.artist:
                print self.artist
            if self.album:
                print self.album
            if self.length > 3600:
                print '%i:%0.2i:%0.2i' % (int(self.length/3600),
                                          int((self.length%3600)/60),
                                          int(self.length%60))
            else:
                print '%i:%0.2i' % (int(self.length/60), int(self.length%60))
            print

        fxd = util.fxdparser.FXD(os.path.join(dirname, 'folder.fxd'))
        fxd.set_handler('folder', self.fxd_callback, mode='w', force=True)
        try:
            fxd.save()
        except IOError:
            # New file
            print "IOError:"
            pass



    def fxd_callback(self, fxd, node):
        # FIXME: fxd.setattr(node, 'title', 'foo')
        info = fxd.get_or_create_child(node, 'info')

        for var in ('artist', 'album', 'length', 'year'):
            if getattr(self, var):
                try:
                    x = str(getattr(self, var)).encode(config.LOCALE, 'ignore')
                    fxd.get_or_create_child(info, var).first_cdata = x
                except UnicodeDecodeError, IOError:
                    pass
    

##### Helper to do all of them

def AddExtendedMeta(path):
    AudioParser(path)
    extract_image(path)
    addPathDB(path)





