import config
import util

from audioitem import AudioItem


def cwd(parent, files):
    items = []
    for file in util.find_matches(files, config.SUFFIX_AUDIO_FILES):
        items += [ AudioItem(file, parent) ]
        files.remove(file)
    return items
