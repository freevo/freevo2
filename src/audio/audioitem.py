#if 0 /*
# -----------------------------------------------------------------------
# audioitem - Item for mp3 and ogg files
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.11  2003/02/15 04:03:02  krister
# Joakim Berglunds patch for finding music/movie cover pics.
#
# Revision 1.10  2003/02/10 16:29:03  dischi
# small bugfix
#
# Revision 1.9  2003/02/10 15:42:32  dischi
# small bugfix
#
# Revision 1.8  2003/01/12 17:06:25  dischi
# Add possibility to extract the id tags from the AudioItem (dump) and to
# init an AudioItem with that informations. If you create an AudioItem
# with that informations, the id tags won't be loaded from file.
#
# Revision 1.7  2003/01/10 21:05:42  dischi
# set the type (like all the other items do)
#
# Revision 1.6  2003/01/10 11:43:32  dischi
# Added patch from Matthieu Weber for Ogg/Vorbis files which contains an
# artist/title/album text which is not pure ASCII (7 bits).
#
# Revision 1.5  2002/12/22 12:59:34  dischi
# Added function sort() to (audio|video|games|image) item to set the sort
# mode. Default is alphabetical based on the name. For mp3s and images
# it's based on the filename. Sort by date is in the code but deactivated
# (see mediamenu.py how to enable it)
#
# Revision 1.4  2002/12/03 19:15:18  dischi
# Give all menu callback functions the parameter arg
#
# Revision 1.3  2002/11/28 19:56:12  dischi
# Added copy function
#
# Revision 1.2  2002/11/25 04:55:29  outlyer
# Two small changes:
#  o Removed some 'print sys.path' lines I left in my last commit
#  o Re-enabled the skin.format_track() function so the display style of MP3
#    titles can be customized.
#
# Revision 1.1  2002/11/24 13:58:44  dischi
# code cleanup
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
import util

from item import Item


DEBUG = config.DEBUG

skin = skin.get_singleton()

class AudioItem(Item):
    """
    This is the common class to get information about audiofiles.
    """
    
    def __init__(self, file, parent, cache = None):
        Item.__init__(self, parent)
        self.drawall    = 1
        self.filename   = file
        self.name       = util.getname(self.filename)
        self.type       = 'audio'
        
        # variables only for AudioItem
        self.title      = ''
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


        if cache:
            self.restore(cache)

        else:
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

        if self.title:
            self.name = skin.format_track(self)
        else:
            self.title = self.name

        cover_logo = os.path.dirname(file)+'/cover.'

        # Only draw the cover if the file exists. We'll
        # use the standard imghdr function to check if
        # it's a real png, and not a lying one :)

        # Check for cover in COVER_DIR
        if os.path.isfile(config.COVER_DIR+os.path.basename(file)+'.png'):
            self.image = config.COVER_DIR+os.path.basename(file)+'.png'
        elif os.path.isfile(config.COVER_DIR+os.path.basename(file)+'.jpg'):
            self.image = config.COVER_DIR+os.path.basename(file)+'.jpg'

        # Check for cover in local dir
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


    def copy(self, obj):
        """
        Special copy value AudioItem
        """
        Item.copy(self, obj)
        if obj.type == 'audio':
            self.title      = obj.title
            self.album      = obj.album
            self.artist     = obj.artist
            self.length     = onj.length
            self.track      = obj.track
            self.trackof    = obj.trackof
            self.year       = obj.year
            self.start      = obj.start
            self.elapsed    = obj.elapsed
            self.remain     = obj.remain
            self.done       = obj.done
            self.pause      = obj.pause
            self.valid	    = obj.valid


    def dump(self):
        return ( self.title, self.album, self.artist, self.length,
                 self.track, self.trackof, self.year )

    def restore(self, data):
        self.title, self.album, self.artist, self.length, self.track, \
                    self.trackof, self.year = data

    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date':
            return '%s%s' % (os.stat(self.filename).st_ctime, self.filename)
        return self.filename


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
                self.album  = vc['ALBUM'][0].encode('latin-1')
            else:
                self.album  = ''
                
            if 'ARTIST' in vc.keys():
                self.artist = vc['ARTIST'][0].encode('latin-1')
            else:
                self.artist = ''
                
            if 'TITLE' in vc.keys():
                self.title  = vc['TITLE'][0].encode('latin-1')
                
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
                self.title  = id3.tag.getTitle()
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


    # ----------------------------------------------------------------------------

    def actions(self):
        """
        return a list of possible actions on this item
        """
        return [ ( self.play, 'Play' ) ]


    def play(self, arg=None, menuw=None):
        """
        Start playing the item
        """
        self.parent.current_item = self
        self.elapsed = 0
        self.audio_player.play(self)


    def stop(self, arg=None, menuw=None):
        """
        Stop the current playing
        """
        self.audio_player.stop()

        
    def draw(self):
        """
        Give information to the skin..
        """
        # Calculate some new values
        if not self.length:
            self.remain = 0
        else:
            self.remain = self.length - self.elapsed
        skin.DrawMP3(self)
        return

