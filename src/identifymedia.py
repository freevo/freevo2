#if 0 /*
# -----------------------------------------------------------------------
# identifymedia.py - the Freevo identifymedia/automount module
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2003/01/19 16:16:18  dischi
# small bugfix
#
# Revision 1.8  2003/01/19 15:56:31  dischi
# New option ROM_SPEED to set the drive speed. Default is 0 (don't set
# speed), a good value seems to be 8.
#
# Revision 1.7  2003/01/14 20:29:26  dischi
# small bugfix
#
# Revision 1.6  2003/01/12 17:57:52  dischi
# Renamed SUFFIX_MPLAYER_FILES to SUFFIX_VIDEO_FILES because we also play
# audio files with mplayer. Also renamed SUFFIX_FREEVO_FILES to
# SUFFIX_VIDEO_DEF_FILES because we use this for movie xml files.
#
# Revision 1.5  2003/01/09 18:56:18  dischi
# Make the autostart work again. If you close a cd tray while you are at the
# main menu, the disc will be autostart (show dir or play dvd)
#
# Revision 1.4  2002/12/30 15:56:11  dischi
# store label in the videoitem
#
# Revision 1.3  2002/12/07 13:28:19  dischi
# rescan disc after database change
#
# Revision 1.2  2002/12/03 18:46:08  dischi
# fix to avoid crashes when you have a bad cd (e.g. empty disc)
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

import sys, socket, random, time, os
from fcntl import ioctl
import struct,re
import threading
import config
import util
import rc
import string
import copy

from video import xml_parser, videoitem
from mediamenu import DirItem

DEBUG = config.DEBUG   # 1 = regular debug, 2 = more verbose

LABEL_REGEXP = re.compile("^(.*[^ ]) *$").match


# taken from cdrom.py so we don't need to import cdrom.py
CDROM_DRIVE_STATUS=0x5326
CDSL_CURRENT=( (int ) ( ~ 0 >> 1 ) )
CDS_DISC_OK=4
CDROM_DISC_STATUS=0x5327
CDS_AUDIO=100
CDROM_SELECT_SPEED=0x5322


class Identify_Thread(threading.Thread):

    # magic!
    # Try to find out as much as possible about the disc in the
    # rom drive: title, image, play options, ...
    def identify(self, media):

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
            media.info = None
            return

        # Same as last time? If so we're done
        if s == media.drive_status:
            os.close(fd)
            return

        media.drive_status = s

        # Is there a disc present?
        if s != CDS_DISC_OK:
            os.close(fd)
            media.info = None
            return

        # Check media type (data, audio)
        s = ioctl(fd, CDROM_DISC_STATUS)
        if s == CDS_AUDIO:
            os.close(fd)
            # XXX add cddb informations here
            media.info = None
            return

        # try to set the speed
        if config.ROM_SPEED:
            try:
                ioctl(fd, CDROM_SELECT_SPEED, config.ROM_SPEED)
            except:
                pass
            
        mediatypes = [('VCD', '/mpegav/', 'vcd'), ('SVCD','/SVCD/', 'vcd'), 
                      ('SVCD','/svcd/', 'vcd'), ('DVD', '/video_ts/', 'dvd') ]

        image = title = movie_info = None

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
        
        # is the id in the database?
        if id in config.MOVIE_INFORMATIONS_ID:
            movie_info = config.MOVIE_INFORMATIONS_ID[id]
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
        util.mount(media.mountdir)

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
            
        info = None

        # Is this a movie disc?
        if mplayer_files and not mp3_files:
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
                    if os.path.isfile((config.TV_SHOW_IMAGES + show_name + ".png").lower()):
                        image = (config.TV_SHOW_IMAGES + show_name + ".png").lower()
                    elif os.path.isfile((config.TV_SHOW_IMAGES + show_name + ".jpg").lower()):
                        image = (config.TV_SHOW_IMAGES + show_name + ".jpg").lower()
                    title = show_name + ' ('+ volumes + ')'

            # nothing found, give up: return the label
            if not title:
                title = label

        # XXX add more intelligence to cds with audio files
        if (not mplayer_files) and mp3_files:
            titel = "AUDIO" , '%s [%s]' % (media.drivename, label)

        # XXX add more intelligence to cds with image files
        elif (not mplayer_files) and (not mp3_files) and image_files:
            titel = "IMAGES" , '%s [%s]' % (media.drivename, label)

        # Mixed media?
        elif mplayer_files or image_files or mp3_files:
            titel = "DATA" , '%s [%s]' % (media.drivename, label)
        
        # Strange, no useable files
        else:
            titel = "DATA" , '%s [%s]' % (media.drivename, label)

        media.info = DirItem(media.mountdir, None)
        
        if movie_info:
            media.info.copy(movie_info)
        if title:
            media.info.name = title
        if image:
            media.info.image = image
            media.info.handle_type = 'video'
        media.info.media = media
        return


    def check_all(self):
        rclient = rc.get_singleton()
        
        for media in config.REMOVABLE_MEDIA:
            last_status = media.drive_status
            self.identify(media)

            if last_status != media.drive_status:
                if DEBUG:
                    print 'MEDIA: Status=%s' % media.drive_status
                    print 'Posting IDENTIFY_MEDIA event'
                if last_status:
                    self.last_media = media
                rclient.post_event(rclient.IDENTIFY_MEDIA)
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

