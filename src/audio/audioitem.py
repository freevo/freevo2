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
# Revision 1.42  2003/12/12 19:20:46  dischi
# use util functions to get the image
#
# Revision 1.41  2003/11/28 20:08:57  dischi
# renamed some config variables
#
# Revision 1.40  2003/11/23 17:03:43  dischi
# Removed fxd handling from AudioItem and created a new FXDHandler class
# in __init__.py to let the directory handle the fxd files. The format
# of audio fxd files changed a bit to match the video fxd format. See
# __init__.py for details.
#
# Revision 1.39  2003/11/22 20:36:34  dischi
# use new vfs
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
import traceback
import config
import util
import rc

from player import PlayerGUI
from item import Item
import mmpython


class AudioItem(Item):
    """
    This is the common class to get information about audiofiles.
    """
    
    def __init__(self, file, parent, name = None, scan = True):
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
            
        self.image = util.getimage(os.path.dirname(file)+'/cover', self.image)

        # Allow per mp3 covers. As per Chris' request ;)
        self.image = util.getimage(file[:file.rfind('.')], self.image)

        # Let's try to find if there is any image in the current directory
        # that could be used as a cover
        if file and not self.image and not file.find('://') != -1:
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
        if attr  == 'length' and self.length:
            # maybe the length was wrong
            if self.length < self.elapsed:
                self.length = self.elapsed
            return '%d:%02d' % (int(self.length / 60), int(self.length % 60))

        if attr  == 'elapsed':
            return '%d:%02d' % (int(self.elapsed / 60), int(self.elapsed % 60))
            
        return Item.getattr(self, attr)

   
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
            return self.parent.DIRECTORY_AUDIO_FORMAT_STRING % song_info
        return config.DIRECTORY_AUDIO_FORMAT_STRING % song_info
        
