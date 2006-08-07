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
    kaa.beacon.launch(verbose='all', autoshutdown=True, wait=True)

kaa.beacon.register_file_type_attrs('video',
    last_played = (int, kaa.beacon.ATTR_SEARCHABLE))

kaa.beacon.register_file_type_attrs('audio',
    last_played = (int, kaa.beacon.ATTR_SEARCHABLE))
