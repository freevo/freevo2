#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
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
# Revision 1.15  2004/12/18 20:08:23  dischi
# use logging module for debug
#
# Revision 1.14  2004/12/18 19:49:48  dischi
# find the recordserver :)
#
# Revision 1.13  2004/12/18 19:05:07  dischi
# make the webserver work again
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

import os
import notifier
import logging

# get logging object
log = logging.getLogger('www')

# set basic recording debug to info
log.setLevel(logging.INFO)


import config

from www.server import Server, RequestHandler

# init notifier
notifier.init( notifier.GENERIC )

# import recordings to attach to the mbus
# FIXME: this is bad!
import tv.recordings

cgi_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../www'))
htdocs  = [ os.path.join(cgi_dir, 'htdocs'),
            os.path.join(config.DOC_DIR, 'html') ]

# launch the server on port 8080
Server('', config.WWW_PORT, RequestHandler, [ cgi_dir, 'www' ], htdocs)
log.info("HTTPServer running on port %s" % str(config.WWW_PORT))

# loop
notifier.loop()
