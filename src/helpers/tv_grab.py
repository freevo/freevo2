#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
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
# Revision 1.13  2004/11/06 17:56:21  dischi
# Current status of the recordserver:
# o add/delete/modify/list recordings
# o add/list favorites
# o tv_grab will force an internal favorite update
# o create recordings based on favorites
# o basic conflict detection
# o store everything in a fxd file
# Recording itself (a.k.a. record/plugins) is not working yet
#
# Revision 1.12  2004/10/20 12:33:01  rshortt
# Put epg loading inside xmltv results check.
#
# Revision 1.11  2004/10/19 19:05:23  dischi
# add data to db even if not sorted
#
# Revision 1.10  2004/10/18 01:21:50  rshortt
# Load data into new pyepg database.
#
# Revision 1.9  2004/08/14 01:26:02  rshortt
# Oops, we don't need a reference to the epg.
#
# Revision 1.8  2004/08/14 01:18:07  rshortt
# Make tv_grab helper work again, now with pyepg.
#
# Revision 1.7  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.6  2004/03/28 15:04:42  rshortt
# Bugfix.
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


import sys
import os
import shutil

import config
import mcomm

import pyepg
epg = pyepg.get_epg(os.path.join(config.FREEVO_CACHEDIR, 'epgdb'))


def usage():
    print 'Downloads the listing for xmltv and cache the data'
    print
    print 'usage: freevo tv_grab [ --query ]'
    print 'options:'
    print '  --query:  print a list of all stations. The list can be used to set TV_CHANNELS'
    sys.exit(0)


def grab():
    if not config.XMLTV_GRABBER:
        print 'No program found to grab the listings. Please set XMLTV_GRABBER'
        print 'in local.conf.py to the grabber you need'
        print
        usage()

    print 'Grabbing listings.'
    xmltvtmp = '/tmp/TV.xml.tmp'
    os.system('%s --output %s --days %s' % ( config.XMLTV_GRABBER, 
                                             xmltvtmp,
                                             config.XMLTV_DAYS ))

    if os.path.exists(xmltvtmp):
        if os.path.isfile(config.XMLTV_SORT):
            print 'Sorting listings.'
            os.system('%s --output %s %s' % ( config.XMLTV_SORT,
                                              xmltvtmp+'.1',
                                              xmltvtmp ))

            shutil.move(xmltvtmp+'.1', xmltvtmp)

        else:
            print 'Not configured to use tv_sort, skipping.'

        print 'Loading data into epgdb, this may take a while'

        shutil.move(xmltvtmp, config.XMLTV_FILE)
        epg.add_data_xmltv(config.XMLTV_FILE)


if __name__ == '__main__':

    if len(sys.argv)>1 and sys.argv[1] == '--help':
        usage()
    
    if len(sys.argv)>1 and sys.argv[1] == '--query':
        print
        print 'searching for station information'

        chanlist = config.detect_channels()

        print
        print 'Possible list of tv channels. If you want to change the station'
        print 'id, copy the next statement into your local_conf.py and edit it.'
        print 'You can also remove lines or resort them'
        print
        print 'TV_CHANNELS = ['
        for c in chanlist[:-1]:
            print '    ( \'%s\', \'%s\', \'%s\' ), ' % c
        print '    ( \'%s\', \'%s\', \'%s\' ) ] ' % chanlist[-1]
        sys.exit(0)

    grab()

    print 'connecting to recordserver'
    rs = mcomm.find('recordserver')
    if not rs:
        print 'recordserver not running'
        sys.exit(0)
    print 'update favorites'
    rs.favorite_update()
