# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# channels.py - Freevo module to handle channel changing.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.29  2004/10/23 15:51:54  rshortt
# -Move get_dummy_programs() out of the ChannelItem class and into the module.
# -Bugfixes for dummy programs.
# -Add channels from config.TV_CHANNELS if they don't exist in the database.
#
# Revision 1.28  2004/10/23 14:46:35  rshortt
# -Move ProgramItem into program_display.py (at least for now).
# -Move when_listings_expire() and get_chan_displayname() to here from util.
# -Remove index for ChanelItem's programs.
# -Add import_programs() for getting programs from the database and adding
#  ProgramItems to self.programs of ChannelItem.  This also checks for gaps
#  in program data and fills them with default ProgramItems.  It sorts the
#  list as well.
# -Modified ChannelItem's get() to check self.programs first, then call
#  import_programs() for what we may be missing.  Also next() and prev() both
#  check self.programs, then call import_programs() if there is no next or
#  prev program.
# -Add import_programs() to ChannelList which calls it on all of its channels.
#
# Revision 1.27  2004/10/18 01:15:20  rshortt
# Changes to use new pyepg:
# -Add ProgramItem and ChannelItem classes which take code from the old tv
#  and channel classes.
# -change freq vars to uri, we already have a freq (KHz, tv/freq.py)
# -preserve tuner_id, which is mostly useful for people in North America as
#  most prefer to see it in the display.
#
# Revision 1.26  2004/10/09 09:11:56  dischi
# wrap epg scanning in a thread
#
# Revision 1.25  2004/08/23 01:23:31  rshortt
# -Add functions for lockfile handling based on the device used.
# -Convenience functions to retrieve settings based on channel id or name.
# -Function to get the actual channel (tuner id) based on a channel id and
#  type (ie: tv0 or dvb1).
#
# Revision 1.24  2004/08/14 01:19:04  rshortt
# Add a simple but effective memory cache.
#
# Revision 1.23  2004/08/13 02:08:25  rshortt
# Add reference to config.TV_DEFAULT_SETTINGS and settings() to Channel class.
# TODO: add logic to include something like TV_SETTINGS_ALTERNATES = { 'tv0' : 'tv1' }
# to say that tv0 and tv1 have the same channels.
#
# Revision 1.22  2004/08/10 19:37:22  dischi
# better pyepg integration
#
# Revision 1.21  2004/08/09 21:19:47  dischi
# make tv guide working again (but very buggy)
#
# Revision 1.20  2004/08/05 17:27:16  dischi
# Major (unfinished) tv update:
# o the epg is now taken from pyepg in lib
# o all player should inherit from player.py
# o VideoGroups are replaced by channels.py
# o the recordserver plugins are in an extra dir
#
# Bugs:
# o The listing area in the tv guide is blank right now, some code
#   needs to be moved to gui but it's not done yet.
# o The only player working right now is xine with dvb
# o channels.py needs much work to support something else than dvb
# o recording looks broken, too
#
# Revision 1.19  2004/07/11 12:33:29  dischi
# no tuner id is ok for dvb
#
# Revision 1.18  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.17  2004/03/05 04:04:10  rshortt
# Only call setChannel on an external tuner plugin if we really have one.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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
import string
import time
import traceback

import config
import tv.freq
import plugin
# import util.fthread as fthread
from item import Item
from tv.program_display import ProgramItem

# The Electronic Program Guide
import pyepg

EPGDB = os.path.join(config.FREEVO_CACHEDIR, 'epgdb')

DEBUG = config.DEBUG

NO_DATA = _('no data')
_channels = None
_epg = None


def get_epg():
    """
    Return an existing instance of the EPG database.
    """

    global _epg

    if not _epg:
        _epg = pyepg.get_epg(EPGDB)
        # _epg = fthread.call(pyepg.get_epg, EPGDB)

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
        _debug_('no channels in memory, loading')
        _channels = ChannelList()

    return _channels


def get_settings_by_id(chan_id):
    """
    """
    
    settings = []

    for c in get_channels().get_all():
        if c.id == chan_id:
            for u in c.uri:
                which = string.split(u, ':')[0]
                settings.append(which)
            return settings


def get_settings_by_name(chan_name):
    """
    """
    
    settings = []

    for c in get_channels().get_all():
        if c.name == chan_name:
            for u in c.uri:
                which = string.split(u, ':')[0]
                settings.append(which)
            return settings


def get_lockfile(which):
    """
    In this function we must figure out which device these settings use
    because we are allowed to have multiple settings for any particular
    device, usually for different inputs (tuner, composite, svideo).
    """

    dev_lock = False
    settings = config.TV_SETTINGS.get(which)
    
    if not settings:
        _debug_('No settings for %s' % which)

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
                   string.replace(dev, os.sep, '_'))
    else:
        lockfile = os.path.join(config.FREEVO_CACHEDIR, 'lock.%s' % which)

    _debug_('lockfile for %s is %s' % (which, lockfile))
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
                if string.split(u, ':')[0] == which:
                    return string.lstrip(u, '%s:' % which)


def get_chan_displayname(channel_id):

    for chan in get_channels().get_all():
        if chan.info['id'] == channel_id:
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


def get_dummy_programs(channel_id, start, stop):
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
                                   id=-1, channel_id=id))

        sec_until_next = default_prog_interval
        d_start = d_stop

    return dummies
 


class ChannelItem(Item):
    """
    Information about one specific channel, also containing
    epg informations.
    """
    def __init__(self, id, call_sign, uri):
        Item.__init__(self)

        self.info['id'] = id
        self.info['call_sign'] = call_sign
        self.info['tuner_id'] = ''
        self.uri = []
        self.programs = []
        self.logo = ''

        if isinstance(uri, list) or isinstance(uri, tuple):
            for u in uri:
                self.__add_uri__(u)
        else:
            self.__add_uri__(uri)

        # XXX: change this to config.TV_CHANNEL_DISPLAY_FORMAT or something as
        #      many people won't want to see the tuner_id.
        # XXX: What should we use, name or title, or both?
        self.name = self.title = self.info['display_name'] = '%s %s' % \
                     (self.info['tuner_id'], self.info['call_sign'])

        # print 'C: %s' % self.info['id']
        # print 'C: %s' % self.id()


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
            type = string.split(u, ':')[0]
            settings[type] = config.TV_SETTINGS.get(type)

        return settings


    def sort_programs(self):
        f = lambda a, b: cmp(a.start, b.start)
        self.programs.sort(f)


    def import_programs(self, start, stop=-1):
        """
        Get programs from the database to create ProgramItems from then
        add them to our local list.  If there are gaps between the programs
        we will add dummy programs to fill it (TODO).
        """
        new_progs = []
        dummy_progs = []

        progs = get_epg().get_programs(self.info['id'], start, stop)
        for p in progs:
            new_progs.append(ProgramItem(p.title, p.start, p.stop,
                                         subtitle=p.subtitle,
                                         description=p.description,
                                         id=p.id,
                                         channel_id=self.info['id']))

            # TODO: add information about program being recorded which
            #       comes from another DB table - same with categories,
            #       ratings and advisories.

        l = len(new_progs)
        if not l:
            for d in get_dummy_programs(self.info['id'], start, stop):
                dummy_progs.append(d)

        for p in new_progs:
            i = new_progs.index(p)
            if i == 0:
                # fill gaps before
                if p.start > start:
                    for d in get_dummy_programs(self.info['id'], start, 
                                                p.start):
                        dummy_progs.append(d)

            if i < l-1:
                # fill gaps between programs
                next_p = new_progs[i+1]
                if p.stop < next_p.start: 
                    for d in get_dummy_programs(self.info['id'], p.stop, 
                                                next_p.start):
                        dummy_progs.append(d)

            elif i == l-1:
                # fill gaps at the end
                if p.stop < stop:
                    for d in get_dummy_programs(self.info['id'], p.stop, stop):
                        dummy_progs.append(d)
                

        for p in new_progs:
            self.programs.append(p)

        for p in dummy_progs:
            self.programs.append(p)

        # TODO: check for duplicates?
        self.sort_programs()


    def get(self, start, stop=0):
        """
        get programs between start and stop time or if stop=0, get
        the program running at 'start'
        """
        progs = []
        need_before = 0
        need_after = 0

        # print 'GET 1: programs len %d' % len(self.programs)
        if len(self.programs):
            # see if we're missing programs before start
            p = self.programs[0]
            if p.start > start:
                need_before = p.start

            p = self.programs[len(self.programs)-1]
            if p.stop < stop:
                need_after = p.stop
        else:
            self.import_programs(start, stop)
     
        if need_before:
            self.import_programs(start, need_before)

        if need_after:
            self.import_programs(need_after, stop)
        
        # print 'GET 2: programs len %d' % len(self.programs)
        for p in self.programs:
            if stop == 0:
                # only get what's running at time start
                if p.start <= start and p.stop > start:
                    progs.append(p)
                    continue

            elif stop == -1:
                # get everything from time start onwards
                if (p.start <= start and p.stop > start) or \
                    p.start > start:
                    progs.append(p)
                    continue

            elif stop > 0:
                # get everything from time start to time stop
                if (p.start <= start and p.stop > start) or \
                   (p.start > start and p.stop < stop) or \
                   (p.start < stop and p.stop >= stop):
                    progs.append(p)
                    continue

        return progs


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

            if self.programs.index(prog) > 0:
                return self.programs[pos-1]

        # print 'prev: at pos %d' % pos

        # print 'prev: returning prog %s' % prog
        return prog
                    


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

        for c in self.epg.get_channels():
            override = False
            for cc in config.TV_CHANNELS:
                if c.id == cc[0]:
                    # Override with config data.
                    self.add_channel(ChannelItem(id=cc[0], call_sign=cc[1], 
                                                 uri=cc[2]))
                    override = True
                    break
                
            if not override:
                self.add_channel(ChannelItem(id=c.id, call_sign=c.call_sign, 
                                             uri=c.tuner_id))

        # Check TV_CHANNELS for any channels that aren't in EPGDB then
        # at them to the list.
        for c in config.TV_CHANNELS:
            if not c[0] in self.channel_dict.keys():
                self.add_channel(ChannelItem(id=c[0], call_sign=c[1], uri=c[2]))
        

    def add_channel(self, channel):
        """
        add a channel to the list
        """
        if not self.channel_dict.has_key(channel.id):
            # Add the channel to both the dictionary and the list. This works
            # well in Python since they will both point to the same object!
            self.channel_dict[channel.id] = channel
            self.channel_list.append(channel)


    def import_programs(self, start, stop=-1):
        """
        """
        for c in self.channel_list:
            c.import_programs(start, stop)


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
    
