#if 0 /*
# -----------------------------------------------------------------------
# genericitem.py - Item for generic objects
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/09/05 20:47:29  mikeruelle
# new games system additions
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
import game

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

import rc
import time
import copy

from item import Item
import event as em
from struct import *
from string import *
from re import *


class GenericItem(Item):
    def __init__(self, file, cmd = None, args = None, imgpath = None, parent = None):
        Item.__init__(self)
        self.type  = 'generic'         # fix value
        self.mode  = 'file'            # file, dvd or vcd
        self.filename = file

        self.name = os.path.splitext(os.path.basename(file))[0]
        self.xml_file = None
        self.parent = parent

        # find image for this file
        # find image for this file
        shot = imgpath + '/' + \
               os.path.splitext(os.path.basename(file))[0] + ".png"
        if os.path.isfile(shot):
            self.image = shot
        elif os.path.isfile(os.path.splitext(file)[0] + ".png"):
            self.image = os.path.splitext(file)[0] + ".png"

        command = '--prio=%s %s %s' % (config.GAMES_NICE,
                                       cmd,
                                       args)

        romname = os.path.basename(file)
        romdir = os.path.dirname(file)
        command = '%s "%s"' % (command, file)

        self.command = command

        self.game_player = game.get_singleton()


    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        return self.name


    # ------------------------------------------------------------------------
    # actions:


    def actions(self):
        return [ ( self.play, 'Play' ) ]


    def play(self, menuw=None):
        self.parent.current_item = self

        if not self.menuw:
            self.menuw = menuw

        if self.menuw.visible:
            self.menuw.hide()

        print "Playing:  %s" % self.filename

        self.game_player.play(self)


    def stop(self, menuw=None):
        self.game_player.stop()


    def eventhandler(self, event, menuw=None, mythread=None):

        if not mythread == None:
            if event == em.STOP:
                self.stop()
                rc.app(None)
                if not menuw == None:
                    menuw.refresh(reload=1)

            elif event == em.MENU:
                mythread.app.write('M')

            elif event == em.GAMES_CONFIG:
                mythread.cmd( 'config' )

            elif event == em.PAUSE or event == em.PLAY:
                mythread.cmd('pause')

            elif event == em.GAMES_RESET:
                mythread.cmd('reset')

            elif event == em.GAMES_SNAPSHOT:
                mythread.cmd('snapshot')

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)

