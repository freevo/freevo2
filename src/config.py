#if 0 /*
# -----------------------------------------------------------------------
# config.py - Handle the configuration file init. Also start logging.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
#   Try to find the freevo_config.py config file in the following places:
#   1) ~/.freevo/freevo_config.py       The user's private config
#   2) /etc/freevo/freevo_config.py     Systemwide config
#   3) ./freevo_config.py               Defaults from the freevo dist
#   
#   Customize freevo_config.py from the freevo dist and copy it to one
#   of the other places where it will not get overwritten by new
#   checkouts/installs of freevo.
#   
#   The format of freevo_config.py might change, in that case you'll
#   have to update your customized version.
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.10  2003/02/07 19:26:56  dischi
# check freevo.conf version _before_ parsing freevo_config.py and REMOTE ist
# searched using cfgfilepath
#
# Revision 1.9  2003/02/07 17:09:19  dischi
# Changed the config file loading based on the guidelines from Krister.
#
# Revision 1.8  2003/01/19 16:03:36  dischi
# reverse the path for searching for the config file. First try to find the
# files in . (maybe you have more than one version of Freevo installed), after
# that the user directory and last the etc directory. All installations (RPM
# and ebuild in the near future) should _move_ the config files to /etc/freevo
# to make it possible to have a user configuration.
#
# Revision 1.7  2003/01/18 16:54:19  dischi
# Search the config file for the remote in different directories:
# ~/freevo, /etc/freevo and ./rc_client
#
# Revision 1.6  2003/01/09 05:04:06  krister
# Added an option to play all movies in a dir, and generate random playlists for them.
#
# Revision 1.5  2003/01/04 16:39:47  dischi
# Added uid to the name of the logfile to avoid conflicts when running
# freevo with different users
#
# Revision 1.4  2002/12/30 15:07:40  dischi
# Small but important changes to the remote control. There is a new variable
# RC_MPLAYER_CMDS to specify mplayer commands for a remote. You can also set
# the variable REMOTE to a file in rc_clients to contain settings for a
# remote. The only one right now is realmagic, feel free to add more.
# RC_MPLAYER_CMDS uses the slave commands from mplayer, src/video/mplayer.py
# now uses -slave and not the key bindings.
#
# Revision 1.3  2002/12/09 14:25:58  dischi
# Added default for snes
#
# Revision 1.2  2002/12/07 13:29:49  dischi
# Make a new database with all movies, even without id and label
#
# Revision 1.1  2002/11/24 13:58:44  dischi
# code cleanup
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# ----------------------------------------------------------------------- */
#endif


import sys, os, time, re
import traceback

# Fallback for a new option, remove later.
MOVIE_PLAYLISTS = 0

# Send debug to stdout as well as to the logfile?
DEBUG_STDOUT = 1

# Debug all modules?
# 0 = Debug output off
# 1 = Some debug output
# A higher number will generate more detailed output from some modules.
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
            logfile = '%s/internal-%s-%s.log' % (LOGDIR, appname, os.getuid())
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
cfgfilepath = [ os.environ['FREEVO_STARTDIR'],
                os.path.expanduser('~/.freevo'),
                '/etc/freevo',
                '.' ]

class Struct:
    pass

# Default settings
CONF = Struct()
CONF.geometry = '800x600'
CONF.width, CONF.height = 800, 600
CONF.display = 'x11'
CONF.tv = 'ntsc'
CONF.chanlist = 'us-cable'
CONF.xmame_SDL = ''
CONF.jpegtran = ''
CONF.mplayer = ''
CONF.snes = ''
CONF.version = 0

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
        

# Search for freevo.conf:
for dir in cfgfilepath:
    freevoconf = dir + '/freevo.conf'
    if os.path.isfile(freevoconf):
        print 'Loading configure settings: %s' % freevoconf
        read_config(freevoconf, CONF)
        break
    
# Load freevo_config.py:
cfgfilename = './freevo_config.py'
if os.path.isfile(cfgfilename):
    print 'Loading cfg: %s' % cfgfilename
    execfile(cfgfilename, globals(), locals())

else:
    print '\nERROR: can\' find freevo_config.py'
    sys.exit(1)


# Search for local_conf.py:
for dir in cfgfilepath:
    overridefile = dir + '/local_conf.py'
    if os.path.isfile(overridefile):
        print 'Loading cfg overrides: %s' % overridefile
        execfile(overridefile, globals(), locals())

        try:
            CONFIG_VERSION
        except NameError:
            print '\nERROR: your local_config.py file has no version information'
            print 'Please check freevo_config.py for changes and set CONFIG_VERSION'
            print 'in %s to %s' % (overridefile, LOCAL_CONF_VERSION)
            sys.exit(1)

        if int(str(CONFIG_VERSION).split('.')[0]) != \
           int(str(LOCAL_CONF_VERSION).split('.')[0]):
            print '\nERROR: The version informations in freevo_config.py doesn\'t'
            print 'match the version in your local_config.py.'
            print 'Please check freevo_config.py for changes and set CONFIG_VERSION'
            print 'in %s to %s' % (overridefile, LOCAL_CONF_VERSION)
            sys.exit(1)

        if int(str(CONFIG_VERSION).split('.')[1]) != \
           int(str(LOCAL_CONF_VERSION).split('.')[1]):
            print 'WARNING: freevo_config.py was changed, please check local_config.py'
        break

else:
    print 'No overrides loaded'
    

#search the remote
if REMOTE:
    for dir in cfgfilepath:
        if os.path.isfile('%s/%s.py' % (dir, REMOTE)):
            print 'load REMOTE file %s/%s.py' % (dir, REMOTE)
            execfile('%s/%s.py' % (dir, REMOTE), globals(), locals())
            break
        if os.path.isfile('%s/rc_client/%s.py' % (dir, REMOTE)):
            print 'load REMOTE file %s/%s.py' % (dir, REMOTE)
            execfile('%s/rc_client/%s.py' % (dir, REMOTE), globals(), locals())
            break
    else:
        print 'No remote config found'


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

MOVIE_INFORMATIONS       = []
MOVIE_INFORMATIONS_ID    = {}
MOVIE_INFORMATIONS_LABEL = []

#
# compile the regexp
#
TV_SHOW_REGEXP_MATCH = re.compile("^.*" + TV_SHOW_REGEXP).match
TV_SHOW_REGEXP_SPLIT = re.compile("[\.\- ]*" + TV_SHOW_REGEXP + "[\.\- ]*").split


#
# search plugins
#

FREEVO_PLUGINS = {}

