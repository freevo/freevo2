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
# Revision 1.9  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
#
# Revision 1.8  2003/05/26 00:40:24  rshortt
# Backing out the vhost code because it was unneccessary and only made things
# harder.  There is no need to use it as a form of security now because of the
# user / pass authentication.  The webserver will now listen on all local adresses.
#
# Revision 1.6  2003/05/12 16:46:18  rshortt
# The webserver now binds to a particular host address, localhost is
# the default so if left unchanged you will only be able to access it
# from the same machine (unless maybe someone does some DNS tricks).
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
from twisted.web import static, server, vhost, script
from twisted.python import log

DEBUG = 1

TRUE = 1
FALSE = 0

logfile = '%s/internal-webserver-%s.log' % (config.LOGDIR, os.getuid())
log.startLogging(open(logfile, 'a'))

docRoot = './src/www/htdocs'

root = static.File(docRoot)
root.processors = { '.rpy': script.ResourceScript, }

root.putChild('vhost', vhost.VHostMonsterResource())
site = server.Site(root)

application = app.Application('web')
application.listenTCP(config.WWW_PORT, site)

application.run(save=0)
