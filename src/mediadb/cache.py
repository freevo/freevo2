import os
import sys
import util.fileops as fileops
import notifier

from listing import Listing

class ProgressBox:
    def __init__(self, msg, max):
        self.msg = msg
        self.max = max
        self.pos = 0
        print '\r%-70s   0%%' % msg,
        sys.__stdout__.flush()
        
    def callback(self):
        self.pos += 1
        progress = '%3d%%' % (self.pos * 100 / self.max)
        print '\r%-70s %s' % (self.msg, progress),
        sys.__stdout__.flush()


def cache_directories(directories, rebuild=False):
    """
    cache all directories with mmpython
    """
    if rebuild:
        print 'deleting cache files..................................',
        sys.__stdout__.flush()
        mediainfo.del_cache()
        print 'done'

    print 'checking mmpython cache files.........................',
    sys.__stdout__.flush()
    listings = []
    for d in directories:
        if d.num_changes:
            listings.append(d)
    print '%s changes' % len(listings)
    
    # cache all dirs
    for l in listings:
        name = l.dirname
        if len(name) > 55:
            name = name[:15] + ' [...] ' + name[-35:]
        msg = ProgressBox('  %4d/%-4d %s' % (listings.index(l) + 1,
                                             len(listings), name),
                          l.num_changes)
        l.update(msg.callback)
        l.cache.save()
        print



# MAIN

import config
import parser
import db

def get_direcories(dirlist, msg):
    """
    cache a list of directories recursive
    """
    if not dirlist:
        return
    all_dirs    = []
    all_listing = []
    # create a list of all subdirs
    for dir in dirlist:
        progress = '%3d%%' % (dirlist.index(dir) * 100 / len(dirlist))
        print '\r%s %s' % (msg, progress),
        sys.__stdout__.flush()
        for dirname in fileops.get_subdirs_recursively(dir):
            if not dirname in all_dirs:
                all_dirs.append(dirname)
                all_listing.append(Listing(dirname))
        if not dir in all_dirs:
            all_dirs.append(dir)
            all_listing.append(Listing(dir))
    return all_dirs, all_listing

notifier.init( notifier.GENERIC )
all_dirs = []
msg = 'scanning directory structure..........................'
print msg,
sys.__stdout__.flush()

config.AUDIO_ITEMS = [ ( 'foo', '/local/mp3/Artists/Dixie Chicks' ) ]
config.VIDEO_ITEMS = [ ( 'foo', '/local/video/movie' ) ]
config.IMAGE_ITEMS = [ ( 'foo', '/local/images/fotos/misc' ) ]

for d in config.VIDEO_ITEMS + config.AUDIO_ITEMS + config.IMAGE_ITEMS:
    if os.path.isdir(d[1]) and d[1] != '/':
        all_dirs.append(d[1])

all_dirs, all_listing = get_direcories(all_dirs, msg)
print '\r%s done' % msg
cache_directories(all_listing)
parser.cache()
db.save()
