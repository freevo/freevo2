#!/usr/bin/env python
#if 0 /*
# -----------------------------------------------------------------------
# webserver.py - start the webserver
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/09/08 19:58:21  dischi
# run servers in endless loop in case of a crash
#
# Revision 1.3  2003/09/06 14:59:38  gsbarbieri
# Fixed to work in non system-wide installs
#
# Revision 1.2  2003/09/05 16:20:11  dischi
# take care for installed version
#
# Revision 1.1  2003/08/31 09:18:41  dischi
# Move webserver start script to helpers. Use 'freevo webserver start'
# and 'freevo webserver stop'.
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

from twisted.internet import app
from twisted.web import static, server, vhost, script
from twisted.python import log

DEBUG = 1

TRUE = 1
FALSE = 0

if len(sys.argv)>1 and sys.argv[1] == '--help':
    print 'start or stop the internal webserver'
    print 'usage freevo webserver [ start | stop ]'
    sys.exit(0)


def main():
    # the start and stop stuff will be handled from the freevo script

    logfile = '%s/internal-webserver-%s.log' % (config.LOGDIR, os.getuid())
    log.startLogging(open(logfile, 'a'))

    if os.path.isdir(os.path.join(os.environ['FREEVO_PYTHON'], 'www/htdocs')):
        docRoot = os.path.join(os.environ['FREEVO_PYTHON'], 'www/htdocs')
    else:
        docRoot = os.path.join(config.SHARE_DIR, 'htdocs')

    root = static.File(docRoot)
    root.processors = { '.rpy': script.ResourceScript, }
    
    root.putChild('vhost', vhost.VHostMonsterResource())
    site = server.Site(root)
    
    application = app.Application('web')
    application.listenTCP(config.WWW_PORT, site)
    
    application.run(save=0)


if __name__ == '__main__':
    import traceback
    while 1:
        try:
            main()
        except:
            traceback.print_exc()
            pass

