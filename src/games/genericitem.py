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
# Revision 1.7  2004/06/06 16:53:39  mikeruelle
# use list version of command for better options parsing regarding things with spaces in there names
#
# Revision 1.6  2004/01/19 21:32:58  mikeruelle
#  a patch from Sylvian to use the new set_url stuff
#
# Revision 1.5  2004/01/14 18:29:49  mikeruelle
# .
#
# Revision 1.4  2003/12/29 22:30:35  dischi
# move to new Item attributes
#
# Revision 1.3  2003/11/29 11:39:38  dischi
# use the given menuw abd not a global one
#
# Revision 1.2  2003/09/25 21:19:57  mikeruelle
# fix crash for missing arg
#
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
        Item.__init__(self, parent)
        self.type  = 'generic'            # fix value
        self.set_url(file, info=True)
        self.parent = parent

        self.name = os.path.splitext(os.path.basename(file))[0]

        # find image for this file
        # find image for this file
        shot = imgpath + '/' + \
               os.path.splitext(os.path.basename(file))[0] + ".png"
        if os.path.isfile(shot):
            self.image = shot
        elif os.path.isfile(os.path.splitext(file)[0] + ".png"):
            self.image = os.path.splitext(file)[0] + ".png"

        command = ['--prio=%s' % config.GAMES_NICE, cmd]
	command.extend(args.split())
	command.append(file)

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


    def play(self, arg=None, menuw=None):
        self.parent.current_item = self

        if not self.menuw:
            self.menuw = menuw

        if self.menuw.visible:
            self.menuw.hide()

        print "Playing:  %s" % self.filename

        self.game_player.play(self, menuw)


    def stop(self, menuw=None):
        self.game_player.stop()


    def eventhandler(self, event, menuw=None):

        if event == em.STOP:
            self.stop()
            rc.app(None)
            if not menuw == None:
                menuw.refresh(reload=1)

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)

