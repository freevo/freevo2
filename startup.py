#
# startup.py
#
# This application starts all the sub-applications that are part of the Freevo
# package, i.e. the main Freevo application, the remote control daemon and the 
# OSD daemon. It then respawns any application that exits until the user
# presses CTRL-C in this terminal.
#
# $Id$

import sys, os, time, signal

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Set DEBUG to 1 to get more printouts
DEBUG = 0

# Time in seconds between polling if the applications are still alive.
# Can be a float.
POLL_DELAY = 0.2

task_args = []
tasks = []


#
# Check if an application can be found in the user's path. The function
# returns 1 if the file 'appname' can be found anywhere in the path.
#
def check_application(appname):
    if os.path.isabs(appname):
        if os.path.isfile(appname):
            return 1
        else:
            return 0

    if appname[0] == '.':
        if os.path.isfile(appname):
            return 1
        else:
            return 0
       
    path = os.path.expandvars('$PATH').split(':')
    for dir in path:
        fname = os.path.join(dir, appname)
        if os.path.isfile(fname):
            return 1

    return 0

    
#
# This class is an abstraction for the applications that are spawned and then
# checked regularly to see that they are alive.
#
class task:

    # Spawn the application
    def __init__(self, app_args):
        # First check if the application can be located in the path
        app = app_args.exec_name
        if not check_application(app):
            print 'PANIC: Cannot find the app "%s" anywhere!' % app
            
        self.appname = app_args.app_name
        self.application = app_args.exec_name
        self.app_args = [self.application] + app_args.exec_args
        self.pid = os.spawnvp(os.P_NOWAIT, self.application, self.app_args)
        #print 'Spawned "%s", pid %s' % (' '.join(self.app_args), self.pid)
        print 'Spawned "%s", pid %s' % (self.app_args, self.pid)


    # Check if the application is still alive, respawn if needed
    def respawn(self):
        pid, exitstat = os.waitpid(self.pid, os.WNOHANG)
        if pid != 0:
            if DEBUG:
                print 'Task %s exited, stat 0x%04x.' % (self.appname, exitstat)
                print ' Delaying before respawn...'
            time.sleep(3.0)

            self.pid = os.spawnv(os.P_NOWAIT, self.application, self.app_args)
            #print 'Respawned "%s", pid %s' % (' '.join(self.app_args), self.pid)
            print 'Respawned "%s", pid %s' % (self.app_args, self.pid)


    # kill -9 application
    def kill(self):
        if self.pid:
            try:
                os.kill(self.pid, signal.SIGTERM)
            except OSError:
                pass  # Task was already killed

        if DEBUG: print 'Killed %s, pid %s' % (self.appname, self.pid)


        
#
# The applications to spawn and keep alive
#

class AppArgs:

    def __init__(self, app_name, exec_name, exec_args = None, exec_args_dict = {}):
        if not exec_args:
            exec_args = []
        self.app_name = app_name
        self.exec_name = exec_name
        for i in range(len(exec_args)):
            processed_arg = exec_args[i] % exec_args_dict
            exec_args[i] = processed_arg
        self.exec_args = exec_args

        
# The remote control simulator, debug output in an Xterm
remote_xterm = ('remote', 'xterm',
                    [ '-title', 'Freevo Remote Simulator', '-geom', '57x50',
                      '-e', 'python', './rc_client/remote.py', '--remote=%(remote)s'])

# The remote control lirc interface, no debug output
remote_quiet = ('remote', 'sh',
                     [ '-c',
                       'python ./rc_client/remote.py --remote=lirc > /dev/null', ])

# The OSD framebuffer driver, no debug output
osd_fb_quiet = ('osd_fb', 'sh', ['-c',
                                 './osd_server/osds_fb > /dev/null'])

# The X11 framebuffer driver, debug output to /tmp/freevo_osdx11.log
osd_x11 = ('osd_x11',
           'sh', ['-c',
                  './osd_server/osds_x11 > %s/internal-osdx11.log' % config.LOGDIR])

# The SDL framebuffer driver
osd_sdl = ('osd_sdl', 'sh', ['-c',
                             './osd_server/osds_sdl'])

# The DXR3 driver, debug output to /tmp/freevo_osddxr3.log
osd_dxr3 = ('osd_dxr3',
           'sh', ['-c',
                  './osd_server/osds_dxr3 > %s/internal-osddxr3.log' % config.LOGDIR])

# The Freevo main application, debug output in an Xterm
freevo_main_xterm = ('freevo', 'xterm',
                     [  '-geom', '80x15', '-title', 'Freevo Main',
                        '-e', 'python',
                       './main.py', '--videotools=%(videotools)s'])

# The Freevo main application, no debug output
freevo_main_quiet = ('freevo', 'sh',
                     [ '-c', 'python ./main.py '
                       '--videotools=%(videotools)s > /dev/null'])

#
# Handle CTRL-C signals from Unix. Kill all apps and exit.
#
def ctrlc_handler(signum, frame):
    global tasks
    
    print 'CTRL-C pressed! Shutting down...'

    # Kill off all subtasks
    for task in tasks:
        task.kill()
        
    # Done
    sys.exit()


#
# Option settings
#
options = {
    '--help'              : 'usage(sys.argv[0])',
    '--remote=lirc-quiet' : 'remote = remote_quiet',
    '--remote=lirc-xterm' : 'extra_args_dict["remote"] = "lirc"',
    '--remote=sim-xterm'  : 'extra_args_dict["remote"] = "sim"',
    '--osd=fb'            : 'osd = osd_fb_quiet',
    '--osd=x11'           : 'osd = osd_x11',
    '--osd=sdl'           : 'osd = osd_sdl',
    '--osd=dxr3'          : 'osd = osd_dxr3',
    '--freevo=main-xterm' : 'freevo = freevo_main_xterm',
    '--freevo=main-quiet' : 'freevo = freevo_main_quiet',
    '--videotools=real'   : 'extra_args_dict["videotools"] = "real"',
    '--videotools=sim'    : 'extra_args_dict["videotools"] = "sim"',
    }

#
# Display program usage and exit
#
def usage(progname):
             
    print 'Usage: %s [freevo-type] [remote-type] [osd-type]' % progname
    print

    opts = options.keys()
    opts.sort()
    for opt in opts:
        print '\t%s' % opt

    sys.exit()

#
# The main loop
#
if __name__ == "__main__":

    # Defaults
    freevo = freevo_main_xterm
    osd = osd_x11
    remote = remote_xterm
    extra_args_dict = {  'videotools' : 'sim', 'remote' : 'sim' }
    
    # Simple argument decoding
    for arg in sys.argv[1:]:
        if options.has_key(arg):
            code = compile(options[arg], '<string>', 'exec')
            eval(code, globals(), locals())
        else:
            print 'Cannot decode option "%s"' % arg
            usage(sys.argv[0])

    # XXX TEST CODE BY KRISTER! This code fragment will load the experimental OSD SDL module
    # if the symbol OSD_SDL is in the config module namespace, but will work fine if it is not.
    # This is used to load my new version of the OSD module without messing around in the source
    # too much...
    if 'OSD_SDL' in dir(config):
        # Do not use the regular remote control app and OSD server, they're both replaced by the
        # SDL OSD server!
        if remote == remote_quiet:
            task_args += [ freevo, remote ]
        else:
            task_args += [ freevo ]
    else:
        # Add the OSD server and remote control client applications
        task_args += [ freevo, osd, remote ]
    
    # Set the signal handler for CTRL-C which will shut down Freevo
    signal.signal(signal.SIGINT, ctrlc_handler)

    # Start up all the sub tasks
    for args in task_args:
        # Create a list of the task objects
        app_args = AppArgs(args[0], args[1], args[2], extra_args_dict)
        tasks += [task(app_args)]

    print '\nStarted Freevo, press CTRL-C to quit'
    
    while 1:
        if DEBUG: print 'Checking for tasks done'
        
        for task in tasks:
            task.respawn()
            
        time.sleep(POLL_DELAY)
