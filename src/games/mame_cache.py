# ----------------------------------------------------------------------
# mame_cache.py - Module for caching MAME rom information for Freevo.
# ----------------------------------------------------------------------
# $Id$
#
# Authors:     Rob Shortt <rob@infointeractive.com>
#
# Notes:  This contains some rominfo code from videogame.py.
# Todo:        
#
# ----------------------------------------------------------------------
#
# ----------------------------------------------------------------------
# 
# Copyright (C) 2002 Rob Shortt
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
#

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

    pickle.dump(mameRomList, open(config.MAME_CACHE, 'w'))
    

#
# We should keep mameRomList up to date.
# This function takes in a list of files and makes sure
# the cache has any relevant information.
#
def updateMameRomList(mame_files):
    mameRomList = getMameRomList()

    cache = mameRomList.getMameRoms()

    # We can use the trashme propery to uncache roms
    # that we no longer care about.
    for rom in cache.values():
        if rom.getTrashme == 1:
            del cache[rom.getFilename()]

    for mame_file in mame_files:
        # Now we only have to run rominfo if we do not know
        # about the rom in question.

        if not cache.has_key(mame_file):
            # If there is a real game title available 
            # title will get overwritten.
            title = os.path.splitext(os.path.basename(mame_file))[0]

            dirname = '' # not supported yet
            image = None
            rominfo = os.popen('./rominfo ' + mame_file , 'r')
            matched = 0
            partial = 0

            for line in rominfo.readlines():
                if string.find(line, 'Error:') != -1:
                    print 'MAME:rominfosrc: "%s"' % line.strip()
                if string.find(line, 'KNOWN:') != -1:
                    print 'MAME:rominfosrc: "%s"' % line.strip()
                    matched = 1
                if string.find(line, 'PARTIAL:') != -1:
                    print 'MAME:rominfosrc: "%s"' % line.strip()
                    partial = 1
                if string.find(line, 'DESCRIPTION:') != -1:
                    # If we have a real title we will use that 
                    # instead of the filename.
                    title = line.strip()
                    print 'MAME:rominfosrc: "%s"' % title
                    title = string.replace(title, 'DESCRIPTION:  ', '')

            rominfo.close()

            if matched == 1 or partial == 1:
                # find image for this file
                if os.path.isfile(os.path.splitext(mame_file)[0] + ".png"):
                    image = os.path.splitext(mame_file)[0] + ".png"
                elif os.path.isfile(os.path.splitext(mame_file)[0] + ".jpg"):
                    image = os.path.splitext(mame_file)[0] + ".jpg"

            newRom = mame_types.MameRom()

            newRom.setTitle(title)
            newRom.setFilename(mame_file)
            newRom.setDirname(dirname)
            newRom.setMatched(matched)
            newRom.setPartial(partial)
            newRom.setImageFile(image)
    
            # Add the new rom to the cache.
            cache[mame_file] = newRom

    # Update our cache and save it.
    mameRomList.setMameRoms(cache)
    saveMameRomList(mameRomList)


#
# This will return a list of things relevant to MameItem based on 
# which directory's contents we are interested in.
# Returns: title, filename, and image file for each mame_file.
#
def getMameItemInfoList(mamedir):

    mame_files = util.match_files(mamedir, config.SUFFIX_MAME_FILES)

    items = []

    updateMameRomList(mame_files)
    mameRomList = getMameRomList()
    roms = mameRomList.getMameRoms()

    # for romkey in roms.keys():
    for romkey in mame_files:
        if roms.has_key(romkey):
            rom = roms[romkey]
        else:
           # Something is broken if we end up here!
           print "Error: %s should be cached by now." % romkey
           continue

        items += [(rom.getTitle(), rom.getFilename(), rom.getImageFile())]
    
    return items    
