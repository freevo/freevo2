#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# plugins.rpy - Show all plugins
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2003/09/12 22:00:00  dischi
# add more documentation
#
# Revision 1.2  2003/09/12 20:56:04  dischi
# again small cosmetic changes
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

import sys, time

from www.web_types import HTMLResource, FreevoResource
import util, config

from helpers.plugins import parse_plugins
from helpers.plugins import info_html

TRUE = 1
FALSE = 0

class PluginResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        fv.printHeader('Freevo Plugin List', 'styles/main.css')

        all_plugins = parse_plugins()

        fv.res += '<a name="head"></a>'
        fv.res += '<p><b>Index</b><ol>'
        
        for p in all_plugins:
            fv.res += '<li><a href="#%s">%s</a></li>' % (p[0], p[0])
        fv.res += '</ol> '

        for p in all_plugins:
            fv.res +=  '<a name="%s"></a>' % p[0]
            fv.res += info_html(p[0], [p])
            fv.res += '<a href="#head">plugin index</a><hr>\n'
        fv.res += '<br><br>'
        fv.printLinks()
        fv.printFooter()
        fv.res+=('</ul>')
        return fv.res
    

resource = PluginResource()
