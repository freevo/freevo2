# ----------------------------------------------------------------------
# audioinfo - Getting info about mp3 files
# ----------------------------------------------------------------------
# $Id$
#
# Authors: Thomas Malt <thomas@malt.no>
#          Aubin Paul <aubin@debian.org>
#          Scott Hassan (afaik)
# Notes:   - Lot of code taken from an mp3 module by Scott Hassan
#          - From now on ogg.vorbis is an optional dependency.
#          - The code for calculating elapsed time and stuff is not 
#            really accurate. We don't get any info from mplayer about
#            how far we've really gotten, we just hope the timeskew
#            isn't to bad.
# Todo:    - Write doc.
#          * Add support for Ogg-Vorbis
# ----------------------------------------------------------------------
# $Log$
# Revision 1.1  2002/11/23 19:24:02  dischi
# New version of the code cleanup, not working right now, wait for more
# checkins in some minutes please
#
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

import os
import sys
import string
import time
import re
import eyed3
import skin
import imghdr
import traceback
import config
import mplayer

from item import Item


DEBUG = config.DEBUG

skin = skin.get_singleton()

class AudioItem(Item):
    """
    This is the common class to get information about audiofiles.
    """
    __pause_timer = 0 # Private variable to store time for pause.
    __lastupdate  = 0.0
    
    def __init__( self, file, parent ):
        Item.__init__(self)
        self.drawall    = 1
        self.filename   = file
        self.parent     = parent
        self.album      = ''
        self.artist     = ''
        self.length     = 0
        self.track      = 0
	self.trackof	= 0
        self.year       = 0
        self.start      = 0
        self.elapsed    = 0
        self.remain     = 0
        self.done       = 0.0
        self.pause      = 0
	self.valid	= 1

        self.name = os.path.splitext(os.path.basename(self.filename))[0]

        # XXX This is really not a very smart way to do it. We should be
        # XXX able to handle files with messed up extentions.

        if re.match('.*[oO][gG]{2}$', self.filename):
            if DEBUG > 1: print "Got ogg..."
            self.set_info_ogg(self.filename)

        elif re.match('.*[mM][pP]3$', self.filename):
            if DEBUG > 1: print "Got mp3..."
            self.set_info_mp3(self.filename)

        else:
            if DEBUG > 1: print "Got something else..."


        cover_logo = os.path.dirname(file)+'/cover.'

        # Only draw the cover if the file exists. We'll
        # use the standard imghdr function to check if
        # it's a real png, and not a lying one :)
        if os.path.isfile(cover_logo+'png') and imghdr.what(cover_logo+'png'):
            self.image = cover_logo+'png'
        elif os.path.isfile(cover_logo+'jpg') and imghdr.what(cover_logo+'jpg'):
            self.image = cover_logo+'jpg'
            
        # Allow per mp3 covers. As per Chris' request ;)
        if os.path.isfile(os.path.splitext(file)[0] + '.png'):
            self.image = os.path.splitext(file)[0] + '.png'
        elif os.path.isfile(os.path.splitext(file)[0] + '.jpg'):
            self.image = os.path.splitext(file)[0] + '.jpg'

        if DEBUG > 1:
            try:
                print "DEBUG:"
                print "  Album: " + str(self.album)
                print " Artist: " + str(self.artist)
                print "  Title: " + str(self.title)
                print "  Track: " + str(self.track)
                print "   Year: " + str(self.year)
                print " Length: " + str(self.length)
                print "  Image: " + str(self.image)
            except UnicodeError:
                print "Oops.. Got UnicodeError.. doing nothing.. :)"

        self.audio_player = mplayer.get_singleton()

    def set_info_ogg(self, file):
        """
        Sets all the info variables with useful info from the oggfile.

        Arguments: Filename of file to get info from
        Returns:   1 if success.
        """
        try:
            import ogg.vorbis
        except ImportError:
            return None
        try: 
            vf = ogg.vorbis.VorbisFile(file)
            vc = vf.comment()
        except ogg.vorbis.VorbisError:
            if DEBUG: print "Got VorbisError.. not an ogg file."
	    self.valid = 0
            return 0
        
        try:
            if 'ALBUM' in vc.keys():
                self.album  = str(vc['ALBUM'][0])
            else:
                self.album  = ''
                
            if 'ARTIST' in vc.keys():
                self.artist = str(vc['ARTIST'][0])
            else:
                self.artist = ''
                
            if 'TITLE' in vc.keys():
                self.name  = str(vc['TITLE'][0])
            else:
                self.name = os.path.splitext(os.path.basename(file))[0]
                
            if 'TRACK' in vc.keys():
                self.track  = str(vc['TRACK'][0])
            elif 'TRACKNUMBER' in vc.keys():
                self.track  = str(vc['TRACKNUMBER'][0])
            else:
                self.track  = ''
                
            if 'YEAR' in vc.keys():
                self.year = str(vc['YEAR'][0])
            else:
                self.year = ''
        except UnicodeError:
            if DEBUG: print "Oops, got UnicodeError"

        self.length = vf.time_total( -1 )
        return 1


    def set_info_mp3(self, filename):
        """
        Sets the info variables with info from the mp3

        Arguments: filename
          Returns: 1 if success
        """

        id3 = None
	try:
	    id3 = eyed3.Mp3AudioFile(filename)
	except eyed3.TagException:
            try:
                id3 = eyed3.Mp3AudioFile(filename, 1)
            except eyed3.InvalidAudioFormatException:
                # File is not an MP3
                self.valid = 0
                return 0
            except:
                # The MP3 tag decoder crashed, assume the file is still
                # MP3 and try to play it anyway
                print 'music: oops, mp3 tag parsing failed!'
                print 'music: filename = "%s"' % filename
                traceback.print_exc()
        except:
            # The MP3 tag decoder crashed, assume the file is still
            # MP3 and try to play it anyway
            print 'music: oops, mp3 tag parsing failed!'
            print 'music: filename = "%s"' % filename
            traceback.print_exc()
            

	if id3:
            if id3.tag:
                self.album  = id3.tag.getAlbum()
                self.artist = id3.tag.getArtist()
                self.name  = id3.tag.getTitle()
                self.track,self.trackof  = id3.tag.getTrackNum()
                self.year   = id3.tag.getYear()
            self.length = id3.getPlayTime()
        else:
            self.album = 'Broken MP3 tag!'

        if not self.name:
            self.name = os.path.splitext(os.path.basename(filename))[0]
        if not self.track:
            self.track = ''
        return 1


    # ###############################################

    def actions(self):
        return [ ( self.play, 'Play' ) ]


    def play(self, menuw=None):
        self.parent.current_item = self
        self.audio_player.play(self)

    def stop(self, menuw=None):
        self.audio_player.stop()
        
    def draw(self):
        """
        Give information to the skin..
        """
        # Calculate some new values
        self.elapsed = self.current_playtime
        if not self.length:
            self.remain = 0
        else:
            self.remain = self.length = self.current_playtime
        skin.DrawMP3(self)
        return

