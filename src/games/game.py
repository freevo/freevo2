#if 0 /*
# -----------------------------------------------------------------------
# game.py - Freevo module to run games. 
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.15  2004/06/06 17:23:37  mikeruelle
# remove bad kill command
#
# Revision 1.14  2004/01/14 18:29:49  mikeruelle
# .
#
# Revision 1.13  2003/11/29 11:39:38  dischi
# use the given menuw abd not a global one
#
# Revision 1.12  2003/10/23 00:30:42  rshortt
# Bugfix for xmame.x11.  Since our new process code xmame will go defunct after
# exit and Freevo will hang.  This used to happen with xmame.SDL and the
# wait() call I am removing was the solution.  I hope that is no longer needed
# without runapp.
#
# Revision 1.11  2003/09/13 10:08:22  dischi
# i18n support
#
# Revision 1.10  2003/09/01 19:46:02  dischi
# add menuw to eventhandler, it may be needed
#
# Revision 1.9  2003/08/23 12:51:42  dischi
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


import sys
import random
import time, os, glob
import string, popen2, fcntl, select, struct
import threading, signal

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications
import menu       # The menu widget class
import osd        # The OSD class, used to communicate with the OSD daemon
import rc         # The RemoteControl class.
import plugin
import event as em

DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

# Setting up the default objects:
osd        = osd.get_singleton()

# Module variable that contains an initialized Game() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = Game()
        
    return _singleton

class Game:

    def __init__(self):
        self.mode = None
        self.app_mode = 'games'

    def play(self, item, menuw):

        self.item = item
        self.filename = item.filename 
        self.command = item.command
        self.mode = item.mode
        self.menuw = menuw
        
        if not os.path.isfile(self.filename):
            osd.clearscreen()
            osd.drawstring(_('File "%s" not found!') % self.filename, 30, 280)
            osd.update()
            time.sleep(2.0) 
            self.menuw.refresh()
            return 0

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        if DEBUG:
            print 'Game.play(): Starting thread, cmd=%s' % self.command
        
	self.app=GameApp(self.command, stop_osd=1)
        self.prev_app = rc.app()
        rc.app(self)

    def stop(self):
        self.app.stop()
	rc.app(None)

    def eventhandler(self, event, menuw=None):
        return self.item.eventhandler(event, self.menuw)

 
# ======================================================================
class GameApp(childapp.ChildApp2):
    def stop_event(self):
        return em.STOP
