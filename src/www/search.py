# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# search.rpy - Web interface to search the Freevo EPG.
# -----------------------------------------------------------------------------
# $Id$
#
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

# python imports
import sys
import time
import logging

# freevo imports
import config
import record.client as rc
from www.base import HTMLResource, FreevoResource

import pyepg


class SearchResource(FreevoResource):

    def render(self, request):
        fv = HTMLResource()
        form = request.query
        by_chan = None

        searchstr = form.get('find')

        fv.printHeader(_('Search'), 'styles/main.css', selected=_('Search'))

        if not searchstr:
            programs = []
        else:
            programs = pyepg.search(searchstr, 
                                    by_chan,
                                    form.get('search_title'), 
                                    form.get('search_subtitle'), 
                                    form.get('search_description'))

        if len(programs) < 1:
            if searchstr:
                fv.res += '<br /><br /><h3>'+_('No matches')+'</h3>'
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

            for p in programs:
                status = 'basic'

# XXX TODO: fix scheduled or favorites status
#                for rp in rec_progs.values():
#
#                    if rp.start == prog.start and rp.channel_id == prog.channel_id:
#                        status = 'scheduled'
#                        try:
#                            if rp.isRecording == True:
#                                status = 'recording'
#                        except:
#                            sys.stderr.write('isRecording not set')
#    
#                if rc.isProgAFavorite(prog, favs):
#                    status = 'favorite'
   

                fv.tableRowOpen('class="chanrow"')
                fv.tableCell(time.strftime('%b %d ' + config.TV_TIMEFORMAT, 
                                           time.localtime(p.start)), 
                             'class="'+status+'" colspan="1"')
                fv.tableCell(time.strftime('%b %d ' + config.TV_TIMEFORMAT, 
                                           time.localtime(p.stop)), 
                             'class="'+status+'" colspan="1"')

                fv.tableCell(Unicode(p.channel.title), 'class="'+status+'" colspan="1"')
                fv.tableCell(Unicode(p.title), 'class="'+status+'" colspan="1"')
                fv.tableCell(Unicode(p.subtitle), 'class="'+status+'" colspan="1"')
    
                if Unicode(p.description) == u'':
                    cell = \
                     _('Sorry, the program description for %s is unavailable.')\
                     % ('<b>'+p.title+'</b>')
                else:
                    cell = Unicode(p.description)

                fv.tableCell(cell, 'class="'+status+'" colspan="1"')
    
                if status == 'scheduled':
                    cell = ('<a href="rec?chan=%s&start=%s&action=remove">'+
                            _('Remove')+'</a>') % (p.channel.id, p.start)
                elif status == 'recording':
                    cell = ('<a href="rec?chan=%s&start=%s&action=add">'+
                           _('Record')+'</a>') % (p.channel.id, p.start)
                else:
                    cell = ('<a href="rec?chan=%s&start=%s&action=add">'+
                           _('Record')+'</a>') % (p.channel.id, p.start)
    
                cell += \
                     (' | <a href="edit_favorite?chan=%s&start=%s&action=add">'+
                     _('New favorite')+'</a>') % (p.channel.id, p.start)

                fv.tableCell(cell, 'class="'+status+'" colspan="1"')
    
                fv.tableRowClose()

            fv.tableClose()

            fv.res += '</div>'

        fv.printAdvancedSearchForm()
        fv.printFooter()

        return String( fv.res )
    
resource = SearchResource()

