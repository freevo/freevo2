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
# Revision 1.16  2002/10/24 05:27:10  outlyer
# Updated audioinfo to use new ID3v2, ID3v1 support. Much cleaner, and uses
# the eyed3 library included. Notable changes:
#
# o Invalid audio files do not cause a crash, both broken oggs and broken mp3s
#    now pop up an "Invalid Audio File" message (also if you just rename a non-
#    audiofile to *.mp3 or *.ogg.
# o Full ID3v2.3 and 2.4 support, v2.2 is not supported, but gracefully falls
#    back to v1.1, if no tags are found, behaviour is normal.
# o Now survives the crash reported by a user
# o There are self.valid and self.trackof variables in audioinfo, to store the
#    validity of the file (passing the header checks for Ogg and MP3) and to
#    store the total numbers of tracks in an album as allowed by the v2.x spec.
# o I'll be updating the skin as well, with support for self.trackof, and to
#    truncate the text in album, artist and title, since they can now be
#    significantly longer than v1.1 and can (and have) run off the screen.
#
# Revision 1.3  2002/10/23 01:18:25  outlyer
# Graceful fallback from 2.x to 1.x if a 2.2 or corrupted 2.x tag is found.
# Only issue left is that we don't get track numbers from v1.1 tags without
# a v1.1 comment defined. It's a weird one.
#
# Revision 1.13  2002/10/13 14:06:50  dischi
# Accept jpg as cover images, too, and when there is no title, return
# the filename as title
#
# Revision 1.12  2002/09/07 06:13:53  krister
# Added check for divide by zero. Cleanups.
#
# Revision 1.11  2002/08/18 06:10:58  krister
# Converted tabs to spaces. Please use tabnanny in the future!
#
# Revision 1.10  2002/08/14 09:28:37  tfmalt
#  o Updated all files using skin to create a skin object with the new
#    get_singleton function. Please tell or add yourself if I forgot a
#    place.
#
# Revision 1.9  2002/08/03 18:10:52  dischi
# Patch from Thomas Malt:
# Discovered some bugs and got rid of them:
#  - Added exception handling a couple of more places where I craches on
#    ogg files with freak corrupt headers.
#
# Revision 1.8  2002/08/03 11:19:21  krister
# Made MP3 track string= if None.
#
# Revision 1.7  2002/08/02 15:32:18  outlyer
# Small changes to fix the badly broken VBR parser that was in audioinfo.py
#  o Moved class into mp3_id3.py since audioinfo.py is/should be a wrapper
#    around various tag implementations
#  o Used brand new VBR-compatible class that doesn't show the many, many
#    problems I had with the previous class.
#
# Note, this adds a new class to mp3_id3.py called mp3header. Maybe we should
# rename mp3_id3.py to another filename, but I don't want to lose our CVS
# history.
#
# Revision 1.6  2002/08/01 00:38:26  outlyer
# More VBR fixes.
#
# Revision 1.5  2002/07/31 14:28:28  outlyer
# Added sampling frequency '9' as '44100' to cope with a (possibly broken) VBR
# mp3 file I had. This prevents an indexerror/crash.
#
# Revision 1.4  2002/07/31 00:59:09  outlyer
# Patch from Thomas Malt <tm@false.linpro.no>
# 1) When paused the timer for the audio did not pause, so when
#    you continued to play the statusbar and stuff would leap forward.
#    fixed.
# 2) On some ogg files with corrupted info I found that audioinfo.py
#    would crash throwing an UnicodeError. Added code to catch the
#    exception, but it doesn't do anything smart to resolve yet.
#
# Revision 1.3  2002/07/29 06:25:29  outlyer
# Added imghdr.what() call back to verify the image is actually an image
# and not lying via the extension. That of course, would make for a crash.
#
# Revision 1.2  2002/07/29 06:21:27  outlyer
# Fixed a minor regression. Added code to get the cover image, as per
# previous behaviour. I've noticed that the mplayer mp3 player takes remarkably
# little CPU on my Celeron 400; less than 1%, so it definitely smokes mpg123
# and mpg321.
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
"""Module for providing information about MP3-files

Usage: audioinfo.MP3Info( 'filename' )
"""

import os
import sys
import string
import time
import re
import eyed3
import skin
import imghdr

DEBUG=1

skin = skin.get_singleton()

class AudioInfo:
    """
    This is the common class to get information about audiofiles.
    """
    __pause_timer = 0 # Private variable to store time for pause.
    __lastupdate  = 0.0
    
    def __init__( self, file, drawall=0 ):
        self.drawall    = drawall
        self.filename   = file
        self.album      = ''
        self.artist     = ''
        self.length     = 0
        self.title      = 0
        self.track      = 0
	self.trackof	= 0
        self.year       = 0
        self.start      = 0
        self.elapsed    = 0
        self.remain     = 0
        self.done       = 0.0
        self.image      = ''
        self.pause      = 0
	self.valid	= 1

        # XXX This is really not a very smart way to do it. We should be
        # XXX able to handle files with messed up extentions.
        if self.is_ogg():
            if DEBUG: print "Got ogg..."
            self.set_info_ogg( self.filename )

        elif self.is_mp3():
            if DEBUG: print "Got mp3..."
            self.set_info_mp3( self.filename )
        else:
            if DEBUG: print "Got something else..."

        temp = self.get_cover_image ( self.filename )
        if DEBUG:
            try:
                print "DEBUG:"
                print "  Album: " + str(self.album)
                print " Artist: " + str(self.artist)
                print "  Title: " + str(self.title)
                print "  Track: " + str(self.track)
                print "   Year: " + str(self.year)
                print " Length: " + str(self.length)
                print "  Image: " + str(temp)
            except UnicodeError:
                print "Oops.. Got UnicodeError.. doing nothing.. :)"

    def get_cover_image( self, filename ):
        cover_logo = os.path.dirname(filename)+'/cover.'

        # Only draw the cover if the file exists. We'll
        # use the standard imghdr function to check if
        # it's a real png, and not a lying one :)
        if os.path.isfile(cover_logo+'png') and imghdr.what(cover_logo+'png'):
            self.image = cover_logo+'png'
        elif os.path.isfile(cover_logo+'jpg') and imghdr.what(cover_logo+'jpg'):
            self.image = cover_logo+'jpg'
            
        # Allow per mp3 covers. As per Chris' request ;)
        if os.path.isfile(os.path.splitext(filename)[0] + '.png'):
            self.image = os.path.splitext(filename)[0] + '.png'
        elif os.path.isfile(os.path.splitext(filename)[0] + '.jpg'):
            self.image = os.path.splitext(filename)[0] + '.jpg'
        return self.image

    def set_cover_image( self, str ):
        self.image = str

    def toggle_pause( self ):
        if self.pause:
            self.pause = 0
            self.start = self.start + (time.time()-self.__pause_timer)
            self.__pause_timer = 0
        else:
            self.pause = 1
            self.__pause_timer = time.time()
            
    def set_info_ogg( self, file ):
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
            vf = ogg.vorbis.VorbisFile( file )
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
                self.title  = str(vc['TITLE'][0])
            else:
                self.title = os.path.splitext(os.path.basename(file))[0]
                
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

    def set_info_mp3( self, file ):
        """
        Sets the info variables with info from the mp3

        Arguments: filename
          Returns: 1 if success
        """
	try:
	    id3 = eyed3.Mp3AudioFile( file )
	except eyed3.TagException:
	    id3 = eyed3.Mp3AudioFile( file, 1)
	except eyed3.InvalidAudioFormatException:
	    # File is not an MP3
	    self.valid = 0
	    return 0

	if id3.tag:
	    self.album  = id3.tag.getAlbum()
            self.artist = id3.tag.getArtist()
            self.title  = id3.tag.getTitle()
     	    self.track,self.trackof  = id3.tag.getTrackNum()
	    self.year   = id3.tag.getYear()

	self.length = id3.getPlayTime()

        if not self.title:
            self.title = os.path.splitext(os.path.basename(file))[0]
        if not self.track:
            self.track = ''
        return 1

    def yes( self ):
        return 1

    def is_ogg( self ):
        if re.match( '.*[oO][gG]{2}$', self.filename ):
            return 1        
        return 0

    def is_mp3(self):
        if re.match( '.*[mM][pP]3$', self.filename ):
            return 1
        return 0
            
    def get_elapsed(self):
        if self.pause:
            return self.elapsed
        return (time.time() - self.start)

    def get_remain(self):
        if( self.elapsed > self.length ):
            self.elapsed = self.length
        return (self.length - self.elapsed)

    def get_done(self):
        if not self.length:
            return 0
        
        if self.elapsed > self.length:
            self.elapsed = self.length
        return (self.elapsed/self.length)*100.0

    def ffwd(self, len=0):
        # Hm.. funny timetravel stuff here :)
        self.start = self.start-len
        
    def rwd(self, len=0):
        # and here.
        self.start = self.start+len
        if self.start > time.time():
            self.start = time.time()
            
    def draw(self):
        """
        Give information to the skin..
        """
        # XXX Let's wait a whole second :)
        if time.time() > (self.__lastupdate + 0.5):
            # print "Doing update of audio GUI..."
            self.elapsed = self.get_elapsed()
            self.remain  = self.get_remain()
            self.done    = self.get_done()
            self.__lastupdate = time.time()
            skin.DrawMP3( self )

        return

# ======================================================================
# End of AudioInfo class
# ======================================================================

