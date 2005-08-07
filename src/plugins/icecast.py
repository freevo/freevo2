# -*- coding: iso-8859-1 -*-
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
# Revision 1.15  2005/08/07 10:21:52  dischi
# deactivate plugins, they are broken
#
# Revision 1.14  2005/07/16 09:48:23  dischi
# adjust to new event interface
#
# Revision 1.13  2004/07/26 18:10:18  dischi
# move global event handling to eventhandler.py
#
# Revision 1.12  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.11  2004/02/14 19:18:31  mikeruelle
# move the icecast changer into icecast.py
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
import traceback
import signal
import time
import plugin
import event as em

class PluginInterface(plugin.DaemonPlugin):
    """
    A plugin to start an icecast server in the background
    please remeber to install/compile icecast yourself and
    adjust paths and passwords appropriately.

    To activate, put the following lines in local_conf.py:
    plugin.activate('icecast') 
     
    ICECAST_WWW_PAGE = 1 
    ICECAST_CMD = '/usr/local/icecast/bin/icecast' 
    ICECAST_CONF_DIR = '/usr/local/icecast/conf' 
    ICES_CMD = '/usr/local/icecast/bin/ices' 
    ICES_OPTIONS = [ '-d', 'FreevoIcecast', 
                     '-g', 'Rock', 
                     '-m', '/freevo', 
                     '-n', 'Freevo_Music_Collection', 
                     '-P', 'hackme', 
                     '-s', 
                     '-r' ] 
    ICES_DEF_LIST = '/usr/local/freevo_data/Music/ROCK/mymix.m3u' 
    """
    def __init__(self):
        self.reason = config.REDESIGN_BROKEN
        return
        plugin.DaemonPlugin.__init__(self)
        self.icecast_pid = None
        self.ices_pid = None
        plugin.activate('icecast.IcecastChanger')

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

    def config(self):
        return [ ('ICECAST_WWW_PAGE', 1, 'boolean to show www page to change list'),
                 ('ICECAST_CMD', '/usr/local/icecast/bin/icecast', 'location of the icecast server binary'),
                 ('ICECAST_CONF_DIR', '/usr/local/icecast/conf', 'location of the icecast server conf directory'),
                 ('ICES_CMD', '/usr/local/icecast/bin/ices', 'location of the ices binary'),
                 ('ICES_DEF_LIST', '/usr/local/freevo_data/Music/ROCK/mymix.m3u', 'default list to start ices with'),
                 ('ICES_OPTIONS', [ '-d', 'FreevoIcecast', '-g', 'Rock', '-m', '/freevo', '-n', 'Freevo_Music_Collection', '-P', 'hackme', '-s', '-r' ], 'default options to start ices with') ]

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
        os.kill(self.ices_pid, signal.SIGTERM)
        os.waitpid(self.ices_pid, 0)
        os.kill(self.icecast_pid, signal.SIGTERM)
        os.waitpid(self.icecast_pid, 0)

class IcecastChanger(plugin.ItemPlugin):
    """
    This plugin is automatically included by the icecast plugin. There
    should be no need to activate it yourself. It's purpose is to add
    the extra action to m3u files to use them as playlists for icecast. 
    """
    def __init__(self):
        self.reason = config.REDESIGN_BROKEN
        return
        plugin.ItemPlugin.__init__(self)

    def change2m3u(self, arg=None, menuw=None):
        myfile = file(os.path.join(config.FREEVO_CACHEDIR, 'changem3u.txt'), 'wb')
        myfile.write(self.item.filename)
        myfile.flush()
        myfile.close()
        em.MENU_BACK_ONE_MENU.post()
        
    def actions(self, item):
        self.item = item
        if item.type == 'playlist':
            fsuffix = os.path.splitext(item.filename)[1].lower()[1:]
            if fsuffix == 'm3u':
                return [ (self.change2m3u,
                          _('Set as icecast playlist')) ]
        return []
