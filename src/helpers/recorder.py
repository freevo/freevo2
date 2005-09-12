# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# recorder.py - external recorder based on kaa.record for Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# This program is the recorder for the Freevo recordserver. The server can't
# do any recordings, it uses recorder like this on in the LAN based on mbus
# to do the real recording. This file doesn't know anything about timeshifting
# or conflicts, it will record what the server wants.
#
# A global for Freevo 2.0 is that this file is independed of Freevo. This
# module is the only one that needs to detect tv cards and the only one doing
# the mapping between internal channel id and the channel id know to the
# device (dvb names or frequencies for analog tv). Right now it uses the Freevo
# card detection code and the epg to do the mapping (which needs to be changed
# in the future).
#
# The module reacts on the following mbus commands (they may change in the
# future):
#
# home-theatre.vdr.list()
# Returns a list of all tv cards
#
# home-theatre.vdr.describe(id)
# Returns a configuration of the card. It is a list of id, priority, channels
# where channels is a list of bouquets which are lists of channel names.
#
# home-theatre.vdr.record(device, channel, start, stop, filename, options)
# This will schedule a recording on the given device with the given channel.
# The user needs to make sure the channel exists (see vdr.describe). The
# recording will be done between start and stop (integers) and it will be
# stored to the given filename (filename can also be an url). The options are
# a list currently not used. The return value is an id that can be used to
# track start and stop of the recording and stop the recording.
#
# home-theatre.vdr.remove(id)
# Remove the recording with the given id. The recording will be stopped when
# currently running.
#
#
# On start and stop the module sends events. Right now only to the last entity
# requesting a list (should be the recordserver, no other module should talk
# to this one).
#
# home-theatre.vdr.started(id)
# home-theatre.vdr.stopped(id)
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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
import logging

# kaa imports
import kaa
import kaa.record
import kaa.epg

# freevo imports
import config

# mbus support
from mcomm import RPCServer, RPCError, RPCReturn

# get logging object
log = logging.getLogger()

# detect tv cards and channels
config.detect('tvcards', 'channels')


class Device(object):
    """
    Base class for all devices. All devices need to inherit from this class
    to get the basic recorder interface + the need to be a kaa.record device
    for the actual recording.
    """
    def __init__(self, id, card):
        self.name = id
        self.priority = card.priority
        self.bouquets = []


class DvbDevice(kaa.record.DvbDevice, Device):
    """
    Class for handling a DVB card. It is based on kaa.record.DvbDevice and
    only adds conversion between global channel ids and dvb ids.
    """
    def __init__(self, id, card):
        kaa.record.DvbDevice.__init__(self, card.adapter, card.channels_conf)
        Device.__init__(self, id, card)
        self.id2dvb = {}
        self.dvb2id = {}

        # Create dvb to global id mapping. Maybe having one
        # access id is not the way to go here
        for channel in kaa.epg.channels:
            self.id2dvb[channel.id] = channel.access_id
            self.dvb2id[channel.access_id] = channel.id

        for bouquet in self.get_bouquet_list():
            self.bouquets.append([])
            for chan in bouquet:
                if not chan in self.dvb2id:
                    log.debug('unknown channel %s' % chan)
                    continue
                self.bouquets[-1].append(self.dvb2id[chan])


    def start_recording(self, channel, output):
        """
        Start a recording (transform channel id). Since the recorder in this
        module only adds one filter to the recording scheduler, we need to
        create the correct cahin here.
        """
        chain = kaa.record.Chain()
        chain.append(kaa.record.Remux())
        chain.append(output)
        channel = self.id2dvb[channel]
        return kaa.record.DvbDevice.start_recording(self, channel, chain)


class Recorder(RPCServer):
    """
    Recorder handling the different devices.
    """
    def __init__(self):
        RPCServer.__init__(self, 'record-daemon')
        self.cards = []
        self.recordings = {}
        self.server = None

        for id, card in config.TV_CARDS.items():
            if id.startswith('dvb'):
                self.cards.append(DvbDevice(id, card))


    def __rpc_devices_list__(self, addr, val):
        """
        RPC handler for home-theatre.vdr.list
        """
        log.info('list request')
        self.server = addr
        return RPCReturn([ x.name for x in self.cards ])


    def __rpc_device_describe__(self, addr, val):
        """
        RPC handler for home-theatre.vdr.describe
        """
        id = self.parse_parameter(val, ( str, ))
        for card in self.cards:
            if not card.name == id:
                continue
            return RPCReturn((card.name, card.priority, card.bouquets))
        return RPCError('%s invalid' % id)


    def __rpc_vdr_record__(self, addr, val):
        """
        RPC handler for home-theatre.vdr.record
        """
        device, channel, start, stop, filename, options = \
                self.parse_parameter(val, ( str, str, int, int, str, list ))
        for card in self.cards:
            if card.name == device:
                device = card
                break
        else:
            return RPCError('%s invalid' % id)

        if filename.startswith('file:/'):
            filename = filename[5:]
        if filename.startswith('udp://') > 0:
            output = kaa.record.UDPSend(filename[6:])
        else:
            output = kaa.record.Filewriter(filename)

        rec = kaa.record.Recording(start, stop, device, channel, output)
        rec.signals['start'].connect(self.send_event, 'vdr.started', rec.id)
        rec.signals['stop'].connect(self.send_event, 'vdr.stopped', rec.id)
        self.recordings[rec.id] = rec
        return RPCReturn(rec.id)


    def __rpc_vdr_remove__(self, addr, val):
        """
        RPC handler for home-theatre.vdr.remove
        """
        id = self.parse_parameter(val, ( int, ))
        log.info('stop recording %s' % id)
        if id in self.recordings:
            self.recordings[id].remove()
            del self.recordings[id]
            return RPCReturn()
        return RPCError('%s invalid' % id)


    def send_event(self, event, id):
        """
        Send events.
        """
        if not self.server:
            return
        self.mbus_instance.send_event(self.server, event, (id,))


# create recorder
r = Recorder()

# start main loop
kaa.main()

# print debug at the end
log.info('terminate')
