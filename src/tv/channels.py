# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# channels.py - Freevo module to handle channel changing.
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
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
import os
import time
import traceback
import logging

# the electronic program guide
import pyepg

# freevo imports
import config
import plugin
import item

log = logging.getLogger('tv')

# tv imports
from program import ProgramItem

EPGDB = os.path.join(config.FREEVO_CACHEDIR, 'epgdb')

_channels = None
_epg = None


def get_epg():
    """
    Return an existing instance of the EPG database.
    """
    global _epg
    if not _epg:
        _epg = pyepg.get_epg(EPGDB)
    return _epg


def get_new_epg():
    """
    Return a fresh instance of the EPG database.
    """
    global _epg
    _epg = pyepg.get_epg(EPGDB)

    return _epg


def get_channels():
    """
    Return an already created ChannelList, this may save a bit of time.
    """
    global _channels
    if not _channels:
        log.info('no channels in memory, loading')
        _channels = ChannelList()
    return _channels


def get_settings_by_id(chan_id):
    """
    """
    settings = []
    for c in get_channels().get_all():
        if c.id == chan_id:
            for u in c.uri:
                which = u.split(':')[0]
                settings.append(which)
            return settings
    return None


def get_settings_by_name(chan_name):
    """
    """
    settings = []
    for c in get_channels().get_all():
        if c.name == chan_name:
            for u in c.uri:
                which = u.split(':')[0]
                settings.append(which)
            return settings
    return None


def get_lockfile(which):
    """
    In this function we must figure out which device these settings use
    because we are allowed to have multiple settings for any particular
    device, usually for different inputs (tuner, composite, svideo).
    """

    dev_lock = False
    settings = config.TV_SETTINGS.get(which)

    if not settings:
        log.info('No settings for %s' % which)

    if isinstance(settings, config.DVBCard):
        dev = settings.adapter
        dev_lock = True

    elif isinstance(settings, config.TVCard):
        dev = settings.vdev
        dev_lock = True

    else:
        print 'Unknown settings for %s!!  This could cause problems!' % which

    if dev_lock:
        lockfile = os.path.join(config.FREEVO_CACHEDIR, 'lock.%s' % \
                   dev.replace(os.sep, '_'))
    else:
        lockfile = os.path.join(config.FREEVO_CACHEDIR, 'lock.%s' % which)

    log.info('lockfile for %s is %s' % (which, lockfile))
    return lockfile


def lock_device(which):
    """
    """

    lockfile = get_lockfile(which)

    if os.path.exists(lockfile):
        return False

    else:
        try:
            open(lockfile, 'w').close()
            return True
        except:
            print 'ERROR: cannot open lockfile for %s' % which
            traceback.print_exc()
            return False


def unlock_device(which):
    """
    """

    lockfile = get_lockfile(which)

    if os.path.exists(lockfile):
        try:
            os.remove(lockfile)
            return True
        except:
            print 'ERROR: cannot remove lockfile for %s' % which
            traceback.print_exc()
            return False

    else:
        return False


def is_locked(which):
    """
    """

    lockfile = get_lockfile(which)

    if os.path.exists(lockfile):
        return True

    else:
        return False


def get_actual_channel(channel_id, which):
    """
    """

    for chan in get_channels().get_all():
        if chan.id == channel_id:
            for u in chan.uri:
                if u.split(':')[0] == which:
                    return u.lstrip('%s:' % which)


def get_chan_displayname(channel_id):

    for chan in get_channels().get_all():
        if chan.chan_id == channel_id:
            return chan.name

    return 'Unknown'


def when_listings_expire():

    last = 0
    left = 0

    for ch in get_channels().get_all():
        prog = ch.programs[len(ch.programs)-1]
        if prog.start > last: last = prog.start

    if last > 0:
        now = time.time()
        if last > now:
            left = int(last - now)
            # convert to hours
            left /= 3600

    return left


def get_dummy_programs(channel, start, stop):
    """
    Return some default ProgramItems with intervals no longer than a
    set default.
    """
    default_prog_interval = 30 * 60
    dummies = []
    d_start = start
    d_stop  = 0

    sec_after_last = start % default_prog_interval
    sec_until_next = default_prog_interval - sec_after_last

    while(d_stop < stop):
        d_stop = d_start + sec_until_next
        if d_stop > stop:
            d_stop = stop

        dummies.append(ProgramItem(u'NO DATA', d_start, d_stop,
                                   id=-1, channel = channel))

        sec_until_next = default_prog_interval
        d_start = d_stop

    return dummies



class ChannelItem(item.Item):
    """
    Information about one specific channel, also containing
    epg informations.
    """
    def __init__(self, id, display_name, uri):
        item.Item.__init__(self)

        self.chan_id  = id
        self.tuner_id = ''
        self.uri      = []
        self.programs = []
        self.logo     = ''

        if isinstance(uri, list) or isinstance(uri, tuple):
            for u in uri:
                self.__add_uri__(u)
        else:
            self.__add_uri__(uri)

        # XXX Change this to config.TV_CHANNEL_DISPLAY_FORMAT or something as
        # XXX many people won't want to see the tuner_id.
        # XXX What should we use, name or title, or both?
        self.name = self.title = display_name


    def __add_uri__(self, uri):
        """
        Add a URI to the internal list where to find that channel.
        Also save the tuner_id because many people, mostly North Americans,
        like to use it (usually in the display).
        """
        if uri.find(':') == -1:
            self.info['tuner_id'] = uri
            uri = '%s:%s' % (config.TV_DEFAULT_SETTINGS, uri)
        else:
            self.info['tuner_id'] = uri.split(':')[1]

        self.uri.append(uri)


    def player(self):
        """
        return player object for playing this channel
        """
        for u in self.uri:
            device, uri = u.split(':')
            print device, uri
            # try all internal URIs
            for p in plugin.getbyname(plugin.TV, True):
                # FIXME: better handling for rate == 1 or 2
                if p.rate(self, device, uri):
                    return p, device, uri
        return None


    def settings(self):
        """
        return a dict of settings for this channel
        """
        settings = {}

        for u in self.uri:
            type = u.split(':')[0]
            settings[type] = config.TV_SETTINGS.get(type)

        return settings


    def sort_programs(self):
        f = lambda a, b: cmp(a.start, b.start)
        self.programs.sort(f)


    def import_programs(self, start, stop=-1, progs=[]):
        """
        Get programs from the database to create ProgramItems from then
        add them to our local list.  If there are gaps between the programs
        we will add dummy programs to fill it (TODO).
        """
        new_progs = []
        dummy_progs = []

        if not progs:
            progs = get_epg().get_programs(self.chan_id, start, stop)
        for p in progs:
            i = ProgramItem(p.title, p.start, p.stop, subtitle=p.subtitle,
                            description=p['description'], id=p.id,
                            channel=self)
            new_progs.append(i)

            # TODO: add information about program being recorded which
            #       comes from another DB table - same with categories,
            #       ratings and advisories.

        l = len(new_progs)
        if not l:
            dummy_progs = get_dummy_programs(self, start, stop)
        else:
            for p in new_progs:
                i = new_progs.index(p)
                if i == 0:
                    # fill gaps before
                    if p.start > start:
                        n = get_dummy_programs(self, start, p.start)
                        dummy_progs += n

                if i < l-1:
                    # fill gaps between programs
                    next_p = new_progs[i+1]
                    if p.stop < next_p.start:
                        n = get_dummy_programs(self, p.stop, next_p.start)
                        dummy_progs += n

                elif i == l-1:
                    # fill gaps at the end
                    if p.stop < stop:
                        n = get_dummy_programs(self, p.stop, stop)
                        dummy_progs += n

        for i in new_progs + dummy_progs:
            if not i in self.programs:
                self.programs.append(i)

        self.sort_programs()


    def get(self, start, stop=0):
        """
        get programs between start and stop time or if stop=0, get
        the program running at 'start'
        """
        # get programs
        if self.programs:
            # see if we're missing programs before start
            p = self.programs[0]
            if p.start > start:
                self.import_programs(start, p.start)
            # see if we're missing programs after end
            p = self.programs[-1]
            if stop == -1:
                self.import_programs(p.stop, stop)
            else:
                if p.stop < stop:
                    self.import_programs(p.stop, stop)
        else:
            self.import_programs(start, stop)

        # return the needed programs
        if stop == 0:
            # only get what's running at time start
            return filter(lambda x: (x.start <= start and x.stop > start),
                          self.programs)
        elif stop == -1:
            # get everything from time start onwards
            return filter(lambda x: (x.start <= start and x.stop > start) or \
                          x.start > start, self.programs)

        elif stop > 0:
            # get everything from time start to time stop
            return filter(lambda x: (x.start <= start and x.stop > start) or \
                          (x.start > start and x.stop < stop) or \
                          (x.start < stop and x.stop >= stop),
                          self.programs)
        raise Exception('bad request: %s-%s' % (start, stop))


    def next(self, prog):
        """
        return next program after 'prog'
        """
        # print 'next: programs len %d' % len(self.programs)
        # for p in self.programs:
        #     print 'P: %s' % p
        # print 'next: at prog %s' % prog

        pos = self.programs.index(prog)
        # print 'next: at pos %d' % pos

        if pos < len(self.programs)-1:
            # print 'next: which is less than %d' % (len(self.programs)-1)
            # return self.programs[pos+1]
            next_prog = self.programs[pos+1]
            # print 'next: nex_prog %s' % next_prog
            return next_prog
        else:
            i_start = self.programs[len(self.programs)-1].stop
            self.import_programs(i_start, i_start+3*3600)

            if self.programs.index(prog) < len(self.programs)-1:
                return self.programs[pos+1]

        # print 'next: returning prog %s' % prog
        return prog


    def prev(self, prog):
        """
        return previous program before 'prog'
        """
        pos = self.programs.index(prog)
        if pos > 0:
            return self.programs[pos-1]
        else:
            i_stop = self.programs[0].start
            self.import_programs(i_stop-3*3600, i_stop)
            return self.programs[self.programs.index(prog)-1]


class ChannelList:
    """
    This is the channel list internal to Freevo.  Here we get channel
    information from pyepg (using EPGDB) and append it with anything
    specific to Freevo like which device to use, or override other
    things such as the display name.
    """

    def __init__(self):
        self.selected = 0
        self.channel_list = []
        self.channel_dict = {}

        if not os.path.isfile(EPGDB):
            print 'No EPGDB found! (%s)' % EPGDB
            return

        try:
            self.epg = get_epg()
        except:
            print 'Failed to load EPGDB! (%s)' % EPGDB
            traceback.print_exc()
            return

        for c in config.TV_CHANNELS:
            self.add_channel(ChannelItem(c[0], c[1], c[2]))


    def add_channel(self, channel):
        """
        add a channel to the list
        """
        if not self.channel_dict.has_key(channel.chan_id):
            # Add the channel to both the dictionary and the list. This works
            # well in Python since they will both point to the same object!
            self.channel_dict[channel.chan_id] = channel
            self.channel_list.append(channel)


    def import_programs(self, start, stop=-1):
        """
        """
        e = self.epg.get_programs([], start, stop)
        for c in self.channel_list:
            id = c.chan_id
            c.import_programs(start, stop, filter(lambda x: x[1] == id, e))


    def down(self):
        """
        go one channel up
        """
        self.selected = (self.selected + 1) % len(self.channel_list)


    def up(self):
        """
        go one channel down
        """
        self.selected = (self.selected + len(self.channel_list) - 1) % \
                         len(self.channel_list)


    def set(self, pos):
        """
        set channel
        """
        self.selected = pos


    def get(self, id=None):
        """
        return channel with id or whichever is selected
        """

        if id:
            chan = self.channel_dict.get(id)
            if chan: return chan

        return self.channel_list[self.selected]


    def get_all(self):
        """
        return all channels
        """
        return self.channel_list

