import os
import config
import sys
import threading
import traceback

sys.path += ['./src/www','./src/tv']

import plugin

TRUE  = 1
FALSE = 0


class PluginInterface(plugin.DaemonPlugin):
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.pid = None

        try:
            self.pid = os.spawnlp(os.P_NOWAIT, './freevo', './freevo', 'execute', 'src/www/webserver.py')
        except:
            print 'Crash!'
            traceback.print_exc()
            sleep(1)
                                                                                
