# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# source_vdr.py - Freevo Electronic Program Guide module for VDR
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rob@infointeractive.com>
# Maintainer:    Rob Shortt <rob@infointeractive.com>
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


import os
import vdr.vdr


def update(guide, vdr_dir=None, channels_file=None, epg_file=None,
             host=None, port=None, access_by='sid',
             exclude_channels=None, verbose=1):
    if not (isinstance(exclude_channels, list) or \
            isinstance(exclude_channels, tuple)):
        exclude_channels = []

    print 'excluding channels: %s' % exclude_channels

    vdr = vdr.vdr.VDR(host=host, port=port, videopath=vdr_dir,
                      channelsfile=channels_file, epgfile=epg_file,
                      close_connection=0)

    if vdr.epgfile and os.path.isfile(vdr.epgfile):
        print 'Using VDR EPG from %s.' % vdr.epgfile
        if os.path.isfile(vdr.channelsfile):
            vdr.readchannels()
        else:
            print 'WARNING: VDR channels file not found as %s.' % \
                  vdr.channelsfile
        vdr.readepg()
    elif vdr.host and vdr.port:
        print 'Using VDR EPG from %s:%s.' % (vdr.host, vdr.port)
        vdr.retrievechannels()
        vdr.retrieveepg()
    else:
        print 'No source for VDR EPG.'
        return False


    chans = vdr.channels.values()
    for c in chans:
        if c.id in exclude_channels:  continue
        if access_by == 'name':
            access_id = c.name
        elif access_by == 'rid':
            access_id = c.rid
        else:
            access_id = c.sid

        if verbose:
            print 'Adding channel: %s as %s' % (c.id, access_id)

        guide.sql_add_channel(c.id, c.name, access_id)
        for e in c.events:
            subtitle = e.subtitle
            if not subtitle: subtitle = ''
            desc = e.desc
            if not desc: desc = ''

            quide.sql_add_program(c.id, e.title, e.start, int(e.start+e.dur),
                                  subtitle=subtitle, description=desc)

    return True
