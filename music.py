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
# Revision 1.19  2002/10/21 02:31:38  krister
# Set DEBUG = config.DEBUG.
#
# Revision 1.18  2002/10/20 18:07:40  dischi
# Added all rom drives with identify media support to the main menu. You
# can't browse DVD, VCD and SVCD and AUDIO-CD support is still missing,
# but it works for mp3 cds.
#
# Revision 1.17  2002/10/12 22:30:45  krister
# Removed debug output.
#
# Revision 1.16  2002/10/08 04:47:47  krister
# Changed the new playlist type list to be displayed correctly. Added popup box for recursive scanning (can take a long time).
#
# Revision 1.15  2002/10/07 05:26:25  outlyer
# Added recursive playlist support from Alex Polite <m2@plusseven.com>
#
# Revision 1.14  2002/10/06 14:42:01  dischi
# log message cleanup
#
# Revision 1.13  2002/10/02 02:40:56  krister
# Applied Alex Polite's patch for using XMMS instead of MPlayer for
# music playing and visualization.
#
# Revision 1.12  2002/09/22 08:50:08  dischi
# deactivated ROM_DRIVES in main menu (crash!). Someone should make this
# identifymedia compatible.
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
import osd     # Yes.. we use the GUI for printing stuff.
import skin    # The skin class

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0

if config.MUSICPLAYER == 'XMMS':
    import xmmsaudioplayer # Module for running xmms
    musicplayer = xmmsaudioplayer.AudioPlayer.get_singleton()
elif config.MUSICPLAYER == 'MPLAYER':
    musicplayer = mplayer.get_singleton()
else:
    raise "Set MUSICPLAYER in freevo_config.py to either XMMS or MPLAYER"

rc      = rc.get_singleton()
osd     = osd.get_singleton()
skin = skin.get_singleton()


def play(arg=None, menuw=None):
    """
    calls the play function of mplayer to play audio.

    The argument is a tuple containing the file to
    be played and a list of the entire playlist so that the player can
    start on the next one.

    Arguments: mode - mode of playing audio for music, video, dvd etc.
               file - filename to play.
               list - is playlist, ie rest of files in directory.
    Returns:   None
    """

    if not arg:
        return
    
    (mode, file, list) = arg
    if not mode:
        mode = 'audio'
        
    musicplayer.play(mode, file, list)
    

#
# EJECT handling
#
def eventhandler(event = None, menuw=None, arg=None):

    global main_menu_selected
    if event == rc.IDENTIFY_MEDIA:
        if menuw.menustack[1] == menuw.menustack[-1]:
            main_menu_selected = menuw.all_items.index(menuw.menustack[1].selected)

        menuw.menustack[1].choices = main_menu_generate()

        menuw.menustack[1].selected = menuw.menustack[1].choices[main_menu_selected]

        if menuw.menustack[1] == menuw.menustack[-1]:
            menuw.init_page()
            menuw.refresh()

    if event == rc.EJECT:

        print 'EJECT1: Arg=%s' % arg

        # Was the handler called for a specific drive?
        if not arg:
            print 'Arg was none'
            if not config.REMOVABLE_MEDIA:
                print 'No removable media defined'
                return # Do nothing if no media defined
            # Otherwise open/close the first drive in the list
            media = config.REMOVABLE_MEDIA[0]
            print 'Selecting first device'
        else:
            media = arg

        print media    
        print dir(media)
        media.move_tray(dir='toggle')

    # Done
    return


# ======================================================================

#
# The Movie module main menu
#
def main_menu_generate():
    items = []    

    for (title, dir) in config.DIR_AUDIO:
        items += [menu.MenuItem(title, parse_entry, (title, dir), eventhandler,
                                type = 'dir')]

    for media in config.REMOVABLE_MEDIA:
        if media.info:

            if not media.info.label:
                print "WARNING: no title for %s given, setting to default" % media.mountdir
                media.info.label = media.mountdir
                
            if media.info.type:
                if media.info.type == 'AUDIO-CD':
                    m = menu.MenuItem('Drive %s (Audio CD)' % media.drivename, None,
                                      None, eventhandler, media)
                    print "Audio cd, not implemented yet"

                elif media.info.type == 'DVD' or media.info.type == 'VCD' or \
                     media.info.type == 'SVCD':

                    m = menu.MenuItem('%s (%s)' % (media.info.label, media.info.type),
                                      None, None, eventhandler, media)
                    m.setImage(('movie', media.info.image))
                    
                else:
                    image_type = 'music'
                    label = media.info.label
                    
                    if media.info.type == 'VIDEO':
                        image_type = 'movie'
                        label += ' (Video CD)' 
                    
                    m = menu.MenuItem(label, parse_entry,
                                      (label, media.mountdir), eventhandler, media)
                    m.setImage((image_type, media.info.image))
                    
        else:
            m = menu.MenuItem('Drive %s (no disc)' % media.drivename, None,
                              None, eventhandler, media)
        items += [m]

    return items


def main_menu(arg=None, menuw=None):
    """
    The music module main menu.

    Arguments:
    Returns:   None
    """

    moviemenu = menu.Menu('MUSIC MAIN MENU', main_menu_generate(), umount_all=1)
    menuw.pushmenu(moviemenu)
            


def parse_entry(arg=None, menuw=None):
    """
    The music module change directory handling function
    formerly known as cwd

    Arguments: Array of arguments - Since that's the way it is done.
    Todo:      Should do a test on dir to see if it is a playlist I open
               for it in main_menu, but it shouldn't be a problem.
               Got crash on playlist handling.
    """
    (new_title, mdir) = arg

    # If the dir is on a removable media it needs to be mounted
    for media in config.REMOVABLE_MEDIA:
        if mdir.find(media.mountdir) == 0:
            media.mount()
            break

    items = []
    if os.path.isdir(mdir):
        dirnames  = util.getdirnames(mdir)
        playlists = util.match_files(mdir, config.SUFFIX_AUDIO_PLAYLISTS)
        files     = util.match_files(mdir, config.SUFFIX_AUDIO_FILES)

        if DEBUG:
            print 'music:parse_entry(): d="%s"' % dirnames
            print 'music:parse_entry(): p="%s"' % playlists
            print 'music:parse_entry(): f="%s"' % files

	    
        # Add recursive playlist
        if dirnames and config.RECURSIVE_PLAYLIST:
            skin.PopupBox('Creating recursive playlist, please be patient...')
	    playlist = config.FREEVO_CACHEDIR + '/freevo-recursiveplaylist.m3u'
            recursive_files = util.match_files_recursively(
                mdir, config.SUFFIX_AUDIO_FILES)
            #write_playlist(recursive_files, playlist)
            create_randomized_playlist(recursive_files, playlist)
            title = 'PL: Random playlist with songs here and below'
            items += [menu.MenuItem(title, make_playlist_menu, playlist,
                                    eventhandler, None, 'list')]

            
        for dirname in dirnames:
            title = '[' + os.path.basename(dirname) + ']'
        
            # XXX Should I do '_' to ' ' translation here and stuff?
            # Yes recursive stupid.
            m = menu.MenuItem( title, parse_entry, (title, dirname),
                               eventhandler, None, 'dir',
                               None, None, None )
            
            if os.path.isfile(dirname+'/cover.png'): 
                m.setImage(('music', (dirname+'/cover.png')))
            if os.path.isfile(dirname+'/cover.jpg'): 
                m.setImage(('music', (dirname+'/cover.jpg')))
            items += [m]

        # Add autogenerated playlist
        if files and config.RANDOM_PLAYLIST:        	
            playlist = config.FREEVO_CACHEDIR + '/freevo-autoplaylist.m3u'
            create_randomized_playlist(files, playlist)
            title = 'PL: Random playlist with all songs here'
            items += [menu.MenuItem(title, make_playlist_menu, playlist,
                                    eventhandler, None, 'list')]
    
        for playlist in playlists:
            title = 'PL: ' + os.path.basename(playlist)[:-4]
            items += [menu.MenuItem(title, make_playlist_menu, playlist,
                                    eventhandler, None, 'list')]
            
        for file in files:
            # XXX Do get title from ID3, Ogg-info here.
            title = os.path.splitext(os.path.basename(file))[0]
            items += [menu.MenuItem( title, play, ('audio', file, files) )]

        mp3menu = menu.Menu('MUSIC MENU', items, xml_file=mdir)
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
        play(None, ['audio', mdir, None])
    


        
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


def make_playlist_menu(arg=None, menuw=None):
    """
    This is the (m3u) playlist handling function.

    Arguments: arg  - the playlist filename
               menuw - the menuwidget, but it's not used for anything. 
    Returns:   Boolean
    """
    
    try:
        lines = open(arg).readlines()
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

    title = os.path.basename(arg)[:-4]
    
    mp3menu = menu.Menu('PLAYLIST: %s' % title, items)
    menuw.pushmenu(mp3menu)
    return 1
