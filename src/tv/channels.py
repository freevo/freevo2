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
import time
import stat
import string
import traceback

import config
import tv.freq, tv.v4l2
import util
import plugin

# The Electronic Program Guide
import pyepg


DEBUG = config.DEBUG

_channels_cache = None

def get_channels():
    global _channels_cache
    reload = False
    pickle = os.path.join(config.FREEVO_CACHEDIR, 'epg')

    if not _channels_cache:
        _debug_('no epg in memory, caching')
        reload = True

    elif not os.path.isfile(pickle):
        _debug_('no epg "%s", will try to rebuild' % pickle)
        reload = True

    elif os.stat(pickle)[stat.ST_MTIME] > _channels_cache.load_time:
        _debug_('epg newer than memory cache, reloading')
        reload = True

    if reload:
        if DEBUG:
            stime = time.time()
        _channels_cache = ChannelList()
        if DEBUG:
            _debug_('epg load took %s seconds' % (time.time()-stime))

    return _channels_cache


def get_settings_by_id(chan_id):
    settings = []

    for c in get_channels().get_all():
        if c.id == chan_id:
            for f in c.freq:
                which = string.split(f, ':')[0]
                settings.append(which)
            return settings


def get_settings_by_name(chan_name):
    settings = []

    for c in get_channels().get_all():
        if c.name == chan_id:
            for f in c.freq:
                which = string.split(f, ':')[0]
                settings.append(which)
            return settings


def get_lockfile(which):
    #  In this function we must figure out which device these settings use
    #  because we are allowed to have multiple settings for any particular
    #  device, usually for different inputs (tuner, composite, svideo).

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
    lockfile = get_lockfile(which)

    if os.path.exists(lockfile):
        return True

    else:
        return False


def get_actual_channel(channel_id, which):
    
    for chan in get_channels().get_all():
        if chan.id == channel_id:
            for f in chan.freq:
                if string.split(f, ':')[0] == which:
                    return string.lstrip(f, '%s:' % which)


class Channel:
    """
    information about one specific channel, also containing
    epg informations
    """
    def __init__(self, name, freq, epg):
        self.name = name
        self.freq = []
        self.epg  = epg
        if isinstance(freq, list) or isinstance(freq, tuple):
            for f in freq:
                self.__add_freq__(f)
        else:
            self.__add_freq__(freq)

        # variables from the epg
        self.id   = self.epg.id

        # functions from the epg
        self.next = self.epg.next
        self.prev = self.epg.prev
        self.get  = self.epg.get


    def __add_freq__(self, freq):
        """
        add a frequence to the internal list where to find that channel
        """
        if freq.find(':') == -1:
            freq = '%s:%s' % (config.TV_DEFAULT_SETTINGS, freq)
        self.freq.append(freq)


    def player(self):
        """
        return player object for playing this channel
        """
        for f in self.freq:
            device, freq = f.split(':')
            print device, freq
            # try all internal frequencies
            for p in plugin.getbyname(plugin.TV, True):
                # FIXME: better handling for rate == 1 or 2
                if p.rate(self, device, freq):
                    return p, device, freq
        return None


    def settings(self):
        """
        return a dict of settings for this channel
        """
        settings = {}

        for f in self.freq:
            type = string.split(f, ':')[0]
            settings[type] = config.TV_SETTINGS.get(type)

        return settings
                    


class ChannelList:

    def __init__(self):
        self.selected = 0
        self.channels = []

        source = config.XMLTV_FILE
        pickle = os.path.join(config.FREEVO_CACHEDIR, 'epg')

        epg = pyepg.load(source, pickle)
        self.load_time = time.time()

        for c in config.TV_CHANNELS:
            self.channels.append(Channel(c[1], c[2], epg.get(c[0])))
        

    def down(self):
        """
        go one channel up
        """
        self.selected = (self.selected + 1) % len(self.channels)


    def up(self):
        """
        go one channel down
        """
        self.selected = (self.selected + len(self.channels) - 1) % len(self.channels)


    def set(self, pos):
        """
        set channel
        """
        self.selected = pos
        

    def get(self):
        """
        return selected channel information
        """
        return self.channels[self.selected]


    def get_all(self):
        """
        return all channels
        """
        return self.channels
    
