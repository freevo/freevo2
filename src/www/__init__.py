import os
import config
import sys
import threading
import traceback

sys.path += ['./src/www','./src/tv']

import plugin
import www.webserver as webserver

TRUE  = 1
FALSE = 0


class PluginInterface(plugin.DaemonPlugin):
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.thread = web_thread()
        try:
            # self.run()
            self.thread.start()
        except:
            print 'Crash!'
            traceback.print_exc()
            sleep(1)
                                                                                
class web_thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.mode_flag = threading.Event()

    def run(self):
        webserver.run()

