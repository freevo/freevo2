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
# Revision 1.35  2003/09/10 19:35:49  dischi
# fix length during runtime
#
# Revision 1.34  2003/08/23 12:51:41  dischi
# removed some old CVS log messages
#
# Revision 1.33  2003/08/22 13:19:46  outlyer
# Patch to allow mplayer-options in Web "Radio" FXD files.
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
    
    def __init__(self, file, parent, name = None, scan = TRUE):
        if scan:
            if parent and parent.media:
                url = 'cd://%s:%s:%s' % (parent.media.devicename, parent.media.mountdir,
                                         file[len(parent.media.mountdir)+1:])
            else:
                url = file
            Item.__init__(self, parent, mmpython.parse(url))
        else:
            Item.__init__(self, parent)
            
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

        if os.path.splitext(file)[1] == '.fxd':
            self.set_info_radio(file)

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
        if attr  == 'length' and self.length:
            # maybe the length was wrong
            if self.length < self.elapsed:
                self.length = self.elapsed
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
                if glob_name == 'mplayer_options':
                    self.mplayer_options = data
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
        
