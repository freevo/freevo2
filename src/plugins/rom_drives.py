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
# Revision 1.16  2003/07/18 19:49:47  dischi
# do not set speed for dvd, it does not work
#
# Revision 1.15  2003/07/12 21:24:19  dischi
# sort list before checkin
#
# Revision 1.14  2003/07/05 09:09:47  dischi
# fixed eject problems
#
# Revision 1.13  2003/07/02 22:05:50  dischi
# o better cache handling
# o shorter label for tv show discs
#
# Revision 1.12  2003/06/30 15:30:54  dischi
# some checking to avoid endless scanning
#
# Revision 1.11  2003/06/29 20:44:21  dischi
# mmpython support
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

import time, os
from fcntl import ioctl
import re
import threading
import thread
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

import mmpython


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
CDS_MIXED=105
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
        self.cached   = FALSE

    def is_tray_open(self):
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
            global im_thread
            if im_thread:
                im_thread.check_all()
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
        media.cached    = FALSE

        # Is there a disc present?
        if s != CDS_DISC_OK:
            os.close(fd)
            return

        # if there is a disc, the tray can't be open
        media.tray_open = FALSE
        data = mmpython.parse(media.devicename)

        if data and data.mime == 'audio/cd':
            os.close(fd)
            disc_id = data.id
            media.info = AudioDiskItem(disc_id, parent=None,
                                       devicename=media.devicename,
                                       display_type='audio')
            media.info.handle_type = 'audio'
            media.info.media = media
            if data.title:
                media.info.name = data.title
            media.info.info = data
            return

        # try to set the speed
        if config.ROM_SPEED and not data.mime == 'video/dvd':
            try:
                ioctl(fd, CDROM_SELECT_SPEED, config.ROM_SPEED)
            except:
                pass

        os.close(fd)
        image = title = movie_info = more_info = xml_file = None

        if not data:
            # this should never happen
            return

        media.id    = data.id
        media.label = data.label
        media.type  = 'cdrom'

        label = data.label
        
        # is the id in the database?
        if media.id in config.MOVIE_INFORMATIONS_ID:
            movie_info = config.MOVIE_INFORMATIONS_ID[media.id]
            if movie_info:
                title = movie_info.name
            
        # no? Maybe we can find a label regexp match
        else:
            for (re_label, movie_info_t) in config.MOVIE_INFORMATIONS_LABEL:
                if re_label.match(media.label):
                    movie_info = movie_info_t
                    if movie_info_t.name:
                        title = movie_info.name
                        m = re_label.match(media.label).groups()
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
                        

        # DVD/VCD/SVCD:
        # There is data from mmpython for these three types
        if data.mime in ('video/vcd', 'video/dvd'):
            if not title:
                title = '%s [%s]' % (data.mime[6:].upper(), media.label)

            if movie_info:
                media.info = copy.copy(movie_info)
            else:
                media.info = videoitem.VideoItem('0', None)

            media.info.name = title
            media.info.mode = data.mime[6:]
            media.info.media = media

            media.type  = data.mime[6:]

            if media.info.info:
                for i in media.info.info:
                    if media.info.info[i]:
                        data[i] = media.info.info[i]
            media.info.info = data

            # copy configure options from track[0] to main item
            # for playback
            for k in ('audio', 'subtitles', 'chapters' ):
                if media.info.info.tracks[0].has_key(k):
                    if not media.info.info.has_key(k):
                        media.info.info.keys.append(k)
                        media.info.info[k] = media.info.info.tracks[0][k]

            if os.path.isfile(config.COVER_DIR+label+'.jpg'):
                media.info.image = config.COVER_DIR+label+'.jpg'

            media.info.num_titles = len(data.tracks)
            # Hack to avoid rescan, remove this when mmpython is used
            # everytime
            media.info.scanned = TRUE
            return

        if data.tracks:
            mplayer_files = []
            mp3_files     = []
            image_files   = []
            for t in data.tracks:
                if t and t['url']:
                    file = t['url'][len(media.devicename)+6:].replace(':', '/')
                    if util.match_suffix(file, config.SUFFIX_VIDEO_FILES):
                        mplayer_files.append(file)
                    if util.match_suffix(file, config.SUFFIX_AUDIO_FILES):
                        mp3_files.append(file)
                    if util.match_suffix(file, config.SUFFIX_IMAGE_FILES):
                        image_files.append(file)
            media.cached = TRUE
                
        else:
            # Disc is data of some sort. Mount it to get the file info
            util.mount(media.mountdir, force=TRUE)

            # Check for movies/audio/images on the disc
            mplayer_files = util.match_files(media.mountdir, config.SUFFIX_VIDEO_FILES)
            mp3_files = util.match_files(media.mountdir, config.SUFFIX_AUDIO_FILES)
            image_files = util.match_files(media.mountdir, config.SUFFIX_IMAGE_FILES)

            util.umount(media.mountdir)


        if DEBUG > 2:
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
                start_ep = 0
                end_ep   = 0

                mplayer_files.sort(lambda l, o: cmp(l.upper(), o.upper()))

                for movie in mplayer_files:
                    if config.TV_SHOW_REGEXP_MATCH(movie):
                        show = config.TV_SHOW_REGEXP_SPLIT(os.path.basename(movie))

                        if show_name and show_name != show[0]:
                            the_same = 0
                        if not show_name:
                            show_name = show[0]
                        if volumes:
                            volumes += ', '
                        current_ep = int(show[1]) * 100 + int(show[2])
                        if end_ep and current_ep == end_ep + 1:
                            end_ep = current_ep
                        elif not end_ep:
                            end_ep = current_ep
                        else:
                            end_ep = -1
                        if not start_ep:
                            start_ep = end_ep
                        volumes += show[1] + "x" + show[2]

                if show_name and the_same:
                    if end_ep > 0:
                        volumes = '%dx%02d - %dx%02d' % (start_ep / 100, start_ep % 100,
                                                         end_ep / 100, end_ep % 100)
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
        self.lock.acquire()
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
        self.lock.release()

                
    def __init__(self):
        threading.Thread.__init__(self)
        self.last_media = None          # last changed media
        self.lock = thread.allocate_lock()

        
    def run(self):

        rebuild_file = '/tmp/freevo-rebuild-database'
        # Make sure the movie database is rebuilt at startup
        os.system('touch %s' % rebuild_file)
        while 1:
            # Check if we need to update the database
            # This is a simple way for external apps to signal changes
            if os.path.exists(rebuild_file):
                if xml_parser.hash_xml_database() == 0:
                    # something is wrong, deactivate this feature
                    rebuild_file = '/this/file/should/not/exist'
                    
                for media in config.REMOVABLE_MEDIA:
                    media.drive_status = None

            self.check_all()
            time.sleep(2)

