#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# help.rpy - The help index to the web interface.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/09/23 18:24:07  dischi
# moved help to a new directory and add more docs
#
# Revision 1.2  2003/09/12 22:00:00  dischi
# add more documentation
#
# Revision 1.1  2003/09/12 20:34:16  dischi
# start internal help system
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

from www.web_types import HTMLResource, FreevoResource

class HelpResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        fv.printHeader('Freevo Help', '/styles/main.css')
        fv.res += 'This is the internal Freevo documentation. The documents \
        are in an early stage of development, if you like to help, please \
        contact the develepers. You find more informations like \
        the <a href="http://freevo.sourceforge.net/cgi-bin/moin.cgi/FrontPage">\
        WiKi (online manual)</a> and mailing lists on the \
        <a href="http://www.freevo.org">Freevo Homepage</a>.\
        Everyone can edit the WiKi (and we can revert them if someone deletes \
        informations), feel free to add informations there.'

        fv.res += '<p><b>Index</b><ol>'
        
        fv.res += '<li><a href="howto.rpy">Freevo Installation Howto</a></li>'
        fv.res += '<li><a href="doc.rpy?file=faq">Frequently Asked Questions</a></li>'
        fv.res += '<li><a href="plugins.rpy">Plugin List</a></li>'
        fv.res += '<li><a href="doc.rpy?file=FxdFiles">FXD files</a></li>'
        fv.res += '<li><a href="doc.rpy?file=SkinInfo">Skinning Informations</a></li>'

        fv.res += '<br><br>'
        fv.printLinks()
        fv.printFooter()
        fv.res+=('</ul>')
        return fv.res
    
resource = HelpResource()
