#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# record_server.py - A network aware TV recording server.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
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
import plugin
import childapp
import notifier
import record.server

# change uid
try:
    if config.TV_RECORD_SERVER_UID and os.getuid() == 0:
        os.setgid(config.TV_RECORD_SERVER_GID)
        os.setuid(config.TV_RECORD_SERVER_UID)
        os.environ['USER'] = pwd.getpwuid(os.getuid())[0]
        os.environ['HOME'] = pwd.getpwuid(os.getuid())[5]
except Exception, e:
    print e

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
        time.sleep(60)
