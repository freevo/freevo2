#!/usr/bin/env python
#if 0 /*
# -----------------------------------------------------------------------
# tv_grab.py - wrapper for xmltv
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/09/08 19:44:00  dischi
# *** empty log message ***
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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
#endif


import sys
import os

import config
import util

def usage():
    print 'Downloads the listing for xmltv and cache the data'
    print
    print 'usage: freevo tv_grab [ -query ]'
    print 'options:'
    print '  -query:  print a list of all stations. The list can be used to set TV_CHANNELS'
    sys.exit(0)


if len(sys.argv)>1 and sys.argv[1] == '--help':
    usage()
    
if not config.XMLTV_GRABBER:
    print 'No program found to grab the listings. Please set XMLTV_GRABBER'
    print 'in local.conf.py to the grabber you need'
    print
    usage()

QUERY = 0
if len(sys.argv)>1 and sys.argv[1] == '-query':
    QUERY = 1
    
if not os.path.isfile(config.XMLTV_FILE) or not QUERY:
    os.system('%s --output %s --days %s' % ( config.XMLTV_GRABBER, config.XMLTV_FILE,
                                             config.XMLTV_DAYS ))

print
print 'searching for station information'
chanlist = config.detect_channels()

if QUERY:
    print
    print 'Possible list of tv channels. If you want to change the station'
    print 'id, copy the next statement into your local_conf.py and edit it.'
    print 'You can also remove lines or resort them'
    print
    print 'TV_CHANNELS = ['
    for c in chanlist[:-1]:
        print '    ( \'%s\', \'%s\', %s ), ' % c
    print '    ( \'%s\', \'%s\', %s ) ] ' % chanlist[-1]
    sys.exit(0)

print 'caching data, this may take a while'

import tv.epg_xmltv
tv.epg_xmltv.get_guide()
