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
# Revision 1.8  2005/07/02 16:46:27  dischi
# use kaa.metadata instead of mmpython
#
# Revision 1.7  2005/06/25 08:52:29  dischi
# switch to new style python classes
#
# Revision 1.6  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.5  2004/02/07 13:07:55  dischi
# fix unicode/encoding problem with sqlite
#
# Revision 1.4  2004/02/01 16:58:34  rshortt
# Catch some exceptions probably having to do with bad data.
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


import os, traceback
import config

# helper functions

def tracknum(track):
    """ 
    Extract the track numbers from a kaa.metadata result
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


class MetaDatabase(object):
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
    

