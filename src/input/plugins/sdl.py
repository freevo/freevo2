#if 0 /*
# -----------------------------------------------------------------------
# sdl.py - SDL input support using pygame.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/09/25 04:42:22  rshortt
# An SDL input handler using pygame.  This may work already but is still a
# work in progress.  Freevo still gets its input using src/gui/displays/sdl.py
# for the time being.  We need to work on universal user defined keymaps.
#
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

import time
import pygame
from pygame.locals import *

import config
import plugin
import rc

rc = rc.get_singleton()

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
    

class PluginInterface(plugin.Plugin):

    def __init__(self):
        plugin.Plugin.__init__(self)

        self.plugin_name = 'SDLINPUT'
        self.mousehidetime = time.time()
        pygame.key.set_repeat(500, 30)

        rc.inputs.append(self)


    def config(self):
        return [
                ( 'SDL_KEYMAP', {0:0}, 'Default keymap for SDL input.' ),
               ]


    def poll(selfi, map=True):
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



