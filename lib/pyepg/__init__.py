from guide import EPGDB

def get_epg(dbfile = '/tmp/epgdb'):
    return EPGDB(dbfile)

