# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# debug.py -
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

import sys
import cPickle
import kaa.notifier

from mediadb import *
from mediadb.globals import *

def print_data(data, space='    '):
    for key, info in data.items():
        if key.startswith('_'):
            continue
        if isinstance(info, (list, tuple)):
            print '%s%s: [' % (space, key)
            for i in info:
                if isinstance(i, dict):
                    print_data(i, space + '  ')
                    print
                else:
                    print '%s  %s' % (space, i)
            print '%s  ]' % (space)

        else:
            print '%s%s: %s' % (space, key, info)
    if not data.has_key(MMINFO):
        return
    mminfo = cPickle.loads(data[MMINFO])
    print_data(mminfo, '      ')
    print

l = Listing(sys.argv[1])
if l.num_changes:
    print 'update listing', l.num_changes
    l.update(fast=False)

print
print 'Listing for %s' % l.cache.dirname
for key in l.cache.data:
    if not key.startswith('_'):
        print '  %s: %s' % (key, l.cache.data[key])
print
for file, info in l.cache.files.items():
    print '  %s' % file
    print_data(info)
print
for file, info in l.cache.overlay.items():
    print '  %s' % file
    print_data(info)
print
