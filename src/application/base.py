# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# base.py - Basic Application inside Freevo
# -----------------------------------------------------------------------
# $Id$
#
# Notes: 
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/08/26 15:32:35  dischi
# some logic change
#
# Revision 1.1  2004/08/25 12:51:43  dischi
# moved Application for eventhandler into extra dir for future templates
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


import traceback

import eventhandler
import gui


class Application:
    """
    A basic application
    """
    def __init__(self, name, event_context, fullscreen, animated=False):
        self._evt_name       = name
        self._evt_context    = event_context
        self._evt_fullscreen = fullscreen
        self._evt_handler    = eventhandler.get_singleton()
        self._evt_stopped    = False
        self._animated       = animated
        self.post_event      = self._evt_handler.post
        self.visible         = False

        
    def eventhandler(self, event, menuw=None):
        """
        eventhandler for this application
        """
        print 'Error, no eventhandler defined for %s' % self.application


    def show(self):
        """
        Show this application. This function will return False if the
        application is already visible in case this function is overloaded.
        In case it is not overloaded, this function will also update the
        display.
        """
        if self.visible:
            return False
        self.visible = True
        self._evt_handler.append(self)
        # check if the new app uses animation to show itself
        if not self._animated:
            _debug_('no show animation for %s -- waiting' % self)
            gui.animation.render().wait()
        if traceback.extract_stack(limit = 2)[0][3] != 'Application.show(self)':
            gui.display.update()
        return True

        
    def hide(self):
        """
        Hide this application. This can be either because a different application
        has started or that the application was stopped and is no longer needed.
        """
        if self.visible:
            # wait until all application change animations are
            # done. There should be none, but just in case to
            # avoid fading in and out the same object
            gui.animation.render().wait()
        self.visible = False


    def stop(self):
        """
        Stop the application. If it is not shown again in the same cycle, the
        hide() function will be called.
        """
        self._evt_stopped = True
