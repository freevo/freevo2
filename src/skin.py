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
# Revision 1.9  2003/12/06 16:49:09  dischi
# do not create a skin object for helpers
#
# Revision 1.8  2003/11/28 19:26:36  dischi
# renamed some config variables
#
# Revision 1.7  2003/09/23 13:42:01  outlyer
# Removed more chatter.
#
# Revision 1.6  2003/09/14 20:09:36  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.5  2003/08/23 12:51:41  dischi
# removed some old CVS log messages
#
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

_singleton = None

def get_singleton():
    """
    Returns an initialized skin object, containing the users preferred
    skin.
    """
    global _singleton
    if _singleton == None:
        # we don't need this for helpers
        if config.HELPER:
            return None
    
        # Loads the skin implementation defined in freevo_config.py
        exec('import skins.' + config.SKIN_MODULE  + '.' + config.SKIN_MODULE  + \
             ' as skinimpl')

        _debug_('Imported skin %s' % config.SKIN_MODULE,2)
    
        _singleton = skinimpl.Skin()

    return _singleton

