#if 0 /*
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# util/dbutil.py - database wrapper
# -----------------------------------------------------------------------
# $Id: dbutil.py,v #
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2004/02/07 13:07:55  dischi
# fix unicode/encoding problem with sqlite
#
# Revision 1.4  2004/02/01 16:58:34  rshortt
# Catch some exceptions probably having to do with bad data.
#
# Revision 1.3  2004/01/18 19:06:00  outlyer
# Add a "commit" function...call it to make sure the insert/updates are
# written to disc.
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

import os, traceback
import config

# helper functions

def tracknum(track):
    """ 
    Extract the track numbers from a mmpython result
    """

    trackno = -1
    trackof = -1

    if track:
        trackno = inti(track.split('/')[0])
        if track.find('/') != -1:
            trackof = inti(track.split('/')[1])
    return (trackno, trackof)    


def escape(sql):
    """
    Escape a SQL query in a manner suitable for sqlite
    """
    if sql:
        sql = sql.replace('\'','\'\'')
        return sql
    else:
        return 'null'

def inti(a):
    ret = 0
    if a:
	try: 
	    ret = int(a)
	except ValueError:
	    traceback.print_exc()
	    ret = 0

    return ret

# defines:
DATABASE = os.path.join(config.FREEVO_CACHEDIR, 'freevo.sqlite')

try:
    import sqlite
except:
    print "Python SQLite not installed!"


class MetaDatabase:
    """ Class for working with the database """
    def __init__(self):
        # Private Variables
        DATABASE = os.path.join(config.FREEVO_CACHEDIR, 'freevo.sqlite')
        self.db = sqlite.connect(DATABASE, client_encoding=config.LOCALE)
        self.cursor = self.db.cursor()

    def runQuery(self,query, close=False):
	try:
            self.cursor.execute(query)
        except TypeError:
            traceback.print_exc()
            return False

        if close:
            # run a single query then close
            result = self.cursor.fetchall()
            self.db.commit()           
            self.db.close()
            return result
        else:
            return self.cursor.fetchall()
        
    def close(self):
        self.db.commit()
        self.db.close()

    def commit(self):
        self.db.commit()

    def checkTable(self,table=None):
        if not table:
            return False
        # verify the table exists
        self.cursor.execute('SELECT name FROM sqlite_master where \
                             name="%s" and type="table"' % table)
        if not self.cursor.fetchone():
            return None
        return table
    

