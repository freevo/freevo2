# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# sysconfig.py - Basic configuration for some utils used in Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# DEPRECATED, use conf from freevo core.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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

__all__ = [ 'CONF', 'cachefile', 'datafile' ]

# Python imports
import os
import sys
import locale
import __builtin__

# new style: use freevo.conf from core
from freevo import conf

# Dummy class for the CONF
class struct(object):
    pass

CONF = struct()

# find the currect encoding
CONF.default_encoding = conf.ENCODING
CONF.encoding = CONF.default_encoding

CONF.cachedir = conf.CACHEDIR
CONF.datadir  = conf.DATADIR
CONF.logdir   = conf.LOGDIR

CONFIGFILE = ''

# read the config file, if no file is found, the default values
# are used.
for dirname in conf.cfgfilepath:
    conffile = os.path.join(dirname, 'freevo.conf')
    if os.path.isfile(conffile):
        c = open(conffile)
        for line in c.readlines():
            if line.startswith('#'):
                continue
            if line.find('=') == -1:
                continue
            vals = line.strip().split('=')
            if not len(vals) == 2:
                print 'invalid config entry: %s' % line
                continue
            name, val = vals[0].strip(), vals[1].strip()
            CONF.__dict__[name] = val

        c.close()
        CONFIGFILE = conffile
        break


# add everything in CONF to the module variable list (but in upper
# case, so CONF.xxx is XXX, too
for key in CONF.__dict__:
    exec('%s = CONF.%s' % (key.upper(), key))


# helper functions to get dirs
cachefile = conf.cachefile
datafile  = conf.datafile
logfile   = conf.logfile
