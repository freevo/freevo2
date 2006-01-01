# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# config/channels.py - Module for detecting what TV channels are available.
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rshortt@users.sf.net>
# Maintainer:    Rob Shortt <rshortt@users.sf.net>
#                Dirk Meyer <dischi@freevo.org>
#
#
# Please see the file doc/CREDITS for a complete list of authors.
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
import kaa.epg

import sysconfig
import config
import plugin

log = logging.getLogger('config')

def refresh():
    log.info('Detecting TV channels.')

    if config.EPG_DATABASE == 'sqlite':
        kaa.epg.connect('sqlite', sysconfig.datafile('epgdb'))
    elif config.EPG_DATABASE == 'sqlite2':
        kaa.epg.connect('sqlite2', sysconfig.datafile('epgdb2'))
    else:
        raise 'unknown database backend %s' % config.EPG_DATABASE
    
    kaa.epg.load(config.TV_CHANNELS, config.TV_CHANNELS_EXCLUDE)
    
    for c in kaa.epg.channels:
        chan_display_opts = {
            'id' : c.id,
            'tunerid' : c.access_id,
            'name' : c.name
        }

        c.title = config.TV_CHANNELS_DISPLAY_FORMAT % chan_display_opts

refresh()
