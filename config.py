#
# config.py - Handle the configuration file init. Also start logging.
#
# Try to find the freevo_config.py config file in the following places:
# 1) ~/.freevo/freevo_config.py       The user's private config
# 2) /etc/freevo/freevo_config.py     Systemwide config
# 3) ./freevo_config.py               Defaults from the freevo dist
#
# Customize freevo_config.py from the freevo dist and copy it to one of the
# other places where it will not get overwritten by new checkouts/installs
# of freevo.
#
# The format of freevo_config.py might change, in that case you'll have to
# update your customized version.
#
# $Id$
#

import sys, os, time, re
import movie_xml

# Send debug to stdout as well as to the logfile?
DEBUG_STDOUT = 1

# Automatically turn on all DEBUG flags in all modules?
DEBUG_ALL = 1

# Debug this module?
DEBUG = 1


if os.path.isdir('/var/log/freevo'):
    LOGDIR = '/var/log/freevo'
else:
    LOGDIR = '/tmp/freevo'
    if not os.path.isdir(LOGDIR):
        os.makedirs(LOGDIR)


# Logging class. Logs stuff on stdout and /tmp/freevo.log
class Logger:

    def __init__(self, logtype='(unknown)'):
        self.lineno = 1
        self.logtype = logtype
        try:
            appname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
            logfile = '%s/internal-%s.log' % (LOGDIR, appname)
            self.fp = open(logfile, 'a')
            print 'Logging info in %s' % logfile
        except IOError:
            print 'Could not open logfile: %s' % logfile
            self.fp = open('/dev/null','a')
        self.softspace = 0
        ts = time.asctime(time.localtime(time.time()))
        self.write('-' * 79 + '\n')
        self.write('Starting %s at %s\n' % (logtype, ts))
        
        
    def write(self, msg):
        global DEBUG_STDOUT
        if DEBUG_STDOUT:
            sys.__stdout__.write(msg)
        self.fp.write(msg)
        self.fp.flush()

        return

        # XXX Work in progress...
        lines = msg.split('\n')
        ts = time.asctime(time.localtime(time.time()))
        for line in lines:
            logmsg = '%d: %-20s (%s): %s\n' % (self.lineno, self.logtype, ts, line)
            self.lineno += 1
            self.fp.write(logmsg)
            self.fp.flush()
            sys.__stdout__.write(logmsg)    # Original stdout
            sys.__stdout__.flush()


    def flush():
        pass


    def close():
        pass
    
            

#
# Redirect stdout and stderr to stdout and /tmp/freevo.log
#

sys.stdout = Logger(sys.argv[0] + ':stdin')
sys.stderr = Logger(sys.argv[0] + ':stderr')


#
# Config file handling
#
cfgfilepath = [ '/etc/freevo',
                os.path.expanduser('~/.freevo'),
                '.'
                ]

class Struct:
    pass

# Default settings
CONF = Struct()
CONF.geometry = '800x600'
CONF.width, CONF.height = 800, 600
CONF.display = 'x11'
CONF.tv = 'ntsc'
CONF.chanlist = 'us-cable'

def read_config(filename, conf):
    if DEBUG: print 'Reading config file %s' % filename
    
    lines = open(filename).readlines()
    for line in lines:
        vals = line.strip().split()
        if DEBUG: print 'Cfg file data: "%s"' % line.strip()
        try:
            name, val = vals[0], vals[2]
        except:
            print 'Error parsing config file data "%s"' % line.strip()
            continue
        conf.__dict__[name] = val

    w, h = conf.geometry.split('x')
    conf.width, conf.height = int(w), int(h)
        
    
found = 0
founddir = ''
for dir in cfgfilepath:
    cfgfilename = dir + '/freevo_config.py'
    if os.path.isfile(cfgfilename):

        freevoconf = os.path.dirname(cfgfilename) + "/freevo.conf"
        if os.path.isfile(freevoconf):
            print 'Loading configure settings: %s' % freevoconf
            read_config(freevoconf, CONF)

        print 'Loading cfg: %s' % cfgfilename
        execfile(cfgfilename, globals(), locals())
        found = 1
        founddir = dir
        break
    else:
        print '%s not found' % cfgfilename

if not found:
    # This is a fatal error, the freevo_config.py file must be loaded!
    print ('Freevo: Fatal error, cannot find freevo_config.py. ' +
          'Looked in the following dirs:')
    for dir in cfgfilepath:
        print ' '*5 + dir

    raise 'Cannot find freevo_config.py'
else:
    overridefile = founddir + '/local_conf.py'
    if os.path.isfile(overridefile):
        print 'Loading cfg overrides: %s' % overridefile
        execfile(overridefile, globals(), locals())
    else:
        print 'No overrides loaded'

    # XXX Check that the user has updated the config file for the new
    # XXX ROM_DRIVES format.
    if ROM_DRIVES:
        for drive in ROM_DRIVES:
            if len(drive) != 3:
                sys.__stdout__.write('ERROR! config.ROM_DRIVES is ' +
                                     'not 3 elements!\n')
                sys.exit(1)


#
# List of objects representing removable media, e.g. CD-ROMs,
# DVDs, etc.
#

REMOVABLE_MEDIA = []

#
# Movie information database.
# The database is built at startup in the identifymedia thread,
# and also if the file '/tmp/freevo-rebuild-database' is created.
#

MOVIE_INFORMATIONS = {}

#
# compile the regexp
#
TV_SHOW_REGEXP_MATCH = re.compile("^.*" + TV_SHOW_REGEXP).match
TV_SHOW_REGEXP_SPLIT = re.compile("[\.\- ]*" + TV_SHOW_REGEXP + "[\.\- ]*").split

