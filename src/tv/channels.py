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


class ProgramItem(Item):
    """
    Information about one TV program.
    """

    def __init__(self, title, start, stop, subtitle='', description='', 
                 id=None, channel_id=None, parent=None):
        if parent:
            Item.__init__(self, parent)
        else:
            Item.__init__(self)

        self.title = self.info['title'] = title
        # self.info['title'] = title
        self.start = self.info['start'] = start
        self.stop = self.info['stop'] = stop
        self.channel_id = channel_id
        self.info['subtitle'] = subtitle
        self.info['description'] = description
        self.info['id'] = id
        self.name = '%d\t%s' % (self.info['start'], self.title)

        self.valid = 1
# XXX: getting acsii error with if title == NO_DATA:
#        if title == NO_DATA:
#            self.valid = 0
#        else:
#            self.valid = 1
        
        self.scheduled  = 0

    def __unicode__(self):
        """
        return as unicode for debug
        """
        bt = time.localtime(self.start)   # Beginning time tuple
        et = time.localtime(self.stop)    # End time tuple
        begins = '%s-%02d-%02d %02d:%02d' % (bt[0], bt[1], bt[2], bt[3], bt[4])
        ends   = '%s-%02d-%02d %02d:%02d' % (et[0], et[1], et[2], et[3], et[4])
        return u'%s to %s  %3s ' % (begins, ends, self.channel_id) + \
                   self.title + u' (%s)' % self.pos


    def __str__(self):
        """
        return as string for debug
        """
        return String(self.__unicode__())

    
    def __cmp__(self, other):
        """
        compare function, return 0 if the objects are identical, 1 otherwise
        """
        if not other:
            return 1
        return self.title != other.title or \
               self.start != other.start or \
               self.stop  != other.stop or \
               self.channel_id != other.channel_id


    def getattr(self, attr):
        """
        return the specific attribute as string or an empty string
        """
        if attr == 'start':
            return Unicode(time.strftime(config.TV_TIMEFORMAT, time.localtime(self.start)))
        if attr == 'stop':
            return Unicode(time.strftime(config.TV_TIMEFORMAT, time.localtime(self.stop)))
        if attr == 'date':
            return Unicode(time.strftime(config.TV_DATEFORMAT, time.localtime(self.start)))
        if attr == 'time':
            return self.getattr('start') + u' - ' + self.getattr('stop')
        if hasattr(self, attr):
            return getattr(self,attr)
        return ''



class ChannelItem(Item):
    """
    Information about one specific channel, also containing
    epg informations.
    """
    def __init__(self, id, call_sign, uri, add_programs=True):
        Item.__init__(self)

        self.info['id'] = id
        self.info['call_sign'] = call_sign
        self.info['tuner_id'] = ''
        self.uri = []
        self.programs = []
        self.logo = ''
        self.index       = {}
        self.index_start = 0
        self.index_end   = 0

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
        if add_programs:
            # Create a list of ProgramItems containing EPG data.
            for p in get_epg().get_programs(self.info['id']):
                # print 'P: %s' % p
                self.programs.append(ProgramItem(p.title, p.start, p.stop,
                                                 subtitle=p.subtitle,
                                                 description=p.description,
                                                 id=p.id,
                                                 channel_id=self.info['id']))

                # TODO: add information about program being recorded which
                #       comes from another DB table - same with categories,
                #       ratings and advisories.

        self.create_index()


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


    def create_index(self):
        """
        create index for faster access
        """
        last     = 0
        index    = 0
        last_key = 0

        self.programs[0].index = 0
        for p in self.programs[1:]:
            index += 1
            p.index = index
            key = int(p.start) / (60 * 60 * 24)
            if not self.index_start:
                self.index_start = key
            self.index_end = key
            if not self.index.has_key(key):
                if last_key:
                    while len(self.index[last_key]) < 48:
                        self.index[last_key].append(last)
                self.index[key] = []
            pos = (int(p.start) / (60 * 30)) % (48)
            p.pos = pos
            
            if len(self.index[key]) >= pos + 1:
                last = index
                continue
            while len(self.index[key]) < pos:
                self.index[key].append(last)
            self.index[key].append(index)
            last = index
            last_key = key
        while len(self.index[key]) < 48:
            self.index[key].append(index)


    def __get_pos__(self, start, stop):
        """
        get internal positions for programs between start and stop
        """
        start -= 60 * 30
        key = int(start) / (60 * 60 * 24)
        if key < self.index_start:
            key = self.index_start
            pos = 0
        else:
            pos = (int(start) / (60 * 30)) % (48)

        start = max(self.index[key][pos], 0)
        
        key = int(stop) / (60 * 60 * 24)
        if key > self.index_end:
            key = self.index_end
            pos = 47
        else:
            pos = (int(stop) / (60 * 30)) % (48) + 1

        if pos >= 48:
            # next day
            key += 1
            if key > self.index_end:
                key = self.index_end
                pos = 47
            else:
                pos = 0

        stop = self.index[key][pos] + 1
        return start, stop


    def get(self, start, stop=0):
        """
        get programs between start and stop time or if stop=0, get
        the program running at 'start'
        """
        print 'RLS: get(%d, %d)' % (start, stop)
        if not stop:
            stop = start
        start_p, stop_p = self.__get_pos__(start, stop)
        f = lambda p, a=start, b=stop: not (p.start > b or p.stop < a)
        try:
            progs = filter(f, self.programs[start_p:stop_p])
            if not len(progs):  return [ None, ]
            return progs
        except Exception, e:
            print 'RLS: return filter failed'
            traceback.print_exc()
            return [ None, ]
                

    def next(self, prog):
        """
        return next program after 'prog'
        """
        pos  = min(len(self.programs)-1, prog.index + 1)
        prog = self.programs[pos]
        if pos < len(self.programs) and not prog.valid:
            return self.next(prog)
        return prog

    
    def prev(self, prog):
        """
        return previous program before 'prog'
        """
        pos = max(0, prog.index - 1)
        prog = self.programs[pos]
        if pos > 0 and not prog.valid:
            return self.prev(prog)
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
        

    def add_channel(self, channel):
        """
        add a channel to the list
        """
        if not self.channel_dict.has_key(channel.id):
            # Add the channel to both the dictionary and the list. This works
            # well in Python since they will both point to the same object!
            self.channel_dict[channel.id] = channel
            self.channel_list.append(channel)


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
    
