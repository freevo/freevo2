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
# Revision 1.34  2003/08/01 17:54:05  dischi
# xine support and cleanups.
# o xine support and configuration in freevo_config.py
# o cleanup in setup_freevo: use one variable to store all needed
#   programs
# o config.py uses setup_freevo to search for missing programs at startup
#
# Revision 1.33  2003/07/30 14:04:38  outlyer
# I don't think we use $CACHEDIR/audio anymore... if anyone needs it, I'll
# uncomment it, else I'll delete it.
#
# Revision 1.32  2003/07/03 04:19:31  outlyer
# Updated cdbackup with Rich's new Ogg patch; also changed some variables,
# and added oggenc to setup and configuration.
#
# Revision 1.31  2003/07/02 20:00:42  dischi
# added defaults for ripping tools
#
# Revision 1.30  2003/06/30 20:26:18  outlyer
# Make freevo a lot less noisy; by default, print warnings and errors;
# if DEBUG is enabled, THEN we print more.
#
# Revision 1.29  2003/06/27 15:24:39  dischi
# small fix
#
# Revision 1.28  2003/06/20 18:18:23  dischi
# add comment about the xmame change to force the user to rerun setup
#
# Revision 1.27  2003/05/11 17:33:22  dischi
# small bugfix
#
# Revision 1.26  2003/04/24 19:55:44  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.25  2003/04/24 11:46:29  dischi
# fixed 'to many open files' bug
#
# Revision 1.24  2003/04/20 17:36:49  dischi
# Renamed TV_SHOW_IMAGE_DIR to TV_SHOW_DATA_DIR. This directory can contain
# images like before, but also fxd files for the tv show with global
# informations (plot/tagline/etc) and mplayer options.
#
# Revision 1.23  2003/04/18 15:01:36  dischi
# support more types of plugins and removed the old item plugin support
#
# Revision 1.22  2003/04/06 21:12:54  dischi
# o Switched to the new main skin
# o some cleanups (removed unneeded inports)
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
import setup_freevo

if not 'FREEVO_STARTDIR' in os.environ:
    print 'WARNING: FREEVO_STARTDIR is not set!'
    os.environ['FREEVO_STARTDIR'] = os.environ['PWD']
    
# Send debug to stdout as well as to the logfile?
DEBUG_STDOUT = 1

# Debug all modules?
# 0 = Debug output off
# 1 = Some debug output
# A higher number will generate more detailed output from some modules.
DEBUG = 0


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
            if DEBUG: print 'Logging info in %s' % logfile
        except IOError:
            print 'Could not open logfile: %s' % logfile
            self.fp = open('/dev/null','a')
        self.softspace = 0
        ts = time.asctime(time.localtime(time.time()))
        if DEBUG: self.write('-' * 79 + '\n')
        if DEBUG: self.write('Starting %s at %s\n' % (logtype, ts))
        
        
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
# These will be overwritten by the contents of 'freevo.conf'
CONF = Struct()
CONF.geometry = '800x600'
CONF.width, CONF.height = 800, 600
CONF.display = 'x11'
CONF.tv = 'ntsc'
CONF.chanlist = 'us-cable'
CONF.version = 0

def print_config_changes(conf_version, file_version, changelist):
    ver_old = float(file_version)
    ver_new = float(conf_version)
    if ver_old == ver_new:
        return
    print
    print 'You are using version %s, changes since then:' % file_version
    changed = [(cv, cd) for (cv, cd) in changelist if cv > ver_old]
    if not changed:
        print 'The changelist has not been updated, please notify the developers!'
    else:
        for change_ver, change_desc in changed:
            print 'Version %s:' % change_ver
            for line in change_desc.split('\n'):
                print '    ', line.strip()
            print
    print
            
    
def read_config(filename, conf):
    if DEBUG: print 'Reading config file %s' % filename

    c = open(filename)
    for line in c.readlines():
        vals = line.strip().split()
        if DEBUG: print 'Cfg file data: "%s"' % line.strip()
        try:
            name, val = vals[0], vals[2]
        except:
            print 'Error parsing config file data "%s"' % line.strip()
            continue
        conf.__dict__[name] = val

    c.close()
    w, h = conf.geometry.split('x')
    conf.width, conf.height = int(w), int(h)
        

# Check that freevo_config.py is not found in the config file dirs
for dirname in [os.path.expanduser('~/.freevo'), '/etc/freevo']:
    freevoconf = dirname + '/freevo_config.py'
    if os.path.isfile(freevoconf):
        print (('\nERROR: freevo_config.py found in %s, please remove it ' +
                'and use local_conf.py instead!') % freevoconf)
        sys.exit(1)
        
# Search for freevo.conf:
for dir in cfgfilepath:
    freevoconf = dir + '/freevo.conf'
    if os.path.isfile(freevoconf):
        if DEBUG: print 'Loading configure settings: %s' % freevoconf
        read_config(freevoconf, CONF)
        break

# search missing programs at runtime
for program, valname, needed in setup_freevo.EXTERNAL_PROGRAMS:
    if not hasattr(CONF, valname) or not getattr(CONF, valname):
        setup_freevo.check_program(CONF, program, valname, needed, verbose=0)
    if not hasattr(CONF, valname) or not getattr(CONF, valname):
        setattr(CONF, valname, '')

# Load freevo_config.py:
cfgfilename = './freevo_config.py'
if os.path.isfile(cfgfilename):
    if DEBUG: print 'Loading cfg: %s' % cfgfilename
    execfile(cfgfilename, globals(), locals())

else:
    print "\nERROR: can't find freevo_config.py"
    sys.exit(1)


# Search for local_conf.py:
for dirname in cfgfilepath:
    overridefile = dirname + '/local_conf.py'
    if os.path.isfile(overridefile):
        if DEBUG: print 'Loading cfg overrides: %s' % overridefile
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
            print '\nERROR: The version information in freevo_config.py doesn\'t'
            print 'match the version in your local_config.py.'
            print 'Please check freevo_config.py for changes and set CONFIG_VERSION'
            print 'in %s to %s' % (overridefile, LOCAL_CONF_VERSION)
            print_config_changes(LOCAL_CONF_VERSION, CONFIG_VERSION,
                                 LOCAL_CONF_CHANGES)
            sys.exit(1)

        if int(str(CONFIG_VERSION).split('.')[1]) != \
           int(str(LOCAL_CONF_VERSION).split('.')[1]):
            print 'WARNING: freevo_config.py was changed, please check local_config.py'
            print_config_changes(LOCAL_CONF_VERSION, CONFIG_VERSION, 
                                 LOCAL_CONF_CHANGES)
        break

else:
    print 'No overrides loaded'
    
# Autodetect the CD/DVD drives in the system if not given in local_conf.py
if not ROM_DRIVES:
    if os.path.isfile('/etc/fstab'):
        RE_CD = '^(/dev/cdrom)[ \t]+([^ \t]+)[ \t]+'
        RE_CDREC ='^(/dev/cdrecorder)[ \t]+([^ \t]+)[ \t]+'
        RE_DVD ='^(/dev/dvd)[ \t]+([^ \t]+)[ \t]+'
        RE_ISO ='^([^ \t]+)[ \t]+([^ \t]+)[ \t]+iso9660'
        RE_AUTOMOUNT = '^none[ \t]+([^ \t]+) supermount dev=([^,]+)'
        fd_fstab = open('/etc/fstab')
        for line in fd_fstab:
            # Match on the devices /dev/cdrom, /dev/dvd, and fstype iso9660
            match_cd = re.compile(RE_CD, re.I).match(line)
            match_cdrec = re.compile(RE_CDREC, re.I).match(line)
            match_dvd = re.compile(RE_DVD, re.I).match(line)
            match_iso = re.compile(RE_ISO, re.I).match(line)
            match_automount = re.compile(RE_AUTOMOUNT, re.I).match(line)
            mntdir = devname = ''
            if match_cd:
                mntdir = match_cd.group(2)
                devname = match_cd.group(1)
                dispname = 'CD-%s' % (len(ROM_DRIVES)+1)
            elif match_cdrec: 
                mntdir = match_cdrec.group(2)
                devname = match_cdrec.group(1)
                dispname = 'CDREC-%s' % (len(ROM_DRIVES)+1)
            elif match_dvd:
                mntdir = match_dvd.group(2)
                devname = match_dvd.group(1)
                dispname = 'DVD-%s' % (len(ROM_DRIVES)+1)
            elif match_iso:
                mntdir = match_iso.group(2)
                devname = match_iso.group(1)
                dispname = 'CD-%s' % (len(ROM_DRIVES)+1)
            elif match_automount:
                mntdir = match_automount.group(1)
                devname = match_automount.group(2)
                # Must check that the supermount device is cd or dvd
                if devname.lower().find('cdrom') != -1:
                    dispname = 'CD-%s' % (len(ROM_DRIVES)+1)
                elif devname.lower().find('dvd') != -1:
                    dispname = 'DVD-%s' % (len(ROM_DRIVES)+1)
                else:
                    mntdir = devname = dispname = ''

            # Weed out duplicates
            for rd_mntdir, rd_devname, rd_dispname in ROM_DRIVES:
                if os.path.realpath(rd_devname) == os.path.realpath(devname):
                    print (('ROM_DRIVES: Auto-detected that %s is the same ' +
                            'device as %s, skipping') % (devname, rd_devname))
                    break
            else:
                # This was not a duplicate of another device
                if mntdir and devname and dispname:
                    ROM_DRIVES += [ (mntdir, devname, dispname) ]
                    print 'ROM_DRIVES: Auto-detected and added "%s"' % (ROM_DRIVES[-1], )
        fd_fstab.close()
                
#
# The runtime version of MPlayer/MEncoder are patched to disable DVD
# protection override (a.k.a decss) by using the flag
# "-nodvdprotection-override". This flag is used by default if the runtime version
# of MPlayer is used to play DVDs, since it is illegal (TBC) to use it in some
# countries. You can modify the program to use the protection override,
# but only if you're 100% sure that it is legal in your jurisdiction!
#
if CONF.mplayer.find('runtime/apps/mplayer') != -1 and MPLAYER_DVD_PROTECTION:
    print
    print 'WARNING: DVD protection override disabled! You will not be able to play',
    print 'protected DVDs!'
    print
    MPLAYER_ARGS['dvd'] += ' -nodvdprotection-override'

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
TV_SHOW_INFORMATIONS     = {}

#
# compile the regexp
#
TV_SHOW_REGEXP_MATCH = re.compile("^.*" + TV_SHOW_REGEXP).match
TV_SHOW_REGEXP_SPLIT = re.compile("[\.\- ]*" + TV_SHOW_REGEXP + "[\.\- ]*").split


#
# create cache subdirs
#

if not os.path.isdir('%s/thumbnails/' % FREEVO_CACHEDIR):
    import stat
    os.mkdir('%s/thumbnails/' % FREEVO_CACHEDIR,
             stat.S_IMODE(os.stat(FREEVO_CACHEDIR)[stat.ST_MODE]))
