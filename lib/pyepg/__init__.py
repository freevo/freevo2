import compat
import epg_xmltv

def list_channels(data = 'tmp/TV.xml'):
    return epg_xmltv.list_channels(data, verbose=True)
    
def load(data = 'tmp/TV.xml'):
    return epg_xmltv.load_guide(data, verbose=True)
    
