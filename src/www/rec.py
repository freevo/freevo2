#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# record.rpy - Web interface to your scheduled recordings.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2005/02/02 02:14:03  rshortt
# Small cleanup.
#
# Revision 1.3  2005/01/13 20:19:33  rshortt
# Place the authentication into www/server.py to protect mote than just
# the .py files.
#
# Revision 1.2  2005/01/08 15:40:55  dischi
# remove TRUE, FALSE, DEBUG and HELPER
#
# Revision 1.1  2004/12/28 00:38:45  rshortt
# Reactivating web guide and scheduling recordings, this is still a major work
# in progress and there are still missing pieces.
#
# Revision 1.19  2004/08/23 00:15:29  rshortt
# Prevent crash if removing a program that has already ended.
#
# Revision 1.18  2004/08/04 13:26:46  outlyer
# Add "Search" to actions for scheduled recordings to find alternate airings
# of the program.
#
# Revision 1.17  2004/07/12 14:43:29  outlyer
# Remove some debugging information.
#
# Revision 1.16  2004/04/11 06:51:17  dischi
# unicode patch
#
# Revision 1.15  2004/03/12 03:05:50  outlyer
# Use the episode title where available.
#
# Revision 1.14  2004/03/04 15:23:36  rshortt
# I am pretty sure we should have %b %d in here, the configurable timestamp doesn't really fit in here.
#
# Revision 1.13  2004/02/23 08:33:21  gsbarbieri
# i18n: help translators job.
#
# Revision 1.12  2004/02/22 23:36:49  gsbarbieri
# Now support listing of non-ascii names/descriptions.
# So far you can have manual recordings with non-ascii names, but no programs
# from the guide, since findProg() has problems with marmelade (twisted).
#
# Revision 1.11  2004/02/19 04:57:59  gsbarbieri
# Support Web Interface i18n.
# To use this, I need to get the gettext() translations in unicode, so some changes are required to files that use "print _('string')", need to make them "print String(_('string'))".
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
# Revision 1.9  2003/10/20 02:24:18  rshortt
# more tv_util fixes
#
# Revision 1.8  2003/09/05 02:48:13  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
# Revision 1.7  2003/07/13 18:08:53  rshortt
# Change tv_util.get_chan_displayname() to accept channel_id instead of
# a TvProgram object and also use config.TV_CHANNELS when available, which
# is 99% of the time.
#
# Revision 1.6  2003/07/06 19:28:35  rshortt
# Now use tv_util.get_chan_displayname() to get each program's channel's
# definate display name.
#
# Revision 1.5  2003/05/22 21:33:24  outlyer
# Lots of cosmetic changes:
#
# o Moved the header/logo into web_types
# o Made the error messages all use <h4> instead of <h2> so they look the same
# o Removed most <hr> tags since they don't really mesh well with the light blue
# o Moved the title into the "status bar" under the logo
#
# Revision 1.4  2003/05/14 01:11:20  rshortt
# More error handling and notice if the record server is down.
#
# Revision 1.3  2003/05/14 00:18:56  rshortt
# Better error handling.
#
# Revision 1.2  2003/05/12 23:02:41  rshortt
# Adding HTTP BASIC Authentication.  In order to use you must override WWW_USERS
# in local_conf.py.  This does not work for directories yet.
#
# Revision 1.1  2003/05/11 22:48:21  rshortt
# Replacements for the cgi files to be used with the new webserver.  These
# already use record_client / record_server.
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

import sys
import time
import traceback

from record.client import recordings

from www.base import HTMLResource, FreevoResource

import config
import pyepg


class RecordResource(FreevoResource):

    def render(self, request):
        fv = HTMLResource()
        form = request.query

        chan = form.get('chan')
        #if isinstance( chan, str ):
        #    chan = Unicode( chan, 'latin-1' )
        
        start = form.get('start')
        action = form.get('action')

        if not recordings.server:
            fv.printHeader('Scheduled Recordings', 'styles/main.css')
            fv.printMessagesFinish(
                [ '<b>'+_('ERROR')+'</b>: '+_('Recording server is unavailable.') ]
                )

            return String( fv.res )

        if action == 'remove':
            progs = recordings.list()
    
            prog = None
            for p in progs:
                if start == '%s' % p.start and chan == '%s' % p.channel:
                    prog = what

            if prog:
                print 'want to remove prog: %s' % String(prog)
                recordings.remove(prog.id)
        elif action == 'add':
            # (status, prog) = ri.findProg(chan, start)
            # prog = pyepg.get_channel(chan)[start]
            try:
                prog = pyepg.get_channel(chan)[int(start)]
            except:
                fv.printHeader('Scheduled Recordings', 'styles/main.css')
                fv.printMessagesFinish(
                    [ '<b>'+_('ERROR') + '</b>: ' + \
                      ( _('No program found on %s at %s.')%\
                        ( '<b>'+chan+'</b>',
                          '<b>'+time.strftime('%x %X',
                                              time.localtime(int(start)))+\
                          '</b>'
                          )
                           )+\
                      ( ' <i>(%s:%s)</i><br>%s' % (chan, start, traceback.print_exc()) ) ] )

                return String(fv.res)

            
            recordings.schedule(prog)


        progs = recordings.list()
        # (status, favs) = ri.getFavorites()

        fv.printHeader(_('Scheduled Recordings'), 'styles/main.css', selected=_('Scheduled Recordings'))

        fv.res += '&nbsp;\n'

        fv.tableOpen('')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell(_('Start Time'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Stop Time'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Channel'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Title'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Episode'),'class="guidehead" colspan="1"')
        fv.tableCell(_('Program Description'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Actions'), 'class="guidehead" colspan="1"')
        fv.tableRowClose()

        f = lambda a, b: cmp(a.start, b.start)
        progs.sort(f)
        for prog in progs:
            p = pyepg.get_channel(prog.channel)[prog.start]
            status = 'basic'

            #(isFav, junk) = ri.isProgAFavorite(prog, favs)
            #if isFav:
            #    status = 'favorite'
            #try:
            #    if prog.isRecording == True:
            #        status = 'recording'
            #except:
            #    # sorry, have to pass without doing anything.
            #    pass

            fv.tableRowOpen('class="chanrow"')
            fv.tableCell(time.strftime('%b %d ' + config.TV_TIMEFORMAT, 
                                       time.localtime(p.start)), 
                         'class="'+status+'" colspan="1"')
            fv.tableCell(time.strftime('%b %d ' + config.TV_TIMEFORMAT, 
                                       time.localtime(p.stop)), 
                         'class="'+status+'" colspan="1"')

            #chan = pyepg.get_channel(p.channel)
            #if not chan: 
            #    chan_name = _('UNKNOWN')
            #else:
            #    chan_name = chan.name

            fv.tableCell(Unicode(p.channel.title), 
                         'class="'+status+'" colspan="1"')
            fv.tableCell(Unicode(p.title), 
                         'class="'+status+'" colspan="1"')

            fv.tableCell(Unicode(p.subtitle),
                         'class="'+status+'" colspan="1"')

    
            if p.description == u'':
                cell = \
                     _('Sorry, the program description for %s is unavailable.')\
                       % ('<b>'+p.title+'</b>')
            else:
                cell = Unicode(p.description)
            fv.tableCell(cell, 'class="'+status+'" colspan="1"')
    
            cell = ('<a href="rec?chan=%s&amp;start=%s&amp;action=remove" title="Remove Scheduled Recording">'+_('Remove')+'</a>'+'<br/>' + '<a href="search?find=%s" title="Search for other airings">' + _('Search') + '</a>') % (p.channel.id, p.start, Unicode(p.title))
            fv.tableCell(cell, 'class="'+status+'" colspan="1"')

            fv.tableRowClose()

        fv.tableClose()
    
        fv.printSearchForm()
        fv.printFooter()

        return String( fv.res )
    
resource = RecordResource()
