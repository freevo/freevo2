#if 0 /*
# -----------------------------------------------------------------------
# skin.py - This is the Freevo top-level skin code.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/04/24 19:55:55  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.1  2002/11/24 13:58:44  dischi
# code cleanup
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
#endif
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

DEBUG = config.DEBUG

# Loads the skin implementation defined in freevo_config.py
sys.path += [os.path.dirname(config.OSD_SKIN)]
modname   = os.path.basename(config.OSD_SKIN)[:-3]
exec('import ' + modname  + ' as skinimpl')

if DEBUG: print 'Imported skin %s' % config.OSD_SKIN
    
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

