# if 0 /*
# -----------------------------------------------------------------------
# cdbackup.py - CD Backup plugin for ripping/backing up CDs to 
# your hard drive
# -----------------------------------------------------------------------
# $Id$
# 
# Notes: This is the cdbackup module which can be accessed from the audio menu 
# by hitting 'e' or enter (not return) whilst a CD is selected.
# 
# It allows you to backup CDs as .wav files or as .mp3s.
# 
# To Activate Plugin, add the following to local_conf.py: 
# plugin.activate('audio.cdbackup') 
# 
# Todo:      
# Add a status bar showing progress
# Parse the output of cdparanoia and lame to determine status of rip, mp3 conversion
# For encoding parameters, make choices dynamic/selectable from menu instead of only local_conf.py
# maybe just use local_conf.py parameters as defaults.
# Be able to stop ripping once it's started.
# Be able to select individual songs for ripping.
# There is slight delay before menu opens up after being selected from main menu, 
# add a hourglass or some other notification that its loading.
# Albums with more than one Artist aren't handled very well.
# -----------------------------------------------------------------------
#
# $Log$
# Revision 1.10  2003/07/03 04:24:45  outlyer
# use OGGENC_CMD, and only show encoding options for encoders that are
# actually available.
#
# Revision 1.9  2003/07/03 04:19:31  outlyer
# Updated cdbackup with Rich's new Ogg patch; also changed some variables,
# and added oggenc to setup and configuration.
#
#
# Revision 1.9  2003/07/03 21:12:58  cornejo
# Added capability to rip to Ogg format.
#
# Revision 1.8  2003/07/01 20:28:29  outlyer
# Two things:
#     o Major code cleanup, removed lots of commented out stuff, changed
#         most of the commands being called
#     o Made mp3 the default in the ripping menu (i.e. the top item rather
#         than wav.
#
# Revision 1.7  2003/07/01 19:56:29  outlyer
# Use util.tagmp3() function by default, since we can choose the tag version.
# Well, it's not in the configuration yet, but soon enough.
#
# Revision 1.6  2003/07/01 14:33:26  outlyer
# Fixed a double escape of single quotes.
#
# Todo:
#
# o Move os.system() into runapp.
# o Use eyeD3 for tagging
#
# Revision 1.5  2003/07/01 06:34:31  outlyer
# Forgot to commit this stuff.
#
# 1. Fix filenames so songs with ' work
# 2. Show time taken to encode in the popup box.
#
# Revision 1.4  2003/07/01 06:10:52  gsbarbieri
# Destination dir is now configurable via AUDIO_BACKUP_DIR
# We have to add this option and others that came with this plugin to
# FREEVO_CONF_CHANGES and LOCAL_CONF_CHANGES.
# Also, this variables should be checked... they're missing some information, like MOVIE_DATA_DIR
#
# Revision 1.3  2003/07/01 04:34:48  outlyer
# Fixed header
#
# Revision 1.2  2003/07/01 04:31:48  outlyer
# Cleanup comments, add 'if DEBUG:' to most print statements and change
# os.system(rm ...) to os.unlink(...)
#
# Revision 1.1  2003/07/01 03:52:41  outlyer
# Added a working cd backup plugin.
# 
# I was able to rip songs succesfully after making some minor changes.
# 
# From the submitted code I made the following changes:
# 
# o Moved all command-line tools to config
# o Put defaults in freevo_config for encoding parameters.
# o Removed all CDDB code, we only use mmpython now.
# 
# Current issues:
# 
# o As far as I can tell, mmpython is swapping the artist and the album
# o No progress or information of any kind. I'll probably put something into
#    the idle bar to at least make it clear something is happening.
# 
# Still, it's very complete and works very well so far.  I put --preset standard as the
# default encoding style for lame, which is reasonable, though not what I would use.
# 
# Revision 1.0  2003/06/09 21:12:58  cornejo
# o Initial Revision - currently only supports ripping a CD to the hard drive 
# o in either .wav or .mp3.
# o Uses directory and file naming as obtained by CDDB CD Artist, Album, and track info. 
# o local_conf.py parameter is used to determine directory structure and file naming scheme.
# o local_conf.py parameter is also used for lame encoding parameters, and id3 tagging info
# o CD Audio detection/identifciation code was copied/modified from rom_drives.py who's Author=dischi
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
# endif

import os
import time
import string

import config

import menu

import rc

from gui.AlertBox import AlertBox
from gui.PopupBox import PopupBox
from gui.ConfirmBox import ConfirmBox

import plugin
from item import Item

import util

import skin
skin = skin.get_singleton()

import os
import sys

import threading

import re

# Included to be able to access the info for Audio CDs
import mmpython

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0

menuwidget = menu.get_singleton()

killflag = 0

song_names = []



class main_backup_thread(threading.Thread):
    device = None
    rip_format = ''
    def __init__(self, rip_format, device=None):
        threading.Thread.__init__(self)
        self.device = device
        self.rip_format = rip_format
        
    def run(self, rip_format='mp3'):        
        if self.rip_format == 'mp3' :
            self.cd_backup_threaded(self.device, rip_format='mp3')
        elif self.rip_format == 'ogg' :
            self.cd_backup_threaded(self.device, rip_format='ogg')                      
        elif self.rip_format == 'wav' :
            self.cd_backup_threaded(self.device, rip_format='wav')        
          
    
    def cd_backup_threaded(self, device, rip_format='mp3'):  
        rip_format = rip_format
        album = 'default_album'
        artist = 'default_artist'
        genre = 'default_genre'
        dir_audio_default = "dir_audio_default"        
        path_head = ''
        
        # Get the artist, album and song_names	
        (artist, album, genre, song_names) = self.get_formatted_cd_info(device)
               
        dir_audio = config.AUDIO_BACKUP_DIR
        
        user_rip_path_prefs = {  'artist': artist,
       	                         'album': album,
                                 'genre': genre }
        
        path_list = re.split("\\/", config.CD_RIP_PN_PREF)
        
        # Get everything up to the last "/"
        if len(path_list) != 0:
            for i in range (0, len(path_list)-1 ):
                path_head +=  '/' + path_list[i]
        path_tail_temp = '/' + path_list[len(path_list)-1]
        
        # If no directory structure preferences were given use default dir structure
        if len(path_list) == 0:
             pathname = dir_audio + "/" + artists + "/" + album + "/"
        # Else use the preferences given by user
        else:
            path_temp  =  dir_audio + path_head
            pathname = path_temp % user_rip_path_prefs
             
        try: 
            os.makedirs(pathname, 0777)
        except:
             if DEBUG: print 'Directory %s already exists' %pathname
             pass
      
        cdparanoia_command = []
        length=len(song_names)

        for i in range (0, len(song_names)):
            # Keep track of track# 
            track = i +1        
            
            # store start time

            begin = time.time()

            # CD_RIP_PATH = '%(artist)s/%(album)/%(song)s'

            # Add the song and track key back into user_rip_path_prefs to be used in the song name
            # as specified in CD_RIP_PN_PREF.  The song name was previously not set
            # so had to wait until here to add it in.

            track = '%0.2d' % int(track)
            user_rip_path_prefs = {  'artist': artist,
                                                 'album': album,
                                                 'genre': genre,
                                                 'track': track,
                                                 'song': song_names[i] }
                                                                                             
            path_tail = path_tail_temp % user_rip_path_prefs 
            
            # If rip_format is mp3 or ogg, then copy the file to /temp/track_being_ripped.wav

            if (string.upper(rip_format) == 'MP3') or (string.upper(rip_format) == 'OGG'):
                pathname_cdparanoia = '/tmp'
                path_tail_cdparanoia   = '/track_being_ripped'
           
            # Otherwise if it's going to be a .wav  just use the the users preferred directory and filename.
            # i.e. don't bother putting into /tmp directory, just use directory and filename of final destination.    

            else: 
                pathname_cdparanoia = pathname
                path_tail_cdparanoia   = path_tail
                            
            # Build the cdparanoia command to be run

            cdparanoia_command = '%s -s %s "%s%s.wav"' % (config.CDPAR_CMD, str(i+1), 
                pathname_cdparanoia, path_tail_cdparanoia)

            if DEBUG: print 'cdparanoia:  %s' % cdparanoia_command
    
            # Have the OS execute the CD Paranoia rip command            
            os.system(cdparanoia_command)
             
            # Build the lame command to be run if mp3 format is selected
            
            if string.upper(rip_format) == 'MP3':
           
                lame_command = '%s --nohist -h %s "%s%s.wav" "%s%s.mp3"' % (config.LAME_CMD,
                    config.CD_RIP_LAME_OPTS, pathname_cdparanoia, path_tail_cdparanoia,
                    pathname, path_tail)

                if DEBUG: 'lame: %s' %lame_command                          
                os.system(lame_command)
               
                util.tagmp3(pathname+path_tail+'.mp3', title=song_names[i], artist=artist, album=album, track=track, 
                    tracktotal=len(song_names))
                    
                # Remove the .wav file.
                rm_command = '%s%s.wav' % (pathname_cdparanoia, path_tail_cdparanoia)
                if os.path.exists (rm_command): os.unlink(rm_command)

            # Build the oggenc command to be run if ogg format is selected                
                                
            elif string.upper(rip_format) == 'OGG':
                oggenc_command = \
                    '%s %s -a "%s" -G "%s" -N "%s" -t "%s" -l "%s" "%s%s.wav" -o "%s%s.ogg"' % \
                    (config.OGGENC_CMD, config.CD_RIP_OGG_OPTS, 
                    artist, genre, track, song_names[i], album,
                    pathname_cdparanoia, path_tail_cdparanoia, pathname, path_tail)

                if DEBUG: 'oggenc_command: %s' %oggenc_command                          
                os.system(oggenc_command)
                    
                # Remove the .wav file.
                rm_command = '%s%s.wav' % (pathname_cdparanoia, path_tail_cdparanoia)
                if os.path.exists (rm_command): os.unlink(rm_command)                
        
        # Flash a popup window indicating copying is done
        time_taken = time.time() - begin + 300
        min = int(time_taken/60)
        sec = int(time_taken%60)
        popup_string="Finished Copying CD in %im%is" % (min,sec)
        #pop = AlertBox(text=popup_string)
        #pop.show()
        # Disabled because if the popup happens when you're listening to music,
        # you can no longer do anything in Freevo.

    def get_formatted_cd_info(self, device):
        cd_info = mmpython.parse(device)
        
        # Check if getting CDDB data failed -is there a better way to do this?
        # Give some defaults with a timestamp to uniqueify artist and album names.
        # So that subsequent CDs with no CDDB data found don't overwrite each other.
        if ((cd_info.title == None) and (cd_info.artist == None)):

            print 'Error: No CDDB data returned from MMPYTHON'
            current_time = time.strftime('%d-%b-%y-%I:%M%P')
            
            print 'The current time is: %s' %current_time
            
            artist ='Unknown Artist ' + current_time + ' - RENAME'
            album ='Unknown CD Album ' + current_time +  ' - RENAME'
            genre ='Other'
           
           # Flash a popup window indicating copying is done
            popup_string="CD info not found!\nMust manually rename files\nwhen finished ripping"

            pop = AlertBox(text=popup_string)
            time.sleep(7)

        # If  valid data was returned from mmpython/CDDB
        else:
            album   = self.replace_special_char(cd_info.title, '-')
            artist     = self.replace_special_char(cd_info.artist, '-')
            genre    = self.replace_special_char(cd_info.tracks[0].genre, '-')

        song_names = []                        
        for track in cd_info.tracks:
            song_names.append(self.replace_special_char(track.title, '-'))
            
        return [artist, album, genre, song_names]                
    
    # This function gets rid of the slash, '/', in a string, and replaces it  with join_string    
    def slash_split(self, string, join_string = '-'):
        split_string= re.split(" \\/ ", string)
        rejoined_string = ''
        # Were there any splits on '/'?
        if len(split_string) > 1:
            for  i in range (0, len(split_string)):
                # Are we at the last slash
                if (i == (len(split_string) - 1)):
                    rejoined_string += split_string[i]
                # if not at the last slash, keep adding to string the join_string                        
                else :
                    rejoined_string += split_string[i] + join_string
        # If there are no slashes , then the list is only 1 element long and there is nothing to do.
        else:
            rejoined_string = string
        
        return rejoined_string               

    # Function to get rid of funky characters that exist in a string
    # so that when for example writing a file to disk, the filename 
    # doesn't contain any special reserved characters.
    # This list of special_chars probably contains some characters that are okay.            
    def replace_special_char(self, string, repl='-'):
        # Regular Expression Special Chars =  . ^ $ * + ? { [ ] \ | ( )
        special_chars = [ '\"',  '\`', '\\\\', '/','~' ]
        new_string = string
        num = 0
       
        for j in special_chars:
            pattern = j
            try: 
                # A few of the special characters get automatically converted to a different char,
                # rather than what is passed in as repl
                if (pattern == "\'"):
                    (new_string, num) = re.subn(pattern, "\\\'", new_string, count=0)
                elif (pattern == '/'):
                    (new_string, num) = re.subn(pattern, '\\\\', new_string, count=0)                    
                else:
                    (new_string, num) = re.subn(pattern, repl, new_string, count=0)
            except:
                print 'Error: Problem trying to call re.subn'
        return new_string    
        
class PluginInterface(plugin.ItemPlugin):
    """
    Plugin to rip and burn MP3s/CDs/Movies 
    """
    artist = ''
    album = ''
    song_names = []
    device = ''

    def actions(self, item):
        self.item = item
        
        try:
            if (self.item.display_type == 'audio'):
                self.device = self.item.devicename
                if DEBUG: print 'devicename = %s' %self.device
                return [ ( self.create_backup_menu, 'Rip the CD to the hard drive', 'Get CDs available for ripping') ]
        except:
            print 'Error: Item is not an AudioCD'
        return []

    def create_backup_menu(self, arg=None, menuw=None):
        mm_menu = self.create_backup_items(self.device, menuw=None)
        menuwidget.pushmenu(mm_menu)
        menuwidget.refresh()

    def create_backup_items(self, arg, menuw):   
        items = []

        if config.LAME_CMD:
            items += [menu.MenuItem('Backup CD to hard drive in mp3 format',
                                self.cd_backup_mp3, arg=arg)]
        if config.OGGENC_CMD:
            items += [menu.MenuItem('Backup CD to hard drive in Ogg format',
                                self.cd_backup_ogg, arg=arg)]
                                
        items += [menu.MenuItem('Backup CD to hard drive in wav format',
                                self.cd_backup_wav, arg=arg)]

        backupmenu = menu.Menu('CD Backup', items, reload_func=self.create_backup_menu)
        rc.app(None)
        return backupmenu
        
    def cd_backup_wav(self, arg, menuw=None):         
        device = arg
        rip_thread = main_backup_thread(device=device, rip_format='wav')        
        rip_thread.start()

    def cd_backup_mp3(self, arg,  menuw=None):            
        device = arg
        rip_thread = main_backup_thread(device=device, rip_format='mp3')        
        rip_thread.start()

    def cd_backup_ogg(self, arg,  menuw=None):            
        device = arg
        rip_thread = main_backup_thread(device=device, rip_format='ogg')        
        rip_thread.start()
        
