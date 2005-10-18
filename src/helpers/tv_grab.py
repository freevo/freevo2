# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# tv_grab.py - Freevo helper to populate the EPG with TV listings.
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#                Rob Shortt <rshortt@users.sf.net>
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
import shutil
from optparse import OptionParser

import kaa.epg

# freevo core imports
from freevo import mcomm

# freevo ui imports
import config
import sysconfig


def grab_xmltv():

    if not config.XMLTV_GRABBER:
        print 'No program found to grab the listings. Please set XMLTV_GRABBER'
        print 'in local.conf.py to the grabber you need'
        print
        sys.exit(0)

    print 'Grabbing listings using XMLTV.'
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

    kaa.epg.update('xmltv', config.XMLTV_FILE)


def grab_vdr():
    print 'Fetching guide from VDR.'

    kaa.epg.update('vdr', config.VDR_DIR, config.VDR_CHANNELS, config.VDR_EPG,
                   config.VDR_HOST, config.VDR_PORT, config.VDR_ACCESS_ID,
                   'both')


def main():
    parser = OptionParser()

    parser.add_option('-s', '--source', dest='source', default='xmltv',
                      help='set the source for the guide: xmltv (default), ' +\
                      'xmltv_nofetch, vdr, or none')
    parser.add_option('-q', '--query', action="store_true", dest='query', 
                      default=False,
                      help='print a list that can be used to set TV_CHANNELS')
    parser.add_option('-e', '--query-exclude', action="store_true",
                      dest='exclude', default=False,
                      help='print a list that can be used to set ' + \
                           'TV_CHANNELS_EXCLUDE')

    (options, args) = parser.parse_args()

    if config.EPG_DATABASE == 'sqlite':
        kaa.epg.connect('sqlite', sysconfig.datafile('epgdb'))
    elif config.EPG_DATABASE == 'sqlite2':
        kaa.epg.connect('sqlite2', sysconfig.datafile('epgdb2'))
    else:
        raise 'unknown database backend %s' % config.EPG_DATABASE

    kaa.epg.load(config.TV_CHANNELS, config.TV_CHANNELS_EXCLUDE)


    if options.query:
        chanlist = kaa.epg.guide.sql_get_channels()

        print
        print 'Possible list of tv channels. If you want to change the name or'
        print 'acess id copy the next statement into your local_conf.py and '
        print 'edit it.'
        print
        print 'TV_CHANNELS = ['
        for c in chanlist[:-1]:
            print '    ( \'%s\', \'%s\', \'%s\' ), ' % (c[kaa.epg.ID], 
                                                        c[kaa.epg.DISPLAY_NAME], 
                                                        c[kaa.epg.ACCESS_ID])
        print '    ( \'%s\', \'%s\', \'%s\' ) ] ' % \
              (chanlist[-1][kaa.epg.ID], chanlist[-1][kaa.epg.DISPLAY_NAME], 
               chanlist[-1][kaa.epg.ACCESS_ID])
        sys.exit(0)


    if options.exclude:
        chanlist = kaa.epg.guide.sql_get_channels()

        print
        print 'Possible list of tv channels to exclude from Freevo.  Any '
        print 'channel ids found in this list will be ignored.  Below is a '
        print 'sample containing ALL of the channels available from the EPG.  '
        print 'If you copy this as is you will see no channels in Freevo at '
        print 'all.'
        print
        print 'TV_CHANNELS_EXCLUDE = ['
        for c in chanlist[:-1]:
            print '    \'%s\',' % c[kaa.epg.ID]
        print '    \'%s\', ] ' % chanlist[-1][kaa.epg.ID]
        sys.exit(0)


    if options.source == 'xmltv':
        grab_xmltv()
    elif options.source == 'xmltv_nofetch':
        kaa.epg.update('xmltv', config.XMLTV_FILE)
    elif options.source == 'vdr':
        grab_vdr()
    elif options.source == 'none':
        pass
    else:
        print 'ERROR: source "%s" not supported.' % options.source
        sys.exit(0)


    print 'connecting to recordserver'
    rs = mcomm.find('recordserver')
    if not rs:
        print 'recordserver not running'
        sys.exit(0)
    print 'update favorites'
    rs.call('favorite.update', None)


if __name__ == '__main__':
    main()

