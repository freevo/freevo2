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
# Revision 1.6  2004/02/19 04:57:59  gsbarbieri
# Support Web Interface i18n.
# To use this, I need to get the gettext() translations in unicode, so some changes are required to files that use "print _('string')", need to make them "print String(_('string'))".
#
# Revision 1.5  2004/02/12 14:04:37  outlyer
# fixes for some issues Dischi pointed out:
#
# o Fix invisible link underlines
# o Change background of "pre" to light gray and add padding
# o Fix CSS so it validates with jigsaw.w3.org
# o Replace #content with content as it should be
#
# Revision 1.4  2004/02/09 21:23:42  outlyer
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
# Revision 1.3  2004/02/06 20:30:32  dischi
# some layout updates
#
# Revision 1.2  2003/11/06 19:56:14  mikeruelle
# remove hard links so we can run when proxied
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
import re

class WikiResource(FreevoResource):
    def __init__(self):
        FreevoResource.__init__(self)
        if os.path.isdir(os.path.join(os.environ['FREEVO_PYTHON'], 'www/htdocs')):
            docRoot = os.path.join(os.environ['FREEVO_PYTHON'], 'www/htdocs')
        else:
            docRoot = os.path.join(config.SHARE_DIR, 'htdocs')
        self.docRoot = docRoot + '/help/wiki'
        
    def _render(self, request):
        fv = HTMLResource()

        form = request.args
        file = fv.formValue(form, 'file')

        src_file = None
        if os.path.isfile(os.path.join(self.docRoot, file + '.html')):
            src_file = os.path.join(self.docRoot, file + '.html')

        if not src_file:
            fv.printHeader(_('Freevo Documentation'), '/styles/main.css', prefix=request.path.count('/')-1)
            fv.res += '<div id="content">'
            fv.res += '<p class="alert">' + _('ERROR')+': '+(_('unable to load %s.html') % file)+'</p>\n'
            fv.res += '<p class="normal">'+ _('If you use a CVS version of Freevo, run <b>autogen.sh</b>.')+'</p>\n'
            fv.res += '</div>\n'
        else:
            pos = 0
            title_reg = re.compile('.*<title>(.*) - Freevo Wiki</title>').match
            for line in util.readfile(src_file):
                if title_reg(line):
                    title = title_reg(line).group(1).replace('DocumentationPage/', '')
                    fv.printHeader(_('Freevo Documentation')+' -- %s' % title,
                                   '/styles/main.css', prefix=request.path.count('/')-1)
                    fv.res += '<div id="content">\n'
                    source = 'http://freevo.sourceforge.net/cgi-bin/moin.cgi/'
                    if file == 'faq':
                        source += 'FrequentlyAskedQuestions'
                    else:
                        source += 'DocumentationPage_2f%s' % file

                    fv.res += '<p>'+(_('This page is generated from the Freevo WiKi. The current '\
                              'Version can be found <a href="%s">here</a>.') % source ) +'</p>'
                if file == 'faq':
                    line = line.replace('<H1>', '<H3>').replace('</H1>', '</H3>')
                line = line.replace('/wiki/img/', '/images/').\
                       replace('DocumentationPage/', '').\
                       replace('/cgi-bin/moin.cgi/DocumentationPage_2f',
                               'doc.rpy?file=').\
                       replace('<a href="/cgi-bin/moin.cgi/PleaseUpdate">'+\
                               'PleaseUpdate</a>', 'PleaseUpdate').\
                       replace('<a href="/cgi-bin/',
                               '<a href="http://freevo.sourceforge.net/cgi-bin/')
                if line.find('<hr>') != -1 and pos == 1:
                    pos = 2
                if pos == 1:
                    fv.res += line
                if line.find('<hr>') != -1 and pos == 0:
                    pos = 1
        fv.res += '<br /><br /></div>\n'
        fv.printLinks(request.path.count('/')-1)
        fv.printFooter()
        fv.res+=('</ul>')
        return String( fv.res )

resource = WikiResource()
