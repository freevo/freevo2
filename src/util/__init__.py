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
# Revision 1.13  2004/02/25 19:50:51  dischi
# fix unicode problem for utf-8
#
# Revision 1.12  2004/02/23 19:39:59  dischi
# fix vfs problem in mediainfo
#
# Revision 1.11  2004/02/23 19:27:07  dischi
# fix mmpython init
#
# Revision 1.10  2004/02/07 11:53:33  dischi
# use "ignore" to make unicode->string possible
#
# Revision 1.9  2004/02/05 19:26:42  dischi
# fix unicode handling
#
# Revision 1.8  2004/01/02 11:19:40  dischi
# import popen3
#
# Revision 1.7  2003/11/29 11:27:41  dischi
# move objectcache to util
#
# Revision 1.6  2003/11/23 16:57:36  dischi
# move xml help stuff to new fxdparser
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

if sys.argv[0].find('setup.py') == -1 and sys.argv[0].find('install.py') == -1:
    import config
    import __builtin__

    def Unicode(string, encoding=config.encoding):
        if type(string) == str:
            try:
                return unicode(string, encoding)
            except Exception, e:
                try:
                    return unicode(string, config.LOCALE)
                except Exception, e:
                    print 'Error: Could not convert %s to unicode' % repr(string)
                    print 'tried encoding %s and %s' % (encoding, config.LOCALE)
                    print e
        return string

    def String(string, encoding=config.encoding):
        if type(string) == unicode:
            return string.encode(encoding, 'replace')
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
