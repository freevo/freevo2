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

import sys, os, time


# Logging class. Logs stuff on stdout and /tmp/freevo.log
class Logger:

    def __init__(self, logtype='(unknown)'):
        self.lineno = 1
        self.logtype = logtype
        self.fp = open('/tmp/freevo.log', 'a') # XXX Add try...catch
        self.softspace = 0
        ts = time.asctime(time.localtime(time.time()))
        self.write('Starting %s at %s\n' % (logtype, ts))
        
        
    def write(self, msg):
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

found = 0
for dir in cfgfilepath:
    cfgfilename = dir + '/freevo_config.py'
    if os.path.isfile(cfgfilename):
        print 'Loading cfg: %s' % cfgfilename
        execfile(cfgfilename, globals(), locals())
        found = 1
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
