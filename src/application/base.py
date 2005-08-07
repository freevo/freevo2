# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# base.py - Basic Application
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

__all__ = [ 'Application' ]

# python imports
import logging

# freevo imports
import input
import eventhandler
import gui
import gui.animation 

# get logging object
log = logging.getLogger()


class Application(object):
    """
    A basic application
    """
    def __init__(self, name, eventmap, fullscreen, animated=False):
        """
        Init the Application object.

        @param name       : internal name of the application
        @param eventmap   : name of the event handler mapping
        @param fullscreen : if the application uses the whole screen
        @param animated   : use fade in/out animation
        """
        self.__name     = name
        self.__eventmap = eventmap
        self.__handler  = eventhandler.get_singleton()

        self.animated   = animated
        self.visible    = False
        self.stopped    = True
        self.fullscreen = fullscreen


    def eventhandler(self, event, menuw=None):
        """
        Eventhandler for this application
        """
        error = 'Error, no eventhandler defined for %s' % self.application
        raise AttributeError(error)


    def show(self):
        """
        Show this application. This function will return False if the
        application is already visible in case this function is overloaded.
        In case it is not overloaded, this function will also update the
        display.
        """
        if self.visible:
            # Already visible. But maybe stopped, correct that
            self.stopped = False
            return False
        # Set visible and append to the eventhandler
        self.visible = True
        self.stopped = False
        if not self in self.__handler:
            self.__handler.append(self)
        # Check if the new app uses animation to show itself
        if not self.animated:
            # This application has no animation for showing. But the old one
            # may have. So we need to wait until the renderer is done.
            # FIXME: what happens if a 'normal' animation is running?
            log.info('no show animation for %s -- waiting' % self.__name)
            gui.animation.render().wait()
        if self.__class__.show == Application.show:
            # show() is not changed in the inherting class. Update the display.
            gui.display.update()
        return True


    def hide(self):
        """
        Hide this application. This can be either because a different
        application has started or that the application was stopped and is no
        longer needed.
        """
        if not self.visible:
            # already hidden
            return
        # Wait until all application change animations are done. There
        # should be none, but just in case to avoid fading in and out the
        # same object.
        # FIXME: what happens if a 'normal' animation is running?
        gui.animation.render().wait()
        self.visible = False


    def stop(self):
        """
        Stop the application. If it is not shown again in the same cycle, the
        hide() function will be called.
        """
        self.stopped = True


    def set_eventmap(self, eventmap):
        """
        Set a new eventmap for the event handler
        """
        self.__eventmap = eventmap
        if self.__handler.get_active() == self:
            # We are the current application with the focus,
            # so set eventmap of the eventhandler to the new eventmap
            input.set_mapping(eventmap)


    def get_eventmap(self):
        """
        Return the eventmap for the application.
        """
        return self.__eventmap


    def get_name(self):
        """
        Get the name of the application.
        """
        return self.__name
    

    def __str__(self):
        """
        String for debugging.
        """
        return self.__name
        
