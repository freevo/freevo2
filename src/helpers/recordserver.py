#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# record_server.py - A network aware TV recording server.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.69  2004/11/28 17:32:05  dischi
# use config.detect
#
# Revision 1.68  2004/11/21 13:29:13  dischi
# fix config import
#
# Revision 1.67  2004/11/19 02:10:28  rshortt
# First crack at moving autodetect code for TV cards into src/system.  Added a
# detect() to system/__init__.py that will call detect() on a system/ module.
# The general idea here is that only Freevo processes that care about certain
# things (ie: devices) will request and have the information.  If you want
# your helper to know about TV_SETTINGS you would:
#
# import config
# import system
# system.detect('tvcards')
#
# Revision 1.66  2004/11/14 15:57:25  dischi
# better chuid handling
#
# Revision 1.65  2004/11/12 20:39:21  dischi
# recordserver is working now
#
# Revision 1.64  2004/11/07 16:42:33  dischi
# activate child dispatcher and move plugin init to server.py
#
# Revision 1.63  2004/11/06 17:56:21  dischi
# Current status of the recordserver:
# o add/delete/modify/list recordings
# o add/list favorites
# o tv_grab will force an internal favorite update
# o create recordings based on favorites
# o basic conflict detection
# o store everything in a fxd file
# Recording itself (a.k.a. record/plugins) is not working yet
#
# Revision 1.62  2004/11/02 20:15:51  dischi
# replace recordserver with mbus test code
#
# Revision 1.61  2004/08/05 17:35:40  dischi
# move recordserver and plugins into extra dir
#
# Revision 1.60  2004/07/24 00:24:30  rshortt
# Upgrade the twisted reactor to something not depricated and move print to
# debug.
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


import time
import os
import pwd
import traceback

import config

# change uid
try:
    if config.TV_RECORD_SERVER_UID and os.getuid() == 0:
        os.setgid(config.TV_RECORD_SERVER_GID)
        os.setuid(config.TV_RECORD_SERVER_UID)
        os.environ['USER'] = pwd.getpwuid(os.getuid())[0]
        os.environ['HOME'] = pwd.getpwuid(os.getuid())[5]
except Exception, e:
    print e

import plugin
import childapp
import notifier
import record.server

config.detect('tvcards')


while 1:
    try:
        notifier.init(notifier.GENERIC)
        notifier.addDispatcher( childapp.watcher.step )
        record.server.RecordServer()
        notifier.loop()
    except KeyboardInterrupt:
        break
    except:
        traceback.print_exc()
        print 'server problem, sleeping 1 min'
        break
        time.sleep(60)
        
