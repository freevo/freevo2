import sys
import os
import stat
import md5

import config
import util

from listing import Listing, FileListing

# 
# Interface
#

def cache():
    """
    Function for the 'cache' helper.
    """
    print 'creating audio metadata...............................',
    sys.__stdout__.flush()
    for dir in config.AUDIO_ITEMS:
        if os.path.isdir(dir[1]):
            AudioParser(dir[1], rescan=True)
    print 'done'


def parse(filename, object, mminfo):
    """
    Add aditional audio based data.
    """
    pass


# 
# Internal helper functions and classes
#

_VARIOUS = u'__various__'

class AudioParser:

    def __init__(self, dirname, force=False, rescan=False):
        self.artist  = ''
        self.album   = ''
        self.year    = ''
        self.length  = 0
        self.changed = False
        self.force   = force

        cachefile    = vfs.getoverlay(os.path.join(dirname, '..', 'freevo.cache'))
        subdirs      = util.getdirnames(dirname, softlinks=False)
        filelist     = None

        parent = FileListing( [ dirname ] )
        if parent.num_changes:
            parent.update()
        dirinfo = parent.get_by_name(os.path.basename(dirname))
            
        if not rescan:
            for subdir in subdirs:
                d = AudioParser(subdir, rescan)
                if d.changed:
                    break

            else:
                # no changes in all subdirs, looks good
                if os.path.isfile(cachefile) and \
                       os.stat(dirname)[stat.ST_MTIME] <= os.stat(cachefile)[stat.ST_MTIME]:
                    # and no changes in here. Do not parse everything again
                    if force:
                        # forces? We need to load our current values
                        for type in ('artist', 'album', 'year', 'length'):
                            if info.has_key(type):
                                setattr(self, type, info[type])
                    return

        if not filelist:
            filelist = util.match_files(dirname, config.AUDIO_SUFFIX)
            
        if not filelist and not subdirs:
            # no files in here? We are done
            return
        
        # ok, something changed here, too bad :-(
        self.changed = True
        self.force   = False

        # scan all subdirs
        for subdir in subdirs:
            d = AudioParser(subdir, force=True, rescan=rescan)
            for type in ('artist', 'album', 'year'):
                setattr(self, type, self.strcmp(getattr(self, type), getattr(d, type)))
            self.length += d.length

        # cache dir first
        listing = Listing(dirname)
        if listing.num_changes:
            listing.update()
            
        use_tracks = True

        for data in listing.match_suffix(config.AUDIO_SUFFIX):
            try:
                for type in ('artist', 'album'):
                    setattr(self, type, self.strcmp(getattr(self, type), data[type]))
                self.year = self.strcmp(self.year, data['date'])
                if data['length']:
                    self.length += int(data['length'])
                use_tracks = use_tracks and data['trackno']
            except OSError:
                pass

        if use_tracks and (self.album or self.artist):
            dirinfo.store_with_mtime('audio_advanced_sort', True)

        if not self.length:
            return

        for type in ('artist', 'album', 'year', 'length'):
            if getattr(self, type):
                dirinfo.store_with_mtime(type, getattr(self, type))

        modtime = os.stat(dirname)[stat.ST_MTIME]
        if not dirinfo['coverscan'] or dirinfo['coverscan'] != modtime:
            dirinfo.store('coverscan', modtime)
            self.extract_image(dirname)

            
    def strcmp(self, s1, s2):
        s1 = Unicode(s1)
        s2 = Unicode(s2)
        
        if not s1 or not s2:
            return s1 or s2
        if s1 == _VARIOUS or s2 == _VARIOUS:
            return _VARIOUS

        if s1.replace(u' ', u'').lower() == s2.replace(u' ', u'').lower():
            return s1
        return _VARIOUS


    def get_md5(self, obj):
        m = md5.new()
        if isinstance(obj,file):     # file
            for line in obj.readlines():
                m.update(line)
            return m.digest()
        else:                        # str
            m.update(obj)
            return m.digest()


    def extract_image(self, path):
        for i in util.match_files(path, ['mp3']):
            try:
                id3 = eyeD3.Mp3AudioFile( i )
            except:
                continue
            myname = vfs.getoverlay(os.path.join(path, 'cover.jpg'))
            if id3.tag:
                images = id3.tag.getImages();
                for img in images:
                    if vfs.isfile(myname) and (self.get_md5(vfs.open(myname,'rb')) == \
                                               self.get_md5(img.imageData)):
                        # Image already there and has identical md5, skip
                        pass 
                    elif not vfs.isfile(myname):
                        f = vfs.open(myname, "wb")
                        f.write(img.imageData)
                        f.flush()
                        f.close()
                    else:
                        # image exists, but sums are different, write a unique cover
                        iname = os.path.splitext(os.path.basename(i))[0]+'.jpg'
                        myname = vfs.getoverlay(os.path.join(path, iname))
                        f = vfs.open(myname, "wb")
                        f.write(img.imageData)
                        f.flush()
                        f.close()

