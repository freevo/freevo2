#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# index.rpy - The main index to the web interface.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/05/12 23:27:11  rshortt
# The start of an index page.
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

import sys, time

from web_types import HTMLResource, FreevoResource

TRUE = 1
FALSE = 0

class IndexResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()

        fv.printHeader('Freevo Web Interface', 'styles/main.css')

        fv.res += '<h2>Someone please design a nice index page. :)</h2>'
        fv.res += '<hr />'
    
        fv.printSearchForm()

        fv.printLinks()

        fv.printFooter()

        return fv.res
    

resource = IndexResource()
