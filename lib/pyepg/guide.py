# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# guide.py - This contains EPGDB which is the pyepg interface to the 
#            database.
# -----------------------------------------------------------------------
# $Id$#
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.10  2004/11/27 15:00:37  dischi
# create db if missing
#
# Revision 1.9  2004/11/27 02:22:38  rshortt
# -Some verbose prints for debug.
# -Debugging and changes to add_program().
# -Impliment add_data_vdr() which uses vdrpylib to get guide info from VDR.
#  This is still full of debug and is a work in progress but its working
#  well at this point.  You can find vdrpylib at http://vdrpylib.sf.net/ and
#  a CVS snapshot is available:  http://vdrpylib.sf.net/vdrpylib-20041126.tar.gz
#
# Revision 1.8  2004/11/19 19:03:29  dischi
# add get_program_by_id
#
# Revision 1.7  2004/11/13 16:10:21  dischi
# replace compat.py and config.py with a sysconfig variante
#
# Revision 1.6  2004/11/12 20:40:36  dischi
# support program get from all channels
#
# Revision 1.5  2004/10/23 16:20:07  rshortt
# Comment out a sometimes spammy debug.
#
# Revision 1.4  2004/10/23 14:29:35  rshortt
# Updates and bugfixes.  Please excuse the mass of commented code and debug.
#
# Revision 1.3  2004/10/20 01:06:30  rshortt
# Unicode changes.
#
# Revision 1.2  2004/10/18 01:04:01  rshortt
# Rework pyepg to use an sqlite database instead of an object pickle.
# The EPGDB class is the primary interface to the databse, wrapping database
# queries in method calls.
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

import os
import traceback
import time
from types import *

try:
    # Freevo sysconfig import
    import sysconfig
except:
    # Fallback for stand alone epg usage
    import config


def escape_query(sql):
    """
    Escape a SQL query in a manner suitable for sqlite
    """
    if not type(sql) in StringTypes:
        return sql

    # sql = sql.replace('\'','\'\'')
    sql = sql.replace('\'','')
    return sql


def escape_value(val):
    """
    Escape a SQL value in a manner to be quoted inside a query
    """ 
    # print 'RLS: val1 - %s' % val
    if not type(val) in StringTypes:
        # print 'RLS: val not StringType'
        return val

    val = val.replace('"', '')
    val = val.replace('\'', '')
    # print 'RLS: val2 - %s' % val
    return val


def inti(a):
    ret = 0
    if a:
	try: 
	    ret = int(a)
	except ValueError:
	    traceback.print_exc()
	    ret = 0

    return ret


try:
    import sqlite
except:
    print "Python SQLite not installed!"

from sqlite import IntegrityError


class EPGDB:
    """ 
    Class for working with the EPG database 
    """

    def __init__(self, dbpath):
        if not os.path.isfile(dbpath):
            print 'epg database missing, creating it'
            scheme = os.path.join(os.path.dirname(__file__), 'epg_schema.sql')
            os.system('sqlite %s < %s 2>/dev/null >/dev/null' % (dbpath, scheme))
            print 'done'
            
        self.db = sqlite.connect(dbpath, client_encoding='utf-8', timeout=10)
        self.cursor = self.db.cursor()


    def execute(self, query, close=False):
        query = escape_query(query)

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
        self.cursor.execute('select name from sqlite_master where \
                             name="%s" and type="table"' % table)
        if not self.cursor.fetchone():
            return None
        return table


    def add_channel(self, id, call_sign, tuner_id):
        query = 'insert or replace into channels (id, call_sign, tuner_id) \
                 values ("%s", "%s", "%s")' % (id, call_sign, tuner_id)

        self.execute(query)
        self.commit()
                

    def get_channel(self, id):
        query = 'select * from channels where id="%s' % id

        channel = self.execute(query)
        if len(channel):
            return channel[0]


    def get_channels(self):
        query = 'select * from channels'

        rows = self.execute(query)
        return rows


    def remove_channel(self, id):
        query = 'delete from channels where id="%s' % id

        self.execute(query)
        self.commit()


    def get_channel_ids(self):
        id_list = []
        query = 'select id from channels'

        rows = self.execute(query)
        for row in rows: 
            id_list.append(row.id)

        return id_list


    def add_program(self, channel_id, title, start, stop, subtitle='', 
                    description='', episode=''):
        now = time.time()
        title = escape_value(title)
        subtitle = escape_value(subtitle)
        description = escape_value(description)
        # print 'DESC: %s' % description
        episode = escape_value(episode)

        old_prog = None

        del_list = []

        #print 'add_program step 1: %f' % float(time.time()-now)
        rows = self.execute('select * from programs where channel_id="%s" \
                            and start=%s' % (channel_id, start))
        #print 'add_program step 2: %f, %d rows' % (float(time.time()-now), len(rows))

        if len(rows) > 1:
            # With the current schema this should NOT be possible.  If we stay
            # with it this may be removed.
            #
            # Bad. We should only have one program for each chanid:start
            # Lets end this right here.
            #rows = self.execute('select id from programs where channel_id="%s" \
            #                     and start=%s' % (channel_id, start))

            # print 'RLS: add_program got %d rows - should delete' % len(rows)
            for row in rows:
                del_list.append(row.id)

            self.remove_programs(del_list)

        elif len(rows) == 1:
            old_prog = rows[0]

        else:
            # we got no results
            pass


        if old_prog:
            if old_prog['title'] == title:
                # program timeslot is unchanged, see if there's anything
                # that we should update
                if old_prog['subtitle'] != subtitle:
                    print 'different subtitles: %s - %s' % (String(old_prog['subtitle']), String(subtitle))
                    self.execute('update programs set subtitle="%s" where id=%d' % (subtitle, old_prog.id))
                    self.commit()
                if old_prog['description'] != description:
                    print 'different descs: %s - %s' % (String(old_prog['description']), String(description))
                    self.execute('update programs set description="%s" where id=%d' % (description, old_prog.id))
                    self.commit()
                if old_prog['episode'] != episode:
                    print 'different episodes: %s - %s' % (String(old_prog['episode']), String(episode))
                    self.execute('update programs set episode="%s" where id=%d' % (episode, old_prog.id))
                    self.commit()
    
                #print 'add_program step 3 (replace) took %f' % float(time.time()-now)
                return

            else:
                print 'different titles: %s - %s' % (String(old_prog.title), String(title))
                # old prog and new prog have same times but different title,
                # this is probably a schedule change, remove the old one
                # TODO: check for shifting times and program overlaps

                #print 'add_program step 4: %f' % float(time.time()-now)
                print 'got old_prog with different title: %s - %s' % \
                      (String(old_prog['title']), String(title))
                self.remove_program(old_prog['id'])

        #
        # If we made it here there's no identical program in the table 
        # to modify.
        #

        # TODO:
        # Delete any entries of the same program title on the same channel 
        # within 10 minues of the start time to somewhat compensate for
        # shifting times.
        # self.execute('delete from programs where channel_id="%s" and \
        #               title="%s" and abs(%s-start)<=600' % \
        #               (channel_id, title, start))
        #for row in res:
        #    if del_list.index(row[0]) >= 0: continue
        #    del_list.append(row[0])
        #self.remove_programs(del_list)


        #
        # If we got this far all we need to do now is insert a new
        # program row.
        #
        #print 'add_program step 5 took %f' % float(time.time()-now)

        query = 'insert into programs (channel_id, title, start, stop, \
                                       subtitle, episode, description) \
                 values ("%s", "%s", %s, %s, "%s", "%s", "%s")' % \
                        (channel_id, title, start, stop, 
                         subtitle, episode, description)

        try:
            self.execute(query)
            self.commit()
        except IntegrityError:
            print 'Program for (%s, %s) exists:' % (String(channel_id), start)
            rows = self.execute('select * from programs where channel_id="%s" \
                                 and start=%s' % (channel_id, start))
            for row in rows:
                print '    %s' % row
            traceback.print_exc()
            
        #print 'add_program step 6 took %f' % float(time.time()-now)
                

    def get_programs(self, channels, start=0, stop=-1):
        # print 'RLS: get_programs(%s,%d,%d)' % (channels, start, stop)
        if not start:
            start = time.time()

        if channels:
            if type(channels) != ListType:
                channels = [ channels, ]

            query = 'select * from programs where'
            for c in channels:
                query = '%s channel_id="%s"' % (query, c)
                if channels.index(c) < len(channels)-1: 
                    query = '%s or' % query
            query = '%s and' % query
        else:
            query = 'select * from programs where'
            
        if stop == 0:
            # only get what's running at time start
            query = '%s start<=%d and stop>%d' % (query, start, start)
        elif stop == -1:
            # get everything from time start onwards
            query = '%s ((start<=%d and stop>%d) or start>%d)' % \
                    (query, start, start, start)
        elif stop > 0:
            # get everything from time start to time stop
            query = '%s ((start<=%d and stop>%d) or \
                             (start>%d and stop<%d) or \
                             (start<%d and stop>=%d))' % \
                    (query, start, start, start, stop, stop, stop)
        else:
            return []

        return self.execute('%s order by start' % query)


    def get_programs_by_id(self, id):
        query = 'select * from programs where id="%s"' % id
        result = self.execute(query)
        if result:
            return result[0]
        return []


    def remove_program(self, id):
        query = 'delete from programs where id=%d' % id

        print 'REMOVE: %s' % escape_query(query)
        self.execute(query)
        self.commit()


    def remove_programs(self, ids):
        query = 'delete from programs where'
        for id in ids:
            query = '%s id=%d' % id
            if ids.index(id) < len(ids)-1: 
                query = '%s or' % query

        print 'REMOVE: %s' % escape_query(query)
        self.execute(query)
        self.commit()


    def search_programs(self, subs, by_chan=None):
        now = time.time()
        clause = 'where stop > %d' % now
        if by_chan:
            clause = '%s and channel_id="%s"' % (clause, by_chan)

        clause = '%s and title like "%%%s%%"' % (clause, subs)

        query = 'select * from programs %s order by channel_id, start' % clause
        # print 'QUERY: %s' % query
        rows = self.execute(query)

        return rows


    # XXX: Should we add a generic load() with a parser argument like before?

    def add_data_xmltv(self, xmltv_file, verbose=1):
        import xmltv
        xmltv.load_guide(self, xmltv_file, verbose=verbose)

        return True


    def add_data_dd(self, dd_file):
        return False


    def add_data_vdr(self, epg_file=None, host=None, port=None):
        try:
            import vdr.vdr
        except:
            print 'vdrpylib is not installed:'
            print 'http://sourceforge.net/projects/vdrpylib/'

        print 'pyepg epgfile1 is %s' % epg_file
        if os.path.isfile(epg_file):
            (vdr_dir, epg_file) = os.path.split(epg_file)
            vdr = vdr.vdr.VDR(epgfile=epg_file, videopath=vdr_dir)
            print 'pyepg epgfile is %s' % vdr.epgfile
            epg = vdr.readepg()
            chans = vdr.channels.values()
            for c in chans:
                # print '%s has %d events' % (c.__str__(), len(c.events))
                print 'Adding channel: %s' % c.id
                self.add_channel(c.id, c.name, c.rid)
                for e in c.events:
                    subtitle = e.subtitle
                    if not subtitle: subtitle = ''
                    desc = e.desc
                    if not desc: desc = ''
       
                    self.add_program(c.id, e.title, e.start, int(e.start+e.dur),
                                     subtitle=subtitle, description=desc)


        elif host and port:
            # ss = s.SVDRP(host='localhost')
            print 'VDR EPG from SVDRP not yet implimented.'
            return False
        else:
            print 'No source for VDR EPG.'
            return False




