# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mediainfo.py - 
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
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

import time
import sys
import os
import stat
import mmpython
import pickle
import cPickle
import re
import logging
import copy

from mmpython.disc.discinfo import cdrom_disc_id

import sysconfig
import config
import util.fxdparser
import util.vfs as vfs
import util.cache as cache
from util.callback import *

log = logging.getLogger('mediainfo')


def print_data(data, space='    '):
    for key, info in data.items():
        if isinstance(info, (list, tuple)):
            print '%s%s: [' % (space, key)
            for i in info:
                if isinstance(i, dict):
                    print_data(i, space + '  ')
                    print
                else:
                    print '%s  %s' % (space, i)
            print '%s  ]' % (space)

        elif not key in ( 'mminfo', 'fxd' ):
            print '%s%s: %s' % (space, key, info)
    if not data.has_key('mminfo'):
        return
    mminfo = cPickle.loads(data['mminfo'])
    print_data(mminfo, '      ')
    print


# XXX MEDIAINFO UPDATE XXX
t1 = time.time()
l = Listing(sys.argv[1])
t2 = time.time()
l.update()
t3 = time.time()
print 'time: %s %s' % (t2 - t1, t3 - t1)
print
print
print 'Listing for %s' % l.cache.dirname
for key in l.cache.data:
    if not key in ('overlay', 'items'):
        print '  %s: %s' % (key, l.cache.data[key])
print
for file, info in l.cache.items.items():
    print '  %s' % file
    print_data(info)
print
for file, info in l.cache.overlay.items():
    print '  %s' % file
    print_data(info)
print
