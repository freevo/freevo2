# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# __init__.py - web init function
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2004/07/10 12:33:43  dischi
# header cleanup
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
import config
import sys
import plugin

class PluginInterface(plugin.DaemonPlugin):
    def __init__(self):
        if config.CONF.display in ('dxr3', 'directfb', 'dfbmga'):
            print 'For some strange reason, the starting of the webserver inside'
            print 'Freevo messes up with the DXR3 and directfb output. The webserver'
            print 'plugin will be disabled. Start it from outside Freevo with'
            print 'freevo webserver [start|stop]'
            self.reason = 'dxr3 or directfb output'
            return
        plugin.DaemonPlugin.__init__(self)
        self.pid = None
        os.system('%s webserver start' % os.environ['FREEVO_SCRIPT'])

    def shutdown(self):
        # print 'WEBSERVER::shutdown: pid=%s' % self.pid
        print 'Stopping webserver plugin.'
        os.system('%s webserver stop' % os.environ['FREEVO_SCRIPT'])
