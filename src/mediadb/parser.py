# python imports
import os
import stat
import mmpython
import pickle
import cPickle
import re

# freevo imports
import config
import util.fxdparser
import util.vfs as vfs

# list of external parser
_parser = []

def init():
    """
    Init the parser module
    """
    for f in os.listdir(os.path.dirname(__file__)):
        if f.endswith('_parser.py'):
            exec('import %s' % f[:-3])
            _parser.append(eval(f[:-3]))


def simplify(object):
    """
    mmpython has huge objects to cache, we don't need them.
    This function simplifies them to be only string, integer, dict or
    list of one of those above. This makes the caching much faster
    """
    ret = {}
    for k in object.keys:
        if not k in [ 'thumbnail', 'url' ] and getattr(object,k) != None:
            value = getattr(object,k)
            if isstring(value):
                value = Unicode(value.replace('\0', '').lstrip().rstrip())
            if value:
                ret[k] = value

    for k in  ( 'video', 'audio'):
        # if it's an AVCORE object, also simplify video and audio
        # lists to string and it
        if hasattr(object, k) and getattr(object, k):
            ret[k] = []
            for o in getattr(object, k):
                ret[k].append(simplify(o))

    if hasattr(object, 'tracks') and object.tracks:
        # read track informations for dvd
        ret['tracks'] = []
        for o in object.tracks:
            track = simplify(o)
            if not track.has_key('audio'):
                track['audio'] = []
            if not track.has_key('subtitles'):
                track['subtitles'] = []
            ret['tracks'].append(track)

    for k in ('subtitles', 'chapters', 'mime', 'id' ):
        if hasattr(object, k) and getattr(object, k):
            ret[k] = getattr(object, k)

    return ret

# regexp for filenames used in getname
_FILENAME_REGEXP = re.compile("^(.*?)_(.)(.*)$")

def getname(file):
    """
    make a nicer display name from file
    """
    if len(file) < 2:
        return Unicode(file)

    # basename without ext
    if file.rfind('/') < file.rfind('.'):
        name = file[file.rfind('/')+1:file.rfind('.')]
    else:
        name = file[file.rfind('/')+1:]
    if not name:
        # Strange, it is a dot file, return the complete
        # filename, I don't know what to do here. This should
        # never happen
        return Unicode(file)

    name = name[0].upper() + name[1:]

    while file.find('_') > 0 and _FILENAME_REGEXP.match(name):
        m = _FILENAME_REGEXP.match(name)
        if m:
            name = m.group(1) + ' ' + m.group(2).upper() + m.group(3)
    if name.endswith('_'):
        name = name[:-1]
    return Unicode(name)


def cover_filter(x):
    """
    Filter function to get valid cover names
    """
    return re.search(config.AUDIO_COVER_REGEXP, x, re.IGNORECASE)



def parse(filename, object):
    """
    Add additional informations to filename, object.
    """
    mminfo = None
    if not object['ext'] in [ 'xml', 'fxd' ]:
        mminfo = mmpython.parse(filename)
    title = getname(filename)
    object['title:filename'] = title
    if mminfo:
        # store mmpython data as pickle for faster loading
        object['mminfo'] = cPickle.dumps(simplify(mminfo),
                                         pickle.HIGHEST_PROTOCOL)
        if mminfo.title:
            object['title'] = mminfo.title
        else:
            object['title'] = title
    elif object.has_key('mminfo'):
        del object['mminfo']
        object['title'] = title
    else:
        object['title'] = title

    if os.path.isdir(filename):
        object['isdir'] = True
        listing = vfs.listdir(filename, include_overlay=True)
        # get directory cover
        for l in listing:
            if l.endswith('/cover.png') or l.endswith('/cover.jpg') or \
                   l.endswith('/cover.gif'):
                object['cover'] = l
                break
        else:
            if object.has_key('cover'):
                del object['cover']
            if object.has_key('audiocover'):
                del object['audiocover']
            files = util.find_matches(listing, ('jpg', 'gif', 'png' ))
            if len(files) == 1:
                object['audiocover'] = files[0]
            elif len(files) > 1 and len(files) < 10:
                files = filter(cover_filter, files)
                if files:
                    object['audiocover'] = files[0]

        # save directory overlay mtime
        overlay = vfs.getoverlay(filename)
        if os.path.isdir(overlay):
            mtime = os.stat(overlay)[stat.ST_MTIME]
            object['overlay_mtime'] = mtime
        else:
            object['overlay_mtime'] = 0
    else:
        if object.has_key('isdir'):
            del object['isdir']

    # call external parser
    for p in _parser:
        p.parse(filename, object, mminfo)


def cache(listing):
    """
    Function for the 'cache' helper.
    """
    for p in _parser:
        p.cache(listing)
        
