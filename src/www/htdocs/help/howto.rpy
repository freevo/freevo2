#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# howto.rpy - Show the freevo_howto
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/10/07 17:13:22  dischi
# fix howto path lookup
#
# Revision 1.1  2003/09/23 18:24:07  dischi
# moved help to a new directory and add more docs
#
# Revision 1.2  2003/09/20 14:11:11  dischi
# find docs for an installed version
#
# Revision 1.1  2003/09/12 22:00:00  dischi
# add more documentation
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

import sys, os

import config
import version
from www.web_types import HTMLResource, FreevoResource
import util, config

SEARCH_PATH = (os.path.join(config.SHARE_DIR, '../doc/freevo-%s' % version.__version__),
               os.path.join(config.SHARE_DIR, '../Docs'))

class HowtoResource(FreevoResource):
    def __init__(self):
        FreevoResource.__init__(self)
        self.BASEDIR = None
        for d in SEARCH_PATH:
            if os.path.isdir(os.path.join(d, 'freevo_howto')):
                self.BASEDIR = os.path.join(d, 'freevo_howto')
            elif os.path.isdir(os.path.join(d, 'howto')):
                self.BASEDIR = os.path.join(d, 'howto')
        
    def _render(self, request):
        fv = HTMLResource()
        pos = 0

        form = request.args
        file = fv.formValue(form, 'file')
        if not file:
            file = 'index.html'

        if not self.BASEDIR:
            fv.printHeader('Freevo Installation HOWTO', '/styles/main.css')
            fv.res += 'ERROR, unable to load freevo_howto html files<br>'
            fv.res += 'If you use a CVS version of Freevo, run "docbook2html '\
                      '-o freevo_howto freevo_howto.sgml" in the Docs directory '\
                      'of Freevo. '\
                      'The files are searched in the following locations:<br><ol>'
            for d in SEARCH_PATH:
                fv.res += '<li>%s</li>\n' % os.path.join(d, 'freevo_howto')
            fv.res += '</ol>'
        else:
            for line in util.readfile(os.path.join(self.BASEDIR, file)):
                if line.find('HREF') == 0 and line.find('http') == -1:
                    line = line[:line.find('="')+2] + 'howto.rpy?file=' + \
                           line[line.find('="')+2:]
                if line.find('>Freevo Installation HOWTO: Build your own media '\
                             'box with Freevo and Linux</TH') == 0:
                    line = ''
                if pos == 0 and line.find('><TITLE') == 0:
                    pos = 1
                elif pos == 1:
                    fv.printHeader('Freevo Installation HOWTO: %s' % line[1:line.find('<')],
                                   '/styles/main.css')
                    pos = 2
                elif pos == 2 and line.find('><BODY') == 0:
                    pos = 3
                elif pos == 3 and line[0] == '>':
                    fv.res += line[1:]
                    pos = 4
                elif pos == 4:
                    if line.find('></BODY') == 0:
                        pos = 5
                    else:
                        fv.res += line
        fv.res += '<br><br>'
        fv.printLinks()
        fv.printFooter()
        fv.res+=('</ul>')
        return fv.res
    

resource = HowtoResource()
