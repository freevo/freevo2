#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# index.rpy - The main index to the web interface.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2003/05/29 11:40:42  rshortt
# Applied a patch by Mike Ruelle that adds info about disk free, scheduled recordings, and shows the time.
#
# Revision 1.4  2003/05/22 21:33:23  outlyer
# Lots of cosmetic changes:
#
# o Moved the header/logo into web_types
# o Made the error messages all use <h4> instead of <h2> so they look the same
# o Removed most <hr> tags since they don't really mesh well with the light blue
# o Moved the title into the "status bar" under the logo
#
# Revision 1.3  2003/05/14 12:31:05  rshortt
# Added the standard Freevo graphic and title.
#
# Revision 1.2  2003/05/14 01:11:20  rshortt
# More error handling and notice if the record server is down.
#
# Revision 1.1  2003/05/12 23:27:11  rshortt
# The start of an index page.
#
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

import sys, time

import record_client 
from web_types import HTMLResource, FreevoResource
import util
import config

TRUE = 1
FALSE = 0

class IndexResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()

        fv.printHeader('Welcome', 'styles/main.css')
    
        fv.res += '<h2>Freevo Web Status as of %s</h2>' % time.strftime('%B %d %H:%M', time.localtime())
    
        (server_available, schedule) = record_client.connectionTest()
        if not server_available:
            fv.res += '<p><font color="red" >Notice: The recording server is down.</font></p>'
        else:
            fv.res += '<p><font color="white" >The recording server is up and running.</font></p>'

        (got_schedule, recordings) = record_client.getScheduledRecordings()
        if got_schedule:
            num_sched_progs = len(recordings.getProgramList().values())
            if num_sched_progs == 1:
                fv.res += '<p><font color="white" >One program scheduled to record.</font></p>'
            elif num_sched_progs > 0:
                fv.res += '<p><font color="white" >%i programs scheduled to record.</font></p>' % num_sched_progs
            else:
                fv.res += '<p><font color="white" >No programs scheduled to record.</font></p>'
        else:
            fv.res += '<p><font color="white" >No programs scheduled to record.</font></p>'

        diskfree = '%i of %i Mb free in %s'  % ( (( util.freespace(config.DIR_RECORD) / 1024) / 1024), ((util.totalspace(config.DIR_RECORD) /1024) /1024), config.DIR_RECORD)
        fv.res += '<p><font color="white" >' + diskfree + '</font></p>'

        fv.printSearchForm()
        fv.printLinks()
        fv.printFooter()
        fv.res+=('</ul>')

        return fv.res
    

resource = IndexResource()
