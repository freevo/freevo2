# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# tvcards.py - Module for detecting what TV cards are available.
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

# python imports
import os
import logging

# freevo imports
import config
from util.ioctl import ioctl, pack, unpack, IOR

# get logging object
log = logging.getLogger('config')


class TVCard(object):
    """
    Class handling an analog tv card
    """
    def __init__(self, number):
        self.vdev = '/dev/video' + number
        self.adev = None
        self.driver = 'unknown'
        self.priority = getattr(config, 'TV%s_PRIORITY' % number, number)

        # TODO: Think about using something like TV[0-9]_CHANLIST and
        #       TV[0-9]_NORM, defaulting to (or we can remove) the CONF ones.
        self.norm = config.CONF.tv.upper()
        self.chanlist = config.CONF.chanlist

        # The capture resolution.  The driver should have a default and probably
        # will only accept specific values.  This will be left up to the user
        # to override.  It must be in "WIDTHxHEIGHT" format.
        self.resolution = None

        # TODO: autodetect input and input_name, setting the "tuner" as default
        self.input = 0
        self.input_name = 'tuner'

        # If passthrough is set then we'll use that channel on the input to get
        # our signal.  For example someone may have an external cable box
        # connected and have to set the local tuner to channel 4 to get it.
        self.passthrough = None

        # Save any user defined channel frequency mappings.
        self.custom_frequencies = getattr(config, 'TV%s_FREQUENCIES' % number, {})


class IVTVCard(TVCard):
    """
    Class handling an ivtv analog tv card
    """
    def __init__(self, number):
        TVCard.__init__(self, number)

        self.priority = getattr(config, 'IVTV%s_PRIORITY' % number, number)
        self.input = 4
        self.codec = {}

        default_codec = {
            'aspect': None,
            'audio_bitmask': 0x00a9,
            'bframes': None,
            'bitrate_mode': 1,
            'bitrate': 4500000,
            'bitrate_peak': 4500000,
            'dnr_mode': None,
            'dnr_spatial': None,
            'dnr_temporal': None,
            'dnr_type': None,
            'framerate': None,
            'framespergop': None,
            'gop_closure': 1,
            'pulldown': None,
            'stream_type': 14
        }

        # Check for user defines IVTV codec options or load good defaults
        # for some attributes.
        config_codec = getattr(config, 'IVTV%s_CODEC' % number, {})
            
        for k,v in default_codec.items():
            if config_codec.has_key(k):
                self.codec[k] = config_codec[k]
            else:
                self.codec[k] = v

        # Save any user defined channel frequency mappings.
        self.custom_frequencies = getattr(config, 'IVTV%s_FREQUENCIES' % number, {})


class DVBCard(object):
    """
    Class handling a DVB card
    """
    def __init__(self, number):
        self.number  = number
        self.adapter = '/dev/dvb/adapter' + number

        INFO_ST = '128s10i'
        val = pack( INFO_ST, "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 )
        devfd = os.open(self.adapter + '/frontend0', os.O_TRUNC)
        r = ioctl(devfd, IOR('o', 61, INFO_ST), val)
        os.close(devfd)
        val = unpack( INFO_ST, r )
        name = val[0]
        if val[1] == 0:
            self.type = 'DVB-S'
            self.priority = 10
        elif val[1] == 1:
            self.type = 'DVB-C'
            self.priority = 9
        elif val[1] == 2:
            self.type = 'DVB-T'
            self.priority = 8
        else:
            self.type = 'unknown (%s)' % val[1]
        if name.find('\0') > 0:
            name = name[:name.find('\0')]
        self.name = name

        if hasattr(config, 'DVB%s_PRIORITY' % number):
            self.priority = getattr(config, 'DVB%s_PRIORITY' % number)

        if hasattr(config, 'DVB%s_CHANNELS_CONF' % number):
            self.channels_conf = getattr(config, 'DVB%s_CHANNELS_CONF' % number)
        else:
            for path in ('~/.freevo', '~/.mplayer', '~/.xine'):
                conf = os.path.join(os.path.expanduser(path), 'channels.conf')
                if os.path.isfile(conf):
                    self.channels_conf = conf
                    break
            else:
                log.error('channels conf not found')
                self.channels_conf = ''
        log.debug('register dvb device %s' % self.adapter)


# auto-load TV_CARDS:
log.info('Detecting TV cards.')

# internal card counter
_analog_tv_number = 0
_ivtv_number = 0

for i in range(10):
    if os.uname()[0] == 'FreeBSD':
        if os.path.exists('/dev/bktr%s' % i):
            key = 'tv%s' % i
            config.TV_CARDS[key] = TVCard
            config.TV_CARDS[key].vdev = '/dev/bktr%s' % i
            config.TV_CARDS[key].driver = 'bsdbt848'
            config.TV_CARDS[key].input = 1
            log.debug('BSD TV card detected as %s' % key)

        continue

    if os.path.isdir('/dev/dvb/adapter%s' % i):
        try:
            config.TV_CARDS['dvb%s' % i] = DVBCard
            log.debug('DVB card detected as dvb%s' % i)
        except OSError:
            # likely no device attached
            pass
        except:
            log.exception('dvb detection')

    vdev = '/dev/video%s' % i
    if os.path.exists(vdev):
        type = 'tv'
        driver = None
        try:
            QUERYCAP_ST  = "16s32s32sLL16x"
            QUERYCAP_NO  = IOR('V',  0, QUERYCAP_ST)

            devfd = os.open(vdev, os.O_TRUNC)
            val = pack(QUERYCAP_ST, "", "", "", 0, 0)
            r = ioctl(devfd, QUERYCAP_NO, val)
            os.close(devfd)
            driver = unpack(QUERYCAP_ST, r)[0]

            log.debug('detected driver: %s' % driver)

            if driver.find('ivtv') != -1:
                type = 'ivtv'

        except OSError:
            # likely no device attached
            continue
        except IOError:
            # found something that doesn't speak v4l2
            continue
        except:
            log.exception('tv detection')
            continue

        if type == 'ivtv':
            key = '%s%s' % (type, _ivtv_number)
            log.debug('IVTV card detected as %s' % key)
            config.TV_CARDS[key]  = IVTVCard
            if _ivtv_number != i:
                config.TV_CARDS[key].vdev = vdev
            _ivtv_number += 1

        else:
            # Default to 'tv' type as set above.
            key = '%s%s' % (type, _analog_tv_number)
            log.debug('TV card detected as %s' % key)
            config.TV_CARDS[key]  = TVCard
            if _analog_tv_number != i:
                config.TV_CARDS[key].vdev = vdev
            _analog_tv_number += 1

        config.TV_CARDS[key].driver = driver


# set default device
if not config.TV_DEFAULT_DEVICE:
    for type in ['dvb0', 'tv0', 'ivtv0']:
        if type in config.TV_CARDS.keys():
            config.TV_DEFAULT_DEVICE = type[:-1]
            break
