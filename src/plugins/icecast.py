import os
import config
import sys
import traceback
import signal
import time

import plugin

TRUE  = 1
FALSE = 0


class PluginInterface(plugin.DaemonPlugin):
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.icecast-pid = None
        self.ices-pid = None

        try:
            # start icecast
            mycmd = os.path.basename(config.ICECAST_CMD)
            self.icecast-pid = os.spawnl(os.P_NOWAIT, config.ICECAST_CMD, mycmd, '-d', config.ICECAST_CONF_DIR)
            time.sleep(1)
            # start ices
            mycmd = os.path.basename(config.ICES_CMD)
            args = config.ICES_OPTIONS
            args.insert(0, mycmd)
            args.append('-F')
            args.append(config.ICES_DEF_LIST)
            olddir = os.getcwd()
            newdir = os.path.dirname(config.ICES_DEF_LIST)
            os.chdir(newdir)
            self.ices-pid = os.spawnv(os.P_NOWAIT, config.ICES_CMD, args)
            os.chdir(olddir)
        except:
            print 'Crash!'
            traceback.print_exc()
            sleep(1)

    def poll(self):
        #see if we got a change list request
        if (os.path.isfile(os.path.join(config.FREEVO_CACHEDIR, 'changem3u.txt'))):
            try:
                mycmd = os.path.basename(config.ICES_CMD)
                newm3ufile = file(os.path.join(config.FREEVO_CACHEDIR, 'changem3u.txt'), 'rb').read()
                os.unlink(os.path.join(config.FREEVO_CACHEDIR, 'changem3u.txt'))
                os.kill(self.pid, signal.SIGTERM)
                os.waitpid(self.pid, 0)
                time.sleep(1)
                args = config.ICES_OPTIONS
                args.insert(0, mycmd)
                args.append('-F')
                args.append(newm3ufile)
                olddir = os.getcwd()
                newdir = os.path.dirname(newm3ufile)
                os.chdir(newdir)
                self.pid = os.spawnv(os.P_NOWAIT, config.ICES_CMD, args)
                os.chdir(olddir)
            except:
                print 'Crash!'
                traceback.print_exc()
                sleep(1)

    def shutdown(self):
        # print 'icecast server::shutdown: pid=%s' % self.pid
        print 'Stopping icecast server plugin.'
        os.kill(self.icecast-pid, signal.SIGTERM)
        os.waitpid(self.pid, 0)
        os.kill(self.ices-pid, signal.SIGTERM)
        os.waitpid(self.pid, 0)

