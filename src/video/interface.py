import config
import util
import xml_parser

from videoitem import VideoItem


def cwd(parent, files):
    items = []

    for file in util.find_matches(files, config.SUFFIX_FREEVO_FILES):
        x = xml_parser.parseMovieFile(file, parent, files)
        if x:
            files.remove(file)
            items += x

    for file in util.find_matches(files, config.SUFFIX_MPLAYER_FILES):
        items += [ VideoItem(file, parent) ]
        files.remove(file)

    return items


def remove(files, items):
    # XXX not implemented yet
    return []

