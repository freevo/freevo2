import os
import sys
import util.fileops as fileops
import notifier
import time

import config
import mediadb

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


def cache_directories(directories):
    """
    cache all directories
    """
    print 'checking database files...............................',
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


def get_directory_listings(dirlist, msg):
    """
    Get a list of Listings recursive of all given directories.
    """
    subdirs  = []
    listings = []
    for dir in dirlist:
        progress = '%3d%%' % (dirlist.index(dir) * 100 / len(dirlist))
        print '\r%s %s' % (msg, progress),
        sys.__stdout__.flush()
        for dirname in fileops.get_subdirs_recursively(dir):
            if not dirname in subdirs:
                subdirs.append(dirname)
                listings.append(mediadb.Listing(dirname))
        if not dir in subdirs:
            subdirs.append(dir)
            listings.append(mediadb.Listing(dir))
    return listings


# init the notifier
notifier.init( notifier.GENERIC )

start = time.clock()
msg = 'scanning directory structure..........................'
print msg,
sys.__stdout__.flush()

# config.AUDIO_ITEMS = [ ( 'foo', '/local/mp3/Artists/Dixie Chicks' ) ]
# config.VIDEO_ITEMS = [ ( 'foo', '/local/video/movie' ) ]
# config.IMAGE_ITEMS = [ ( 'foo', '/local/images/fotos/misc' ) ]

directories = []
for d in config.VIDEO_ITEMS + config.AUDIO_ITEMS + config.IMAGE_ITEMS:
    if os.path.isdir(d[1]) and d[1] != '/':
        directories.append(d[1])

listings = get_directory_listings(directories, msg)
print '\r%s done' % msg
cache_directories(listings)
l = mediadb.FileListing(directories)
if l.num_changes:
    l.update()
mediadb.cache(l)
mediadb.save()
print
print 'caching complete after %s seconds' % (time.clock() - start)
