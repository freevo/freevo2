#if 0 /*
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
# Revision 1.13  2004/05/31 10:41:22  dischi
# add function to get info about skin status
#
# Revision 1.12  2004/03/14 11:42:34  dischi
# make idlebar have a background image
#
# Revision 1.11  2004/02/24 19:36:25  dischi
# add function to change a skin area
#
# Revision 1.10  2004/02/14 13:01:08  dischi
# copy all needed function from the skin implementation to this module
#
# Revision 1.9  2003/12/06 16:49:09  dischi
# do not create a skin object for helpers
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

import config
import sys
import os.path

_singleton = None

# a list of all functions the skin needs to have
__all__ = ( 'Rectange', 'Image', 'Area', 'register', 'delete', 'change_area',
            'set_base_fxd', 'load', 'get_skins', 'get_settings',
            'toggle_display_style', 'get_display_style', 'get_popupbox_style',
            'get_font', 'get_image', 'get_icon', 'items_per_page', 'clear', 'redraw',
            'prepare', 'draw' )
    

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


def active():
    """
    returns if the skin is active right now (not cleared)
    """
    return not _singleton.force_redraw


if __freevo_app__ == 'main':
    # init the skin
    get_singleton()

    # the all function to this module
    for i in __all__:
        exec('%s = _singleton.%s' % (i,i))
        
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
    
