#if 0 /*
# -----------------------------------------------------------------------
# shutdown.py  -  shutdown plugin / handling
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.6  2004/06/09 19:42:08  dischi
# fix crash
#
# Revision 1.5  2004/06/06 14:16:08  dischi
# small fix for confirm and enable shutdown sys
#
# Revision 1.4  2004/05/30 18:28:15  dischi
# More event / main loop cleanup. rc.py has a changed interface now
#
# Revision 1.3  2004/03/14 11:50:02  dischi
# added restart
#
# 
# Revision 1.3  2004/03/12 02:45:44 dopeflish
# add system restart function
#
# Revision 1.2  2004/01/19 20:25:53  dischi
# sync metainfo before stopping
#
# Revision 1.1  2003/12/30 15:30:08  dischi
# put all shutdown stuff into one file
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
import time
import sys

import config

from gui import ConfirmBox
from item import Item
from plugin import MainMenuPlugin


def shutdown(menuw=None, argshutdown=None, argrestart=None, exit=False):
    """
    Function to shut down freevo or the whole system. This system will be
    shut down when argshutdown is True, restarted when argrestart is true,
    else only Freevo will be stopped.
    """
    import osd
    import plugin
    import rc
    import util.mediainfo
    
    osd = osd.get_singleton()

    util.mediainfo.sync()
    if not osd.active:
        # this function is called from the signal handler, but
        # we are dead already.
        sys.exit(0)

    osd.clearscreen(color=osd.COL_BLACK)
    osd.drawstringframed(_('shutting down...'), 0, 0, osd.width, osd.height,
                         osd.getfont(config.OSD_DEFAULT_FONTNAME,
                                     config.OSD_DEFAULT_FONTSIZE),
                         fgcolor=osd.COL_ORANGE, align_h='center', align_v='center')
    osd.update()
    time.sleep(0.5)

    if argshutdown or argrestart:  
        # shutdown dual head for mga
        if config.CONF.display == 'mga':
            os.system('%s runapp matroxset -f /dev/fb1 -m 0' % \
                      os.environ['FREEVO_SCRIPT'])
            time.sleep(1)
            os.system('%s runapp matroxset -f /dev/fb0 -m 1' % \
                      os.environ['FREEVO_SCRIPT'])
            time.sleep(1)

        plugin.shutdown()
        rc.shutdown()
        osd.shutdown()

        if argshutdown and not argrestart:
            os.system(config.SHUTDOWN_SYS_CMD)
        elif argrestart and not argshutdown:
            os.system(config.RESTART_SYS_CMD)
        # let freevo be killed by init, looks nicer for mga
        while 1:
            time.sleep(1)
        return

    #
    # Exit Freevo
    #
    
    # Shutdown any daemon plugins that need it.
    plugin.shutdown()

    # Shutdown all children still running
    rc.shutdown()

    # SDL must be shutdown to restore video modes etc
    osd.clearscreen(color=osd.COL_BLACK)
    osd.shutdown()

    if exit:
        # realy exit, we are called by the signal handler
        sys.exit(0)

    os.system('%s stop' % os.environ['FREEVO_SCRIPT'])

    # Just wait until we're dead. SDL cannot be polled here anyway.
    while 1:
        time.sleep(1)
        


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
                          (self.confirm_system, _('Shutdown system') ),
                          (self.confirm_system_restart, _('Restart system') ) ]
        else:
            items = [ (self.shutdown_freevo, _('Shutdown Freevo') ),
                          (self.shutdown_system, _('Shutdown system') ),
                          (self.shutdown_system_restart, _('Restart system') ) ]
        if config.ENABLE_SHUTDOWN_SYS:
            items = [ items[1], items[0], items[2] ]

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

    def confirm_system_restart(self, arg=None, menuw=None):
        """
        Pops up a ConfirmBox.
        """
        self.menuw = menuw
        what = _('Do you really want to restart the system?')
        ConfirmBox(text=what, handler=self.shutdown_system_restart, default_choice=1).show()


    def shutdown_freevo(self, arg=None, menuw=None):
        """
        shutdown freevo, don't shutdown the system
        """
        shutdown(menuw=menuw, argshutdown=False, argrestart=False)

        
    def shutdown_system(self, arg=None, menuw=None):
        """
        shutdown the complete system
        """
        shutdown(menuw=menuw, argshutdown=True, argrestart=False)

    def shutdown_system_restart(self, arg=None, menuw=None):
        """
        restart the complete system
        """
        shutdown(menuw=menuw, argshutdown=False, argrestart=True)

        
        


#
# the plugins defined here
#

class PluginInterface(MainMenuPlugin):
    """
    Plugin to shutdown Freevo from the main menu
    """

    def items(self, parent):
        return [ ShutdownItem(parent) ]


