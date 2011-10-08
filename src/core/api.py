# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# api.py - API to access various Freevo classes and objects needed for plugins
# -----------------------------------------------------------------------------
# $Id$
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

__all__ = [ 'FREEVO_SHARE_DIR', 'FREEVO_DATA_DIR', 'config', 'Plugin', 'load_plugins',
            'activate_plugin', 'register_plugin', 'get_plugin', 'signals', 'ResourceHandler' ]

# python imports
import os

# freevo core imports
from xmlconfig import xmlconfig

# freevo.core imports
import event
from plugin import *

# directory variables
FREEVO_INSTALL_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../../..'))
FREEVO_SHARE_DIR = os.path.abspath(os.path.join(FREEVO_INSTALL_DIR, 'share/freevo2'))
FREEVO_DATA_DIR = '/var/lib/freevo'
if os.getuid():
    FREEVO_DATA_DIR = os.path.expanduser('~/.freevo/data')
if not os.path.isdir(FREEVO_DATA_DIR):
    os.makedirs(FREEVO_DATA_DIR)

# generate config
pycfgfile = os.path.join(FREEVO_DATA_DIR, 'freevo_config.py')
cfgdir = os.path.join(FREEVO_SHARE_DIR, 'config')
cfgsource = [ os.path.join(cfgdir, f) for f in os.listdir(cfgdir) if f.endswith('.cxml') ]
xmlconfig(pycfgfile, cfgsource, 'freevo.ui')

# load config structure. This will add 'config', 'plugins' and 'events'
execfile(pycfgfile)

# create empty signals dict
signals = {}

# add events defined in xml config to event.py.
for e in events:
    setattr(event, e, event.Event(e))

# activate plugins from config
def load_plugins(module):
    for plugin in plugins:
        group = config
        for attr in plugin.split('.'):
            group = getattr(group, attr)
        if group.activate:
            plugin = plugin.replace('plugin.', '').replace('..', '.')
            if isinstance(group.activate, bool):
                activate_plugin(plugin)
            else:
                activate_plugin(plugin, level=group.activate)
    init_plugins(module)

from resources import ResourceHandler

import beacon
