#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# iceslistchanger.rpy - change ices playlist via web interface.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/09/05 02:48:13  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
# Revision 1.1  2003/06/24 17:52:00  dischi
# added iceslistchanger
#
# Revision 1.1  2003/05/12 23:27:11  mruelle
# The start of an m3u list changer page.
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

import sys, time, os, urllib

from www.web_types import HTMLResource, FreevoResource
import util, config

TRUE = 1
FALSE = 0

class IceslistchangerResource(FreevoResource):

    def change2m3u(self, mylist):
        myfile = file(os.path.join(config.FREEVO_CACHEDIR, 'changem3u.txt'), 'wb')
        myfile.write(mylist)
        myfile.flush()
        myfile.close()

    def _render(self, request):
        fv = HTMLResource()
        form = request.args
 
        directories = config.DIR_AUDIO
        rpyscript = 'iceslistchanger.rpy'
        #rpyscript = os.path.basename(os.environ['SCRIPT_FILENAME'])
        rpydir = fv.formValue(form, 'dir')
        rpym3u = fv.formValue(form, 'm3u')

        fv.printHeader('Change ICES Play List', 'styles/main.css')

        #make the file to change m3u list ices plugin will pick up on poll
        if rpym3u:
            self.change2m3u(rpym3u)
            fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('Music List', 'class="guidehead" align="center" colspan="1"')
            fv.tableRowClose()
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('List has been changed to %s' % rpym3u, 'class="basic" align="left" colspan="1"')
            fv.tableRowClose()
            fv.tableClose()

        if rpydir:
            fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('Pick a Music List', 'class="guidehead" align="center" colspan="1"')
            fv.tableRowClose()
            # find m3u's
            rpym3ulist = util.match_files_recursively(rpydir, config.SUFFIX_AUDIO_PLAYLISTS)
            for m3u in rpym3ulist:
                title = os.path.basename(m3u)
                link = '<a href="' + rpyscript +'?m3u='+urllib.quote(m3u)+'">'+title+'</a>'

                fv.tableRowOpen('class="chanrow"')
                fv.tableCell(link, 'class="basic" align="left" colspan="1"')
                fv.tableRowClose()
            fv.tableClose()
        else:
            fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('Pick a Music Directory', 'class="guidehead" align="center" colspan="1"')
            fv.tableRowClose()
            for d in directories:
                (title, dir) = d
                link = '<a href="' + rpyscript +'?dir='+urllib.quote(dir)+'">'+title+'</a>'
                fv.tableRowOpen('class="chanrow"')
                fv.tableCell(link, 'class="basic" align="left" colspan="1"')
                fv.tableRowClose()
            fv.tableClose()

    
        fv.printSearchForm()
        fv.printLinks()
        fv.printFooter()
        fv.res+=('</ul>')

        return fv.res



resource = IceslistchangerResource()
