# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# config.py - Handle the configuration files
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2007 Dirk Meyer, et al.
#
# First Edition: Krister Lagerstrom <krister-freevo@kmlager.com>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
import sys
import os
import logging

import kaa.strutils
import kaa.popcorn

import freevo.conf

# freevo imports
from freevo.ui import input, plugin

# import event names
from freevo.ui.event import *

# get logging object
log = logging.getLogger('config')

# generate config
pycfgfile = freevo.conf.datafile('freevo_config.py')
cfgdir = os.path.join(freevo.conf.SHAREDIR, 'config')
cfgsource = [ os.path.join(cfgdir, f) for f in os.listdir(cfgdir) ]
freevo.conf.xmlconfig(pycfgfile, cfgsource)
execfile(pycfgfile)

# add external stuff
config.add_variable('player', kaa.popcorn.config)

# load config
config.load(os.path.expanduser('~/.freevo/freevo2.conf'), create=True)

# plugins ist a list of known plugins
for p in plugins:
    c = config
    for attr in p.split('.'):
        c = getattr(c, attr)
    if c.activate:
        plugin.activate(p.replace('plugin.', '').replace('..', '.'), level=c.activate)
    
ICON_DIR  = os.path.join(freevo.conf.SHAREDIR, 'icons')
IMAGE_DIR = os.path.join(freevo.conf.SHAREDIR, 'images')

#
# Load old freevo_config.py:
#
FREEVO_CONFIG = os.path.join(freevo.conf.SHAREDIR, 'freevo_config.py')
if os.path.isfile(FREEVO_CONFIG):
    log.info('Loading cfg: %s' % FREEVO_CONFIG)
    execfile(FREEVO_CONFIG, globals(), locals())
    
else:
    log.critical("Error: %s: no such file" % FREEVO_CONFIG)
    sys.exit(1)


#
# Search for local_conf.py:
#

has_config = False
for a in sys.argv:
    if has_config == True:
        has_config = a
    if a == '-c':
        has_config = True
    
for dirname in freevo.conf.cfgfilepath:
    if isinstance(has_config, str):
        overridefile = has_config
    else:
        overridefile = dirname + '/local_conf.py'
    if os.path.isfile(overridefile):
        log.info('Loading cfg overrides: %s' % overridefile)
        execfile(overridefile, globals(), locals())
        break
