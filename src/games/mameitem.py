# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# mameitem.py - Item for mame objects
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.22  2005/01/08 15:40:51  dischi
# remove TRUE, FALSE, DEBUG and HELPER
#
# Revision 1.21  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.20  2004/06/06 16:53:39  mikeruelle
# use list version of command for better options parsing regarding things
# with spaces in there names
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


import os
import re

import config
import util
import game
import rc

import menu
import event as em
import time
import copy
import mame_cache

from item import Item


class MameItem(Item):
    def __init__(self, title, file, image = None, cmd = None, args = None, imgpath = None, parent = None, info = None):
        Item.__init__(self, parent)
        self.type  = 'mame'            # fix value
        self.set_url(file, info=True)
        self.image = image
        self.name  = title
        self.parent = parent

        # find image for this file
        if image == None:
            shot = imgpath + '/' + \
                os.path.splitext(os.path.basename(file))[0] + ".png"
            if os.path.isfile(shot):
                self.image = shot
            elif os.path.isfile(os.path.splitext(file)[0] + ".png"):
                self.image = os.path.splitext(file)[0] + ".png"

        command = ['--prio=%s' % config.GAMES_NICE, cmd]
        command.extend(args.split())

        # Some files needs special arguments to mame, they can be
        # put in a <file>.mame options file. The <file>
        # includes the suffix (.zip, etc)!
        # The arguments in the options file are added at the end of the
        # regular mame arguments.
        if os.path.isfile(file + '.mame'):
	    addargs = open(filename + '.mame').read().strip()
            command.extend(addargs.split())
            print 'Read additional options = "%s"' % addargs

        command.append(file)

        self.command = command

        self.game_player = game.get_singleton()
	if info:
	    self.info = { 'description' : '%s - %s - %s' % (info['description'],info['manufacturer'],info['year']) }
	else:
	    self.info = { 'description' : 'No ROM information' }
        

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

