#if 0 /*
# -----------------------------------------------------------------------
# wap_types.py - Classes useful for the wap interface.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/01/09 19:35:49  outlyer
# Inherit DEBUG parameter from config, move some prints into DEBUG
#
# Revision 1.1  2003/09/02 22:36:27  mikeruelle
# commit bart heremans wap recording page
#
# Revision 1.1  2003/09/02 21:14:22  mikeruelle
# First rev of a wap recording interface contributed by Bart Heremans
#
# Revision 1.0  2003/07/14 19:30:36  BHeremans
# 
# First Version
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

import os, sys, time

import config

from twisted.web.resource import Resource

DEBUG = config.DEBUG
TRUE = 1
FALSE = 0

class FreevoWapResource(Resource):

    def render(self, request):
        request.setHeader('Content-Type', 'text/vnd.wap.wml')            
        return self._render(request)

class WapResource:

    def __init__(self):
        self.res = ''

    def formValue(self, form=None, key=None):
        if not form or not key:
            return None

        try: 
            val = form[key][0]
        except: 
            val = None
    
        return val

    def printHeader(self):
        self.res += '<?xml version="1.0"?>\n '  
        self.res += '<!DOCTYPE wml PUBLIC "-//WAPFORUM//DTD WML 1.1//EN" "http://www.wapforum.org/DTD/wml_1.1.xml">\n'
        self.res += '<wml>\n'

    def printFooter(self):
        self.res += '</wml>\n '  

    def validate(self, request):
        session = request.getSession()
	form = request.args
	
        username = self.formValue(form, 'u')
        password = self.formValue(form, 'p')

        if not username :
	    session.validated="no"
	else:
	    realpass = config.WWW_USERS.get(username)
            if password == realpass:
                session.validated="yes"
            else:
                session.validated="no"
