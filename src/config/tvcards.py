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
import util.ioctl as ioctl

# get logging object
log = logging.getLogger('config')


class TVCard(object):
    """
    Class handling an analog tv card
    """
    def __init__(self, number):
        self.vdev = '/dev/video' + number
        self.adev = None
        self.norm = config.CONF.tv.upper()
        self.chanlist = config.CONF.chanlist
        self.input = 0
        # TODO: autodetect input_name
        self.input_name = 'tuner'
        self.driver = 'unknown'

        # If passthrough is set then we'll use that channel on the input to get
        # our signal.  For example someone may have an external cable box
        # connected and have to set the local tuner to channel 4 to get it.
        self.passthrough = None


class IVTVCard(TVCard):
    """
    Class handling an ivtv analog tv card
    """
    def __init__(self, number):
        TVCard.__init__(self, number)

        # XXX TODO: take care of proper PAL / NTSC defaults
        self.input = 4
        self.resolution = '720x480'
        self.aspect = 2
        self.audio_bitmask = 0x00a9
        self.bframes = 3
        self.bitrate_mode = 1
        self.bitrate = 4500000
        self.bitrate_peak = 4500000
        self.dnr_mode = 0
        self.dnr_spatial = 0
        self.dnr_temporal = 0
        self.dnr_type = 0
        self.framerate = 0
        self.framespergop = 15
        self.gop_closure = 1
        self.pulldown = 0
        self.stream_type = 14


class DVBCard(object):
    """
    Class handling a DVB card
    """
    def __init__(self, number):
        self.number  = number
        self.adapter = '/dev/dvb/adapter' + number
        self.number = number
        INFO_ST = '128s10i'
        val = ioctl.pack( INFO_ST, "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 )
        devfd = os.open(self.adapter + '/frontend0', os.O_TRUNC)
        r = ioctl.ioctl(devfd, ioctl.IOR('o', 61, INFO_ST), val)
        os.close(devfd)
        val = ioctl.unpack( INFO_ST, r )
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
            import tv.v4l2
            v = tv.v4l2.Videodev(device=vdev)
            driver = v.driver
            if driver.find('ivtv') != -1:
                type = 'ivtv'
            v.close()
            del v
        except OSError:
            # likely no device attached
            continue
        except IOError:
            # found something that doesn't speak v4l2
            continue
        except:
            log.exception('tv detection')

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
