import compat
import epg_xmltv
import stat
import os

def load(data = '/tmp/TV.xml'):
    return epg_xmltv.load_guide(data, verbose=True)
    
def timestamp(data = '/tmp/TV.xml'):
    return 0

