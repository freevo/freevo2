import os
import config
import generic

class PluginInterface(generic.PluginInterface):

    def __init__(self, device='dvb0'):
        self.name = device
        self.device = config.TV_SETTINGS[device]
        generic.PluginInterface.__init__(self)

        self.suffix = '.ts'

        if self.device.type == 'DVB-T':
            rating = 10
        elif self.device.type == 'DVB-C':
            rating = 20 
        else:
            rating = 15 
        channels = []
        for c in self.device.channels:
            channels.append([c])
        self.channels = [ device, rating, channels ]

        
    def get_cmd(self, rec):
        channel = self.device.channels[rec.channel]
        if rec.url.startswith('file:'):
            filename = rec.url[5:]
        else:
            filename = rec.url
        return [ config.CONF.mplayer, '-dumpstream', '-dumpfile',
                 filename, 'dvb://' + String(channel) ]

    
    def get_channel_list(self):
        return [ self.channels ]

