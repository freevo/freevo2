#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# search.rpy - Web interface to search the Freevo EPG.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.21  2004/05/20 15:52:35  outlyer
# Use the user-specified time format... date is still hardcoded though.
#
# Revision 1.20  2004/03/22 05:33:59  outlyer
# Removed a line of debug.
#
# Revision 1.19  2004/03/17 15:56:54  outlyer
# Add Episode field to search results...
#
# Revision 1.18  2004/03/10 20:33:40  rshortt
# Fix selected tab.
#
# Revision 1.17  2004/03/09 00:14:35  rshortt
# Add advanced search and link to search page.  Next will probably add genre
# options.
#
# Revision 1.16  2004/02/23 08:33:21  gsbarbieri
# i18n: help translators job.
#
# Revision 1.15  2004/02/19 04:57:59  gsbarbieri
# Support Web Interface i18n.
# To use this, I need to get the gettext() translations in unicode, so some changes are required to files that use "print _('string')", need to make them "print String(_('string'))".
#
# Revision 1.14  2004/02/14 19:28:12  outlyer
# Fix a display issue.
#
# Revision 1.13  2004/02/09 21:23:42  outlyer
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
# Revision 1.12  2003/10/20 02:24:18  rshortt
# more tv_util fixes
#
# Revision 1.11  2003/09/05 02:48:13  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
# Revision 1.10  2003/07/13 18:08:53  rshortt
# Change tv_util.get_chan_displayname() to accept channel_id instead of
# a TvProgram object and also use config.TV_CHANNELS when available, which
# is 99% of the time.
#
# Revision 1.9  2003/07/06 20:08:05  rshortt
# Search now uses tv_util.get_chan_displayname(prog) for the display also.
#
# Revision 1.8  2003/05/30 19:17:27  rshortt
# Removing the old header, it was being printed too.
#
# Revision 1.7  2003/05/22 21:33:24  outlyer
# Lots of cosmetic changes:
#
# o Moved the header/logo into web_types
# o Made the error messages all use <h4> instead of <h2> so they look the same
# o Removed most <hr> tags since they don't really mesh well with the light blue
# o Moved the title into the "status bar" under the logo
#
# Revision 1.6  2003/05/16 03:21:33  rshortt
# Bugfix.
#
# Revision 1.5  2003/05/14 01:11:20  rshortt
# More error handling and notice if the record server is down.
#
# Revision 1.4  2003/05/12 23:26:10  rshortt
# small bugfix
#
# Revision 1.3  2003/05/12 23:02:41  rshortt
# Adding HTTP BASIC Authentication.  In order to use you must override WWW_USERS
# in local_conf.py.  This does not work for directories yet.
#
# Revision 1.2  2003/05/12 11:21:51  rshortt
# bugfixes
#
# Revision 1.1  2003/05/11 22:48:21  rshortt
# Replacements for the cgi files to be used with the new webserver.  These
# already use record_client / record_server.
#
# Revision 1.2  2003/02/11 06:40:57  krister
# Applied Robs patch for std fileheaders.
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
import util.tv_util as tv_util

import tv.record_client as ri
from www.web_types import HTMLResource, FreevoResource
import config

TRUE = 1
FALSE = 0


class SearchResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        form = request.args

        (server_available, message) = ri.connectionTest()
        if not server_available:
            fv.printHeader(_('Search Results'), 'styles/main.css', selected=_('Search'))
            fv.res += '<h4>'+_('ERROR')+': '+_('recording server is unavailable')+'</h4>'
            fv.printAdvancedSearchForm()
            fv.printLinks()
            fv.printFooter()

            return String( fv.res )

        find = fv.formValue(form, 'find')
        if fv.formValue(form, 'movies_only'):
            movies_only = 1
        else:
            movies_only = 0

        #print 'DEBUG: movies_only=%s' % movies_only

        (got_matches, progs) = ri.findMatches(find, movies_only)

        if got_matches: 
            (result, favs) = ri.getFavorites()
            (result, recordings) = ri.getScheduledRecordings()
            if result:
                rec_progs = recordings.getProgramList()

        fv.printHeader(_('Search'), 'styles/main.css', selected=_('Search'))

        fv.res += '<br /><br />'
        fv.printAdvancedSearchForm()

        if not got_matches:
            if find or movies_only: 
                fv.res += '<h3>'+_('No matches')+'</h3>'

        else:
            fv.res += '<div id="content"><br>'
            fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell(_('Start Time'), 'class="guidehead" colspan="1"')
            fv.tableCell(_('Stop Time'), 'class="guidehead" colspan="1"')
            fv.tableCell(_('Channel'), 'class="guidehead" colspan="1"')
            fv.tableCell(_('Title'), 'class="guidehead" colspan="1"')
            fv.tableCell(_('Episode'),'class="guidehead" colspan="1"')
            fv.tableCell(_('Program Description'), 'class="guidehead" colspan="1"')
            fv.tableCell(_('Actions'), 'class="guidehead" colspan="1"')
            fv.tableRowClose()

            for prog in progs:

                status = 'basic'

                for rp in rec_progs.values():

                    if rp.start == prog.start and rp.channel_id == prog.channel_id:
                        status = 'scheduled'
                        try:
                            if rp.isRecording == TRUE:
                                status = 'recording'
                        except:
                            sys.stderr.write('isRecording not set')
    
                if ri.isProgAFavorite(prog, favs):
                    status = 'favorite'
   

                fv.tableRowOpen('class="chanrow"')
                fv.tableCell(time.strftime('%b %d ' + config.TV_TIMEFORMAT, time.localtime(prog.start)), 'class="'+status+'" colspan="1"')
                fv.tableCell(time.strftime('%b %d ' + config.TV_TIMEFORMAT, time.localtime(prog.stop)), 'class="'+status+'" colspan="1"')

                chan = tv_util.get_chan_displayname(prog.channel_id)
                if not chan: chan = 'UNKNOWN'
                fv.tableCell(chan, 'class="'+status+'" colspan="1"')

                fv.tableCell(prog.title, 'class="'+status+'" colspan="1"')
                if prog.sub_title:
                    fv.tableCell(prog.sub_title, 'class="'+status+'" colspan="1"')
                else:
                    fv.tableCell('&nbsp;', 'class="'+status+'" colspan="1"')
                    
    
                if prog.desc == '':
                    cell = _('Sorry, the program description for %s is unavailable.') % ('<b>'+prog.title+'</b>')
                else:
                    cell = prog.desc
                fv.tableCell(cell, 'class="'+status+'" colspan="1"')
    
                if status == 'scheduled':
                    cell = ('<a href="record.rpy?chan=%s&start=%s&action=remove">'+_('Remove')+'</a>') % (prog.channel_id, prog.start)
                elif status == 'recording':
                    cell = ('<a href="record.rpy?chan=%s&start=%s&action=add">'+_('Record')+'</a>') % (prog.channel_id, prog.start)
                else:
                    cell = ('<a href="record.rpy?chan=%s&start=%s&action=add">'+_('Record')+'</a>') % (prog.channel_id, prog.start)
    
                cell += (' | <a href="edit_favorite.rpy?chan=%s&start=%s&action=add">'+_('New favorite')+'</a>') % (prog.channel_id, prog.start)
                fv.tableCell(cell, 'class="'+status+'" colspan="1"')
    
                fv.tableRowClose()

            fv.tableClose()

        fv.res += '</div>'
        # fv.printSearchForm()

        fv.printLinks()

        fv.printFooter()

        return String( fv.res )
    
resource = SearchResource()

