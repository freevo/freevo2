#!/usr/bin/env python

#if 0 /*
# -----------------------------------------------------------------------
# webserver.py - A small webserver based on twisted.web
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2003/05/11 23:00:03  rshortt
# Fix logging and doc root.
#
# Revision 1.4  2003/05/11 22:44:02  rshortt
# A new webserver based on twisted web.  This webserver will support user authentication.
#
#
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
#endif

import sys, os

import config

from twisted.internet import app
from twisted.web import static, server, vhost, twcgi, script, trp
from twisted.python import log

DEBUG = 1

TRUE = 1
FALSE = 0

logfile = '%s/internal-webserver-%s.log' % (config.LOGDIR, os.getuid())
log.startLogging(open(logfile, 'a'))

docRoot = './src/www/htdocs'

root = static.File(docRoot)
root.processors = {
            '.cgi': twcgi.CGIScript,
            '.epy': script.PythonScript,
            '.rpy': script.ResourceScript,
}

root.putChild('vhost', vhost.VHostMonsterResource())
site = server.Site(root)
application = app.Application('web')
application.listenTCP(config.WWW_PORT, site)

application.run(save=0)
