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
# Revision 1.29  2003/07/04 14:37:17  outlyer
# Missing named parameter 'info' was causing crashes when using cdaudio.
# Also had to make a change in mmpython:
#
# factory.py:
# 119: elif scheme == 'cd' or scheme == 'cdda':
#
# Revision 1.28  2003/07/03 23:13:46  dischi
# moved mmpython parsing to audioinfo to support playlists
#
# Revision 1.27  2003/06/29 20:42:14  dischi
# changes for mmpython support
#
# Revision 1.26  2003/06/09 18:12:50  outlyer
# Rename eyed3 to eyeD3
#
# Revision 1.25  2003/05/19 19:00:08  outlyer
# Trapping the IOError that Fridtjof Busse was getting with Ogg files,
# hopefully we can track down the problem this way, and avoid crashes at the
# same time.
#
# Revision 1.24  2003/05/16 13:17:45  outlyer
# Bugfix for web radio station caching from Urmet J?nes <urmet@uninet.ee>
#
# Revision 1.23  2003/05/11 18:08:06  dischi
# added AUDIO_FORMAT_STRING to format the audio items
#
# Revision 1.22  2003/05/08 14:17:36  outlyer
# Initial version of Paul's FXD radio station support. I made some changes from
# the original patch, in that I added an URL field to the audioitem class instead of
# using the year field as his patch did. I will be adding a example FXD file to
# testfiles as well.
#
# Revision 1.21  2003/04/24 19:55:59  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.20  2003/04/21 13:27:46  dischi
# o make it possible to hide() the audio player
# o mplayer is now a plugin, controlled by the PlayerGUI
#
# Revision 1.19  2003/04/20 12:43:32  dischi
# make the rc events global in rc.py to avoid get_singleton. There is now
# a function app() to get/set the app. Also the events should be passed to
# the daemon plugins when there is no handler for them before. Please test
# it, especialy the mixer functions.
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
import string
import time
import re
import imghdr
import traceback
import config
import util
import rc

from player import PlayerGUI
from item import Item
import mmpython


DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

class AudioItem(Item):
    """
    This is the common class to get information about audiofiles.
    """
    
    def __init__(self, file, parent, info = None, name = None):
        if parent and parent.media:
            url = 'cd://%s:%s:%s' % (parent.media.devicename, parent.media.mountdir,
                                     file[len(parent.media.mountdir)+1:])
        else:
            url = file

        Item.__init__(self, parent, mmpython.parse(url))
        self.filename   = file[:]
        self.url        = None
        if name:
            self.name   = name
        elif not self.name:
            self.name   = util.getname(file)
        self.type       = 'audio'
        
        self.start      = 0
        self.elapsed    = 0
        self.remain     = 0
        self.done       = 0.0
        self.pause      = 0
	self.valid	= 1

        try:
            self.length = self.info['length']
        except:
            self.length = 0
            
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

        # Let's try to find if there is any image in the current directory
        # that could be used as a cover
        if not self.image and not file.find('://') != -1:
            images = ()
            covers = ()
            files =()
            def image_filter(x):
                return re.match('.*(jpg|png)$', x, re.IGNORECASE)
            def cover_filter(x):
                return re.search(config.AUDIO_COVER_REGEXP, x, re.IGNORECASE)

            # Pick an image if it is the only image in this dir, or it matches
            # the configurable regexp
            try:
                files = os.listdir(os.path.dirname(file))
            except OSError:
                print "oops, os.listdir() error"
                traceback.print_exc()
            images = filter(image_filter, files)
            image = None
            if len(images) == 1:
                image = os.path.join(os.path.dirname(file), images[0])
            elif len(images) > 1:
                covers = filter(cover_filter, images)
                if covers:
                    image = os.path.join(os.path.dirname(file), covers[0])
            self.image = image


    def copy(self, obj):
        """
        Special copy value AudioItem
        """
        Item.copy(self, obj)
        if obj.type == 'audio':
            self.title      = obj.title
            self.start      = obj.start
            self.length     = obj.length
            self.elapsed    = obj.elapsed
            self.remain     = obj.remain
            self.done       = obj.done
            self.pause      = obj.pause
            self.valid	    = obj.valid
            self.url        = obj.url



    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date':
            return '%s%s' % (os.stat(self.filename).st_ctime, self.filename)
        return self.filename


    def getattr(self, attr):
        """
        return the specific attribute as string or an empty string
        """
        if attr  == 'length':
            return '%d:%02d' % (int(self.length / 60), int(self.length % 60))

        if attr  == 'elapsed':
            return '%d:%02d' % (int(self.elapsed / 60), int(self.elapsed % 60))
            
        return Item.getattr(self, attr)

    def set_info_radio(self, filename):
        """
        Sets the info variables with info from the fxd

        Arguments: filename
          Returns: 1 if success
        """
        import xmllib
        import xml
        from xml.parsers import expat
        sourcexml = open(filename, 'r')
        xmlpp = sourcexml.read()

        def s_el(name, attrs):
            global glob_name
            glob_name = name
        def e_el(name):
            print "   (attribute", name, "ends)"
        def c_data(data):
            global glob_name
            global glob_val
            global glob_url
            print glob_name, data
            if data:
                if glob_name == 'title':
                    self.title = data
                    glob_name = 0
                if glob_name == 'genre':
                    self.album = data
                    glob_name = 0
                if glob_name == 'desc':
                    self.artist = data
                    glob_name = 0
                if glob_name == 'url':
                    self.url = data
                    print "URL:", self.url
                    glob_name = 0
        prs = xml.parsers.expat.ParserCreate()
        prs.StartElementHandler = s_el
        prs.EndElementHandler = e_el
        prs.CharacterDataHandler = c_data
        prs.returns_unicode = 0
        prs.Parse(xmlpp)
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

        if not self.menuw:
            self.menuw = menuw

        self.player = PlayerGUI(self, menuw)
        error = self.player.play()

        if error and menuw:
            AlertBox(text=error).show()
            rc.post_event(rc.PLAY_END)


    def stop(self, arg=None, menuw=None):
        """
        Stop the current playing
        """
        self.player.stop()

    def format_track(self):
        """ Return a formatted string for use in music.py """
	# Since we can't specify the length of the integer in the
	# format string (Python doesn't seem to recognize it) we
	# strip it out first, when we see the only thing that can be
	# a number.


        # Before we begin, make sure track is an integer
    
        if self.track:
            try:
    	        mytrack = ('%0.2d' % int(self.track))
            except ValueError:
    	        mytrack = None
        else:
           mytrack = None
    
        song_info = {  'a'  : self.artist,
       	               'l'  : self.album,
    	               'n'  : mytrack,
    	               't'  : self.title,
    	               'y'  : self.year,
    	               'f'  : self.name }

        if self.parent and hasattr(self.parent, 'AUDIO_FORMAT_STRING'):
            return self.parent.AUDIO_FORMAT_STRING % song_info
        return config.AUDIO_FORMAT_STRING % song_info
        
