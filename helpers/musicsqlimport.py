#!/usr/bin/env python

# The basics
import os,string,fnmatch,sys

# The DB stuff
import sqlite

# Metadata tools
import mmpython,fchksum

sys.path.append('./src/')
import config, util

CACHEDIR = config.FREEVO_CACHEDIR
DBFILE  ='freevo.sqlite'
DATABASE = CACHEDIR +"/" + DBFILE

# Utility functions

def inti(a):
    if a:
        return int(a)
    else:
        return 0

def escape(sql):
    if sql:
        sql = sql.replace('\'','\'\'')
        return sql
    return 'null'

# Only call once... how do we check if the tables exist?


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
    cursor.execute("CREATE TABLE music (id INTEGER PRIMARY KEY, dirtitle VARCHAR(255), md5 VARCHAR(32) UNIQUE, path VARCHAR(255), filename VARCHAR(255), type VARCHAR(3), artist VARCHAR(255), title VARCHAR(255), album VARCHAR(255), year VARCHAR(255), track NUMERIC(3), track_total NUMERIC(3), bpm NUMERIC(3), last_play float, play_count NUMERIC, start_time VARCHAR, end_time VARCHAR, rating NUMERIC, eq  VARCHAR)")
    db.commit()
    db.close()

def make_query(filename,dirtitle):
    md5 = 'null'

    if not os.path.exists(filename):
        print "File %s does not exist" % (filename)
        return None
    
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
        % (escape(dirtitle),md5,escape(os.path.dirname(filename)),escape(os.path.basename(filename)), \
           'mp3',escape(a['artist']),escape(a['title']),escape(a['album']),inti(a['date']),trackno, \
           trackof, 100,0,0,'0','262',0,'null')

    SQL = 'INSERT OR IGNORE INTO music VALUES ' + VALUES

    return SQL

def mainloop(path='/media/Music',dirtitle='',type='*.mp3'):

    db = sqlite.connect(DATABASE,autocommit=0)
    cursor = db.cursor()

    songs = util.recursefolders(path,1,type,1)
    tempvar = ''
    for song in songs:
        cursor.execute(make_query(song,dirtitle))

    # Only call commit after we're done to save time... (autocommit slows down the db dramatically)
    db.commit()
    db.close()

if __name__ == '__main__':
    if not check_db():
        print "Creating data file..."
        create_db()
    print "Populating Database with entries"
    for dir in config.DIR_AUDIO:
        print "Scanning %s" % dir[0]
        mainloop(dir[1],dir[0])
