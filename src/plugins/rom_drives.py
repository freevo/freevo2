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
# Revision 1.44  2003/11/28 20:08:57  dischi
# renamed some config variables
#
# Revision 1.43  2003/11/28 19:26:37  dischi
# renamed some config variables
#
# Revision 1.42  2003/11/24 19:25:28  dischi
# adjust to variable moving
#
# Revision 1.41  2003/11/22 20:36:04  dischi
# use new vfs
#
# Revision 1.40  2003/11/09 16:17:32  dischi
# fix mmpython info parsing for movies on disc
#
# Revision 1.39  2003/11/09 13:05:04  dischi
# support for disc images without fxd file
#
# Revision 1.38  2003/11/08 12:57:54  dischi
# also set speed for audio discs
#
# Revision 1.37  2003/10/18 17:57:22  dischi
# remove debug
#
# Revision 1.36  2003/10/04 18:37:29  dischi
# i18n changes and True/False usage
#
# Revision 1.35  2003/09/25 09:48:42  dischi
# handling if CDROM.py is missing
#
# Revision 1.34  2003/09/23 13:45:20  outlyer
# Making more informational text quiet by default.
#
# Revision 1.33  2003/09/21 13:32:10  dischi
# fix smart disc naming
#
# Revision 1.32  2003/09/20 15:08:26  dischi
# some adjustments to the missing testfiles
#
# Revision 1.31  2003/09/19 22:12:59  dischi
# kill some debug for level 1
#
# Revision 1.30  2003/09/19 16:04:37  outlyer
# Ugly, ugly change to work around a crash.
#
# Revision 1.29  2003/09/14 20:09:37  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.28  2003/09/13 10:08:22  dischi
# i18n support
#
# Revision 1.27  2003/08/29 23:41:32  outlyer
# Revert the warning-fix that was a function-breaker
#
# Revision 1.26  2003/08/26 19:53:38  outlyer
# Quiet another Python 2.4 warning
#
# Revision 1.25  2003/08/25 12:08:20  outlyer
# Additional compatibility patches for FreeBSD from Lars Eggert
#
# Revision 1.24  2003/08/24 05:20:15  gsbarbieri
# Empty cdroms type is now 'empty_cdrom' instead of None
#
# Revision 1.23  2003/08/23 19:57:41  dischi
# fix audiocd type setting
#
# Revision 1.22  2003/08/23 18:35:40  dischi
# use new set_xml_file function in DirItem
#
# Revision 1.21  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
#
# Revision 1.20  2003/08/23 12:10:00  dischi
# move to CDROM.py stuff and remove external eject
#
# Revision 1.19  2003/08/21 20:54:44  gsbarbieri
#    *ROM media just shows up when needed, ie: audiocd is not displayed in
# video main menu.
#    * ROM media is able to use variants, subtitles and more.
#    * When media is not present, ask for it and wait until media is
# identified. A better solution is to force identify media and BLOCK until
# it's done.
#
# Revision 1.18  2003/08/20 21:51:34  outlyer
# Use Python 'touch' rather than system call
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
try:
    from CDROM import *
except ImportError:
    if os.uname()[0] == 'FreeBSD':
        # FreeBSD ioctls - there is no CDROM.py...
        CDIOCEJECT = 0x20006318
        CDIOCCLOSE = 0x2000631c
        CDIOREADTOCENTRYS = 0xc0086305
        CD_LBA_FORMAT = 1
        CD_MSF_FORMAT = 2
        CDS_NO_DISC = 1
        CDS_DISC_OK = 4
    else:
        # strange ioctrls missing
        CDROMEJECT = 0x5309
        CDROMCLOSETRAY = 0x5319
        CDROM_DRIVE_STATUS = 0x5326
        CDROM_SELECT_SPEED = 0x5322
        CDS_NO_DISC = 1
        CDS_DISC_OK = 4
        
import traceback

import config
import util
import rc
import event as em
import plugin

import video

from audio.audiodiskitem import AudioDiskItem
from video.videoitem import VideoItem
from item import Item

import mmpython


from directory import DirItem

LABEL_REGEXP = re.compile("^(.*[^ ]) *$").match

from struct import *
import array

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
            return True

        # Handle the EJECT key for the main menu
        elif event == em.EJECT and len(menuw.menustack) == 1:

            # Are there any drives defined?
            if config.REMOVABLE_MEDIA:
                # The default is the first drive in the list
                media = config.REMOVABLE_MEDIA[0]  
                media.move_tray(dir='toggle')
                return True
            


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
                m.name = _('Drive %s (no disc)') % media.drivename
                m.type = media.type
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
            return True
        return False
    

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
        self.cached   = False

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
            _debug_('Ejecting disc in drive %s' % self.drivename,2)

            if notify:
                pop = PopupBox(text=_('Ejecting disc in drive %s') % self.drivename) 
                pop.show()

            try:
                fd = os.open(self.devicename, os.O_RDONLY | os.O_NONBLOCK)
                if os.uname()[0] == 'FreeBSD':
                    s = ioctl(fd, CDIOCEJECT, 0)
                else:
                    s = ioctl(fd, CDROMEJECT)
                os.close(fd)
            except:
                try:
                    traceback.print_exc()
                except IOError:
                    # believe it or not, this sometimes causes an IOError if
                    # you've got a music track playing in the background (detached)
                    pass
                # maybe we need to close the fd if ioctl fails, maybe
                # open fails and there is no fd
                try:
                    os.close(fd)
                except:
                    pass

            self.tray_open = 1
            if notify:
                pop.destroy()

        
        elif dir == 'close':
            _debug_('Inserting %s' % self.drivename,2)

            if notify:
                pop = PopupBox(text=_('Reading disc in drive %s') % self.drivename)
                pop.show()

            # close the tray, identifymedia does the rest,
            # including refresh screen
            try:
                fd = os.open(self.devicename, os.O_RDONLY | os.O_NONBLOCK)
                if os.uname()[0] == 'FreeBSD':            
                    s = ioctl(fd, CDIOCCLOSE, 0)
                else:
                    s = ioctl(fd, CDROMCLOSETRAY)
                os.close(fd)
            except:
                traceback.print_exc()
                # maybe we need to close the fd if ioctl fails, maybe
                # open fails and there is no fd
                try:
                    os.close(fd)
                except:
                    pass

            self.tray_open = 0
            global im_thread
            if im_thread:
                im_thread.check_all()
            if notify:
                pop.destroy()

    
    def mount(self):
        """Mount the media
        """

        _debug_('Mounting disc in drive %s' % self.drivename,2)
        util.mount(self.mountdir, force=True)
        return

    
    def umount(self):
        """Mount the media
        """

        _debug_('Unmounting disc in drive %s' % self.drivename,2)
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
            CDSL_CURRENT = ( (int ) ( ~ 0 >> 1 ) )
            fd = os.open(media.devicename, os.O_RDONLY | os.O_NONBLOCK)
            if os.uname()[0] == 'FreeBSD':
                try:
                    data = array.array('c', '\000'*4096)
                    (address, length) = data.buffer_info()
                    buf = pack('BBHP', CD_MSF_FORMAT, 0, length, address)
                    s = ioctl(fd, CDIOREADTOCENTRYS, buf)
                    s = CDS_DISC_OK
                except:
                    s = CDS_NO_DISC
            else:
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
        media.cached    = False

        # Is there a disc present?
        if s != CDS_DISC_OK:
            os.close(fd)
            return

        # if there is a disc, the tray can't be open
        media.tray_open = False
        data = mmpython.parse(media.devicename)

        # try to set the speed
        if config.ROM_SPEED and data and not data.mime == 'video/dvd':
            try:
                ioctl(fd, CDROM_SELECT_SPEED, config.ROM_SPEED)
            except:
                pass

        if data and data.mime == 'audio/cd':
            os.close(fd)
            disc_id = data.id
            media.info = AudioDiskItem(disc_id, parent=None,
                                       devicename=media.devicename,
                                       display_type='audio')
            media.type  = media.info.type
            media.info.handle_type = 'audio'
            media.info.media = media
            if data.title:
                media.info.name = data.title
            media.info.info = data
            return

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
        if media.id in video.fxd_database['id']:
            movie_info = video.fxd_database['id'][media.id]
            if movie_info:
                title = movie_info.name
            
        # no? Maybe we can find a label regexp match
        else:
            for (re_label, movie_info_t) in video.fxd_database['label']:
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
                media.info = VideoItem('0', None)
                if config.OVERLAY_DIR:
                    media.info.image = util.getimage(os.path.join(config.OVERLAY_DIR,
                                                                  'disc-set', media.id))

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

            media.info.num_titles = len(data.tracks)
            # Hack to avoid rescan, remove this when mmpython is used
            # everytime
            media.info.scanned = True
            return

        if data.tracks:
            mplayer_files = []
            mp3_files     = []
            image_files   = []
            for t in data.tracks:
                if t and t['url']:
                    file = t['url'][len(media.devicename)+6:].replace(':', '/')
                    if util.match_suffix(file, config.VIDEO_SUFFIX):
                        mplayer_files.append(file)
                    if util.match_suffix(file, config.AUDIO_SUFFIX):
                        mp3_files.append(file)
                    if util.match_suffix(file, config.IMAGE_SUFFIX):
                        image_files.append(file)
            media.cached = True
                
        else:
            # Disc is data of some sort. Mount it to get the file info
            util.mount(media.mountdir, force=True)

            # Check for movies/audio/images on the disc
            mplayer_files = util.match_files(media.mountdir, config.VIDEO_SUFFIX)
            mp3_files = util.match_files(media.mountdir, config.AUDIO_SUFFIX)
            image_files = util.match_files(media.mountdir, config.IMAGE_SUFFIX)

            util.umount(media.mountdir)


        _debug_('identifymedia: mplayer = "%s"' % mplayer_files, level = 2)
        _debug_('identifymedia: mp3="%s"' % mp3_files, level = 2)
        _debug_('identifymedia: image="%s"' % image_files, level = 2)
            
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
                    if config.VIDEO_SHOW_REGEXP_MATCH(movie):
                        show = config.VIDEO_SHOW_REGEXP_SPLIT(os.path.basename(movie))

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

                if show_name and the_same and config.VIDEO_SHOW_DATA_DIR:
                    if end_ep > 0:
                        volumes = '%dx%02d - %dx%02d' % (start_ep / 100, start_ep % 100,
                                                         end_ep / 100, end_ep % 100)
                    k = config.VIDEO_SHOW_DATA_DIR + show_name
                    if os.path.isfile((k + ".png").lower()):
                        image = (k + ".png").lower()
                    elif os.path.isfile((k + ".jpg").lower()):
                        image = (k + ".jpg").lower()
                    title = show_name + ' ('+ volumes + ')'
                    if video.tv_show_informations.has_key(show_name.lower()):
                        tvinfo = video.tv_show_informations[show_name.lower()]
                        more_info = tvinfo[1]
                        if not image:
                            image = tvinfo[0]
                        if not xml_file:
                            xml_file = tvinfo[3]
                        
                elif (not show_name) and len(mplayer_files) == 1:
                    movie = mplayer_files[0]
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
        if xml_file and not media.info.xml_file:
            media.info.set_xml_file(xml_file)
            
        if len(mplayer_files) == 1:
            util.mount(media.mountdir)
            media.videoinfo = VideoItem(mplayer_files[0], None)
            util.umount(media.mountdir)
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
                _debug_('MEDIA: Status=%s' % media.drive_status,2)
                _debug_('Posting IDENTIFY_MEDIA event',2)
                if last_status:
                    self.last_media = media
                rc.post_event(plugin.event('IDENTIFY_MEDIA'))
        self.lock.release()

                
    def __init__(self):
        threading.Thread.__init__(self)
        self.last_media = None          # last changed media
        self.lock = thread.allocate_lock()

        
    def run(self):

        rebuild_file = '/tmp/freevo-rebuild-database'
        # Make sure the movie database is rebuilt at startup
        util.touch(rebuild_file)
        while 1:
            # Check if we need to update the database
            # This is a simple way for external apps to signal changes
            if os.path.exists(rebuild_file):
                if video.hash_fxd_movie_database() == 0:
                    # something is wrong, deactivate this feature
                    rebuild_file = '/this/file/should/not/exist'
                    
                for media in config.REMOVABLE_MEDIA:
                    media.drive_status = None

            self.check_all()
            time.sleep(2)

