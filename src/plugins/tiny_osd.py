# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# time_osd.py - An osd for Freevo
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#   This plugin is an osd for freevo. It displays the message send by the
#   event OSD_MESSAGE
#
#   This file should be called osd.py, but this conflicts with the global
#   osd.py. This global file should be renamed, because it's no osd, it's
#   a render engine
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.21  2005/06/04 17:18:13  dischi
# adjust to gui changes
#
# Revision 1.20  2005/05/05 17:34:00  dischi
# adjust to new gui submodule imports
#
# Revision 1.19  2005/02/06 16:59:12  dischi
# small bugfixes from Viggo Fredriksen
#
# Revision 1.18  2004/12/31 11:57:44  dischi
# renamed SKIN_* and OSD_* variables to GUI_*
#
# Revision 1.17  2004/11/20 18:23:03  dischi
# use python logger module for debug
#
# Revision 1.16  2004/10/08 20:19:35  dischi
# register to OSD_MESSAGE only
#
# Revision 1.15  2004/10/06 19:24:02  dischi
# switch from rc.py to pyNotifier
#
# Revision 1.14  2004/08/22 20:12:16  dischi
# changes to new mevas based gui code
#
# Revision 1.13  2004/08/01 10:49:06  dischi
# move to new gui code
#
# Revision 1.12  2004/07/24 12:23:39  dischi
# deactivate plugin
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

# external imports
import notifier

# freevo imports
import config
import plugin
import gui
import gui.widgets
import gui.theme

from event import OSD_MESSAGE

import logging
log = logging.getLogger()

class PluginInterface(plugin.DaemonPlugin):
    """
    osd plugin.

    This plugin shows messages send from other parts of Freevo on
    the screen for 2 seconds.

    activate with plugin.activate('plugin.tiny_osd')
    """
    def __init__(self):
        """
        init the osd
        """
        plugin.DaemonPlugin.__init__(self)
        self.events = [ 'OSD_MESSAGE' ]
        self.message = ''
        self.gui_object = None
        self._timer_id  = None


    def update(self):
        """
        update the display
        """
        display = gui.display
        if self.gui_object:
            # remove the current text from the display
            self.gui_object.unparent()
            self.gui_object = None

        if not self.message:
            # if we don't have a text right now,
            # update the display without the old message
            display.update()
            return

        # get the osd from from the settings
        font = gui.theme.font('osd')

        over_x = config.GUI_OVERSCAN_X
        over_y = config.GUI_OVERSCAN_Y

        # create the text object
        y = over_y + 10
        if plugin.getbyname('idlebar') != None:
            y += 60


        self.gui_object = gui.widgets.Text(self.message, (over_x, y),
                                           (display.width - 10 - 2 * over_x,
                                            over_y + 10 + font.height),
                                           font, align_h='right')

        # make sure the object is on top of everything else
        self.gui_object.set_zindex(200)

        # add the text and update the display
        display.add_child(self.gui_object)
        display.update()


    def eventhandler(self, event, menuw=None):
        """
        catch OSD_MESSAGE and display it, return False, maybe someone
        else is watching for the event.
        """
        if event == OSD_MESSAGE:
            self.message = event.arg
            if self._timer_id != None:
                # a not used callback is active, remove it
                notifier.removeTimer( self._timer_id )
            # register a callback in 2 seconds for hiding
            self._timer_id = notifier.addTimer( 2000,
                                                notifier.Callback( self.hide ) )
            self.update()
        return False


    def hide(self):
        """
        Hide the osd
        """
        self.message = ''
        self._timer_id = None
        self.update()

        return False
