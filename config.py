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
import util

# XML support
from xml.utils import qp_xml



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
founddir = ''
for dir in cfgfilepath:
    cfgfilename = dir + '/freevo_config.py'
    if os.path.isfile(cfgfilename):
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

#
# find movie informations
#

def XML_to_MOVIE_INFORMATIONS(file, info_struct):
    try:
        parser = qp_xml.Parser()
        box = parser.parse(open(file).read())
    except:
        print "XML file %s corrupt" % file
    else:
        title = image = ""
        id = []
        if box.children[0].name == 'movie':
            for node in box.children[0].children:
                if node.name == u'title':
                    title = node.textof()
                if node.name == u'id':
                    id += [node.textof()]
                elif node.name == u'cover' and \
                     os.path.isfile(os.path.join(os.path.dirname(file),node.textof())):
                    image = os.path.join(os.path.dirname(file), node.textof())
        if title and id:
            for i in id:
                info_struct += [(title, image, i)]


MOVIE_INFORMATIONS = []

for name,dir in DIR_MOVIES:
    for file in util.recursefolders(dir,1,'*.xml',1):
        XML_to_MOVIE_INFORMATIONS(file, MOVIE_INFORMATIONS)

for file in util.recursefolders(MOVIE_DATA_DIR,1,'*.xml',1):
    XML_to_MOVIE_INFORMATIONS(file, MOVIE_INFORMATIONS)

