# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# config/channels.py - Module for detecting what TV channels are available.
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rshortt@users.sf.net>
# Maintainer:    Rob Shortt <rshortt@users.sf.net>
#                Dirk Meyer <dmeyer@tzi.de>
#
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

import logging
import pyepg

import sysconfig
import config
import plugin

log = logging.getLogger('config')


def add_uri(channel, uri):
    """
    Add a URI to the internal list where to find that channel.
    Also save the access_id because many people, mostly North Americans,
    like to use it (usually in the display).
    """
    if uri.find(':') == -1:
        channel.access_id = uri
        defaults = []
        if isinstance(config.TV_DEFAULT_DEVICE, list) or \
           isinstance(config.TV_DEFAULT_DEVICE, tuple):
            for s in config.TV_DEFAULT_DEVICE:
                defaults.append(s)
        elif config.TV_DEFAULT_DEVICE:
            defaults.append(config.TV_DEFAULT_DEVICE)

        for which in defaults:
            try:
                int(which[-1:])
            except ValueError: 
                # This means that TV_DEFAULT_DEVICE does NOT end with
                # a number (it is dvb/tv/ivtv) so we add this channel
                # to all matching TV_CARDS.
                for s in config.TV_CARDS:
                    if s.find(which) == 0:
                        add_uri(channel, '%s:%s' % (s, uri))
                return

            channel.uri.append('%s:%s' % (which, uri))
    else:
        try:
            int(uri[:uri.find(':')][-1])
        except:
            # uri doesn't end with a number, add all cards with this based
            for s in config.TV_CARDS:
                if s.find(uri[:uri.find(':')]) == 0:
                    add_uri(channel, '%s:%s' % (s, uri[uri.find(':')+1:]))
            return
        channel.access_id = uri.split(':')[1]
        channel.uri.append(uri)


def get_uri(channel, card):
    """
    Return something to access this channel with based on a particular
    card.
    """
    for u in channel.uri:
        device, uri = u.split(':')
        if device == card:
            return uri

    # If all else fails.
    return channel.access_id


def player(channel):
    for u in channel.uri:
        # try all internal URIs
        device, uri = u.split(':')

        tvp = plugin.getbyname(plugin.TV, True)
        if not tvp or len(tvp) == 0: 
            return None

        for p in tvp:
            # FIXME: better handling for rate == 1 or 2
            if p.rate(channel, device, uri):
                return p, device, uri

    return None


def refresh():
    log.info('Detecting TV channels.')

    pyepg.connect('sqlite', sysconfig.datafile('epgdb'))
    pyepg.load(config.TV_CHANNELS, config.TV_CHANNELS_EXCLUDE)
    
    for c in pyepg.channels:
        c.uri = []
        c.get_uri = get_uri
        c.player  = player

        if isinstance(c.access_id, (list, tuple)):
            for a_id in c.access_id:
                add_uri(c, a_id)
        else:
            add_uri(c, c.access_id)

        chan_display_opts = {
            'id' : c.id,
            'tunerid' : c.access_id,
            'name' : c.name
        }

        c.title = config.TV_CHANNELS_DISPLAY_FORMAT % chan_display_opts


    # add all possible channels to the cards
    for card in config.TV_CARDS:
        channels = {}
        for chan in pyepg.channels:
            for u in chan.uri:
                if u.find(':') == -1:
                    continue  # safeguard, shouldn't happen
                if card == u.split(':')[0]:
                    channels[String(chan.id)] = u.split(':', 1)[1]
    
        config.TV_CARDS[card].channels = channels

refresh()
