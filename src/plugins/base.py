#if 0 /*
# -----------------------------------------------------------------------
# base.py  -  Some basic plugins
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.10  2003/11/30 14:36:42  dischi
# new skin handling
#
# Revision 1.9  2003/10/29 20:47:44  dischi
# make it possible to bypass confirmation of shutdown
#
# Revision 1.8  2003/10/29 03:37:46  krister
# Added confirmation of shutdown. Do we need an option to disable this?
#
# Revision 1.7  2003/10/04 18:37:29  dischi
# i18n changes and True/False usage
#
# Revision 1.6  2003/09/14 20:09:36  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.5  2003/09/13 10:08:22  dischi
# i18n support
#
# Revision 1.4  2003/08/24 06:58:18  gsbarbieri
# Partial support for "out" icons in main menu.
# The missing part is in listing_area, which have other changes to
# allow box_under_icon feature (I mailed the list asking for opinions on
# that)
#
# Revision 1.3  2003/04/24 19:56:34  dischi
# comment cleanup for 1.3.2-pre4
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

import os

import config

from gui import ConfirmBox
from item import Item
from plugin import MainMenuPlugin


class ShutdownItem(Item):
    """
    Item for shutdown
    """
    def __init__(self, parent=None):
        Item.__init__(self, parent, skin_type='shutdown')
        self.menuw = None


    def actions(self):
        """
        return a list of actions for this item
        """
        if config.CONFIRM_SHUTDOWN:
            items = [ (self.confirm_freevo, _('Shutdown Freevo') ),
                      (self.confirm_system, _('Shutdown system') ) ]
        else:
            items = [ (self.shutdown_freevo, _('Shutdown Freevo') ),
                      (self.shutdown_system, _('Shutdown system') ) ]
        if config.ENABLE_SHUTDOWN_SYS:
            items.reverse()
        return items


    def confirm_freevo(self, arg=None, menuw=None):
        """
        Pops up a ConfirmBox.
        """
        self.menuw = menuw
        what = _('Do you really want to shut down Freevo?')
        ConfirmBox(text=what, handler=self.shutdown_freevo, default_choice=1).show()
        
        
    def confirm_system(self, arg=None, menuw=None):
        """
        Pops up a ConfirmBox.
        """
        self.menuw = menuw
        what = _('Do you really want to shut down the system?')
        ConfirmBox(text=what, handler=self.shutdown_system, default_choice=1).show()
        

    def shutdown_freevo(self, arg=None, menuw=None):
        """
        shutdown freevo, don't shutdown the system
        """
        import main
        if not self.menuw:
            self.menuw = menuw
        main.shutdown(menuw=self.menuw, arg=False)

        
    def shutdown_system(self, arg=None, menuw=None):
        """
        shutdown the complete system
        """
        import main
        if not self.menuw:
            self.menuw = menuw
        main.shutdown(menuw=self.menuw, arg=True)
        
        


#
# the plugins defined here
#

class shutdown(MainMenuPlugin):
    """
    Plugin to shutdown Freevo from the main menu
    """

    def items(self, parent):
        return [ ShutdownItem(parent) ]


