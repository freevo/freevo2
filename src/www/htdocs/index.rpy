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
# Revision 1.11  2004/02/09 22:44:16  outlyer
# All time displays should respect the time format in the user's config.
#
# Revision 1.10  2004/02/09 21:23:42  outlyer
# New web interface...
#
# * Removed as much of the embedded design as possible, 99% is in CSS now
# * Converted most tags to XHTML 1.0 standard
# * Changed layout tables into CSS; content tables are still there
# * Respect the user configuration on time display
# * Added lots of "placeholder" tags so the design can be altered pretty
#   substantially without touching the code. (This means using
#   span/div/etc. where possible and using 'display: none' if it's not in
#   _my_ design, but might be used by someone else.
# * Converted graphical arrows into HTML arrows
# * Many minor cosmetic changes
#
# Revision 1.9  2003/11/28 19:31:52  dischi
# renamed some config variables
#
# Revision 1.8  2003/10/20 02:24:17  rshortt
# more tv_util fixes
#
# Revision 1.7  2003/09/05 02:48:13  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
# Revision 1.6  2003/07/26 17:15:15  rshortt
# Some changes from Mike Ruelle that let you know if your xmltv data is out
# of date and also tell you if something is recording (and what it is).
#
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

import tv.record_client 
from www.web_types import HTMLResource, FreevoResource
import util, config
import util.tv_util as tv_util

TRUE = 1
FALSE = 0

class IndexResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()

        fv.printHeader('Welcome', 'styles/main.css',selected='Home')
        fv.res += '<div id="contentmain">\n'
        
        fv.res += '<br/><br/><h2>Freevo Web Status as of %s</h2>' % \
                time.strftime('%B %d ' + config.TV_TIMEFORMAT, time.localtime())
    
        (server_available, schedule) = tv.record_client.connectionTest()
        if not server_available:
            fv.res += '<p class="alert">Notice: The recording server is down.</p>\n'
        else:
            fv.res += '<p class="normal">The recording server is up and running.</p>\n'

        listexpire = tv_util.when_listings_expire()
        if listexpire == 1:
            fv.res += '<p class="alert">Notice: Your listings expire in 1 hour.</p>\n'
        elif listexpire < 12:
            fv.res += '<p class="alert">Notice: Your listings expire in %s hours.</p>\n' % listexpire 
        else:
            fv.res += '<p class="normal">Your listings are up to date.</p>\n'

        (got_schedule, recordings) = tv.record_client.getScheduledRecordings()
        if got_schedule:
            progl = recordings.getProgramList().values()
            f = lambda a, b: cmp(a.start, b.start)
            progl.sort(f)
            for prog in progl:
                try:
                    if prog.isRecording == TRUE:
                        fv.res += '<p class="alert">Now Recording %s.</p>\n' % prog.title
	                break
                except:
                    pass
            num_sched_progs = len(progl)
            if num_sched_progs == 1:
                fv.res += '<p class="normal">One program scheduled to record.</p>\n'
            elif num_sched_progs > 0:
                fv.res += '<p class="normal">%i programs scheduled to record.</p>\n' % num_sched_progs
            else:
                fv.res += '<p class="normal">No programs scheduled to record.</p>\n'
        else:
            fv.res += '<p class="normal">No programs scheduled to record.</p>\n'

        diskfree = '%i of %i Mb free in %s'  % ( (( util.freespace(config.TV_RECORD_DIR) / 1024) / 1024), ((util.totalspace(config.TV_RECORD_DIR) /1024) /1024), config.TV_RECORD_DIR)
        fv.res += '<p class="normal">' + diskfree + '</p>\n'
        fv.res += '</div>'
        fv.printSearchForm()
        #fv.printLinks()
        fv.printFooter()

        return fv.res
    

resource = IndexResource()
