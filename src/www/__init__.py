import os
import config
import sys
import plugin

class PluginInterface(plugin.DaemonPlugin):
    def __init__(self):
        if config.CONF.display == 'dxr3':
            print 'For some strange reason, the starting of the webserver inside'
            print 'Freevo messes up with the DXR3 output. The webserver plugin'
            print 'will be disabled. Start it from outside Freevo with'
            print 'freevo webserver [start|stop]'
            self.reason = 'dxr3 output'
            return
        plugin.DaemonPlugin.__init__(self)
        self.pid = None
        os.system('%s webserver start' % os.environ['FREEVO_SCRIPT'])

    def shutdown(self):
        # print 'WEBSERVER::shutdown: pid=%s' % self.pid
        print 'Stopping webserver plugin.'
        os.system('%s webserver stop' % os.environ['FREEVO_SCRIPT'])
