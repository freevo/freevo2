import os
import re

import config
import util

# XML support
from xml.utils import qp_xml

from videoinfo import VideoInfo

# Set to 1 for debug output
DEBUG = config.DEBUG
TRUE = 1
FALSE = 0


#
# parse <video> tag    
#
def xml_parseVideo(video_node, dir):
    playlist = []
    mode = 'video'
    mplayer_options = ""

    for node in video_node.children:
        if node.name == u'dvd':
            mode = 'dvd'
        if node.name == u'vcd':
            mode = 'vcd'
        if node.name == u'mplayer_options':
            mplayer_options += node.textof()

        if node.name == u'files':
            for file_nodes in node.children:
                if file_nodes.name == u'filename':
                    filename = file_nodes.textof()
                    if filename.find('://') == -1:
                        filename = os.path.join(dir, filename)
                    playlist += [filename]

        # XXX fix this to merge all -vop arguments into one
        # XXX one -vob .... argument
        if node.name == u'crop':
            try:
                crop = "-vop crop=%s:%s:%s:%s " % \
                       (node.attrs[('', "width")], node.attrs[('', "height")], \
                        node.attrs[('', "x")], node.attrs[('', "y")])
                mplayer_options += crop
            except KeyError:
                pass

    mi = VideoInfo(playlist)
    #mi.type = mode
    mi.mplayer_options = mplayer_options
    return mi



#
# parse <info> tag (not implemented yet)
#
def xml_parseInfo(info_node, i):
    for node in info_node.children:
        if node.name == u'url':
            i.url = node.textof().encode('latin-1')
        if node.name == u'genre':
            i.genre = node.textof().encode('latin-1')
        if node.name == u'runtime':
            i.runtime = node.textof().encode('latin-1')
        if node.name == u'tagline':
            i.tagline = node.textof().encode('latin-1')
        if node.name == u'plot':
            i.plot = node.textof().encode('latin-1')
        if node.name == u'year':
            i.year = node.textof().encode('latin-1')
        if node.name == u'rating':
            i.rating = node.textof().encode('latin-1')


#
# parse a XML movie file
#
def parseMovieFile(file):
    dir = os.path.dirname(file)
    movies = []
    
    try:
        parser = qp_xml.Parser()
        box = parser.parse(open(file).read())
    except:
        print "XML file %s corrupt" % file
        return []


    for c in box.children:
        if c.name == 'movie':
            mpinfo = None

            for node in c.children:
                if node.name == u'video':
                    minfo = xml_parseVideo(node, dir)

            if minfo:
                for node in c.children:
                    if node.name == u'title':
                        minfo.name = node.textof().encode('latin-1')
                    elif node.name == u'cover' and \
                         os.path.isfile(os.path.join(dir,node.textof())):
                        minfo.image = os.path.join(dir, node.textof())
                    elif node.name == u'id':
                        minfo.rom_id += [node.textof()]
                    elif node.name == u'label':
                        minfo.label += [node.textof()]
                    elif node.name == u'info':
                        xml_parseInfo(node, minfo)
                        
                minfo.xml_file = file
                movies += [ minfo ]

    return movies


# --------------------------------------------------------------------------------------

    
#
# hash all XML movie files
#
def hash_xml_database():
    config.MOVIE_INFORMATIONS_ID    = {}
    config.MOVIE_INFORMATIONS_LABEL = []

    return

    if os.path.exists("/tmp/freevo-rebuild-database"):
        os.system('rm -f /tmp/freevo-rebuild-database')

    if DEBUG: print "Building the xml hash database...",

    for name,dir in config.DIR_MOVIES:
        for file in util.recursefolders(dir,1,'*.xml',1):
            info = parse(file, os.path.dirname(file),[])
            if info.rom_id:
                for i in info.rom_id:
                    if len(i) > 16:
                        i = i[0:16]
                    config.MOVIE_INFORMATIONS_ID[i] = info
            if info.rom_label:
                for l in info.rom_label:
                    l_re = re.compile(l)
                    config.MOVIE_INFORMATIONS_LABEL += [(l_re, info)]
                
    for file in util.recursefolders(config.MOVIE_DATA_DIR,1,'*.xml',1):
        info = parse(file, os.path.dirname(file),[])
        if info.rom_id:
            for i in info.rom_id:
                if len(i) > 16:
                    i = i[0:16]
                config.MOVIE_INFORMATIONS_ID[i] = info
        if info.rom_label:
            for l in info.rom_label:
                l_re = re.compile(l)
                config.MOVIE_INFORMATIONS_LABEL += [(l_re, info)]

    if DEBUG: print 'done'
