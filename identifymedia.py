import sys, socket, random, time, os
from fcntl import ioctl
import cdrom
import struct,re
import threading
import config
import util
import rc
import string


rclient = rc.get_singleton()

LABEL_REGEXP = re.compile("^(.*[^ ]) *$").match

class Identify_Thread(threading.Thread):

    def identify(self, cd_entry):
        dir, device, name, ejected, last_code, info = cd_entry

        try:
            fd = os.open(device, os.O_RDONLY | os.O_NONBLOCK)
        except:
            return last_code, None
            
        s = ioctl(fd, cdrom.CDROM_DRIVE_STATUS, cdrom.CDSL_CURRENT)

        if s == last_code:
            os.close(fd)
            return last_code, None

        last_code = s
        
        if s != cdrom.CDS_DISC_OK:
            os.close(fd)
            return last_code, None


        s = ioctl(fd, cdrom.CDROM_DISC_STATUS)
        if s == cdrom.CDS_AUDIO:
            os.close(fd)
            # add cddb informations here
            return last_code, ( 'AUDIO-CD', None, None, None )

        mediatypes = [('VCD','/mpegav/', 'vcd'), ('SVCD','/SVCD/', 'vcd'), \
                      ('DVD','/video_ts/', 'dvd') ]

        image = title = None

        os.close(fd)
        img = open(device)
        img.seek(0x0000832d)
        id = img.read(16)
        img.seek(32808, 0)
        label = img.read(32)
        m = LABEL_REGEXP(label)
        if m:
            label = m.group(1)
        img.close()

        if id in config.MOVIE_INFORMATIONS.keys():
            title, image, xml_filename = config.MOVIE_INFORMATIONS[id]
            

        os.system("mount %s" % dir)

        for media in mediatypes:
            if os.path.exists(dir + media[1]):
                os.system("umount %s" % dir)
                info = media[0], '%s [%s]' % (media[0], label), image, (media[2], 1, [])
                return last_code, info
                
        mplayer_files = util.match_files(dir, config.SUFFIX_MPLAYER_FILES)
        mp3_files = util.match_files(dir, config.SUFFIX_AUDIO_FILES)
        image_files = util.match_files(dir, config.SUFFIX_AUDIO_FILES)

        os.system("umount %s" % dir)

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
                title = string.capitalize\
                        (os.path.splitext(os.path.basename(mplayer_files[0]))[0])
                info = 'DIVX', title, image, ('video', mplayer_files[0], [])

            if info:
                return last_code, info

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
            return last_code, info

        if not mplayer_files and mp3_files:
            info = "AUDIO" , 'CD [%s]' % label, None, None

        elif not mplayer_files and not mp3_files and image_files:
            info = "IMAGE", 'CD [%s]' % label, None, None

        elif mplayer_files or image_files or mp3_files:
            if title:
                info = 'DATA', title, image, None
            else:
                info = "DATA", 'CD [%s]' % label, None, None

        else:
            info = "Data" , 'CD [%s]' % label, None, None
            
        return last_code, info


    def check_all(self):
        if config.ROM_DRIVES != None: 
            pos = 0
            for entry in config.ROM_DRIVES:
                new_entry = self.identify(entry)
                if new_entry[1]:
                    print ">>> %s" % new_entry[1][0]
                
                dir, device, name, ejected, last_code, info = entry
                new_code, info = new_entry

                if new_code != last_code:
                    config.ROM_DRIVES[pos] = (dir, device, name, ejected, new_code, info)
                    if last_code != -1:
                        rclient.post_event(rclient.IDENTIFY_MEDIA)
                pos += 1
                
                
    def __init__(self):
        threading.Thread.__init__(self)
        if config.ROM_DRIVES != None: 
            pos = 0
            for (dir, device, name, ejected) in config.ROM_DRIVES:
                config.ROM_DRIVES[pos] = (dir, device, name, ejected, -1, None)
                pos += 1
        self.check_all()
        
    def run(self):
        while 1:
            time.sleep(2)

            # check if we need to update the database
            if os.path.exists("/tmp/freevo-rebuild-database"):
                movie_xml.hash_xml_database()

            self.check_all()
