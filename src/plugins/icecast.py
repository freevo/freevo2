#if 0 /*
# -----------------------------------------------------------------------
# icecast.py - icecaset plugin for freevo
# -----------------------------------------------------------------------
# $Id$
#
# Notes: 
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
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


import os
import config
import sys
import traceback
import signal
import time

import plugin

TRUE  = 1
FALSE = 0


class PluginInterface(plugin.DaemonPlugin):
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.icecast_pid = None
        self.ices_pid = None

        try:
            # start icecast
            mycmd = os.path.basename(config.ICECAST_CMD)
            self.icecast_pid = os.spawnl(os.P_NOWAIT, config.ICECAST_CMD,
                                         mycmd, '-d', config.ICECAST_CONF_DIR)
            time.sleep(1)
            # start ices
            mycmd = os.path.basename(config.ICES_CMD)
            args = config.ICES_OPTIONS
            args.insert(0, mycmd)
            args.append('-F')
            args.append(config.ICES_DEF_LIST)
            olddir = os.getcwd()
            newdir = os.path.dirname(config.ICES_DEF_LIST)
            os.chdir(newdir)
            self.ices_pid = os.spawnv(os.P_NOWAIT, config.ICES_CMD, args)
            os.chdir(olddir)
        except:
            print 'Crash!'
            traceback.print_exc()
            sleep(1)

    def poll(self):
        #see if we got a change list request
        if (os.path.isfile(os.path.join(config.FREEVO_CACHEDIR, 'changem3u.txt'))):
            try:
                mycmd = os.path.basename(config.ICES_CMD)
                newm3ufile = file(os.path.join(config.FREEVO_CACHEDIR,
                                               'changem3u.txt'), 'rb').read()
                if os.path.exists(os.path.join(config.FREEVO_CACHEDIR, 'changem3u.txt')):
                    os.unlink(os.path.join(config.FREEVO_CACHEDIR, 'changem3u.txt'))
                os.kill(self.ices_pid, signal.SIGTERM)
                os.waitpid(self.ices_pid, 0)
                time.sleep(1)
                args = config.ICES_OPTIONS
                args.insert(0, mycmd)
                args.append('-F')
                args.append(newm3ufile)
                olddir = os.getcwd()
                newdir = os.path.dirname(newm3ufile)
                os.chdir(newdir)
                self.ices_pid = os.spawnv(os.P_NOWAIT, config.ICES_CMD, args)
                os.chdir(olddir)
            except:
                print 'Crash!'
                traceback.print_exc()
                sleep(1)

    def shutdown(self):
        # print 'icecast server::shutdown: pid=%s' % self.pid
        print 'Stopping icecast server plugin.'
        os.kill(self.icecast_pid, signal.SIGTERM)
        os.waitpid(self.icecast_pid, 0)
        os.kill(self.ices_pid, signal.SIGTERM)
        os.waitpid(self.ices_pid, 0)

