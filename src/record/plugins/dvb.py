import os
import config
import generic

class PluginInterface(generic.PluginInterface):

    def __init__(self):
        self.name = 'dvb0'
        generic.PluginInterface.__init__(self)

        channels = []
        f = open(os.path.expanduser('~/.mplayer/channels.conf'))
        for l in f.readlines():
            dvbname = l[:l.find(':')]
            for c in config.TV_CHANNELS:
                if c[2] == dvbname:
                    channels.append([c[0]])
        self.channels = [ 'dvb0', 10, channels ]


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

    
    def get_channel_list(self):
        return [ self.channels ]

