# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# api.py - API to access various Freevo classes and objects needed for plugins
# -----------------------------------------------------------------------------
# $Id: __init__.py 10817 2008-06-20 15:41:17Z dmeyer $
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2009 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
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

__all__ = [ 'config', 'plugins', 'util' ]

# python imports
import os

# freevo core imports
import freevo.conf
import freevo.xmlconfig

# freevo.ui imports
import event

# expose SHAREDIR to other modules
SHAREDIR = freevo.conf.SHAREDIR

# generate config
pycfgfile = freevo.conf.datafile('freevo_config.py')
cfgdir = os.path.join(SHAREDIR, 'config')
cfgsource = [ os.path.join(cfgdir, f) for f in os.listdir(cfgdir) if f.endswith('.cxml') ]
freevo.xmlconfig.xmlconfig(pycfgfile, cfgsource, 'freevo.ui')

# load config structure. This will add 'config', 'plugins' and 'events'
execfile(pycfgfile)

# add events defined in xml config to event.py.
for e in events:
    setattr(event, e, event.Event(e))

import util
