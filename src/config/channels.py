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

import config
from tv.channels import ChannelList

log = logging.getLogger('config')


def refresh():
    log.info('Detecting TV channels.')

    config.TV_CHANNELLIST = ChannelList()
    log.debug('got %d channels' % len(config.TV_CHANNELLIST.channel_list))

    # add all possible channels to the cards
    for card in config.TV_CARDS:
        channels = {}
        for chan in config.TV_CHANNELLIST.get_all():
            for u in chan.uri:
                if u.find(':') == -1: continue  # safeguard, shouldn't happen
                if card == u.split(':')[0]:
                    channels[String(chan.chan_id)] = u.split(':', 1)[1]
    
        config.TV_CARDS[card].channels = channels

refresh()
