#!/usr/bin/env python
#
# A little program to demonstrate what can be done with sqlite
# It only outputs static playlists in .m3u format now, but you can
# see what can be done.
#
import sqlite
import os, sys
sys.path.append('./src/')
sys.path.append('./helpers/')
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
        print "Database missing or empty, please run ./helpers/musicsqlimport.py"
        print "before running this program"
        sys.exit(1)
    
    if not len(sys.argv) > 1:
        print 'Usage: '
        print '\t%s <query type> <number of songs> <output m3u file>' % sys.argv[0]
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
