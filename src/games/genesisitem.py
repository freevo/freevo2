# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# genesisitem.py - Item for GENESIS/MEGADRIVE objects
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.8  2004/06/06 16:53:39  mikeruelle
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
from zipped_rom import unzip_rom

# Extensions used by GENESIS ROMs
genesisromExtensions = ['smd', 'bin']

class GenesisItem(Item):
    def __init__(self, file, cmd = None, args = None, imgpath = None, parent = None):
        Item.__init__(self, parent)
        self.type  = 'genesis'            # fix value
        self.set_url(file, info=True)
        self.parent = parent
        romName = ''

        genesisFile = None
        unzipped = unzip_rom(file, genesisromExtensions)
        if unzipped:
            genesisFile = open(unzipped, 'rb')
        else:
            genesisFile = open(file, 'rb')

        fileExt = lower(os.path.splitext(os.path.basename(file))[1])
        if  fileExt == '.bin':
            genesisFile.seek(0x120)
            romName = genesisFile.read(48)
        elif fileExt == '.smd':
            for i in range(24):
                genesisFile.seek(0x2290+i)
                romName += genesisFile.read(1)
                genesisFile.seek(0x290+i)
                romName += genesisFile.read(1)
        else:
            romName = os.path.splitext(os.path.basename(file))[0]
        genesisFile.close()
        if unzipped:
            os.unlink(unzipped)
        # Some guys modify the internal rom name with som crap -> detect it now
        if lower(romName[0:6]) == 'dumped' or lower(romName[0:6]) == 'copied':
            self.name =  os.path.splitext(os.path.basename(file))[0]
        else:
            if match('[a-zA-Z0-9 ]{4}', romName[0:4]) == None or romName[0:1] == ' ':
                self.name =  os.path.splitext(os.path.basename(file))[0]
            else:
                self.name = capwords(romName)
        self.parent = parent

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

