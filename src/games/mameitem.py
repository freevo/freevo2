#if 0 /*
# -----------------------------------------------------------------------
# mametem.py - Item for mame objects
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2002/11/24 19:10:19  dischi
# Added mame support to the new code. Since the hole new code is
# experimental, mame is activated by default. Change local_skin.xml
# to deactivate it after running ./cleanup
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

import os
import re

import config
import util
import mame

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

import menu
import rc
import skin
import osd
import time
import copy

rc         = rc.get_singleton()
skin       = skin.get_singleton()
osd        = osd.get_singleton()

from item import Item


class MameItem(Item):
    def __init__(self, title, file, image = None, parent = None):
        Item.__init__(self)
        self.type  = 'mame'            # fix value
        self.mode  = 'file'            # file, dvd or vcd
        self.image = image
        self.name = title
        self.files = [ file, ]

        # mame_options does not do anything yet
        self.mame_options = ''

        self.xml_file = None
        self.parent = parent
        
        # find image for this file
        if image == None:
            if os.path.isfile(os.path.splitext(file)[0] + ".png"):
                self.image = os.path.splitext(file)[0] + ".png"
            elif os.path.isfile(os.path.splitext(file)[0] + ".jpg"):
                self.image = os.path.splitext(file)[0] + ".jpg"

        self.mame_player = mame.get_singleton()
        

    # ------------------------------------------------------------------------
    # actions:


    def actions(self):
        return [ ( self.play, 'Play' ) ]
    

    def play(self, menuw=None):
        self.parent.current_item = self

        print "now running %s" % self.files
        self.current_file = self.files[0]
        mame_options = self.mame_options

        # mame.py sould probably be changed so play is called like this:
        # self.mame_player.play(self.current_file, mame_options, self)

        self.mame_player.play('mame', self.current_file, [], 0, mame_options)


    def stop(self, menuw=None):
        self.mame_player.stop()
