#if 0 /*
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# util/__init__.py - Some Utilities
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.17  2004/06/13 18:49:39  dischi
# do not take care of install.py
#
# Revision 1.16  2004/03/13 22:30:02  dischi
# better string transformation
#
# Revision 1.15  2004/02/28 21:04:17  dischi
# unicode fixes
#
# Revision 1.14  2004/02/27 20:15:03  dischi
# more unicode fixes
#
# Revision 1.13  2004/02/25 19:50:51  dischi
# fix unicode problem for utf-8
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

import sys

# import the stuff from misc and fileops to be compatible
# with util in only one file

if sys.argv[0].find('setup.py') == -1:
    import config
    import __builtin__

    def Unicode(string, encoding=config.encoding):
        if string.__class__ == str:
            try:
                return unicode(string, encoding)
            except Exception, e:
                try:
                    return unicode(string, config.LOCALE)
                except Exception, e:
                    print 'Error: Could not convert %s to unicode' % repr(string)
                    print 'tried encoding %s and %s' % (encoding, config.LOCALE)
                    print e
        elif string.__class__ != unicode:
            return unicode(str(string), config.LOCALE)
        
        return string


    def String(string, encoding=config.encoding):
        if string.__class__ == unicode:
            return string.encode(encoding, 'replace')
        if string.__class__ != str:
            try:
                return str(string)
            except:
                return unicode(string).encode(encoding, 'replace')
        return string

    
    import vfs
    from misc import *
    from fileops import *

    import fxdparser
    import objectcache
    import popen3
    
    __builtin__.__dict__['vfs']     = vfs
    __builtin__.__dict__['Unicode'] = Unicode
    __builtin__.__dict__['String']  = String

    import mediainfo
