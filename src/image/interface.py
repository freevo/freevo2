import config
import util

from imageitem import ImageItem


def cwd(parent, files):
    items = []
    for file in util.find_matches(files, config.SUFFIX_IMAGE_FILES):
        items += [ ImageItem(file, parent) ]
        files.remove(file)
    return items
