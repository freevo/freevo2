#!/usr/bin/env python
#if 0 /*
# -----------------------------------------------------------------------
# makeplaylist.py - create a playlist from the sqlite database
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# A little program to demonstrate what can be done with sqlite
# It only outputs static playlists in .m3u format now, but you can
# see what can be done.
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
#
# Revision 1.1  2003/08/23 09:09:18  dischi
# moved some helpers to src/helpers
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


import sqlite
import os, sys
import config, util
import musicsqlimport as fdb


base = 'SELECT path, filename FROM music ' 

topten = base + 'ORDER BY play_count DESC'
notrecent = base + 'ORDER BY last_play'
nineties = base + 'WHERE year like "199%"'
oldsongs = base + 'WHERE year < 1990'

queries =  [('Favourite Songs (Most Played)',topten),
         ('Songs not listened to in awhile', notrecent),
         ('Songs from the 1990s',nineties),
         ('Songs before the 1990s',oldsongs) ]


if __name__ == '__main__':
    if not fdb.check_db():
        print "Database missing or empty, please run 'freevo musicsqlimport'"
        print "before running this program"
        sys.exit(1)
    
    if not len(sys.argv) > 1 or sys.argv[1] == '--help':
        print 'Usage: '
        print '\tfreevo makeplaylist <query type> <number of songs> <output m3u file>'
        print
        print '\tThe following queries are available.'
        print
        m = 0
        for query in queries:
            print '\t%i - %s' % (m, query[0])
            m = m + 1
    else:
        output = None
        db = sqlite.connect(fdb.DATABASE,autocommit=0)
        cursor = db.cursor()
        #cursor.execute(queries[sys.argv[1]][1])
        q = int(sys.argv[1])
        sql = queries[q][1]
        if len(sys.argv) > 2:
            sql = sql +  ' LIMIT %i' % (int(sys.argv[2]))

        if len(sys.argv) > 3:
            # write to file or stdout?
            output = '%s.m3u' % (sys.argv[3])
            print "Writing to output file: %s..." % (output)
            f = open(output,'w+')


        cursor.execute(sql)
        for row in cursor.fetchall():
            line = os.path.join(row['path'],row['filename'])
            if output: 
                f.write(line+'\n')
            else: 
                print line
