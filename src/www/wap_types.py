# -*- coding: iso-8859-1 -*-
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
# Revision 1.4  2004/07/10 12:33:43  dischi
# header cleanup
#
# Revision 1.3  2004/02/19 04:57:59  gsbarbieri
# Support Web Interface i18n.
# 
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
        self.res += '<?xml version="1.0" encoding="'+ config.encoding +'"?>\n'
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
