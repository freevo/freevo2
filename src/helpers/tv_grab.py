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
# Revision 1.6  2004/03/28 15:04:42  rshortt
# Bugfix.
#
# Revision 1.5  2004/03/16 01:04:18  rshortt
# Changes to stop two processes tripping over the creation of the epg pickle file.
#
# Revision 1.4  2003/10/20 00:32:11  rshortt
# Placed most of the work into functions and added a check for '__main__' for
# the command line.  I'm planning on importing this module from recordserver
# and calling functions to grab and sort listings at a configurable time.
#
# Alco changed '-query' to '--query' for consistency's sake.
#
# Revision 1.3  2003/10/15 19:26:55  rshortt
# The channel number portion of TV_CHANNELS entries is handled as a string,
# this is especially important for some European channels ie: E8.
#
# Revision 1.2  2003/10/14 02:44:11  rshortt
# Adding an option for tv_grab to use tv_sort on the listings and also to
# update your favorites schedule.
#
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
import shutil

import config

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

            shutil.copyfile(xmltvtmp+'.1', xmltvtmp)
            os.unlink(xmltvtmp+'.1')

        else:
            print 'Not configured to use tv_sort, skipping.'

        print 'caching data, this may take a while'

        import tv.epg_xmltv
        tv.epg_xmltv.get_guide(XMLTV_FILE=xmltvtmp)


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

    import tv.record_client as rc
    
    print 'Scheduling favorites for recording:  '

    (result, response) = rc.updateFavoritesSchedule()
    print '    %s' % response


