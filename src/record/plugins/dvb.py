import os
import config
import generic

import util.fileops

class PluginInterface(generic.PluginInterface):

    def __init__(self, device='dvb0', rating=0):
        self.name = device
        self.device = config.TV_SETTINGS[device]

	home = os.environ[ 'HOME' ]
	pathes = [ os.path.join( home, '.freevo' ),
		   os.path.join( home, '.mplayer' ),
		   os.path.join( home, '.xine' ) ]
        self.program = 'mplayer'
        if self.device.type == 'DVB-T':
            rating = rating or 8
	    self.program = 'tzap'
            self.program_file = util.fileops.find_file_in_path( self.program )
            if self.program_file:
                pathes.insert( 0, os.path.join( home, '.tzap' ) )
        elif self.device.type == 'DVB-C':
            rating = rating or 10
        else:
            rating = rating or 9
	
        if not self.program_file:
	    self.program = 'mplayer'
	    self.program_file = config.CONF.mplayer
	
	self.configfile = util.fileops.find_file_in_path( 'channels.conf',
							  pathes )
	if not self.configfile:
	    self.reason = 'no channels configuration found'
	    return

        generic.PluginInterface.__init__(self)
        self.suffix = '.ts'

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

        if self.program == 'mplayer':
            return [ self.program_file, '-dumpstream', '-dumpfile',
                     filename, 'dvb://' + String(channel) ]
        elif self.program == 'tzap':
	    return [ self.program_file, '-o', filename, '-c', self.configfile,
	             '-a', self.device.number, String( channel ) ]

    
    def get_channel_list(self):
        return [ self.channels ]

