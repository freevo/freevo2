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

DEBUG = 2   # 1 = regular debug, 2 = more verbose

LABEL_REGEXP = re.compile("^(.*[^ ]) *$").match


class Identify_Thread(threading.Thread):

    def identify(self, media):

        # Check drive status (tray pos, disc ready)
        try:
            fd = os.open(media.devicename, os.O_RDONLY | os.O_NONBLOCK)
            s = ioctl(fd, cdrom.CDROM_DRIVE_STATUS, cdrom.CDSL_CURRENT)
        except:
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
            media.info = ('AUDIO-CD', None, None, None)
            return

        mediatypes = [('VCD', '/mpegav/', 'vcd'), ('SVCD','/SVCD/', 'vcd'), 
                      ('SVCD','/svcd/', 'vcd'), ('DVD', '/video_ts/', 'dvd') ]

        image = title = None

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

        if id in config.MOVIE_INFORMATIONS:
            title, image, xml_filename = config.MOVIE_INFORMATIONS[id]
            
        # Disc is data of some sort. Mount it to get the file info
        util.mount(media.mountdir)

        for mediatype in mediatypes:
            if os.path.exists(media.mountdir + mediatype[1]):
                util.umount(media.mountdir)
                # XXX Add Dischis -cdrom-device fix!
                media.info = (mediatype[0],
                              'Drive %s [%s %s]' % (media.drivename,
                                                    mediatype[0], label),
                              image, (mediatype[2], media.mountdir, []))
                return
                
        mplayer_files = util.match_files(media.mountdir, config.SUFFIX_MPLAYER_FILES)
        mp3_files = util.match_files(media.mountdir, config.SUFFIX_AUDIO_FILES)
        image_files = util.match_files(media.mountdir, config.SUFFIX_IMAGE_FILES)

        util.umount(media.mountdir)

        if DEBUG:
            print 'identifymedia: mplayer = "%s"' % mplayer_files
            print 'identifymedia: mp3="%s"' % mp3_files
            print 'identifymedia: image="%s"' % image_files
            
        info = None

        if mplayer_files and not mp3_files:

            # return the title and action is play
            if title and len(mplayer_files) == 1:
                # XXX add mplayer_options, too
                info = 'DIVX', title, image, ('video', mplayer_files[0], [])

            # return the title
            elif title:
                info = 'DIVX', title, image, None

            # only one movie on DVD/CD, title is movie name and action is play
            elif len(mplayer_files) == 1:
                s = os.path.splitext(os.path.basename(mplayer_files[0]))[0]
                title = s.capitalize()
                info = 'DIVX', title, image, ('video', mplayer_files[0], [])

            # We're done if it was 
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
                info = "DIVX", show_name + ' ('+ volumes + ')', image, None

            else:
                # nothing found, return the label
                info = "DIVX", 'CD [%s]' % label, None, None
            media.info = info
            return

        if (not mplayer_files) and mp3_files:
            info = "AUDIO" , 'CD [%s]' % label, None, None

        elif (not mplayer_files) and (not mp3_files) and image_files:
            info = "IMAGE", 'CD [%s]' % label, None, None

        elif mplayer_files or image_files or mp3_files:
            if title:
                info = 'DATA', title, image, None
            else:
                info = "DATA", 'CD [%s]' % label, None, None

        else:
            info = "DATA" , 'CD [%s]' % label, None, None

        media.info = info

        return


    def check_all(self):
        rclient = rc.get_singleton()
        
        for media in config.REMOVABLE_MEDIA:
            last_status = media.drive_status
            self.identify(media)

            if last_status != media.drive_status:
                if DEBUG:
                    print 'MEDIA: Status=%s, info=%s' % (media.drive_status,
                                                         media.info),
                    print ' Posting IDENTIFY_MEDIA event'
                rclient.post_event(rclient.IDENTIFY_MEDIA)
            else:
                if DEBUG > 1:
                    print 'MEDIA: Status=%s, info=%s' % (media.drive_status,
                                                         media.info)
                
                
    def __init__(self):
        threading.Thread.__init__(self)

        
    def run(self):
        # Make sure the movie database is rebuilt at startup
        os.system('touch /tmp/freevo-rebuild-database')
        while 1:
            time.sleep(2)

            # Check if we need to update the database
            # This is a simple way for external apps to signal changes
            if os.path.exists("/tmp/freevo-rebuild-database"):
                movie_xml.hash_xml_database()

            self.check_all()
