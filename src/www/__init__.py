import os
import config
import sys
import threading
import traceback

import plugin

TRUE  = 1
FALSE = 0


class PluginInterface(plugin.DaemonPlugin):
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.pid = None
        os.system('%s webserver start' % os.environ['FREEVO_SCRIPT'])

    def shutdown(self):
        # print 'WEBSERVER::shutdown: pid=%s' % self.pid
        print 'Stopping webserver plugin.'
        os.system('%s webserver stop' % os.environ['FREEVO_SCRIPT'])
