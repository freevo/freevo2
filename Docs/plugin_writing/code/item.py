import plugin
import config

class PluginInterface(plugin.ItemPlugin):
    def actions(self, item):
        if item.type == 'video':
            return [ (self.remove_sws, 'Remove Software Scaler'),
                     (self.sws, 'Use Software Scaler') ]
        else:
            return []
        
    def remove_sws(self, menuw=None, arg=None):
        config.MPLAYER_SOFTWARE_SCALER = ''
        menuw.back_one_menu()
        
    def sws(self, menuw=None, arg=None):
        config.MPLAYER_SOFTWARE_SCALER = "-subfont-text-scale 15 -fs -sws 0 "\
                                         "-vf scale=%s:-3"\
                                         " -font /usr/share/mplayer/fonts/"\
                                         "font-arial-28-iso-8859-2/font.desc" % \
                                         config.CONF.width
        menuw.back_one_menu()
