import compat
import guide
import stat
import os

def load(datafile, cachefile=None, parser='xmltv'):
    return guide.TvGuide(datafile, cachefile, parser, verbose=True)
    
def timestamp(data = '/tmp/TV.xml'):
    return 0

