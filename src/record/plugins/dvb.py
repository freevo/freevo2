import os
import config
from record.recorder import Plugin

class PluginInterface(Plugin):

    def __init__(self):
        print 'plugin: activating dvb record'
        Plugin.__init__(self)

    def get_cmd(self, rec):
        # FIXME
        frequency = 0 

        # FIXME:
        tunerid = rec.channel
        for c in config.TV_CHANNELS:
            if tunerid == c[0] or tunerid == c[1]:
                tunerid = c[2]
                break

        if rec.url.startswith('file:'):
            filename = rec.url[5:]
        else:
            filename = rec.url

        return [ config.CONF.mplayer, '-dumpstream', '-dumpfile',
                 filename, 'dvb://' + String(tunerid) ]
    
