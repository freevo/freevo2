#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# record_server.py - A network aware TV recording server.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
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

import notifier

# change uid
try:
    if config.TV_RECORD_SERVER_UID and os.getuid() == 0:
        os.setgid(config.TV_RECORD_SERVER_GID)
        os.setuid(config.TV_RECORD_SERVER_UID)
        os.environ['USER'] = pwd.getpwuid(os.getuid())[0]
        os.environ['HOME'] = pwd.getpwuid(os.getuid())[5]
except Exception, e:
    print e

# load record plugins
plugin.init(exclusive=['record'])

while 1:
    try:
        notifier.init( notifier.GENERIC )

        # import recorder server
        import record.server
        start = time.time()
        record.server.RecordServer()
        notifier.loop()
        break
    except:
        traceback.print_exc()
        if start + 10 > time.time():
            print 'server problem, sleeping 1 min'
            time.sleep(60)
