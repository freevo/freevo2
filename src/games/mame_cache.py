#if 0 /*
# -----------------------------------------------------------------------
# mame_cache.py - Module for caching MAME rom information for Freevo.
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This contains some rominfo code from videogame.py.
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.6  2003/06/20 01:33:56  rshortt
# Removing the need for the rominfo program.  Now we parse the output of
# xmame --listinfo directly and build a list of all supported MAME roms.
# This should only need to be updated when you upgrade xmame and you should
# remove your existing romlist-n.pickled.
#
# Revision 1.5  2003/04/24 19:56:11  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.4  2002/12/09 14:23:53  dischi
# Added games patch from Rob Shortt to use the interface.py and snes support
#
# Revision 1.3  2002/12/07 11:23:52  dischi
# moved rominfo into the games subdir
#
# Revision 1.2  2002/11/24 19:52:56  dischi
# Changed header to the freevo default
#
# Revision 1.1  2002/11/24 19:10:19  dischi
# Added mame support to the new code. Since the hole new code is
# experimental, mame is activated by default. Change local_skin.xml
# to deactivate it after running ./cleanup
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
import time, os, string
import cPickle as pickle

# Classes to keep track of our roms
import mame_types

# Configuration file. 
import config

# Various utilities
import util

# RegExp
import re

from gui.PopupBox import PopupBox

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0


#
# Lets get a MameRomList if one is available from disk.  If not 
# then we shall return an empty one.
#
def getMameRomList():
    file_ver = None
    mameRomList = None

    if os.path.isfile(config.MAME_CACHE):
        mameRomList = pickle.load(open(config.MAME_CACHE, 'r'))

        try:
            file_ver = mameRomList.TYPES_VERSION
        except AttributeError:
            print 'The cache does not have a version and must be recreated.'

        if file_ver != mame_types.TYPES_VERSION:
            print (('MameRomList version number %s is stale (new is %s), must ' +
                    'be reloaded') % (file_ver, mame_types.TYPES_VERSION))
        else:
            if DEBUG:
                print 'Got MameRomList (version %s).' % file_ver

    if mameRomList == None:
        mameRomList = mame_types.MameRomList()

    print "MameRomList has %s items." % len(mameRomList.getMameRoms())
    return mameRomList


#
# function to save the cache to disk
#
def saveMameRomList(mameRomList):

    if not mameRomList or mameRomList == None:
        mameRomList = mame_types.MameRomList()

    try: 
        pickle.dump(mameRomList, open(config.MAME_CACHE, 'w'), 1)
    except:
        print 'strange cPickle error...try pickle'
	import pickle as pypickle
	pypickle.dump(mameRomList, open(config.MAME_CACHE, 'w'), 1)

    

#
# We should keep mameRomList up to date.
# This function takes in a list of files and makes sure
# the cache has any relevant information.
#
def updateMameRomList():

    try:
        listinfo = os.popen(config.MAME_CMD + ' --listinfo', 'r')
    except:
        print 'Unable to get mame listinfo.'
	return FALSE

    newRom = mame_types.MameRom()
    cache = {}

    for line in listinfo.readlines():
        if re.compile("^\tname").match(line):
            newRom.name = re.compile("^\tname (.*)").match(line).group(1)
        elif re.compile("^\tdescription").match(line):
            newRom.description = re.compile("^\tdescription (.*)").match(line).group(1)[1:-1]
        elif re.compile("^\tyear").match(line):
            newRom.year = re.compile("^\tyear (.*)").match(line).group(1)
        elif re.compile("^\tmanufacturer").match(line):
            newRom.manufacturer = re.compile("^\tmanufacturer (.*)").match(line).group(1)[1:-1]
        elif re.compile("^\tcloneof").match(line):
            newRom.cloneof = re.compile("^\tcloneof (.*)").match(line).group(1)
        elif re.compile("^\tromof").match(line):
            newRom.romof = re.compile("^\tromof (.*)").match(line).group(1)
        elif re.compile("^game \(").match(line):
            # We've reached a new game so dump everthing we have so far
            if newRom.name:
                # add the new rom to the cache.
                cache[newRom.name] = newRom
                # make a new mameRom
                newRom = mame_types.MameRom()

    listinfo.close()

    mameRomList = mame_types.MameRomList()
    mameRomList.setMameRoms(cache)
    saveMameRomList(mameRomList)


#
# This will return a list of things relevant to MameItem based on 
# which mame files we have cached.  It ignores files we don't.
# Returns: title, filename, and image file for each mame_file.
#
def getMameItemInfoList(mame_files):
    items = []
    rm_files = []

    # Only build the cache if it doesn't exis.
    if not os.path.isfile(config.MAME_CACHE):
        waitmsg = PopupBox(text='Generating MAME cache, please wait.')
	waitmsg.show()
        updateMameRomList()
	waitmsg.destroy()

    mameRomList = getMameRomList()
    roms = mameRomList.getMameRoms()

    for romfile in mame_files:
        key = os.path.splitext(os.path.basename(romfile))[0]
        if roms.has_key(key):
            rom = roms[key]
            items += [(rom.description, romfile, None)]
            rm_files.append(romfile)
    
    return (rm_files, items)
