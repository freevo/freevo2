#if 0 /*
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
# Revision 1.6  2003/04/10 16:37:41  dischi
# Fix menu redraw after playing ended (untested, please test)
#
# Revision 1.5  2003/04/06 21:12:57  dischi
# o Switched to the new main skin
# o some cleanups (removed unneeded inports)
#
# Revision 1.4  2003/01/11 10:55:56  dischi
# Call refresh with reload=1 when the menu was disabled during playback
#
# Revision 1.3  2002/12/22 12:59:34  dischi
# Added function sort() to (audio|video|games|image) item to set the sort
# mode. Default is alphabetical based on the name. For mp3s and images
# it's based on the filename. Sort by date is in the code but deactivated
# (see mediamenu.py how to enable it)
#
# Revision 1.2  2002/12/09 14:23:53  dischi
# Added games patch from Rob Shortt to use the interface.py and snes support
#
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
import game

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

import menu
import rc
import time
import copy

rc = rc.get_singleton()


from item import Item


class MameItem(Item):
    def __init__(self, title, file, image = None, parent = None):
        Item.__init__(self)
        self.type  = 'mame'            # fix value
        self.mode  = 'file'            # file, dvd or vcd
        self.image = image
        self.name = title
        self.filename = file

        self.xml_file = None
        self.parent = parent
        
        # find image for this file
        if image == None:
            if os.path.isfile(os.path.splitext(file)[0] + ".png"):
                self.image = os.path.splitext(file)[0] + ".png"
            elif os.path.isfile(os.path.splitext(file)[0] + ".jpg"):
                self.image = os.path.splitext(file)[0] + ".jpg"

        command = '--prio=%s %s %s' % (config.GAMES_NICE,
                                       config.MAME_CMD,
                                       config.MAME_ARGS_DEF)

        # Some files needs special arguments to mame, they can be
        # put in a <file>.mame options file. The <file>
        # includes the suffix (.zip, etc)!
        # The arguments in the options file are added at the end of the
        # regular mame arguments.
        if os.path.isfile(file + '.mame'):
            command += (' ' + open(filename + '.mame').read().strip())
            if DEBUG: print 'Read options, command = "%s"' % command

        romname = os.path.basename(file)
        romdir = os.path.dirname(file)
        command = '%s -rp %s "%s"' % (command, romdir, romname)

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

        self.game_player.play(self)


    def stop(self, menuw=None):
        self.game_player.stop()


    def eventhandler(self, event, menuw=None, mythread=None):

        if not mythread == None:
            if event == rc.STOP or event == rc.SELECT:
                self.stop()
                rc.app = None
                if not menuw == None:
                    menuw.refresh(reload=1)
            elif event == rc.MENU:
                mythread.app.write('M')
            elif event == rc.DISPLAY:
                mythread.cmd( 'config' )
            elif event == rc.PAUSE or event == rc.PLAY:
                mythread.cmd('pause')
            elif event == rc.ENTER:
                mythread.cmd('reset')
            elif event == rc.REC:
                mythread.cmd('snapshot')

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)

