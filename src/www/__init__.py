# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# __init__.py - webserver plugin to start the server inside Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# Fisrt Version: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

# python imports
import logging

# freevo imports
import os
import config
import plugin

# get logging object
log = logging.getLogger('www')


class PluginInterface(plugin.Plugin):
    """
    webserver plugin
    """
    def __init__(self):
        """
        Start the webserver
        """
        from www.server import Server, RequestHandler

        plugin.Plugin.__init__(self)
        cgi_dir = os.path.join(os.path.dirname(__file__), '../www')
        cgi_dir = os.path.abspath(cgi_dir)
        htdocs  = [ os.path.join(cgi_dir, 'htdocs'),
                    os.path.join(config.SHARE_DIR, 'htdocs'),
                    os.path.join(config.DOC_DIR, 'html') ]
        # launch the server
        Server('', config.WWW_PORT, RequestHandler, [ cgi_dir, 'www' ], htdocs)
        log.info("HTTPServer running on port %s" % str(config.WWW_PORT))
