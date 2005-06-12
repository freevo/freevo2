# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# rom_drives.py - the Freevo identifymedia/automount plugin
# -----------------------------------------------------------------------------
# $Id$
#
# Note: this file uses threads. This can't be done in a better way because
# some calls like ioctl block until they are done (even setting the fd to
# non blocking doesn't help). When moving the tray this tackes too much time.
# And while the tray is moving, other calls like a simple os.open for the
# scanner also blocks.
#
# Because of all this the scanner is in a thread and so is the tray moving.
# Both use a lock variable to make sure nothing bad happens. Faster stuff like
# 'identify' on a changed media uses other non thread safe parts of Freevo,
# they are called from the main loop.
#
# Since threads can mess up everything, the thread and lock parts should have
# a good documentation. Do not change anything here without knowing what
# effect it may have on the threads.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------


# python imports
import os
import re
import copy
import struct
import array
import logging
import thread

import notifier

# freevo imports
import sysconfig
import config
import eventhandler
import plugin
import util
from util.ioctl import ioctl
import util.fthread
import mediadb

from event import *
from directory import DirItem
from gui.windows import WaitBox
from item import Item

# FIXME: use Mimetype for this
from audio.audiodiskitem import AudioDiskItem
from video.videoitem import VideoItem


# the logging object
log = logging.getLogger()

# detect the rom drives
config.detect('rom_drives')

try:
    from CDROM import *
    # test if CDROM_DRIVE_STATUS is there
    # (for some strange reason, this is missing sometimes)
    CDROM_DRIVE_STATUS
except:
    if os.uname()[0] == 'FreeBSD':
        # FreeBSD ioctls - there is no CDROM.py...
        CDIOCEJECT = 0x20006318
        CDIOCCLOSE = 0x2000631c
        CDIOREADTOCENTRYS = 0xc0086305L
        CD_LBA_FORMAT = 1
        CD_MSF_FORMAT = 2
        CDS_NO_DISC = 1
        CDS_DISC_OK = 4
    else:
        # strange ioctls missing
        CDROMEJECT = 0x5309
        CDROMCLOSETRAY = 0x5319
        CDROM_DRIVE_STATUS = 0x5326
        CDROM_SELECT_SPEED = 0x5322
        CDS_NO_DISC = 1
        CDS_DISC_OK = 4


LABEL_REGEXP = re.compile("^(.*[^ ]) *$").match


# Watcher
watcher = None

# list of rom drives
rom_drives = []


class autostart(plugin.DaemonPlugin):
    """
    Plugin to autostart if a new medium is inserted while Freevo shows
    the main menu
    """
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.event_listener = True


    def eventhandler(self, event):
        """
        eventhandler to handle the IDENTIFY_MEDIA plugin event and the
        EJECT event. Also take care of the umounting when going back to
        the main menu.
        """
        if not eventhandler.is_menu():
            return False

        if event == MENU_GOTO_MAINMENU:
            # going to main menu, umount all media
            for media in rom_drives:
                if media.is_mounted():
                    media.umount()
            # return False, this event is needed later
            return False
        
        menuw = eventhandler.get()
        if not menuw or len(menuw.menustack) > 1:
            # not in main menu
            return False
        
        # if we are at the main menu and there is an IDENTIFY_MEDIA event,
        # try to autorun the media
        if plugin.isevent(event) == 'IDENTIFY_MEDIA' and not event.arg[1]:
            media = event.arg[0]
            if media.item:
                media.item.parent = menuw.menustack[0].selected
            if media.item and media.item.actions():
                if media.type == 'audio':
                    # disc marked as audio, play everything
                    if media.item.type == 'dir':
                        media.item.play(menuw, recursive=True)
                    elif media.item.type == 'audiocd':
                        media.item.play(menuw=menuw)
                    else:
                        media.item.actions()[0][0](menuw=menuw)
                elif media.videoitem:
                    # disc has one video file, play it
                    media.videoitem.actions()[0][0](menuw=menuw)
                else:
                    # ok, do whatever this item has to offer
                    media.item.actions()[0][0](menuw=menuw)
            else:
                menuw.refresh()
            return True

        # Handle the EJECT key for the main menu
        elif event == EJECT:
            # Are there any drives defined?
            if rom_drives:
                # The default is the first drive in the list
                media = rom_drives[0]
                media.move_tray(dir='toggle')
                return True


class rom_items(plugin.MainMenuPlugin, plugin.DaemonPlugin):
    """
    Plugin to add the rom drives to a main menu. This can be the global main
    menu or most likely the video/audio/image/games main menu
    """
    def __init__(self):
        plugin.MainMenuPlugin.__init__(self)
        plugin.DaemonPlugin.__init__(self)
        self.event_listener = True


    def items(self, parent):
        """
        return the list of rom drives
        """
        items = []
        for media in rom_drives:
            if media.is_mounted():
                # umount media when creating the items
                media.umount()
            if media.item:
                if parent.display_type == 'video' and media.videoitem:
                    m = media.videoitem
                    # FIXME: how to play video is maybe subdirs?

                else:
                    if media.item.type == 'dir':
                        media.item.display_type = parent.display_type
                        media.item.skin_display_type = parent.display_type
                    m = media.item

            else:
                m = Item(parent)
                m.name = _('Drive %s (no disc)') % media.drivename
                m.type = media.type
                m.media = media
                media.item = m

            m.parent = parent
            items.append(m)

        return items


    def eventhandler(self, event):
        """
        eventhandler to handle the umount
        """
        if event == MENU_GOTO_MAINMENU:
            # going to main menu, umount all media
            for media in rom_drives:
                if media.is_mounted():
                    media.umount()
            # return False, this event is needed later
            return False
        return False

    
class RemovableMedia(vfs.Mountpoint):
    """
    Object about one drive
    """
    def __init__(self, mountdir='', devicename='', drivename=''):
        # This is read-only stuff for the drive itself
        vfs.Mountpoint.__init__(self, mountdir, devicename, 'empty_cdrom')
        self.drivename = drivename
        rom_drives.append(self)

        # Dynamic stuff
        self.tray_open = 0
        self.drive_status = None  # return code from ioctl for DRIVE_STATUS

        self.label       = ''
        self.info        = None
        self.item        = None
        self.videoitem   = None
        self.lock        = thread.allocate_lock()


    def move_tray(self, dir='toggle', notify=1):
        """
        Move the tray. dir can be toggle/open/close
        """
        if not self.lock.acquire(0):
            # unable to acquire the lock, looks like a move tray or
            # a media change identification is in progress
            log.info('media locked')
            return

        # At this point we have a lock and no scan or move again will
        # do some nasty things with the media

        if dir == 'toggle':
            if self.tray_open:
                dir = 'close'
            else:
                dir = 'open'
        pop = None
        if dir == 'open':
            log.debug('Ejecting disc in drive %s' % self.drivename)
            msg = _('Ejecting disc in drive %s')
        elif dir == 'close':
            log.debug('Inserting %s' % self.drivename)
            msg = _('Reading disc in drive %s')
        if notify:
            pop = WaitBox(text= msg % self.drivename)
            pop.show()

        # Start tray moving thread. This thread will release the lock
        # when the tray is moved
        util.fthread.Thread(self.__move_tray_thread, dir, pop).start()


    def __move_tray_thread(self, dir, popup):
        """
        The real tray moving (called in a thread).
        """
        # open fd to the drive
        fd = os.open(self.devicename, os.O_RDONLY | os.O_NONBLOCK)
        if dir == 'open':
            # open the tray
            if os.uname()[0] == 'FreeBSD':
                cmd = CDIOCEJECT
            else:
                cmd = CDROMEJECT
            self.tray_open = 1

        elif dir == 'close':
            # close the tray, identifymedia does the rest,
            # including refresh screen
            if os.uname()[0] == 'FreeBSD':
                cmd = CDIOCCLOSE
            else:
                cmd = CDROMCLOSETRAY
            self.tray_open = 0

        try:
            # try to move the tray
            s = ioctl(fd, cmd, 0)
        except Exception, e:
            log.exception('move tray error')
        try:
            # close the fd to the drive
            os.close(fd)
        except:
            log.exception('close fd')

        # release the lock
        self.lock.release()
        if watcher and not self.tray_open:
            # call watcher for update from main
            util.fthread.call_from_main(watcher.poll)
        if popup:
            # delete popup (from main)
            util.fthread.call_from_main(popup.destroy)


    def check_status_thread(self):
        """
        Return True if the status has changed (new disc / removed disc).
        Note: This functions blocks, so it needs to be called in a thread.
        """
        if self.lock.locked():
            # locked for some reasons, return
            return False

        # Check drive status (tray pos, disc ready)
        try:
            fd = os.open(self.devicename, os.O_RDONLY | os.O_NONBLOCK)
            if os.uname()[0] == 'FreeBSD':
                try:
                    data = array.array('c', '\000'*4096)
                    (address, length) = data.buffer_info()
                    buf = struct.pack('BBHP', CD_MSF_FORMAT, 0,
                                      length, address)
                    s = ioctl(fd, CDIOREADTOCENTRYS, buf)
                    s = CDS_DISC_OK
                except:
                    s = CDS_NO_DISC
            else:
                CDSL_CURRENT = ( (int ) ( ~ 0 >> 1 ) )
                s = ioctl(fd, CDROM_DRIVE_STATUS, CDSL_CURRENT)
        except:
            # maybe we need to close the fd if ioctl fails, maybe
            # open fails and there is no fd
            try:
                os.close(fd)
            except:
                pass
            self.drive_status = None
            return False

        # Same as last time? If so we're done
        if s == self.drive_status:
            os.close(fd)
            return False

        # Lock the media now. It is not possible to call this function
        # again from the watcher or move the tray until the checking is done.
        if not self.lock.acquire(0):
            # Oops, the lock isn't free. This shouldn't happen in normal
            # cases but it may be that the user wanted to move the tray
            # between the beginning of this function and now. So we can't
            # scan the media, return without doing anything.
            return False

        # Now the media is locked and we can do some stuff without anyone
        # doing something else with it.

        self.drive_status = s

        self.set_id('')
        self.label     = ''
        self.type      = 'empty_cdrom'
        self.item      = None
        self.videoitem = None

        # Is there a disc present?
        if s != CDS_DISC_OK:
            os.close(fd)
            # send media changed event and unlock the media
            util.fthread.call_from_main(self.send_event)
            return False

        # if there is a disc, the tray can't be open
        self.tray_open = False

        # scan the disc
        self.info = mediadb.get(self)
        if config.ROM_SPEED and not self.info['mime'] == 'video/dvd':
            # try to set the speed
            try:
                ioctl(fd, CDROM_SELECT_SPEED, config.ROM_SPEED)
            except:
                pass
        os.close(fd)
        # call identity from main loop
        util.fthread.call_from_main(self.identify)
        # Note: the lock is still in place. It will be released by
        # identify later from the main loop when everything is done.
        return True


    def send_event(self):
        """
        Send a changed notification and release the lock.
        """
        log.info('MEDIA: Status=%s' % self.drive_status)
        log.info('Posting IDENTIFY_MEDIA event')
        arg = (self, not hasattr(self, 'already_scanned'))
        self.already_scanned = True
        eventhandler.post(plugin.event('IDENTIFY_MEDIA', arg=arg))
        # release the lock
        self.lock.release()


    def identify(self):
        """
        magic!
        Try to find out as much as possible about the disc in the
        rom drive: title, image, play options, ...
        This function is called by the main loop but the call itself was
        requested by a thread. The lock of the media is still active, so
        it must be released. Since this function is only called on changes
        we have to call send_event which will unlock the lock.
        """
        if not self.info.disc_ok:
            # bad disc, e.g. blank disc.
            # send disc change event
            self.send_event()
            return

        if self.info['mime'] == 'audio/cd':
            disc_id = self.info['id']
            self.item = AudioDiskItem(disc_id, parent=None,
                                       devicename=self.devicename,
                                       display_type='audio')
            self.type = self.item.type
            self.item.media = self
            if self.info['title']:
                self.item.name = self.info['title']
            self.item.info = self.info
            # send disc change event
            self.send_event()
            return

        image = title = movie_info = more_info = fxd_file = None

        self.set_id(self.info['id'])
        self.label = self.info['label']
        self.type  = 'cdrom'

        label = self.info['label']

        # is the id in the database?
        for mimetype in plugin.mimetype():
            if not mimetype.database():
                continue
            movie_info = mimetype.database().get_media(self)
            if movie_info:
                title = movie_info.name
                image = movie_info.image
                break

        # DVD/VCD/SVCD:
        # There is self.info from mmpython for these three types
        if self.info['mime'] in ('video/vcd', 'video/dvd'):
            if not title:
                title = self.label.replace('_', ' ').lstrip().rstrip()
                title = '%s [%s]' % (self.info['mime'][6:].upper(), title)

            if movie_info:
                self.item = copy.copy(movie_info)
            else:
                self.item = VideoItem('', None)
                f = os.path.join(config.OVERLAY_DIR, 'disc-set', self.id)
                self.item.image = util.getimage(f)
            variables = self.item.info.get_variables()
            self.item.name  = title
            self.item.media = self
            self.item.set_url(self.info)
            self.item.info.set_variables(variables)
            self.type = self.info['mime'][6:]
            # send disc change event
            self.send_event()
            return

        # Check for movies/audio/images on the disc
        video_files = util.find_matches(self.info['listing'],
                                        config.VIDEO_SUFFIX)
        num_video = len(video_files)

        num_audio = len(util.find_matches(self.info['listing'],
                                          config.AUDIO_SUFFIX))
        num_image = len(util.find_matches(self.info['listing'],
                                          config.IMAGE_SUFFIX))

        self.item = DirItem(self.info, None)
        self.item.info = self.info

        # if there is a video file on the root dir of the disc, we guess
        # it's a video disc. There may also be audio files and images, but
        # they only belong to the movie
        if video_files:
            self.type = 'video'

            # try to find out if it is a series cd
            if not title:
                show_name = ""
                the_same  = 1
                volumes   = ''
                start_ep  = 0
                end_ep    = 0

                video_files.sort(lambda l, o: cmp(l.upper(), o.upper()))

                for movie in video_files:
                    if config.VIDEO_SHOW_REGEXP_MATCH(movie):
                        bn = os.path.basename(movie)
                        show = config.VIDEO_SHOW_REGEXP_SPLIT(bn)

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
                        volumes = '%dx%02d - %dx%02d' % (start_ep / 100,
                                                         start_ep % 100,
                                                         end_ep / 100,
                                                         end_ep % 100)
                    k = config.VIDEO_SHOW_DATA_DIR + show_name
                    if os.path.isfile((k + ".png").lower()):
                        image = (k + ".png").lower()
                    elif os.path.isfile((k + ".jpg").lower()):
                        image = (k + ".jpg").lower()
                    title = show_name + ' ('+ volumes + ')'
                    for mimetype in plugin.mimetype():
                        if not mimetype.database() or \
                               not hasattr(mimetype.database(), 'tv_show'):
                            continue
                        tv_show = mimetype.database().tv_show
                        if tv_show.has_key(show_name.lower()):
                            tvinfo = tv_show[show_name.lower()]
                            more_info = tvinfo[1]
                            if not image:
                                image = tvinfo[0]
                            if not fxd_file:
                                fxd_file = tvinfo[3]

                elif (not show_name) and len(video_files) == 1:
                    movie = video_files[0]
                    title = os.path.splitext(os.path.basename(movie))[0]

            # nothing found, give up: return the label
            if not title:
                title = label


        # If there are no videos and only audio files (and maybe images)
        # it is an audio disc (autostart will auto play everything)
        elif not num_video and num_audio:
            self.type = 'audio'
            title = '%s [%s]' % (self.drivename, label)

        # Only images? OK than, make it an image disc
        elif not num_video and not num_audio and num_image:
            self.type = 'image'
            title = '%s [%s]' % (self.drivename, label)

        # Mixed media?
        elif num_video or num_audio or num_image:
            self.type = None
            title = '%s [%s]' % (self.drivename, label)

        # Strange, no useable files
        else:
            self.type = None
            title = '%s [%s]' % (self.drivename, label)


        # set the infos we have now
        if title:
            self.item.name = title

        if image:
            self.item.image = image

        if more_info:
            self.item.info.set_variables(more_info)

        if fxd_file and not self.item.fxd_file:
            self.item.set_fxd_file(fxd_file)


        # One video in the root dir. This sounds like a disc with one
        # movie on it. Save the information about it and autostart will
        # play this.
        if len(video_files) == 1 and self.item['num_dir_items'] == 0:
            self.mount()
            if movie_info:
                self.videoitem = copy.deepcopy(movie_info)
            else:
                self.videoitem = VideoItem(video_files[0], None)
            self.umount()
            self.videoitem.media    = self
            self.videoitem.media_id = self.id

            # set the infos we have
            if title:
                self.videoitem.name = title

            if image:
                self.videoitem.image = image

            if more_info:
                self.videoitem.set_variables(more_info)

            if fxd_file:
                self.videoitem.fxd_file = fxd_file

        self.item.media = self
        # send disc change event
        self.send_event()
        return True


class Watcher:
    """
    Object to watch the rom drives for changes
    """
    def __init__(self):
        self.rebuild_file = sysconfig.cachefile('freevo-rebuild-database')

        # Add the drives to the config.removable_media list. There doesn't have
        # to be any drives defined.
        if config.ROM_DRIVES != None:
            for i in range(len(config.ROM_DRIVES)):
                (dir, device, name) = config.ROM_DRIVES[i]
                media = RemovableMedia(mountdir=dir, devicename=device,
                                       drivename=name)
                # close the tray without popup message
                media.move_tray(dir='close', notify=0)

        # Remove the ROM_DRIVES member to make sure it is not used by
        # legacy code!
        del config.ROM_DRIVES

        # register callback
        notifier.addTimer(2000, self.poll)


    def poll(self):
        """
        Poll function
        """
        # Check if we need to update the database
        # This is a simple way for external apps to signal changes
        if os.path.exists(self.rebuild_file):
            for mimetype in plugin.mimetype():
                if mimetype.database():
                    if not mimetype.database().update():
                        # something is wrong, deactivate this feature
                        self.rebuild_file = '/this/file/should/not/exist'

            for media in rom_drives:
                media.drive_status = None

        if eventhandler.is_menu():
            # check only in the menu
            for media in rom_drives:
                if media.lock.locked():
                    # scan waiting in thread
                    continue
                # Start a thread for the scanning. This is not a perfect
                # solution because it will create a thread for each drive
                # every 2 seconds, but it works well.
                util.fthread.Thread(media.check_status_thread).start()
        return True


# start the watcher
watcher = Watcher()
