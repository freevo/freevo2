# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# guide.py - interface to the database
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
#                Rob Shortt <rob@infointeractive.com>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#                Rob Shortt <rob@infointeractive.com>
#
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
# -----------------------------------------------------------------------------

# python imports
import time
import logging
from types import *

try:
    # Freevo sysconfig import
    import sysconfig
except:
    # Fallback for stand alone epg usage
    import config

# pyepg imports
from channel import Channel
from program import Program

# get logging object
log = logging.getLogger('pyepg')


class Guide:
    """
    Class for working with the EPG database
    """
    def __init__(self):
        self.selected_index = 0
        self.channel_list = []
        self.channel_dict = {}


    def connect(self, frontent, *args):
        """
        Connect to the database frontent
        """
        exec('from db_%s import Database' % frontent)
        self.db = Database(*args)


    def load(self, TV_CHANNELS=[], TV_CHANNELS_EXCLUDE=[]):
        """
        Load channel listing from the database
        """
        self.exclude_channels = TV_CHANNELS_EXCLUDE
        # Check TV_CHANNELS and add them to the list
        for c in TV_CHANNELS:
            self.add_channel(Channel(c[0], c[1], c[2:], self))

        # Check the db for channels. All channels not in the exclude list
        # will be added if not already in the list
        for c in self.sql_get_channels():
            if String(c['id']) in TV_CHANNELS_EXCLUDE:
                # Skip channels that we explicitly do not want.
                continue
            if not c['id'] in self.channel_dict.keys():
                self.add_channel(Channel(c['id'], c['display_name'],
                                         c['access_id'], self))


    def close(self):
        self.db.commit()
        self.db.close()


    def __escape_query(self, sql):
        """
        Escape a SQL query in a manner suitable for sqlite
        """
        if not type(sql) in StringTypes:
            return sql
        sql = sql.replace('\'','')
        return sql


    def __escape_value(self, val):
        """
        Escape a SQL value in a manner to be quoted inside a query
        """
        if not type(val) in StringTypes:
            return val
        return val.replace('"', '').replace('\'', '')


    #
    # SQL functions
    #
    # This functions will return a sql result and should not by used
    # outside pyepg
    #

    def sql_execute(self, query, close=False):
        query = self.__escape_query(query)

	try:
            result = self.db.execute(query)
        except TypeError:
            log.exception('execute error')
            return False

        if close:
            # run a single query then close
            self.db.commit()
            self.db.close()
            return result
        else:
            return result


    def sql_commit(self):
        self.db.commit()


    def sql_checkTable(self,table=None):
        if not table:
            return False
        # verify the table exists
        if not self.db.execute('select name from sqlite_master where ' + \
                               'name="%s" and type="table"' % table):
            return None
        return table


    def sql_add_channel(self, id, display_name, access_id):
        query = 'insert or replace into channels (id, display_name, access_id)\
                 values ("%s", "%s", "%s")' % (id, display_name, access_id)
        self.sql_execute(query)
        self.sql_commit()


    def sql_get_channel(self, id):
        query = 'select * from channels where id="%s' % id

        channel = self.sql_execute(query)
        if len(channel):
            return channel[0]


    def sql_get_channels(self):
        query = 'select * from channels order by access_id'
        return self.sql_execute(query)


    def sql_remove_channel(self, id):
        query = 'delete from channels where id="%s' % id
        self.sql_execute(query)
        self.sql_commit()


    def sql_get_channel_ids(self):
        id_list = []
        query = 'select id from channels'

        rows = self.sql_execute(query)
        for row in rows:
            id_list.append(row.id)

        return id_list


    def sql_add_program(self, channel_id, title, start, stop, subtitle='',
                        description='', episode=''):
        now = time.time()
        title = self.__escape_value(title)
        subtitle = self.__escape_value(subtitle).strip(' \t-_')
        description = self.__escape_value(description).strip(' \t-_')
        episode = self.__escape_value(episode).strip(' \t-_')

        old_prog = None

        del_list = []

        query = 'select * from programs where channel_id="%s" ' % channel_id +\
                'and start>%s and start<%s' % (start, stop)
        rows = self.sql_execute(query)
        if len(rows) and (len(rows) > 1 or rows[0]['start'] != start or \
                          rows[0]['stop'] != stop):
            log.info('changed program time table:')
            # The time table changed. Old programs overlapp new once
            # Better remove everything here
            for row in rows:
                log.info('delete %s:' % row['title'])
                del_list.append(row.id)
            self.sql_remove_programs(del_list)

        query = 'select * from programs where channel_id="%s" ' % channel_id +\
                'and start=%s' % start
        rows = self.sql_execute(query)
        if len(rows) == 1:
            old_prog = rows[0]
            if Unicode(old_prog['title']) == Unicode(title):
                # program timeslot is unchanged, see if there's anything
                # that we should update
                if Unicode(old_prog['subtitle']) != Unicode(subtitle):
                    log.debug('different subtitles: %s - %s' % \
                             (String(old_prog['subtitle']), String(subtitle)))
                    query = 'update programs set subtitle="%s" where id=%d'
                    self.sql_execute(query % (subtitle, old_prog.id))
                    self.sql_commit()
                if Unicode(old_prog['description']) != Unicode(description):
                    log.debug('different descs: %s - %s' % \
                             (String(old_prog['description']),
                              String(description)))
                    query = 'update programs set description="%s" where id=%d'
                    self.sql_execute(query % (description, old_prog.id))
                    self.sql_commit()
                if Unicode(old_prog['episode']) != Unicode(episode):
                    log.info('different episodes: %s - %s' % \
                             (String(old_prog['episode']), String(episode)))
                    query = 'update programs set episode="%s" where id=%d'
                    self.sql_execute(query % (episode, old_prog.id))
                    self.sql_commit()
                return

            else:
                log.info('different titles: %s - %s' % \
                         (String(old_prog.title), String(title)))
                # old prog and new prog have same times but different title,
                # this is probably a schedule change, remove the old one
                # TODO: check for shifting times and program overlaps
                self.sql_remove_program(old_prog['id'])

        #
        # If we made it here there's no identical program in the table
        # to modify.
        #

        # TODO:
        # Delete any entries of the same program title on the same channel
        # within 10 minues of the start time to somewhat compensate for
        # shifting times.
        # self.sql_execute('delete from programs where channel_id="%s" and \
        #               title="%s" and abs(%s-start)<=600' % \
        #               (channel_id, title, start))
        #for row in res:
        #    if del_list.index(row[0]) >= 0: continue
        #    del_list.append(row[0])
        #self.sql_remove_programs(del_list)


        #
        # If we got this far all we need to do now is insert a new
        # program row.
        #
        query = 'insert into programs (channel_id, title, start, stop, \
                                       subtitle, episode, description) \
                 values ("%s", "%s", %s, %s, "%s", "%s", "%s")' % \
                        (channel_id, title, start, stop,
                         subtitle, episode, description)

        try:
            self.sql_execute(query)
            self.sql_commit()
        except Exception, e:
            log.error('Program for (%s, %s) exists:' % \
                      (String(channel_id), start))
            log.exception('trace:')
            query = 'select * from programs where channel_id="%s" and start=%s'
            rows = self.sql_execute(query % (channel_id, start))
            self.sql_commit()
            for row in rows:
                log.error('    %s' % row)


    def sql_get_programs(self, channels, start=0, stop=-1):
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
            query = 'SELECT * FROM programs WHERE'

        if stop == 0:
            # only get what's running at time start
            query = '%s start<=%d and stop>%d' % (query, start, start)
        elif stop == -1:
            # get everything from time start onwards
            query = '%s ((start<=%d and stop>%d) or start>%d)' % \
                    (query, start, start, start)
        elif stop > 0:
            # get everything from time start to time stop
            query = '%s start <= %s AND stop >= %s' % \
                    (query, stop, start)
        else:
            return []

        return self.sql_execute('%s order by start' % query)


    def sql_remove_program(self, id):
        query = 'delete from programs where id=%d' % id
        self.sql_execute(query)

        query = 'delete from program_category where program_id=%d' % id
        self.sql_execute(query)

        query = 'delete from program_advisory where program_id=%d' % id
        self.sql_execute(query)

        query = 'delete from record_programs where program_id=%d' % id
        self.sql_execute(query)

        query = 'delete from recorded_programs where program_id=%d' % id
        self.sql_execute(query)

        self.sql_commit()


    def sql_expire_programs(self):
        EXPIRE_TIME = time.time() - 12*3600

        query = 'delete from program_category where program_id in \
                 (select id from programs where \
                id not in (select program_id from recorded_programs) \
                and stop<%d)' % EXPIRE_TIME
        rows = self.sql_execute(query)

        query = 'delete from program_advisory where program_id in \
                 (select id from programs where \
                id not in (select program_id from recorded_programs) \
                and stop<%d)' % EXPIRE_TIME
        rows = self.sql_execute(query)

        query = 'delete from programs where \
                 id not in (select program_id from recorded_programs) \
                 and stop<%d' % EXPIRE_TIME
        rows = self.sql_execute(query)

        self.sql_commit()


    def sql_remove_programs(self, ids):
        clause = ''
        for id in ids:
            clause += ' id=%d' % id
            if ids.index(id) < len(ids)-1:
                clause += ' or'

        query = 'delete from programs where %s' % clause
        self.sql_execute(query)

        clause = ''
        for id in ids:
            clause += ' program_id=%d' % id
            if ids.index(id) < len(ids)-1:
                clause += ' or'

        query = 'delete from program_category where %s' % clause
        self.sql_execute(query)

        query = 'delete from program_advisory where %s' % clause
        self.sql_execute(query)

        query = 'delete from record_programs where %s' % clause
        self.sql_execute(query)

        query = 'delete from recorded_programs where %s' % clause
        self.sql_execute(query)

        self.sql_execute(query)
        self.sql_commit()


    #
    # User Interface
    #
    # Interface functions to get channels / programs
    #

    def update(self, backend, *args, **kwargs):
        """
        Add data with the given backend to the database. The code for the
        real adding is in source_`backend`.py
        """
        exec('import source_%s as backend' % backend)
        backend.update(self, *args, **kwargs)
        self.sql_expire_programs()


    def sort_channels(self):
        """
        Sort the internal channel list (not implemented yet)
        """
        pass


    def add_channel(self, channel):
        """
        Add a channel to the list
        """
        if not self.channel_dict.has_key(channel.id):
            # Add the channel to both the dictionary and the list. This works
            # well in Python since they will both point to the same object!
            self.channel_dict[channel.id] = channel
            self.channel_list.append(channel)


    def __getitem__(self, key):
        """
        Get a channel by position in the list (integer) or by the database
        id (string)
        """
        if isinstance(key, int):
            return self.channel_list[key]
        else:
            return self.channel_dict[key]


    def get_channel(self, start=None, pos=0):
        """
        Get a channel relative to the given channel 'start'. The function
        will start from the beginning of the list if the index is greater
        as the channel list length and wrap to the end if lower zero.
        If start is not given it will return the channel based on the
        selected_index, which is also updated every method call.
        """
        if type(start) in StringTypes:
            start = self.channel_dict.get(start)

        if start:
            cpos = self.channel_list.index(start)
        else:
            cpos = self.selected_index

        self.selected_index = (cpos + pos) % len(self.channel_list)
        return self.channel_list[self.selected_index]


    def search(self, searchstr, by_chan=None, search_title=True,
               search_subtitle=True, search_description=True):
        """
        Return a list of programs with a title similar to the given parameter.
        If by_chan is given, it has to be a valid channel id and only programs
        from this channel will be returned. Result is a list of Programs.
        This function will only return programs with a stop time greater the
        current time.
        """
        if not (search_title or search_subtitle or search_description):
            return []

        now = time.time()
        clause = 'where stop > %d' % now
        if by_chan:
            clause = '%s and channel_id="%s"' % (clause, by_chan)

        clause += ' and ('

        if search_title:
            clause = '%s title like "%%%s%%"' % (clause, searchstr)

        if search_subtitle:
            if search_title: clause += ' or'
            clause = '%s subtitle like "%%%s%%"' % (clause, searchstr)

        if search_description:
            if search_title or se: clause += ' or'
            clause = '%s description like "%%%s%%"' % (clause, searchstr)

        clause += ' )'

        query = 'select * from programs %s order by channel_id, start' % clause
        result = []
        for p in self.sql_execute(query):
            if self.channel_dict.has_key(p.channel_id):
                result.append(Program(p.id, p.title, p.start, p.stop,
                                      p.episode, p.subtitle,
                                      description=p['description'],
                                      channel=self.channel_dict[p.channel_id]))
        return result


    def get_program_by_id(self, id):
        """
        Get a program by a database id. Return None if the program is not
        found.
        """
        query = 'select * from programs where id="%s"' % id
        result = self.sql_execute(query)
        if result:
            p = result[0]
            if self.channel_dict.has_key(p.channel_id):
                return Program(p.id, p.title, p.start, p.stop,
                               p.episode, p.subtitle,
                               description=p['description'],
                               channel=self.channel_dict[p.channel_id])
        return None
