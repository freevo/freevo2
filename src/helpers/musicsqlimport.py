#!/usr/bin/env python
#if 0 /*
# -----------------------------------------------------------------------
# musicsqlimport.py - import all music files into sql database
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/08/23 12:51:42  dischi
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

# The basics
import os,string,fnmatch,sys

# The DB stuff
import sqlite

# Metadata tools
import mmpython

import config, util

CACHEDIR = config.FREEVO_CACHEDIR
DBFILE  ='freevo.sqlite'

DATABASE = os.path.join(config.FREEVO_CACHEDIR, DBFILE)
mmpython.use_cache('%s/mmpython' % (config.FREEVO_CACHEDIR))

# Utility functions

def inti(a):
    if a:
        return int(a)
    else:
        return 0

def check_db():
    # verify the database exists
    if not os.path.exists(DATABASE):
        return None
    # verify the table exists
    db = sqlite.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute('SELECT name FROM sqlite_master where name="music" and type="table"')
    if not cursor.fetchone()[0] == 'music':
        return None
    return DATABASE

def create_db():
    db = sqlite.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute("CREATE TABLE music (id INTEGER PRIMARY KEY, dirtitle VARCHAR(255), md5 VARCHAR(32) UNIQUE, path VARCHAR(255), filename VARCHAR(255), type VARCHAR(3), artist VARCHAR(255), title VARCHAR(255), album VARCHAR(255), year VARCHAR(255), track NUMERIC(3), track_total NUMERIC(3), bpm NUMERIC(3), last_play float, play_count NUMERIC, start_time NUMERIC, end_time NUMERIC, rating NUMERIC, eq  VARCHAR)")
    db.commit()
    db.close()

def make_query(filename,dirtitle):
    md5 = 'null'

    if not os.path.exists(filename):
        print "File %s does not exist" % (filename)
        return None

    mmpython.cache_dir(os.path.dirname(filename))

    a = mmpython.parse(filename)

    md5 = util.md5file(filename)

    # This is ugly, how do I clean it up?
    trackno = -1
    trackof = -1


    if a['trackno']:
        trackno = inti(a['trackno'].split('/')[0])
        if a['trackno'].find('/') != -1:
            trackof = inti(a['trackno'].split('/')[1])

    VALUES = "(null,\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',%i,%i,%i,\'%s\',%f,%i,\'%s\',\'%s\',%i,\'%s\')" \
        % (util.escape(dirtitle),md5,util.escape(os.path.dirname(filename)),util.escape(os.path.basename(filename)), \
           'mp3',util.escape(a['artist']),util.escape(a['title']),util.escape(a['album']),inti(a['date']),trackno, \
           trackof, 100,0,0,'0',inti(a['length']),0,'null')

    SQL = 'INSERT OR IGNORE INTO music VALUES ' + VALUES

    return SQL

def mainloop(path='/media/Music',dirtitle='',type='*.mp3'):

    db = sqlite.connect(DATABASE,autocommit=0)
    cursor = db.cursor()

    songs = util.recursefolders(path,1,type,1)

    cursor.execute('SELECT path, filename FROM music')
    count = 0
    for row in cursor.fetchall():
        try:
            songs.remove(os.path.join(row['path'],row['filename']))
            count = count + 1
        except ValueError:
            # Why doesn't it just give a return code
            pass
  
    if count > 0:
        print "Skipped %i songs already in the database..." % (count)

    tempvar = ''
    for song in songs:
        cursor.execute(make_query(song,dirtitle))

    # Only call commit after we're done to save time...
    # (autocommit slows down the db dramatically)
    db.commit()
    db.close()




if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1] == '--help':
        print 'Freevo musicsqlimport helper'
        print 'adds all mp3 files into the database'
        sys.exit(0)
        
    if not check_db():
        print "Creating data file..."
        create_db()

    if len(sys.argv) > 1:
        print "Adding %s to %s..." % (sys.argv[1],config.DIR_AUDIO[0][0])
        mainloop(sys.argv[1],config.DIR_AUDIO[0][0])
    else:
        print "Populating Database with entries"
        for dir in config.DIR_AUDIO:
            print "Scanning %s" % dir[0]
            mainloop(dir[1],dir[0])
