#
# startup.py
#
# This application starts all the sub-applications that are part of the Freevo
# package, i.e. the main Freevo application, the remote control daemon and the 
# OSD daemon. It then respawns any application that exits until the user
# presses CTRL-C in this terminal.
#

import sys, os, time, signal

# Set DEBUG to 1 to get more printouts
DEBUG = 0

# Time in seconds between polling if the applications are still alive.
# Can be a float.
POLL_DELAY = 0.2

#
# This class is an abstraction for the applications that are spawned and then
# checked regularly to see that they are alive.
#
class task:

    # Spawn the application
    def __init__(self, app_args):
        self.appname = app_args.app_name
        self.application = app_args.exec_name
        self.app_args = [self.application] + app_args.exec_args
        self.pid = os.spawnv(os.P_NOWAIT, self.application, self.app_args)
        #print 'Spawned "%s", pid %s' % (' '.join(self.app_args), self.pid)
        print 'Spawned "%s", pid %s' % (self.app_args, self.pid)


    # Check if the application is still alive, respawn if needed
    def respawn(self):
        if os.waitpid(self.pid, os.WNOHANG)[0] != 0:
            if DEBUG: print 'Task %s exited' % self.appname
            self.pid = os.spawnv(os.P_NOWAIT, self.application, self.app_args)
            print 'Respawned "%s", pid %s' % (' '.join(self.app_args), self.pid)


    # kill -9 application
    def kill(self):
        if self.pid:
            os.kill(self.pid, signal.SIGKILL)

        if DEBUG: print 'Killed %s, pid %s' % (self.appname, self.pid)


        
#
# The applications to spawn and keep alive
#

class AppArgs:

    def __init__(self, app_name, exec_name, exec_args = [], exec_args_dict = {}):
        self.app_name = app_name
        self.exec_name = exec_name
        for i in range(len(exec_args)):
            processed_arg = exec_args[i] % exec_args_dict
            exec_args[i] = processed_arg
        self.exec_args = exec_args

        
# The remote control simulator, debug output in an Xterm
remote_xterm = ('remote', '/usr/X11R6/bin/xterm',
                    [ '-title', 'Freevo Remote Simulator', '-geom', '80x50',
                      '-e', 'python', './rc_client/remote.py', '--remote=%(remote)s'])

# The remote control lirc interface, no debug output
remote_quiet = ('remote', '/bin/sh',
                     [ '-c',
                       '/usr/local/bin/python ./rc_client/remote.py --remote=lirc > /dev/null', ])

# The OSD framebuffer driver, no debug output
osd_fb_quiet = ('osd_fb', '/bin/sh', ['-c',
                                      './osd_server/osd_fb/osd_fb > /dev/null'])

# The X11 framebuffer driver
osd_x11 = ('osd_x11', '/bin/sh', ['-c',
                                  './osd_server/osd_fb/osd_x11 > /dev/null'])

# The Freevo main application, debug output in an Xterm
freevo_main_xterm = ('freevo', '/usr/X11R6/bin/xterm',
                     [ '-title', 'Freevo Main', '-e', '/usr/local/bin/python',
                       './main.py', '--videotools=%(videotools)s'])

# The Freevo main application, no debug output
freevo_main_quiet = ('freevo', '/bin/sh',
                     [ '-c', '/usr/local/bin/python ./main.py '
                       '--videotools=%(videotools)s > /dev/null'])

task_args = []
tasks = []

#
# Handle CTRL-C signals from Unix. Kill all apps and exit.
#
def ctrlc_handler(signum, frame):
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
