import config
import util

import mame_cache
from mameitem import MameItem
from snesitem import SnesItem


def cwd(parent, files):
    items = []

    mame_files = util.find_matches(files, config.SUFFIX_MAME_FILES)

    # This will only add real mame roms to the cache.
    (rm_files, mame_list) = mame_cache.getMameItemInfoList(mame_files)

    for rm_file in rm_files:
        files.remove(rm_file)

    for ml in mame_list:   
        items += [ MameItem(ml[0], ml[1], ml[2], parent) ]

    for file in util.find_matches(files, config.SUFFIX_SNES_FILES):
        items += [ SnesItem(file, parent) ]
        files.remove(file)


    return items


def remove(files, items):
    # XXX not implemented yet
    return []
