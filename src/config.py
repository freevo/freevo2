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
# Revision 1.21  2003/03/21 19:51:34  dischi
# moved some main menu settings from skin to freevo_config.py (new skin only)
#
# Revision 1.20  2003/03/15 10:03:40  dischi
# create subdirs in the cache directory
#
# Revision 1.19  2003/03/01 10:45:43  dischi
# new variable config.NEW_SKIN to integrate the gui code
#
# Revision 1.18  2003/02/25 04:37:29  krister
# Updated local_conf version to 2.0 to make it clear that the remote control stuff changed. Added automatic information about what has changed in the config files since the user's version.
#
# Revision 1.17  2003/02/22 22:32:12  krister
# Init FREEVO_STARTDIR if not set.
#
# Revision 1.16  2003/02/20 19:03:42  dischi
# Removed REMOTE because we use lirc now
#
# Revision 1.15  2003/02/12 19:45:39  krister
# Fixed more stupid bugs in rom-drives autodetect for automounted drives.
#
# Revision 1.14  2003/02/12 16:20:31  krister
# Fixed stupid bugs in rom-drives autodetect for cdrecorder and automounted drives.
#
# Revision 1.13  2003/02/12 06:32:28  krister
# Added cdrecord and supermounted drives autodetection for ROM_DRIVES.
#
# Revision 1.12  2003/02/11 06:07:59  krister
# Improved CV/DVD autodetection. Use mad for mp3 playing, fixes a decoding bug.
#
# Revision 1.11  2003/02/11 04:37:29  krister
# Added an empty local_conf.py template for new users. It is now an error if freevo_config.py is found in /etc/freevo etc. Changed DVD protection to use a flag. MPlayer stores debug logs in FREEVO_STARTDIR, and stops with an error if they cannot be written.
#
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

if not 'FREEVO_STARTDIR' in os.environ:
    print 'WARNING: FREEVO_STARTDIR is not set!'
    os.environ['FREEVO_STARTDIR'] = os.environ['PWD']
    
# XXX Fallback for a new option, remove later.
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
# These will be overwritten by the contents of 'freevo.conf'
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

class MainMenuItem:
    def __init__(self, label, action, arg):
        self.label = label
        self.action = action
        self.arg = arg
        

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
        print 'Loading configure settings: %s' % freevoconf
        read_config(freevoconf, CONF)
        break
    
# Load freevo_config.py:
cfgfilename = './freevo_config.py'
if os.path.isfile(cfgfilename):
    print 'Loading cfg: %s' % cfgfilename
    execfile(cfgfilename, globals(), locals())

else:
    print "\nERROR: can't find freevo_config.py"
    sys.exit(1)


# Search for local_conf.py:
for dirname in cfgfilepath:
    overridefile = dirname + '/local_conf.py'
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
    MPLAYER_ARGS_DVD += ' -nodvdprotection-override'
    

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


#
# create cache subdirs
#

if not os.path.isdir('%s/thumbnails/' % FREEVO_CACHEDIR):
    import stat
    os.mkdir('%s/thumbnails/' % FREEVO_CACHEDIR,
             stat.S_IMODE(os.stat(FREEVO_CACHEDIR)[stat.ST_MODE]))

if not os.path.isdir('%s/audio/' % FREEVO_CACHEDIR):
    import stat
    os.mkdir('%s/audio/' % FREEVO_CACHEDIR,
             stat.S_IMODE(os.stat(FREEVO_CACHEDIR)[stat.ST_MODE]))

NEW_SKIN = (OSD_SKIN == 'skins/dischi1/skin_dischi1.py')
