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


class EPGDB:
    """ 
    Class for working with the EPG database 
    """

    def __init__(self, dbpath):
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
        title = escape_value(title)
        subtitle = escape_value(subtitle)
        description = escape_value(description)
        # print 'DESC: %s' % description
        episode = escape_value(episode)

        old_prog = None

        del_list = []

        rows = self.execute('select * from programs where channel_id="%s" \
                            and start=%s' % (channel_id, start))

        if len(rows) > 1:
            # Bad. We should only have one program for each chanid:start
            # Lets end this right here.
            #rows = self.execute('select id from programs where channel_id="%s" \
            #                     and start=%s' % (channel_id, start))

            # print 'RLS: add_program got %d rows - should delete' % len(rows)
            for row in rows:
                del_list.append(row.id)

            self.remove_programs(del_list)
            del_list = []

        elif len(rows) == 1:
            old_prog = rows[0]

        else:
            # we got no results
            pass


        if old_prog and old_prog.title == title:
            # program timeslot is unchanged, see if there's anything
            # that we should update
            if old_prog.subtitle != subtitle:
                self.execute('update programs set subtitle="%s" \
                              where id="%s"' % (subtitle, old_prog.id))
                self.commit()
            if old_prog.description != description:
                self.execute('update programs set description="%s" \
                              where id="%s"' % (description, old_prog.id))
                self.commit()
            if old_prog.episode != episode:
                self.execute('update programs set episode="%s" \
                              where id="%s"' % (episode, old_prog.id))
                self.commit()

            return

        else:
            # old prog and new prog have same times but different title,
            # this is probably a schedule change, remove the old one
            # TODO: check for shifting times and program overlaps

            self.remove_program(old_prog)

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

        query = 'insert into programs (channel_id, title, start, stop, \
                                       subtitle, episode, description) \
                 values ("%s", "%s", %s, %s, "%s", "%s", "%s")' % \
                        (channel_id, title, start, stop, 
                         subtitle, episode, description)

        # print 'RLS: no dupes of %s at %d on %s' % (title, start, channel_id)
        # print 'QUERY: "%s"' % query
        self.execute(query)
        self.commit()
                

    def get_programs(self, channels, start=0, stop=-1):
        print 'RLS: get_programs(%s,%d,%d)' % (channels, start, stop)
        if type(channels) != ListType:
            channels = [ channels, ]
    
        now = time.time()
        if not start:
            start = now

        query = 'select * from programs where'
        for c in channels:
            query = '%s channel_id="%s"' % (query, c)
            if channels.index(c) < len(channels)-1: 
                query = '%s or' % query

        if stop == 0:
            # only get what's running at time start
            query = '%s and start<=%d and stop>%d' % (query, start, start)
        elif stop == -1:
            # get everything from time start onwards
            query = '%s and ((start<=%d and stop>%d) or start>%d)' % \
                    (query, start, start, start)
        elif stop > 0:
            # get everything from time start to time stop
            query = '%s and ((start<=%d and stop>%d) or \
                             (start>%d and stop<%d) or \
                             (start<%d and stop>=%d))' % \
                    (query, start, start, start, stop, stop, stop)
        else:
            return []

        query = '%s order by start' % query
        rows = self.execute(query)
        return rows


    def remove_program(self, id):
        query = 'delete from programs where id="%s' % id

        # print 'REMOVE: %s' % escape_query(query)
        self.execute(query)
        self.commit()


    def remove_programs(self, ids):
        query = 'delete from programs where'
        for id in ids:
            query = '%s id="%s"' % (query, id)
            if ids.index(id) < len(ids)-1: 
                query = '%s or' % query

        # print 'REMOVE: %s' % escape_query(query)
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


    def add_data_vdr(self, vdr_epg_file):
        try:
            import vdrpylib
        except:
            print 'vdrpylib not installed'

        return False




