import config
import util

from imageitem import ImageItem


def cwd(parent, files):
    items = []
    for file in util.find_matches(files, config.SUFFIX_IMAGE_FILES):
        items += [ ImageItem(file, parent) ]
        files.remove(file)
    return items


def remove(files, items):
    del_items = []
    for item in items:
        for file in files:
            if item.type == 'image' and item.filename == file:
                del_items += [ item ]
                files.remove(file)
                
    return del_items
