# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# skin.py - This is the Freevo top-level skin code.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#    Works as a middle layer between the users preferred skin and rest of
#    the system.
#    
#    Which skin you want to use is set in freevo_config.py. This small
#    module gets your skin preferences from the configuration file and loads
#    the correct skin implementation into the system.
#    
#    The path to the skin implementation is also added to the system path.
#    
#    get_singleton() returns an initialized skin object which is kept unique
#    and consistent throughout.
#
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.20  2004/08/05 17:37:35  dischi
# remove more functions
#
# Revision 1.19  2004/08/01 10:54:15  dischi
# remove outdated code
#
# Revision 1.18  2004/07/25 18:22:27  dischi
# changes to reflect gui update
#
# Revision 1.17  2004/07/24 12:23:09  dischi
# replaced osd.py with a dummy
#
# Revision 1.16  2004/07/23 19:44:00  dischi
# move most of the settings code out of the skin engine
#
# Revision 1.15  2004/07/22 21:18:37  dischi
# replaced code with dummy pointing into gui
#
# Revision 1.14  2004/07/10 12:33:36  dischi
# header cleanup
#
# Revision 1.13  2004/05/31 10:41:22  dischi
# add function to get info about skin status
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


import config
import sys
import os.path

_singleton = None

# a list of all functions the skin needs to have
__all__ = ( 'Rectange', 'Image', 'Area', 'register', 'delete', 'change_area',
            'toggle_display_style', 'items_per_page', 'clear', 'draw' )
    
__all__gui__ = ( 'get_settings', 'get_font', 'get_image', 'get_icon' )
    

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

        import gui
        _singleton = gui.get_skin()
    return _singleton


if __freevo_app__ == 'main':
    # init the skin
    get_singleton()

    # the all function to this module
    for i in __all__:
        exec('%s = _singleton.%s' % (i,i))

    import gui
    
    for i in __all__gui__:
        exec('%s = gui.%s' % (i,i))

else:
    # set all skin functions to the dummy function so nothing
    # bad happens when we call it from inside a helper
    class dummy_class:
        def __init__(*arg1, **arg2):
            pass
        
    def dummy_function(*arg1, **arg2):
        pass

    for i in __all__:
        if i[0] == i[0].upper():
            exec('%s = dummy_class' % i)
        else:
            exec('%s = dummy_function' % i)
    
