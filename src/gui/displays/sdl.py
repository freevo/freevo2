# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# sdl.py - SDL output display
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2004/09/25 15:58:44  mikeruelle
# need this import for keyboard to work
#
# Revision 1.7  2004/09/25 05:17:59  rshortt
# This was broken because I removed rc.Keyboard.  Here I add Keyboard class
# to this module and also the default keymap.  All of this stuff should actually
# go away tomorrow or so.
#
# Revision 1.6  2004/08/27 14:17:55  dischi
# support holding a key pressed
#
# Revision 1.5  2004/08/24 16:42:42  dischi
# Made the fxdsettings in gui the theme engine and made a better
# integration for it. There is also an event now to let the plugins
# know that the theme is changed.
#
# Revision 1.4  2004/08/23 20:33:41  dischi
# smaller bugfixes, restart has some problems
#
# Revision 1.3  2004/08/23 14:29:46  dischi
# displays have information about animation support now
#
# Revision 1.2  2004/08/23 12:36:50  dischi
# cleanup, add doc
#
#
# -----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002 Krister Lagerstrom, et al.
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

# basic python imports
import time
import pygame
from pygame.locals import *

# mevas imports
from mevas.displays.pygamecanvas import PygameCanvas

# Freevo imports
import config
import rc
import eventhandler

DEFAULT_KEYMAP = {
    K_F1          : 'SLEEP',
    K_HOME        : 'MENU',
    K_g           : 'GUIDE',
    K_ESCAPE      : 'EXIT',
    K_UP          : 'UP',
    K_DOWN        : 'DOWN',
    K_LEFT        : 'LEFT',
    K_RIGHT       : 'RIGHT',
    K_SPACE       : 'SELECT',
    K_RETURN      : 'SELECT',
    K_F2          : 'POWER',
    K_F3          : 'MUTE',
    K_KP_MINUS    : 'VOL-',
    K_n           : 'VOL-',
    K_KP_PLUS     : 'VOL+',
    K_m           : 'VOL+',
    K_c           : 'CH+',
    K_v           : 'CH-',
    K_1           : '1',
    K_2           : '2',
    K_3           : '3',
    K_4           : '4',
    K_5           : '5',
    K_6           : '6',
    K_7           : '7',
    K_8           : '8',
    K_9           : '9',
    K_0           : '0',
    K_d           : 'DISPLAY',
    K_e           : 'ENTER',
    K_UNDERSCORE  : 'PREV_CH',
    K_o           : 'PIP_ONOFF',
    K_w           : 'PIP_SWAP',
    K_i           : 'PIP_MOVE',
    K_F4          : 'TV_VCR',
    K_r           : 'REW',
    K_p           : 'PLAY',
    K_f           : 'FFWD',
    K_u           : 'PAUSE',
    K_s           : 'STOP',
    K_F6          : 'REC',
    K_PERIOD      : 'EJECT',
    K_l           : 'SUBTITLE',
    K_a           : 'LANG'
    }

class Keyboard:
    """
    Class to handle keyboard input
    """
    def __init__(self, callback):
        """
        init the keyboard event handler
        """
        self.callback = callback


    def poll(self):
        """
        return next event
        """
        e = self.callback()
        if e:
            eventhandler.post_key(e)



class Display(PygameCanvas):
    """
    Display class for SDL output
    """
    def __init__(self, size, default=False):
        PygameCanvas.__init__(self, size)
        self.mousehidetime = time.time()
        rc.get_singleton().inputs.append(Keyboard(self.poll))
        self.running = True
        self.animation_possible = True
        pygame.key.set_repeat(500, 30)

        
    def hide(self):
        """
        Hide the output display. In most cases this does nothing since
        a simple window doesn't matter. If OSD_STOP_WHEN_PLAYING the
        ygame display will be shut down.
        """
        if config.OSD_STOP_WHEN_PLAYING:
            self.stop()


    def show(self):
        """
        Show the output window again if it is not visible
        """
        if config.OSD_STOP_WHEN_PLAYING:
            self.restart()


    def stop(self):
        """
        Stop the display
        """
        if self.running:
            pygame.display.quit()
            self.freeze()
            self.running = False

        
    def restart(self):
        """
        Restart the display if it is currently stopped
        """
        if not self.running:
            self._screen  = pygame.display.set_mode((self.width, self.height), 0, 32)
            self.thaw()
            self.running = True

        
    def poll(self, map=True):
        """
        callback for SDL event
        """
        if not pygame.display.get_init():
            return
        
        # Check if mouse should be visible or hidden
        mouserel = pygame.mouse.get_rel()
        mousedist = (mouserel[0]**2 + mouserel[1]**2) ** 0.5

        if mousedist > 4.0:
            pygame.mouse.set_visible(1)
            self.mousehidetime = time.time() + 1.0  # Hide the mouse in 2s
        else:
            if time.time() > self.mousehidetime:
                pygame.mouse.set_visible(0)

        # Return the next key event, or None if the queue is empty.
        # Everything else (mouse etc) is discarded.
        while 1:
            event = pygame.event.poll()

            if event.type == NOEVENT:
                return
            
            if event.type == KEYDOWN:
                # FIXME: map support not integrated yet
                if not map and event.key > 30:
                    try:
                        if event.unicode != u'':
                            return event.unicode
                    except:
                        pass
                    
                if event.key in DEFAULT_KEYMAP.keys():
                    # FIXME: Turn off the helpscreen if it was on
                    return DEFAULT_KEYMAP[event.key]

                elif event.key == K_h:
                    print 'FIXME: add help'

                elif event.key == K_z:
                    print 'FIXME: toogle fullscreen'

                elif event.key == K_F10:
                    # Take a screenshot
                    print 'FIXME: take screenshot'

                else:
                    # don't know what this is, return it as it is
                    try:
                        if event.unicode != u'':
                            return event.unicode
                    except:
                        return None
        

