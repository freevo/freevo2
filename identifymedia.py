# ----------------------------------------------------------------------
# identifymedia.py - the Freevo identifymedia/automount module
# ----------------------------------------------------------------------
# $Id$
#
# Authors:     Krister Lagerstrom <krister@kmlager.com>
#              Dirk Meyer <dischi@tzi.de>
# Notes:
# Todo:        
#
# ----------------------------------------------------------------------
# $Log$
# Revision 1.14  2002/09/30 05:56:28  krister
# Fixed a bug in the file-close.
#
# Revision 1.13  2002/09/30 05:52:59  krister
# Added a close on error for the filedescriptor, hopefully prevents open files lying around.
#
# Revision 1.12  2002/09/18 18:42:19  dischi
# Some small changes here and there, nothing important
#
#
# ----------------------------------------------------------------------
# 
# Copyright (C) 2002 Krister Lagerstrom
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
# ----------------------------------------------------------------------
#


import sys, socket, random, time, os
from fcntl import ioctl
import cdrom
import struct,re
import threading
import config
import util
import rc
import string
import movie_xml

from main import RemovableMediaInfo

DEBUG = 1   # 1 = regular debug, 2 = more verbose

LABEL_REGEXP = re.compile("^(.*[^ ]) *$").match


class Identify_Thread(threading.Thread):

    # magic!
    # Try to find out as much as possible about the disc in the
    # rom drive: title, image, play options, ...
    def identify(self, media):

        # Check drive status (tray pos, disc ready)
        try:
            fd = os.open(media.devicename, os.O_RDONLY | os.O_NONBLOCK)
            s = ioctl(fd, cdrom.CDROM_DRIVE_STATUS, cdrom.CDSL_CURRENT)
        except:
            os.close(fd)
            media.drive_status = None
            media.info = None
            return

        # Same as last time? If so we're done
        if s == media.drive_status:
            os.close(fd)
            return

        media.drive_status = s

        # Is there a disc present?
        if s != cdrom.CDS_DISC_OK:
            os.close(fd)
            media.info = None
            return

        # Check media type (data, audio)
        s = ioctl(fd, cdrom.CDROM_DISC_STATUS)
        if s == cdrom.CDS_AUDIO:
            os.close(fd)
            # XXX add cddb informations here
            media.info = RemovableMediaInfo('AUDIO-CD')
            return

        mediatypes = [('VCD', '/mpegav/', 'vcd'), ('SVCD','/SVCD/', 'vcd'), 
                      ('SVCD','/svcd/', 'vcd'), ('DVD', '/video_ts/', 'dvd') ]

        image = title = xml_filename = None

        # Read the volume label directly from the ISO9660 file system
        os.close(fd)
        img = open(media.devicename)
        img.seek(0x0000832d)
        id = img.read(16)
        img.seek(32808, 0)
        label = img.read(32)
        m = LABEL_REGEXP(label)
        if m:
            label = m.group(1)
        img.close()

        # is the id in the database?
        if id in config.MOVIE_INFORMATIONS_ID:
            title, image, xml_filename = config.MOVIE_INFORMATIONS_ID[id]

        # no? Maybe we can find a label regexp match
        else:
            for db_info in config.MOVIE_INFORMATIONS_LABEL:
                if db_info[0].match(label):
                    title, image, xml_filename = db_info[1:]
                    m = db_info[0].match(label).groups()
                    re_count = 1

                    # found, now change the title with the regexp. E.g.:
                    # label is "bla_2", the label regexp "bla_[0-9]" and the title
                    # is "Something \1", the \1 will be replaced with the first item
                    # in the regexp group, here 2. The title is now "Something 2"
                    for g in m:
                        title=string.replace(title, '\\%s' % re_count, g)
                        re_count += 1
                        
        # Disc is data of some sort. Mount it to get the file info
        util.mount(media.mountdir)

        # Check for DVD/VCD/SVCD
        for mediatype in mediatypes:
            if os.path.exists(media.mountdir + mediatype[1]):
                util.umount(media.mountdir)

                if not title:
                    title = '%s [%s]' % (mediatype[0], label)

                media.info = RemovableMediaInfo(mediatype[0], title, image,\
                                                (mediatype[2], media.mountdir, []),\
                                                xml_file = xml_filename)
                return

        # Check for movies/audio/images on the disc
        mplayer_files = util.match_files(media.mountdir, config.SUFFIX_MPLAYER_FILES)
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

            # return the title and action is play
            if title and len(mplayer_files) == 1:
                # XXX add mplayer_options, too
                info = RemovableMediaInfo('DIVX', title, image, \
                                          ('video', mplayer_files[0], []))

            # return the title
            elif title:
                info = RemovableMediaInfo('DIVX', title, image, xml_file = xml_filename)

            # only one movie on DVD/CD, title is movie name and action is play
            elif len(mplayer_files) == 1:
                s = os.path.splitext(os.path.basename(mplayer_files[0]))[0]
                title = s.capitalize()
                info = RemovableMediaInfo('DIVX', title, image, \
                                          ('video', mplayer_files[0], []))

            # We're done if we have 'info' 
            if info:
                media.info = info
                return

            # try to find out if it is a series cd
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
                info = RemovableMediaInfo("DIVX", show_name + ' ('+ volumes + ')', image,
                                          xml_file = xml_filename)

            else:
                # nothing found, give up: return the label
                info = RemovableMediaInfo("DIVX", label)

            media.info = info
            return



        # XXX add more intelligence to cds with audio files
        if (not mplayer_files) and mp3_files:
            info = RemovableMediaInfo("AUDIO" , '%s [%s]' % (media.drivename, label))



        # XXX add more intelligence to cds with image files
        elif (not mplayer_files) and (not mp3_files) and image_files:
            info = RemovableMediaInfo("IMAGE", '%s [%s]' % (media.drivename, label))


        # Mixed media?
        elif mplayer_files or image_files or mp3_files:
            # Do we have title informations?
            if title:
                info = RemovableMediaInfo('DATA', title, image, xml_file = xml_filename)
            else:
                info = RemovableMediaInfo("DATA", '%s [%s]' % (media.drivename, label))

        # Strange, no useable files
        else:
            info = RemovableMediaInfo("DATA" , '%s [%s]' % (media.drivename, label))

        media.info = info

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
                rclient.post_event(rclient.IDENTIFY_MEDIA)
            else:
                if DEBUG > 1:
                    print 'MEDIA: Status=%s' % media.drive_status
                
                
    def __init__(self):
        threading.Thread.__init__(self)

        
    def run(self):
        # Make sure the movie database is rebuilt at startup
        os.system('touch /tmp/freevo-rebuild-database')
        while 1:
            # Check if we need to update the database
            # This is a simple way for external apps to signal changes
            if os.path.exists("/tmp/freevo-rebuild-database"):
                movie_xml.hash_xml_database()

            self.check_all()
            time.sleep(2)

