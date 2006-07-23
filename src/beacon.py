import sys
import kaa.beacon

class ExtMap(dict):

    def get(self, attr):
        r = dict.get(self, attr)
        if r == None:
            self[attr] = []
            return self[attr]
        return r
    
def extmap_filter(results):
    extmap = ExtMap()
    if not isinstance(results, (list, tuple)):
        results = [ results ]
    for r in results:
        t = r.get('type')
        if t and t != 'file':
            extmap.get('beacon:%s' % t).append(r)
        elif r.isdir():
            extmap.get('beacon:dir').append(r)
        elif r.isfile():
            pos = r.get('name').rfind('.')
            if pos <= 0 and pos +1 == len(r.get('name')):
                extmap.get('beacon:file').append(r)
            else:
                extmap.get(r.get('name')[pos+1:]).append(r)
        else:
            extmap.get('beacon:item').append(r)
    return extmap

kaa.beacon.register_filter('extmap', extmap_filter)
try:
    kaa.beacon.connect()
except kaa.beacon.ConnectError:
    print 'unable to connect to beacon server'
    sys.exit(1)
