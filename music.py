# ----------------------------------------------------------------------
# music.py - This is the Freevo MP3 and OGG-Vorbis module. 
# ----------------------------------------------------------------------
# $Id$
#
# Authors:     Krister Lagerstrom <krister@kmlager.com>
#              Aubin Paul <aubin@punknews.org>
#              Dirk Meyer <dmeyer@tzi.de>
#              Thomas Malt <thomas@malt.no>
# Notes:       - Functions having arg and menuw arguments in different
#                order is confusing.
# Todo:        * Add support for Ogg-Vorbis
#              * Start using mplayer as playing engine.
#
# ----------------------------------------------------------------------
# $Log$
# Revision 1.2  2002/07/31 18:31:29  outlyer
# Cleaned up mpg123 references. 1.2.5 should only use mplayer, so let's
# not be confusing. Note: The RPM spec files still contain mpg123, but
# since they're for 1.2.4, it's ok for now.
#
# Revision 1.1  2002/07/29 05:24:35  outlyer
# Lots and lots of changes for new mplayer-based audio playing code.
# o You'll need to modify your config file, as well as setup the new mplayer
#   module by editing main.py
# o This change includes Ogg Support, but that requires the ogg.vorbis
#   module. If you don't want it, just don't install ogg.vorbis :)
#
# ----------------------------------------------------------------------
# 
# Copyright (C) 2002 Krister Lagerstrom
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
"""The Freevo Audio-playing module

More documentation to be written.
"""
__date__    = "2002-07-26"
__version__ = "$Revision$"


import sys
import random
import time, os
import string, popen2, fcntl, select, struct

import config  # Configuration file object. currently executes a lot of code.
import util    # Various utilities defined for freevo.
import menu    # The menu widget class
import mplayer # Module for running mplayer.
import rc      # The remote controller class

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

mplayer = mplayer.get_singleton()
rc      = rc.get_singleton()

def play( arg=None, menuw=None ):
    """
    calls the play function of mplayer to play audio.

    old comment:
    Play an MP3 file using the slave mode interface.
    The argument is a tuple containing the file to
    be played and a list of the entire playlist so that the player can
    start on the next one.

    Arguments: mode - mode of playing audio for music, video, dvd etc.
               file - filename to play.
               list - is playlist, ie rest of files in directory.
    Returns:   None
    """
    
    (mode, file, list) = arg
    if not mode:
        mode = 'audio'
        
    mplayer.play( mode, file, list )
    

def main_menu(arg=None, menuw=None):
    """
    The music module main menu.

    Arguments:
    Returns:   None
    """

    items = []    
    for (title, file ) in config.DIR_MP3:
        if os.path.isdir:
            type = 'dir'
        elif os.path.isfile:
            type = 'file'
        
        items += [ menu.MenuItem( title, parse_entry, (title, file),
                                  handle_config, (type, file),
                                  None, None, None ) ]
                                  
    
    mp3menu = menu.Menu('MUSIC MAIN MENU', items)
    menuw.pushmenu(mp3menu)



def parse_entry( arg=None, menuw=None ):
    """
    The music module change directory handling function
    formerly known as cwd

    Arguments: Array of arguments - Since that's the way it is done.
    Todo:      Should do a test on dir to see if it is a playlist I open
               for it in main_menu, but it shouldn't be a problem.
               Got crash on playlist handling.
    """
    (new_title, dir) = arg

    items = []
    if os.path.isdir( dir ):
        dirnames  = util.getdirnames(dir)
        playlists = util.match_files(dir, config.SUFFIX_AUDIO_PLAYLISTS)
        files     = util.match_files(dir, config.SUFFIX_AUDIO_FILES)

        for dirname in dirnames:
            title = '[' + os.path.basename(dirname) + ']'
        
            # XXX Should I do '_' to ' ' translation here and stuff?
            # Yes recursive stupid.
            m = menu.MenuItem( title, parse_entry, (title, dirname),
                               handle_config, ('dir', dirname),
                               None, None, None )
            
            if os.path.isfile(dirname+'/cover.png'): 
                m.setImage(('music', (dirname+'/cover.png')))
            if os.path.isfile(dirname+'/cover.jpg'): 
                m.setImage(('music', (dirname+'/cover.jpg')))
            items += [m]

        # Add autogenerated playlist
        if files:
            plist_fname = config.FREEVO_CACHEDIR + '/freevo-autoplaylist.m3u'
            create_randomized_playlist(files, plist_fname)
            title = 'PL: Randomized playlist with all songs in this directory'
            items += [menu.MenuItem(title, make_playlist_menu, plist_fname)]
    
        for playlist in playlists:
            title = 'PL: ' + os.path.basename(playlist)[:-4]
            items += [menu.MenuItem( title, make_playlist_menu, playlist,
                                    handle_config, ('list', playlist) )]
            
    
        for file in files:
            # XXX Do get title from ID3, Ogg-info here.
            title = os.path.basename(file)[:-4]
            items += [menu.MenuItem( title, play, ('audio', file, files) )]

        mp3menu = menu.Menu('MUSIC MENU', items, dir=dir)
        menuw.pushmenu(mp3menu)

    else:
        """ Note:
        What happens here if the user specifies a file directly?
        We should be able to handle that. that opens for a more
        generic function..
        """
        # items = []
        # title = new_title
        # items += [menu.MenuItem( title, play, ('audio', dir, None) )]
        play( None, ['audio', dir, None] )
    


def handle_config( event=None, menuw=None, arg=None ):
    """
    Handles the configuration of directories and files, building
    play lists and stuff eventually.
    
    Arguments: event - event identifier.
               menuw - menu widget.
               arg   - argument to event.
    Returns:   None
    Authors:   Thomas Malt <thomas@malt.no>
               dischi
    Started:   2002-07-26 18:17 tm
    Changed:   $Date$ $Author$
    """

    (type, file) = arg
    
    print( 'inside handle_config actually. type = ' + type + ' file = ' +
           file + ' event = ' + event )
    

        
#
# Autogenerated randomized playlist with all MP3 files in this directory
#
def create_randomized_playlist(files, fname):
    templist = open(fname, 'w')

    # Do not modify the list that was passed
    flist = files[:]
    
    while flist:
        element = random.choice(flist)
        flist.remove(element)
        templist.write(element + '\n')


def make_playlist_menu( list=None, menuw=None ):
    """
    This is the (m3u) playlist handling function.

    Arguments: list  - the playlist filename
               menuw - the menuwidget, but it's not used for anything. 
    Returns:   Boolean
    """
    
    try:
        lines = open( list ).readlines()
    except IOError:
        print 'Cannot open file "%s"' % list
        return 0
    
    playlist_lines_dos = map(lambda l: l.strip(), lines)
    playlist_lines     = filter(lambda l: l[0] != '#', playlist_lines_dos)

    items = []
    for filename in playlist_lines:
        # XXX Should probably do som audio_info magic here.
        songname = os.path.splitext(os.path.basename(filename))[0]
        items += [ menu.MenuItem( songname, play,
                                  ('audio', filename, playlist_lines) )]

    title = os.path.basename( list )[:-4]
    
    mp3menu = menu.Menu('PLAYLIST: %s' % title, items)
    menuw.pushmenu(mp3menu)
    return 1
