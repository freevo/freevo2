# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# db_sqlite.py - interface to sqlite
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
#                Rob Shortt <rob@infointeractive.com>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#                Rob Shortt <rob@infointeractive.com>
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
import logging

# notifier
import notifier

# sqlite
import sqlite
from sqlite import IntegrityError, OperationalError

# get logging object
log = logging.getLogger('pyepg')


class Database:
    """
    Database class for sqlite usage
    """
    def __init__(self, dbpath):
        if not os.path.isfile(dbpath):
            log.warning('epg database missing, creating it')
            scheme = os.path.join(os.path.dirname(__file__), 'epg_schema.sql')
            os.system('sqlite %s < %s 2>/dev/null >/dev/null' % \
                      (dbpath, scheme))
        while 1:
            try:
                self.db = sqlite.connect(dbpath, client_encoding='utf-8',
                                         timeout=10)
                break
            except OperationalError, e:
                notifier.step(False, False)
        self.cursor = self.db.cursor()


    def commit(self):
        self.db.commit()

    def close(self):
        self.db.close()

    def execute(self, query):
        while 1:
            try:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            except OperationalError, e:
                notifier.step(False, False)
