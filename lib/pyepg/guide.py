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
# Revision 1.13  2004/12/09 20:23:00  dischi
# merged freevo/src/tv/channels.py into the guide, needs much cleanup
#
# Revision 1.12  2004/12/05 17:08:53  dischi
# wait when db is locked
#
# Revision 1.11  2004/12/04 01:31:49  rshortt
# -get_channels() roughly sorts the channels returned.  We will add sorting
#  options to Freevo.
# -Some unicode fixes.
# -remove_program() will purge a program from all tables (which aren't
#  actually in use yet)
# -expire_programs(): new method to remove old data from the EPG to keep it
#  small (and faster).  This will not remove a programs entry if is found in
#  the recorded_programs table (not in use yet either).
# -add_data_xmltv(): pass along which channels to exclude.  Call expire_programs()
# -add_data_vdr(): accept more VDR properties, also support SVDRP.  This also
#  checks which channels to exclude. Call expire_programs().
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

from channel import Channel
from program import Program

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

from sqlite import IntegrityError, OperationalError
import notifier


class _SQLite:
    def __init__(self, dbpath):
        while 1:
            try:
                self.db = sqlite.connect(dbpath, client_encoding='utf-8',
                                         timeout=10)
                break
            except OperationalError, e:
                notifier.step(False, False)
        self.cursor = self.db.cursor()


    def commit(self):
        self.db.commit()

    def close(self):
        self.db.close()

    def execute(self, query):
        while 1:
            try:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            except OperationalError, e:
                notifier.step(False, False)

        
class EPGDB:
    """ 
    Class for working with the EPG database 
    """
    def __init__(self):
        self.channel_list = []
        self.channel_dict = {}

    def connect(self, dbpath):
        if not os.path.isfile(dbpath):
            print 'epg database missing, creating it'
            scheme = os.path.join(os.path.dirname(__file__), 'epg_schema.sql')
            os.system('sqlite %s < %s 2>/dev/null >/dev/null' % (dbpath, scheme))
            print 'done'
        self.db = _SQLite(dbpath)


    def init(self, TV_CHANNELS=[], TV_CHANNELS_EXCLUDE=[]):

        # Check TV_CHANNELS and add them to the list
        for c in TV_CHANNELS:
            self.add_channel(Channel(c[0], c[1], c[2:], self))

        # Check the EPGDB for channels. All channels not in the exclude list
        # will be added if not already in the list
        for c in self.get_channels():
            if String(c['id']) in TV_CHANNELS_EXCLUDE:
                # Skip channels that we explicitly do not want.
                continue
            if not c['id'] in self.channel_dict.keys():
                self.add_channel(Channel(c['id'], c['display_name'], c['access_id'], self))



    def execute(self, query, close=False):
        query = escape_query(query)

	try:
            result = self.db.execute(query)
        except TypeError:
            traceback.print_exc()
            return False

        if close:
            # run a single query then close
            self.db.commit()           
            self.db.close()
            return result
        else:
            return result
        

    def close(self):
        self.db.commit()
        self.db.close()

    def commit(self):
        self.db.commit()


    def checkTable(self,table=None):
        if not table:
            return False
        # verify the table exists
        if not self.db.execute('select name from sqlite_master where ' + \
                               'name="%s" and type="table"' % table):
            return None
        return table


    def db_add_channel(self, id, display_name, access_id):
        query = 'insert or replace into channels (id, display_name, access_id) \
                 values ("%s", "%s", "%s")' % (id, display_name, access_id)

        self.execute(query)
        self.commit()
                

    def get_channel(self, id):
        query = 'select * from channels where id="%s' % id

        channel = self.execute(query)
        if len(channel):
            return channel[0]


    def get_channels(self):
        query = 'select * from channels order by access_id'
        return self.execute(query)


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
            if Unicode(old_prog['title']) == Unicode(title):
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
            self.commit()
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
        self.execute(query)

        query = 'delete from program_category where program_id=%d' % id
        self.execute(query)

        query = 'delete from program_advisory where program_id=%d' % id
        self.execute(query)

        query = 'delete from record_programs where program_id=%d' % id
        self.execute(query)

        query = 'delete from recorded_programs where program_id=%d' % id
        self.execute(query)

        self.commit()


    def expire_programs(self):
        EXPIRE_TIME = time.time() - 12*3600

        query = 'delete from program_category where program_id in \
                 (select id from programs where \
                id not in (select program_id from recorded_programs) \
                and stop<%d)' % EXPIRE_TIME
        rows = self.execute(query)

        query = 'delete from program_advisory where program_id in \
                 (select id from programs where \
                id not in (select program_id from recorded_programs) \
                and stop<%d)' % EXPIRE_TIME
        rows = self.execute(query)

        query = 'delete from programs where \
                 id not in (select program_id from recorded_programs) \
                 and stop<%d' % EXPIRE_TIME
        rows = self.execute(query)

        self.commit()


    def remove_programs(self, ids):
        clause = ''
        for id in ids:
            clause += ' id=%d' % id
            if ids.index(id) < len(ids)-1: 
                clause += ' or'

        query = 'delete from programs where %s' % clause
        #print 'REMOVE: %s' % escape_query(query)
        self.execute(query)

        clause = ''
        for id in ids:
            clause += ' program_id=%d' % id
            if ids.index(id) < len(ids)-1: 
                clause += ' or'

        query = 'delete from program_category where %s' % clause
        #print 'REMOVE: %s' % escape_query(query)
        self.execute(query)

        query = 'delete from program_advisory where %s' % clause
        #print 'REMOVE: %s' % escape_query(query)
        self.execute(query)

        query = 'delete from record_programs where %s' % clause
        #print 'REMOVE: %s' % escape_query(query)
        self.execute(query)

        query = 'delete from recorded_programs where %s' % clause
        #print 'REMOVE: %s' % escape_query(query)
        self.execute(query)

        #print 'REMOVE: %s' % escape_query(query)
        self.execute(query)
        self.commit()


    def add_data_xmltv(self, xmltv_file, exclude_channels=None, verbose=1):
        import xmltv
        xmltv.load_guide(self, xmltv_file, exclude_channels, verbose)

        self.expire_programs()

        return True


    def add_data_dd(self, dd_file):
        return False


    def add_data_vdr(self, vdr_dir=None, channels_file=None, epg_file=None, 
                     host=None, port=None, access_by='sid', 
                     exclude_channels=None, verbose=1):
        try:
            import vdr.vdr
        except:
            print 'vdrpylib is not installed:'
            print 'http://sourceforge.net/projects/vdrpylib/'

        if not (isinstance(exclude_channels, list) or \
                isinstance(exclude_channels, tuple)):
            exclude_channels = []

        print 'excluding channels: %s' % exclude_channels

        vdr = vdr.vdr.VDR(host=host, port=port, videopath=vdr_dir, 
                          channelsfile=channels_file, epgfile=epg_file,
                          close_connection=0)

        if vdr.epgfile and os.path.isfile(vdr.epgfile):
            print 'Using VDR EPG from %s.' % vdr.epgfile
            if os.path.isfile(vdr.channelsfile):
                vdr.readchannels()
            else:
                print 'WARNING: VDR channels file not found as %s.' % \
                      vdr.channelsfile
            vdr.readepg()
        elif vdr.host and vdr.port:
            print 'Using VDR EPG from %s:%s.' % (vdr.host, vdr.port)
            vdr.retrievechannels()
            vdr.retrieveepg()
        else:
            print 'No source for VDR EPG.'
            return False


        chans = vdr.channels.values()
        for c in chans:
            if c.id in exclude_channels:  continue
            if access_by == 'name':
               access_id = c.name
            elif access_by == 'rid':
               access_id = c.rid
            else:
               access_id = c.sid
            
            if verbose:
                print 'Adding channel: %s as %s' % (c.id, access_id)

            self.db_add_channel(c.id, c.name, access_id)
            for e in c.events:
                subtitle = e.subtitle
                if not subtitle: subtitle = ''
                desc = e.desc
                if not desc: desc = ''
       
                self.add_program(c.id, e.title, e.start, int(e.start+e.dur),
                                 subtitle=subtitle, description=desc)

        self.expire_programs()

        return True

    # channel list code

    def sort_channels(self):
        pass


    def add_channel(self, channel):
        """
        add a channel to the list
        """
        if not self.channel_dict.has_key(channel.id):
            # Add the channel to both the dictionary and the list. This works
            # well in Python since they will both point to the same object!
            self.channel_dict[channel.id] = channel
            self.channel_list.append(channel)


    def __getitem__(self, key):
        return self.channel_list[key]


    def get_channel(self, pos, start=None):
        if not start:
            start = self.channel_list[0]
        cpos = self.channel_list.index(start)
        pos  = (cpos + pos) % len(self.channel_list)
        return self.channel_list[pos]
    
        
    def search_programs(self, subs, by_chan=None):
        now = time.time()
        clause = 'where stop > %d' % now
        if by_chan:
            clause = '%s and channel_id="%s"' % (clause, by_chan)

        clause = '%s and title like "%%%s%%"' % (clause, subs)

        query = 'select * from programs %s order by channel_id, start' % clause
        result = []
        for p in self.execute(query):
            if self.channel_dict.has_key(p.channel_id):
                result.append(Program(p.id, p.title, p.start, p.stop, p.episode,
                                      p.subtitle, description=p['description'], 
                                      channel=self.channel_dict[p.channel_id]))
        return result


