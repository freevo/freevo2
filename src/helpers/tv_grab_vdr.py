# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# tv_grab_vdr.py - Import EPG from VDR (http://www.cadsoft.de/vdr/) into Freevo
# -----------------------------------------------------------------------------
# $Id$
#
#
# This helper relies on a few VDR config variables for Freevo (local_conf.py).
# These are (for example):
#   VDR_DIR       = '/video'
#   VDR_HOST      = 'localhost'
#   VDR_PORT      = 2001
#   VDR_EPG       = 'epg.dat'
#   VDR_CHANNELS  = 'channels.conf'
#   VDR_ACCESS_ID = 'sid'
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rshortt@users.sf.net>
# Maintainer:    Rob Shortt <rshortt@users.sf.net>
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

import sys
import os

import pyepg
import config
import sysconfig
import mcomm

pyepg.connect('sqlite', sysconfig.datafile('epgdb'))
pyepg.load(config.TV_CHANNELS, config.TV_CHANNELS_EXCLUDE) 


def usage():
    print 'Fills the EPG databse with data from VDR.'
    print
    print 'usage: freevo tv_grab_vdr'
    print 'options:'
    sys.exit(0)


def grab():
    print 'Fetching guide from VDR.'

    pyepg.update('vdr', config.VDR_DIR, config.VDR_CHANNELS, config.VDR_EPG, 
                 config.VDR_HOST, config.VDR_PORT, config.VDR_ACCESS_ID)


if __name__ == '__main__':

    if len(sys.argv)>1 and sys.argv[1] == '--help':
        usage()
    
    grab()

    print 'connecting to recordserver'
    rs = mcomm.find('recordserver')
    if not rs:
        print 'recordserver not running'
        sys.exit(0)
    print 'update favorites'
    rs.favorite_update()
