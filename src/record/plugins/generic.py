import os
import config
from record.recorder import Plugin

class PluginInterface(Plugin):
    def __init__(self):
        Plugin.__init__(self)
        print 'plugin: activating generic record'

    def get_cmd(self, rec):
        # FIXME
        frequency = 0 

        # FIXME:
        tunerid = rec.channel
        for c in config.TV_CHANNELS:
            if tunerid == c[0] or tunerid == c[1]:
                tunerid = c[2]
                break
            
        duration = rec.stop - rec.start
        if rec.url.startswith('file:'):
            filename = rec.url[5:]
            basename = os.path.basename(filename)
        else:
            filename = rec.url
            basename = ''
        cl_options = { 'channel'       : tunerid,
                       'frequency'     : frequency,
                       'filename'      : filename,
                       'url'           : filename,
                       'base_filename' : basename,
                       'title'         : rec.name,
                       'subtitle'      : rec.subtitle,
                       'seconds'       : duration }

        return config.VCR_CMD % cl_options
