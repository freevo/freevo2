# ----------------------------------------------------------------------
# skin.py - This is the Freevo top-level skin code.
# ----------------------------------------------------------------------
# $Id$
# 
# Notes: This looks like some wierd kind of reversed inheritance or
#        something. Why do we call all these functions from impl. istead
#        of inheriting.. oh.. I don't get it.
# ----------------------------------------------------------------------
#
# $Log$
# Revision 1.7  2002/08/14 09:26:48  tfmalt
#  o Recommitted my changes. Updated all other files aswell. Now: this works
#    flawlessly for me. Please tell if it breaks something for others. I will
#    fix it ASAP.
#
# Revision 1.5  2002/08/13 23:49:51  tfmalt
# o Skin.py cleanup and rewrite. Trimmed to be only a middle layer between
#   the settings in freevo_config and the rest of the system.
#
# ----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
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
# ----------------------------------------------------------------------
"""
Works as a middle layer between the users preferred skin and rest of
the system.

Which skin you want to use is set in freevo_config.py. This small
module gets your skin preferences from the configuration file and loads
the correct skin implementation into the system.

The path to the skin implementation is also added to the system path.

get_singleton() returns an initialized skin object which is kept unique
and consistent throughout.
"""
__version__ = "$Revision$"
__date__    = "$Date$"
__author__  = """Krister Lagerstrom <krister@kmlager.com>,
Thomas malt <thomas@malt.no>""" # See, I snuck it in again ;)

import config # Freevo configuration.
import sys
import os.path

# Loads the skin implementation defined in freevo_config.py
sys.path += [os.path.dirname(config.OSD_SKIN)]
modname   = os.path.basename(config.OSD_SKIN)[:-3]
exec('import ' + modname  + ' as skinimpl')

_singleton = None

def get_singleton():
    """
    Returns an initialized skin object, containing the users preferred
    skin.
    """
    global _singleton
    if _singleton == None:
        _singleton = skinimpl.Skin()

    return _singleton

