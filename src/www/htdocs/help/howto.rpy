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
# Revision 1.5  2003/11/06 19:56:45  mikeruelle
# remove hard links so we can run when proxied
#
# Revision 1.4  2003/11/01 15:20:38  dischi
# better howto support
#
# Revision 1.3  2003/10/31 18:56:14  dischi
# Add framework for plugin writing howto
#
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

# to add a new docbook style howto, just add the identifier to this
# list
TYPES = {
    'install': ('installation', 'Freevo Installation HOWTO',
                'Freevo Installation HOWTO: Build your own media box with Freevo and Linux'),
    'plugin':  ('plugin_writing', 'Freevo Plugin Writing HOWTO',
                'Freevo Plugin Writing HOWTO: Writing your own plugins for Freevo')
    }
                
class HowtoResource(FreevoResource):
    def __init__(self):
        FreevoResource.__init__(self)
        self.BASEDIR = {}
        for type in TYPES:
            dirname = TYPES[type][0]
            for d in SEARCH_PATH:
                if os.path.isdir(os.path.join(d, dirname, 'html')):
                    self.BASEDIR[type] = os.path.join(d, dirname, 'html')
                elif os.path.isfile(os.path.join(d, dirname, 'index.html')):
                    self.BASEDIR[type] = os.path.join(d, dirname)
                elif os.path.isfile(os.path.join(d, dirname, 'book1.html')):
                    self.BASEDIR[type] = os.path.join(d, dirname)
        
    def _render(self, request):
        fv = HTMLResource()
        pos = 0

        form = request.args
        file = fv.formValue(form, 'file')
        if not file:
            file = 'index.html'

        type = fv.formValue(form, 'type')
        if not type:
            type = 'install'
            
        name = TYPES[type][1]
            
        if not self.BASEDIR.has_key(type):
            fv.printHeader(name, '/styles/main.css')
            fv.res += 'ERROR, unable to load html files<br>'
            fv.res += 'If you use a CVS version of Freevo, run "autogen.sh". '\
                      'The files are searched in the following locations:<br><ol>'
            for d in SEARCH_PATH:
                fv.res += '<li>%s/%s</li>\n' % (d, TYPES[type][0])
            fv.res += '</ol>'

        else:
            if not os.path.isfile(os.path.join(self.BASEDIR[type], file)) \
                   and file == 'index.html':
                file = 'book1.html'

            for line in util.readfile(os.path.join(self.BASEDIR[type], file)):
                if line.find('HREF') == 0 and line.find('http') == -1:
                    line = line[:line.find('="')+2] + 'howto.rpy?type=' + \
                           type + '&file=' + line[line.find('="')+2:]

                for t in TYPES:
                    if line.find('>%s</TH' % TYPES[t][2]) == 0:
                        line = ''
                        break

                # remove border for some DocBook stylesheets
                if line.find('BGCOLOR="#E0E0E0"') == 0:
                    line = ''
                    
                if pos == 0 and line.find('><TITLE') == 0:
                    pos = 1
                elif pos == 1:
                    fv.printHeader('%s: %s' % (name, line[1:line.find('<')]),
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
        fv.printLinks(request.path.count('/')-1)
        fv.printFooter()
        fv.res+=('</ul>')
        return fv.res
    

resource = HowtoResource()
