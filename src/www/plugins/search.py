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

# freevo core imports
import freevo.ipc.tvserver as tvserver

# freevo imports
import config
from www.base import HTMLResource, FreevoResource

import kaa.epg

# get logging object
log = logging.getLogger('www')


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
            programs = kaa.epg.search(Unicode(searchstr), 
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

            rec_progs = tvserver.recordings.list()

            for p in programs:
                status = 'basic'

                for rp in rec_progs:
                    if p.channel.id == rp.channel and rp.start == p.start:
                        if rp.status == u'recording':
                           status = 'recording'
                        elif rp.status == u'conflict':
                           # TODO: css class for conflict
                           status = 'basic'
                        elif rp.status == u'saved':
                           # TODO: css class for saved
                           status = 'basic'
                        elif rp.status != u'deleted':
                           status = 'scheduled'

#    FIXME:
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
                    cell = ('<a href="recordings?chan=%s&start=%s&action=remove">'+
                            _('Remove')+'</a>') % (p.channel.id, p.start)
                elif status == 'recording':
                    cell = ('<a href="recordings?chan=%s&start=%s&action=remove">'+
                           _('Record')+'</a>') % (p.channel.id, p.start)
                else:
                    cell = ('<a href="recordings?chan=%s&start=%s&action=add">'+
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

