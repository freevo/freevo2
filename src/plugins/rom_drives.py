#if 0 /*
# -----------------------------------------------------------------------
# rom_drives.py - the Freevo identifymedia/automount plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2003/05/29 09:06:18  dischi
# small fix again
#
# Revision 1.8  2003/05/28 15:11:43  dischi
# small bugfix
#
# Revision 1.7  2003/05/27 17:53:35  dischi
# Added new event handler module
#
# Revision 1.6  2003/04/26 15:09:19  dischi
# changes for the new mount/umount
#
# Revision 1.5  2003/04/24 19:56:38  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.4  2003/04/24 19:14:50  dischi
# pass xml_file to directory and videoitems
#
# Revision 1.3  2003/04/20 17:36:49  dischi
# Renamed TV_SHOW_IMAGE_DIR to TV_SHOW_DATA_DIR. This directory can contain
# images like before, but also fxd files for the tv show with global
# informations (plot/tagline/etc) and mplayer options.
#
# Revision 1.2  2003/04/20 12:43:33  dischi
# make the rc events global in rc.py to avoid get_singleton. There is now
# a function app() to get/set the app. Also the events should be passed to
# the daemon plugins when there is no handler for them before. Please test
# it, especialy the mixer functions.
#
# Revision 1.1  2003/04/20 10:53:23  dischi
# moved identifymedia and mediamenu to plugins
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

import time, os
from fcntl import ioctl
import re
import threading
import string
import copy

import config
import util
import rc
import event as em
import plugin

from audio.audiodiskitem import AudioDiskItem
from video.videoitem import VideoItem
from item import Item

TRUE  = 1
FALSE = 0

# CDDB Stuff
try:
    import DiscID, CDDB
except:
    print "CDDB not installed."
    pass

from video import xml_parser, videoitem
from directory import DirItem

DEBUG = config.DEBUG   # 1 = regular debug, 2 = more verbose

LABEL_REGEXP = re.compile("^(.*[^ ]) *$").match


# taken from cdrom.py so we don't need to import cdrom.py
CDROM_DRIVE_STATUS=0x5326
CDSL_CURRENT=( (int ) ( ~ 0 >> 1 ) )
CDS_DISC_OK=4
CDROM_DISC_STATUS=0x5327
CDS_AUDIO=100
CDROM_SELECT_SPEED=0x5322


# Identify_Thread
im_thread = None

from gui.PopupBox import PopupBox


def init():
    # Add the drives to the config.removable_media list. There doesn't have
    # to be any drives defined.
    if config.ROM_DRIVES != None: 
        for i in range(len(config.ROM_DRIVES)):
            (dir, device, name) = config.ROM_DRIVES[i]
            media = RemovableMedia(mountdir=dir, devicename=device,
                                   drivename=name)
            # close the tray without popup message
            media.move_tray(dir='close', notify=0)
            config.REMOVABLE_MEDIA.append(media)

    # Remove the ROM_DRIVES member to make sure it is not used by
    # legacy code!
    del config.ROM_DRIVES   # XXX Remove later
    
    # Start identifymedia thread
    global im_thread
    im_thread = Identify_Thread()
    im_thread.setDaemon(1)
    im_thread.start()


class autostart(plugin.DaemonPlugin):
    """
    Plugin to autostart if a new medium is inserted while Freevo shows
    the main menu
    """
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        global im_thread
        if not im_thread:
            init()
            
    def eventhandler(self, event = None, menuw=None, arg=None):
        """
        eventhandler to handle the IDENTIFY_MEDIA plugin event and the
        EJECT event
        """
        global im_thread
        
        # if we are at the main menu and there is an IDENTIFY_MEDIA event,
        # try to autorun the media
        if plugin.isevent(event) == 'IDENTIFY_MEDIA' and im_thread.last_media and \
           menuw and len(menuw.menustack) == 1:
            media = im_thread.last_media
            if media.info:
                media.info.parent = menuw.menustack[0].selected
            if media.info and media.info.actions():
                media.info.actions()[0][0](menuw=menuw)
            else:
                menuw.refresh()
            return TRUE

        # Handle the EJECT key for the main menu
        elif event == em.EJECT and len(menuw.menustack) == 1:

            # Are there any drives defined?
            if config.REMOVABLE_MEDIA:
                # The default is the first drive in the list
                media = config.REMOVABLE_MEDIA[0]  
                media.move_tray(dir='toggle')
                return TRUE
            


class rom_items(plugin.MainMenuPlugin):
    """
    Plugin to add the rom drives to a main menu. This can be the global main menu
    or most likely the video/audio/image/games main menu
    """
    def __init__(self):
        plugin.MainMenuPlugin.__init__(self)
        self.parent = None
        global im_thread
        if not im_thread:
            init()
        
    def items(self, parent):
        """
        return the list of rom drives
        """
        self.parent = parent
        items = []
        for media in config.REMOVABLE_MEDIA:
            if media.info:
                # if this is a video item (e.g. DVD) and we are not in video
                # mode, deactivate it
                if media.info.type == 'video' and parent.display_type != 'video':
                    m = Item(parent)
                    m.type = media.info.type
                    m.copy(media.info)
                    m.media = media

                elif parent.display_type == 'video' and media.videoinfo:
                    m = media.videoinfo
                    
                else:
                    if media.info.type == 'dir':
                        media.info.display_type = parent.display_type
                    m = media.info

            else:
                m = Item(parent)
                m.name = 'Drive %s (no disc)' % media.drivename
                m.media = media
                media.info = m

            # hack: now make self the parent to get the events
            m.parent = parent
            m.eventhandler_plugins.append(self.items_eventhandler)
            items.append(m)
            
        return items


    def items_eventhandler(self, event, item, menuw):
        """
        handle EJECT for the rom drives
        """
        if event == em.EJECT and item.media and menuw and \
           menuw.menustack[1] == menuw.menustack[-1]:
            item.media.move_tray(dir='toggle')
            return TRUE
        return FALSE
    

class RemovableMedia:
    """
    Object about one drive
    """
    def __init__(self, mountdir='', devicename='', drivename=''):
        # This is read-only stuff for the drive itself
        self.mountdir = mountdir
        self.devicename = devicename
        self.drivename = drivename

        # Dynamic stuff
        self.tray_open = 0
        self.drive_status = None  # return code from ioctl for DRIVE_STATUS

        self.id        = ''
        self.label     = ''
        self.info      = None
        self.videoinfo = None
        self.type      = 'empty_cdrom'

    def is_tray_open(self):
        if self.tray_open and self.info:
            # if we have an info, the tray can't be open
            self.tray_open = FALSE
        return self.tray_open

    def move_tray(self, dir='toggle', notify=1):
        """Move the tray. dir can be toggle/open/close
        """

        if dir == 'toggle':
            if self.is_tray_open():
                dir = 'close'
            else:
                dir = 'open'

        if dir == 'open':
            if DEBUG: print 'Ejecting disc in drive %s' % self.drivename
            if notify:
                pop = PopupBox(text='Ejecting disc in drive %s' % self.drivename) 
                pop.show()
            os.system('eject %s' % self.devicename)
            self.tray_open = 1
            if notify:
                pop.destroy()

        
        elif dir == 'close':
            if DEBUG: print 'Inserting %s' % self.drivename
            if notify:
                pop = PopupBox(text='Reading disc in drive %s' % self.drivename)
                pop.show()

            # close the tray, identifymedia does the rest,
            # including refresh screen
            os.system('eject -t %s' % self.devicename)
            self.tray_open = 0
            if notify:
                pop.destroy()

    
    def mount(self):
        """Mount the media
        """

        if DEBUG: print 'Mounting disc in drive %s' % self.drivename
        util.mount(self.mountdir, force=TRUE)
        return

    
    def umount(self):
        """Mount the media
        """

        if DEBUG: print 'Unmounting disc in drive %s' % self.drivename
        util.umount(self.mountdir)
        return
    



class Identify_Thread(threading.Thread):
    """
    Thread to watch the rom drives for changes
    """
    def identify(self, media):
        """
        magic!
        Try to find out as much as possible about the disc in the
        rom drive: title, image, play options, ...
        """
        # Check drive status (tray pos, disc ready)
        try:
            fd = os.open(media.devicename, os.O_RDONLY | os.O_NONBLOCK)
            s = ioctl(fd, CDROM_DRIVE_STATUS, CDSL_CURRENT)
        except:
            # maybe we need to close the fd if ioctl fails, maybe
            # open fails and there is no fd
            try:
                os.close(fd)
            except:
                pass
            media.drive_status = None
            return

        # Same as last time? If so we're done
        if s == media.drive_status:
            os.close(fd)
            return

        media.drive_status = s

        media.id        = ''
        media.label     = ''
        media.type      = 'empty_cdrom'
        media.info      = None
        media.videoinfo = None

        # Is there a disc present?
        if s != CDS_DISC_OK:
            os.close(fd)
            return

        # Check media type (data, audio)
        s = ioctl(fd, CDROM_DISC_STATUS)
        if s == CDS_AUDIO:
            os.close(fd)
            media.type  = 'audiocd'
            try:
                cdrom = DiscID.open(media.devicename)
                disc_id = DiscID.disc_id(cdrom)
                media.info = AudioDiskItem(disc_id, parent=None, name='',
                                           devicename=media.devicename,
                                           display_type='audio')
                (query_stat, query_info) = CDDB.query(disc_id)

                media.info.handle_type = 'audio'
                if query_stat == 200:
                    media.info.title = query_info['title']

                elif query_stat == 210 or query_stat == 211:
                    print "multiple matches found! Matches are:"
                    for i in query_info:
                        print "ID: %s Category: %s Title: %s" % \
                              (i['disc_id'], i['category'], i['title'])
                else:
                    print "failure getting disc info, status %i" % query_stat
                    media.info.title = 'Unknown CD Album'
            except:
                pass
            return

        # try to set the speed
        if config.ROM_SPEED:
            try:
                ioctl(fd, CDROM_SELECT_SPEED, config.ROM_SPEED)
            except:
                pass
            
        mediatypes = [('VCD', '/mpegav/', 'vcd'), ('SVCD','/SVCD/', 'vcd'), 
                      ('SVCD','/svcd/', 'vcd'), ('DVD', '/video_ts/', 'dvd'),
		      ('DVD','/VIDEO_TS/','dvd')]

        image = title = movie_info = more_info = xml_file = None

        # Read the volume label directly from the ISO9660 file system
        
        os.close(fd)
        try:
            img = open(media.devicename)
            img.seek(0x0000832d)
            id = img.read(16)
            img.seek(32808, 0)
            label = img.read(32)
            m = LABEL_REGEXP(label)
            if m:
                label = m.group(1)
            img.close()
        except IOError:
            print 'I/O error on disc %s' % media.devicename
            return

        media.id    = id+label
        media.label = ''
        media.type  = 'cdrom'
        
        # is the id in the database?
        if id+label in config.MOVIE_INFORMATIONS_ID:
            movie_info = config.MOVIE_INFORMATIONS_ID[id+label]
            if movie_info:
                title = movie_info.name
            
        # no? Maybe we can find a label regexp match
        else:
            for (re_label, movie_info_t) in config.MOVIE_INFORMATIONS_LABEL:
                if re_label.match(label):
                    movie_info = movie_info_t
                    if movie_info_t.name:
                        title = movie_info.name
                        m = re_label.match(label).groups()
                        re_count = 1

                        # found, now change the title with the regexp. E.g.:
                        # label is "bla_2", the label regexp "bla_[0-9]" and the title
                        # is "Something \1", the \1 will be replaced with the first item
                        # in the regexp group, here 2. The title is now "Something 2"
                        for g in m:
                            title=string.replace(title, '\\%s' % re_count, g)
                            re_count += 1
                        break
                
        if movie_info:
            image = movie_info.image
                        
        # Disc is data of some sort. Mount it to get the file info
        util.mount(media.mountdir, force=TRUE)

        # Check for DVD/VCD/SVCD
        for mediatype in mediatypes:
            if os.path.exists(media.mountdir + mediatype[1]):
                util.umount(media.mountdir)

                if not title:
                    title = '%s [%s]' % (mediatype[0], label)

                if movie_info:
                    media.info = copy.copy(movie_info)
                else:
                    media.info = videoitem.VideoItem('0', None)

                media.info.label = label
                media.info.name = title
                media.info.mode = mediatype[2]
                media.info.media = media

                media.type  = mediatype[2]

                if os.path.isfile(config.COVER_DIR+label+'.jpg'):
                    media.info.image = config.COVER_DIR+label+'.jpg'
                return
        
        # Check for movies/audio/images on the disc
        mplayer_files = util.match_files(media.mountdir, config.SUFFIX_VIDEO_FILES)
        mp3_files = util.match_files(media.mountdir, config.SUFFIX_AUDIO_FILES)
        image_files = util.match_files(media.mountdir, config.SUFFIX_IMAGE_FILES)

        util.umount(media.mountdir)

        if DEBUG:
            print 'identifymedia: mplayer = "%s"' % mplayer_files
            print 'identifymedia: mp3="%s"' % mp3_files
            print 'identifymedia: image="%s"' % image_files
            
        media.info = DirItem(media.mountdir, None)
        
        # Is this a movie disc?
        if mplayer_files and not mp3_files:
            media.info.handle_type = 'video'

            # try to find out if it is a series cd
            if not title:
                show_name = ""
                the_same  = 1
                volumes   = ''
                for movie in mplayer_files:
                    if config.TV_SHOW_REGEXP_MATCH(movie):
                        show = config.TV_SHOW_REGEXP_SPLIT(os.path.basename(movie))

                        if show_name and show_name != show[0]: the_same = 0
                        if not show_name: show_name = show[0]
                        if volumes: volumes += ', '
                        volumes += show[1] + "x" + show[2]

                if show_name and the_same:
                    k = config.TV_SHOW_DATA_DIR + show_name
                    if os.path.isfile((k + ".png").lower()):
                        image = (k + ".png").lower()
                    elif os.path.isfile((k + ".jpg").lower()):
                        image = (k + ".jpg").lower()
                    title = show_name + ' ('+ volumes + ')'
                    if config.TV_SHOW_INFORMATIONS.has_key(show_name.lower()):
                        tvinfo = config.TV_SHOW_INFORMATIONS[show_name.lower()]
                        more_info = tvinfo[1]
                        if not image:
                            image = tvinfo[0]
                        if not xml_file:
                            xml_file = tvinfo[3]
                    
                elif not show_name:
                    if os.path.isfile(config.COVER_DIR+\
                                      os.path.splitext(os.path.basename(movie))[0]+'.png'):
                        image = config.COVER_DIR+\
                                os.path.splitext(os.path.basename(movie))[0]+'.png'
                    elif os.path.isfile(config.COVER_DIR+\
                                        os.path.splitext(os.path.basename(movie))[0]+'.jpg'):
                        image = config.COVER_DIR+\
                                os.path.splitext(os.path.basename(movie))[0]+'.jpg'
                    title = os.path.splitext(os.path.basename(movie))[0]
            # nothing found, give up: return the label
            if not title:
                title = label


        # XXX add more intelligence to cds with audio files
        elif (not mplayer_files) and mp3_files:
            media.info.handle_type = 'audio'
            title = '%s [%s]' % (media.drivename, label)

        # XXX add more intelligence to cds with image files
        elif (not mplayer_files) and (not mp3_files) and image_files:
            media.info.handle_type = 'image'
            title = '%s [%s]' % (media.drivename, label)

        # Mixed media?
        elif mplayer_files or image_files or mp3_files:
            media.info.handle_type = None
            title = '%s [%s]' % (media.drivename, label)
        
        # Strange, no useable files
        else:
            media.info.handle_type = None
            title = '%s [%s]' % (media.drivename, label)


        if movie_info:
            media.info.copy(movie_info)
        if title:
            media.info.name = title
        if image:
            media.info.image = image
        if more_info:
            media.info.info = more_info
        if xml_file:
            media.info.xml_file = xml_file

        if len(mplayer_files) == 1:
            media.videoinfo = VideoItem(mplayer_files[0], None)
            media.videoinfo.media = media
            media.videoinfo.media_id = media.id
            media.videoinfo.label = media.label
            
            if movie_info:
                media.videoinfo.copy(movie_info)
            if title:
                media.videoinfo.name = title
            if image:
                media.videoinfo.image = image
            if more_info:
                media.videoinfo.info = more_info
            if xml_file:
                media.videoinfo.xml_file = xml_file
            
        media.info.media = media
        return


    def check_all(self):
        for media in config.REMOVABLE_MEDIA:
            last_status = media.drive_status
            self.identify(media)

            if last_status != media.drive_status:
                if DEBUG:
                    print 'MEDIA: Status=%s' % media.drive_status
                    print 'Posting IDENTIFY_MEDIA event'
                if last_status:
                    self.last_media = media
                rc.post_event(plugin.event('IDENTIFY_MEDIA'))
            else:
                if DEBUG > 1:
                    print 'MEDIA: Status=%s' % media.drive_status

                
    def __init__(self):
        threading.Thread.__init__(self)
        self.last_media = None          # last changed media

        
    def run(self):
        # Make sure the movie database is rebuilt at startup
        os.system('touch /tmp/freevo-rebuild-database')
        while 1:
            # Check if we need to update the database
            # This is a simple way for external apps to signal changes
            if os.path.exists("/tmp/freevo-rebuild-database"):
                xml_parser.hash_xml_database()
                for media in config.REMOVABLE_MEDIA:
                    media.drive_status = None

            self.check_all()
            time.sleep(2)

