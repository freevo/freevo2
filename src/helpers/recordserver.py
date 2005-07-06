# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# recordserver.py - start script for the recordserver
# -----------------------------------------------------------------------------
# $Id$
#
# This helper will start the freevo recordserver.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
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
import os
import pwd
import logging

# kaa imports
import kaa.notifier

# create logger objects in sysconfig
import sysconfig

# get logging object
log = logging.getLogger('record')

# set basic recording debug to info
log.setLevel(logging.INFO)

# import freevo config
import config

# change uid
try:
    if config.TV_RECORD_SERVER_UID and os.getuid() == 0:
        os.setgid(config.TV_RECORD_SERVER_GID)
        os.setuid(config.TV_RECORD_SERVER_UID)
        os.environ['USER'] = pwd.getpwuid(os.getuid())[0]
        os.environ['HOME'] = pwd.getpwuid(os.getuid())[5]
except Exception, e:
    log.warning('unable to set uid: %s' % e)

# import recordserver
import record.server

# start recordserver
record.server.RecordServer()

kaa.notifier.loop()
kaa.notifier.shutdown()
