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
CONF.xmame_SDL = ''
CONF.jpegtran = ''
CONF.mplayer = ''
CONF.snes = ''

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
            if not CONF.mplayer:
                print
                print "please re-run configure, it has changed"
                sys.exit(1)

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


if REMOTE and os.path.isfile('rc_client/%s.py' % REMOTE):
    execfile('rc_client/%s.py' % REMOTE, globals(), locals())
    

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
