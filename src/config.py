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
# Revision 1.70  2003/11/22 20:35:10  dischi
# config changes for the use new vfs
#
# Revision 1.69  2003/11/21 17:55:09  dischi
# new SUFFIX_VIDEO_FILES layout
#
# Revision 1.68  2003/11/09 22:34:17  rshortt
# We need True/False defs a bit higher up.
#
# Revision 1.67  2003/11/09 17:08:24  dischi
# add /usr/local/etc/freevo as search path
#
# Revision 1.66  2003/11/01 16:28:43  dischi
# encode program names to avoid a crash in the web guide
#
# Revision 1.65  2003/10/24 03:28:08  krister
# Fixed a bug where the ROM drives autodetection would crash if ROM_DRIVES=None
#
# Revision 1.64  2003/10/22 19:08:33  dischi
# make it possible to deactivate rom drive support
#
# Revision 1.63  2003/10/19 11:17:37  dischi
# move gettext into config so that everything has _()
#
# Revision 1.62  2003/10/18 21:37:53  rshortt
# Fixing some logic for HELPERS because recordserver and webserver are also
# helpers.
#
# Also adding a VideoGroup class (WIP) that will help in centralizing Freevo's
# channel list and add support for multiple v4l devices.  I will talk more
# about this after the 1.4 release.
#
# Revision 1.61  2003/10/18 10:44:54  dischi
# bugfix to detect if we are (web|record)server or not
#
# Revision 1.60  2003/10/08 03:29:21  outlyer
# Just move all FutureWarnings to config. This removes all the silly hex
# constant warnings.
#
# Revision 1.59  2003/10/04 17:55:14  dischi
# small fixes
#
# Revision 1.58  2003/09/26 10:02:26  dischi
# no auto debug to file to keep Aubin from changing all debugs to 2
#
# Revision 1.57  2003/09/23 19:41:31  dischi
# add more help
#
# Revision 1.56  2003/09/22 20:17:04  dischi
# do not use dxr3 output for helpers
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
import traceback
import __builtin__
import version

if float(sys.version[0:3]) >= 2.3:
    import warnings
    warnings.simplefilter("ignore", category=FutureWarning)

VERSION = version.__version__

# For Internationalization purpose
# an exception is raised with Python 2.1 if LANG is unavailable.
import gettext
try:
    gettext.install('freevo', os.environ['FREEVO_LOCALE'])
except: # unavailable, define '_' for all modules
    import __builtin__
    __builtin__.__dict__['_']= lambda m: m


# add True and False to __builtin__ for older python versions
if float(sys.version[0:3]) < 2.3:
    __builtin__.__dict__['True']  = 1
    __builtin__.__dict__['False'] = 0

# temp solution until this is fixed to True and False
# in all freevo modules
__builtin__.__dict__['TRUE']  = 1
__builtin__.__dict__['FALSE'] = 0


class Logger:
    """
    Class to create a logger object which will send messages to stdout
    and log them into a logfile
    """
    def __init__(self, logtype='(unknown)'):
        self.lineno = 1
        self.logtype = logtype
        appname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        logfile = '%s/%s-%s.log' % (LOGDIR, appname, os.getuid())
        self.logfile = logfile
        try:
            self.fp = open(logfile, 'a')
        except IOError:
            print 'Could not open logfile: %s' % logfile
            self.fp = open('/dev/null','a')
        self.softspace = 0
        
    def write(self, msg):
        global DEBUG_STDOUT
        if DEBUG_STDOUT:
            sys.__stdout__.write(msg)
        self.fp.write(msg)
        self.fp.flush()
        return

    def log(self, msg):
        self.fp.write(msg)
        self.fp.flush()
        return

    def flush():
        pass

    def close():
        pass
    

class VideoGroup:
    """
    vdev:        The video device, such as /dev/video.
    adev:        The audio device, such as /dev/dsp.
    input_type:  tuner, composite, svideo, webcam
    tuner_type:  internal (on a v4l device), or external (cable or sat box)
    tuner_norm:  NTSC, PAL, SECAM
    tuner_chanlist:  us-cable, 
    tuner_chan:  If using input_type=tuner and tuner_type=external set this to
                 what channel it needs to be to get the signal, usually 3 or 4.
    recordable:  True or False.  Can you record from this VideoGroup.
    desc:        A nice description for this VideoGroup.
    """

    def __init__(self, vdev='/dev/video', adev='/dev/dsp', input_type='tuner',
                 tuner_norm='NTSC', tuner_chanlist='us-cable', 
                 tuner_type='internal', tuner_chan=None, external_tuner=None,
                 et_conf=None, et_device=None, et_remote=None,
                 recordable=True, desc='Freevo default VideoGroup'):

        # XXX: Put checks in here for supplied values.
        self.vdev = vdev
        self.adev = adev
        self.input_type = input_type
        self.tuner_type = tuner_type
        self.tuner_norm = tuner_norm
        self.tuner_chanlist = tuner_chanlist
        self.tuner_chan = tuner_chan
        self.external_tuner = external_tuner
        self.et_conf = et_conf
        self.et_device = et_device
        self.et_remote = et_remote
        self.recordable = recordable
        self.desc = desc
        self.in_use = FALSE
        self.tuner = None


def print_config_changes(conf_version, file_version, changelist):
    """
    print changes made between version on the screen
    """
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
            

def print_help():
    """
    print some help about config files
    """
    print 'Freevo is not completely configured to start'
    print 'The configuration is based on three files. This may sound oversized, but this'
    print 'way it\'s easier to configure.'
    print
    print 'First Freevo loads a file called \'freevo.conf\'. This file will be generated by'
    print 'calling \'freevo setup\'. Use \'freevo setup --help\' to get information'
    print 'about the parameter. Based on the informations in that file, Freevo will guess'
    print 'some settings for your system. This takes place in a file called '
    print '\'freevo_config.py\'. Since this file may change from time to time, you should'
    print 'not edit this file. After freevo_config.py is loaded, Freevo will look for a file'
    print 'called \'local_conf.py\'. You can overwrite the variables from \'freevo_config.py\''
    print 'in here. There is an example for \'local_conf.py\' called \'local_conf.py.example\''
    print 'in the Freevo distribution.'
    print
    print 'If you need more help, use the internal webserver to get more informations'
    print 'how to setup Freevo. To do this, you need to set'
    print 'WWW_USERS = { \'username\' : \'password\' }'
    print 'in your local_conf.py and then you can access the doc at '
    print 'http://localhost:8080/help/'
    print
    print 'The location of freevo_config.py is %s' % os.environ['FREEVO_CONFIG']
    print 'Freevo searches for freevo.conf and local_conf.py in the following locations:'
    for dirname in cfgfilepath:
        print '  '+dirname
    print



#
# get information about what is started here:
# helper = some script from src/helpers or is webserver or recordserver
#
HELPER          = 0
IS_RECORDSERVER = 0
IS_WEBSERVER    = 0

if sys.argv[0].find('main.py') == -1:
    HELPER=1
if sys.argv[0].find('recordserver.py') != -1:
    IS_RECORDSERVER = 1
elif sys.argv[0].find('webserver.py') != -1:
    IS_WEBSERVER = 1

#
# Send debug to stdout as well as to the logfile?
#
DEBUG_STDOUT = 1

#
# Debug all modules?
# 0 = Debug output off
# 1 = Some debug output
# A higher number will generate more detailed output from some modules.
#
DEBUG = 0

#
# find the log directory
#
if os.path.isdir('/var/log/freevo'):
    LOGDIR = '/var/log/freevo'
else:
    LOGDIR = '/tmp/freevo'
    if not os.path.isdir(LOGDIR):
        os.makedirs(LOGDIR)


#
# Redirect stdout and stderr to stdout and /tmp/freevo.log
#
if not HELPER:
    sys.stdout = Logger(sys.argv[0] + ':stdin')
    sys.stderr = Logger(sys.argv[0] + ':stderr')
    ts = time.asctime(time.localtime(time.time()))
    sys.stdout.log('-' * 79 + '\n')
    sys.stdout.log('Freevo start at %s\n' % ts)
    sys.stdout.log('-' * 79 + '\n')

def _debug_function_(s, level=1):
    if DEBUG < level:
        return
    # add the current trace to the string
    where =  traceback.extract_stack(limit = 2)[0]
    s = '%s (%s): %s' % (where[0][where[0].rfind('/')+1:], where[1], s)
    # print debug message
    print s

            
__builtin__.__dict__['_debug_']= _debug_function_


#
# Config file handling
#
cfgfilepath = [ '.', os.path.expanduser('~/.freevo'), '/etc/freevo',
                '/usr/local/etc/freevo' ]


#
# Default settings
# These will be overwritten by the contents of 'freevo.conf'
#
CONF = setup_freevo.Struct()
CONF.geometry = '800x600'
CONF.width, CONF.height = 800, 600
CONF.display = 'x11'
CONF.tv = 'ntsc'
CONF.chanlist = 'us-cable'
CONF.version = 0

#
# Read the environment set by the start script
#
SHARE_DIR = os.environ['FREEVO_SHARE']
CONTRIB_DIR = os.environ['FREEVO_CONTRIB']
SKIN_DIR  = os.path.join(SHARE_DIR, 'skins')
ICON_DIR  = os.path.join(SHARE_DIR, 'icons')
IMAGE_DIR = os.path.join(SHARE_DIR, 'images')
FONT_DIR  = os.path.join(SHARE_DIR, 'fonts')

RUNAPP = os.environ['RUNAPP']


#
# Check that freevo_config.py is not found in the config file dirs
#
for dirname in cfgfilepath[1:]:
    freevoconf = dirname + '/freevo_config.py'
    if os.path.isfile(freevoconf):
        print (('\nERROR: freevo_config.py found in %s, please remove it ' +
                'and use local_conf.py instead!') % freevoconf)
        sys.exit(1)
        
#
# Search for freevo.conf:
#
for dirname in cfgfilepath:
    freevoconf = dirname + '/freevo.conf'
    if os.path.isfile(freevoconf):
        _debug_('Loading configure settings: %s' % freevoconf)

        c = open(freevoconf)
        for line in c.readlines():
            vals = line.strip().split()
            _debug_('Cfg file data: "%s"' % line.strip(), 2)
            try:
                name, val = vals[0], vals[2]
            except:
                print 'Error parsing config file data "%s"' % line.strip()
                continue
            CONF.__dict__[name] = val

        c.close()
        w, h = CONF.geometry.split('x')
        CONF.width, CONF.height = int(w), int(h)
        break
else:
    print
    print 'Error: freevo.conf not found'
    print
    print_help()
    sys.exit(1)


#
# search missing programs at runtime
#
for program, valname, needed in setup_freevo.EXTERNAL_PROGRAMS:
    if not hasattr(CONF, valname) or not getattr(CONF, valname):
        setup_freevo.check_program(CONF, program, valname, needed, verbose=0)
    if not hasattr(CONF, valname) or not getattr(CONF, valname):
        setattr(CONF, valname, '')

#
# fall back to x11 if display is mga or fb and DISPLAY ist set
# or switch to fbdev if we have no DISPLAY and x11 or dga is used
#
if not HELPER:
    if os.environ.has_key('DISPLAY') and os.environ['DISPLAY']:
        if CONF.display in ('mga', 'fbdev'):
            print
            print 'Warning: display is set to %s, but the environment ' % CONF.display + \
                  'has DISPLAY=%s.' % os.environ['DISPLAY']
            print 'this could mess up your X display, setting display to x11.'
            print 'If you really want to do this, start \'DISPLAY="" freevo\''
            print
            CONF.display='x11'
    else:
        if CONF.display == 'x11':
            print
            print 'Warning: display is set to %s, but the environment ' % CONF.display + \
                  'has no DISPLAY set. Setting display to fbdev.'
            print
            CONF.display='fbdev'

elif CONF.display == 'dxr3':
    # don't use dxr3 for helpers. They don't use the osd anyway, but
    # it may mess up the dxr3 output (don't ask why).
    CONF.display='fbdev'
    
#
# Load freevo_config.py:
#
if os.path.isfile(os.environ['FREEVO_CONFIG']):
    _debug_('Loading cfg: %s' % os.environ['FREEVO_CONFIG'])
    execfile(os.environ['FREEVO_CONFIG'], globals(), locals())
    
else:
    print
    print "Error: %s: no such file" % os.environ['FREEVO_CONFIG']
    print
    sys.exit(1)


#
# Search for local_conf.py:
#
for dirname in cfgfilepath:
    overridefile = dirname + '/local_conf.py'
    if os.path.isfile(overridefile):
        if DEBUG: print 'Loading cfg overrides: %s' % overridefile
        execfile(overridefile, globals(), locals())

        try:
            CONFIG_VERSION
        except NameError:
            print
            print 'Error: your local_config.py file has no version information'
            print 'Please check freevo_config.py for changes and set CONFIG_VERSION'
            print 'in %s to %s' % (overridefile, LOCAL_CONF_VERSION)
            print
            sys.exit(1)

        if int(str(CONFIG_VERSION).split('.')[0]) != \
           int(str(LOCAL_CONF_VERSION).split('.')[0]):
            print
            print 'Error: The version information in freevo_config.py doesn\'t'
            print 'match the version in your local_config.py.'
            print 'Please check freevo_config.py for changes and set CONFIG_VERSION'
            print 'in %s to %s' % (overridefile, LOCAL_CONF_VERSION)
            print_config_changes(LOCAL_CONF_VERSION, CONFIG_VERSION,
                                 LOCAL_CONF_CHANGES)
            sys.exit(1)

        if int(str(CONFIG_VERSION).split('.')[1]) != \
           int(str(LOCAL_CONF_VERSION).split('.')[1]):
            print
            print 'Warning: freevo_config.py was changed, please check local_config.py'
            print_config_changes(LOCAL_CONF_VERSION, CONFIG_VERSION, 
                                 LOCAL_CONF_CHANGES)
        break

else:
    print
    print 'Error: local_conf.py not found'
    print
    print_help()
    print
    print 'Since it\'s highly unlikly you want to start Freevo without further'
    print 'configuration, Freevo will exit now.'
    sys.exit(0)


if not HELPER:
    _debug_('Logging to %s' % sys.stdout.logfile)
   
#
# force fullscreen when freevo is it's own windowmanager
#
if len(sys.argv) >= 2 and sys.argv[1] == '--force-fs':
    START_FULLSCREEN_X = 1


#
# set default font
#
OSD_DEFAULT_FONTNAME = os.path.join(FONT_DIR, OSD_DEFAULT_FONTNAME)

#
# set list of video files to []
# (fill be filled from the plugins) 
#
SUFFIX_VIDEO_FILES = []

#
# set data dirs
#
if not DIR_MOVIES:
    ONLY_SCAN_DATADIR = True
    DIR_MOVIES = [ ('Root', '/') ]
    if os.environ.has_key('HOME') and os.environ['HOME']:
        DIR_MOVIES = [ ('Home', os.environ['HOME']) ] + DIR_MOVIES
    if not HELPER and plugin.is_active('mediamenu', 'video'):
            print
            print 'Error: DIR_MOVIES not set, set it to Home directory'
            print
            
if not DIR_AUDIO:
    DIR_AUDIO = [ ('Root', '/') ]
    if os.environ.has_key('HOME') and os.environ['HOME']:
        DIR_AUDIO = [ ('Home', os.environ['HOME']) ] + DIR_AUDIO
    if not HELPER and plugin.is_active('mediamenu', 'audio'):
        print
        print 'Error: DIR_AUDIO not set, set it to Home directory'
        print

if not DIR_IMAGES:
    DIR_IMAGES = [ ('Root', '/') ]
    if os.environ.has_key('HOME') and os.environ['HOME']:
        DIR_IMAGES = [ ('Home', os.environ['HOME']) ] + DIR_IMAGES
    if not HELPER and plugin.is_active('mediamenu', ('image', True)):
        print 
        print 'Error: DIR_IMAGES not set, set it to Home directory'
        print
        
if not DIR_GAMES:
    DIR_GAMES = [ ('Root', '/') ]
    if os.environ.has_key('HOME') and os.environ['HOME']:
        DIR_GAMES = [ ('Home', os.environ['HOME']) ] + DIR_GAMES
    if not HELPER and plugin.is_active('mediamenu', 'games'):
        print
        print 'Error: DIR_GAMES not set, set it to Home directory'
        print

if not DIR_RECORD:
    DIR_RECORD = DIR_MOVIES[0][1]
    if not HELPER and plugin.is_active('tv'):
        print
        print 'Error: DIR_RECORD not set'
        print 'Please set DIR_RECORD to the directory, where recordings should be stored or'
        print 'remove the tv plugin. Autoset variable to %s.' % DIR_RECORD
        print
        
if not TV_SHOW_DATA_DIR and not HELPER:
    print 'Error: TV_SHOW_DATA_DIR not found'
    
#
# Autodetect the CD/DVD drives in the system if not given in local_conf.py
#
# ROM_DRIVES == None means autodetect
# ROM_DRIVES == [] means ignore ROM drives
#
if ROM_DRIVES == None:
    ROM_DRIVES = []
    if os.path.isfile('/etc/fstab'):        
        re_cd        = re.compile( '^(/dev/cdrom[0-9]*|/dev/[am]?cd[0-9]+[a-z]?)[ \t]+([^ \t]+)[ \t]+', re.I )
        re_cdrec     = re.compile( '^(/dev/cdrecorder[0-9]*)[ \t]+([^ \t]+)[ \t]+', re.I )
        re_dvd       = re.compile( '^(/dev/dvd[0-9]*)[ \t]+([^ \t]+)[ \t]+', re.I )
        re_iso       = re.compile( '^([^ \t]+)[ \t]+([^ \t]+)[ \t]+(iso|cd)9660', re.I )
        re_automount = re.compile( '^none[ \t]+([^ \t]+) supermount dev=([^,]+)', re.I )
        re_bymountcd = re.compile( '^(/dev/[^ \t]+)[ \t]+([^ ]*cdrom[0-9]*)[ \t]+', re.I )
        re_bymountdvd= re.compile( '^(/dev/[^ \t]+)[ \t]+([^ ]*dvd[0-9]*)[ \t]+', re.I )
        fd_fstab = open('/etc/fstab')
        for line in fd_fstab:
            # Match on the devices /dev/cdrom, /dev/dvd, and fstype iso9660
            match_cd        = re_cd.match(line)
            match_cdrec     = re_cdrec.match(line)
            match_dvd       = re_dvd.match(line)
            match_iso       = re_iso.match(line)
            match_automount = re_automount.match(line)
            match_bymountcd = re_bymountcd.match(line)
            match_bymountdvd= re_bymountdvd.match(line)
            mntdir = devname = ''
            if match_cd or match_bymountcd:
                m = match_cd or match_bymountcd
                mntdir = m.group(2)
                devname = m.group(1)
                dispname = 'CD-%s' % (len(ROM_DRIVES)+1)
            elif match_cdrec: 
                mntdir = match_cdrec.group(2)
                devname = match_cdrec.group(1)
                dispname = 'CDREC-%s' % (len(ROM_DRIVES)+1)
            elif match_dvd or match_bymountdvd:
                m = match_dvd or match_bymountdvd
                mntdir = m.group(2)
                devname = m.group(1)
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

            if os.uname()[0] == 'FreeBSD':
                # FreeBSD-STABLE mount point is often device name + "c",
                # strip that off
                if devname and devname[-1] == 'c':
                    devname = devname[:-1]
                # Use native FreeBSD device names
                dispname = devname[5:]
 
            # Weed out duplicates
            for rd_mntdir, rd_devname, rd_dispname in ROM_DRIVES:
                if os.path.realpath(rd_devname) == os.path.realpath(devname):
                    if not HELPER:
                        print (('ROM_DRIVES: Auto-detected that %s is the same ' +
                                'device as %s, skipping') % (devname, rd_devname))
                    break
            else:
                # This was not a duplicate of another device
                if mntdir and devname and dispname:
                    ROM_DRIVES += [ (mntdir, devname, dispname) ]
                    if not HELPER:
                        print 'ROM_DRIVES: Auto-detected and added "%s"' % (ROM_DRIVES[-1], )
        fd_fstab.close()
                


#
# List of objects representing removable media, e.g. CD-ROMs,
# DVDs, etc.
#
REMOVABLE_MEDIA = []


#
# Auto detect xmltv channel list
#

def sortchannels(list, key):
    # This should be more generic, but I couldn't get it
    # to sort properly without specifying the nested array
    # index for the tunerid and forcing 'int'
    for l in list:
        if len(l[key]) == 1:
            l[key].append(('0',))
    nlist = map(lambda x, key=key: (int(x[key][1][0]), x), list)
    nlist.sort()
    return map(lambda (key, x): x, nlist)


def detect_channels():
    """
    Auto detect a list of possible channels in the xmltv file
    """
    import codecs
    import cPickle, pickle

    file = XMLTV_FILE
    path = FREEVO_CACHEDIR
    pfile = 'xmltv_channels.pickle'

    pname = os.path.join(path,pfile)

    if not os.path.isfile(file):
        if not HELPER:
            print
            print 'Error: can\'t find %s' % file
            print 'Use xmltv to create this file or when you don\'t want to use the tv'
            print 'module at all, add TV_CHANNELS = [] and plugin.remove(\'tv\') to your'
            print 'local_conf.py. TVguide is deactivated now.'
            print
        return []
        
    elif os.path.isfile(pname) and (os.path.getmtime(pname) >
                                    os.path.getmtime(file)):
        try:
            f = open(pname, 'r')
            try:
                data = cPickle.load(f)
            except:
                data = pickle.load(f)
            f.close()
            return data
        except:
            print 'Error: unable to read cachefile %s' % pname
            return []

    else:
        from tv import xmltv
        input = open(file, 'r')
        tmp   = open('/tmp/xmltv_parser', 'w')
        while(1):
            line =input.readline()
            if not line:
                break
            if line.find('<programme') > 0:
                tmp.write('</tv>\n')
                break
            tmp.write(line)

        input.close()
        tmp.close()

        tmp   = open('/tmp/xmltv_parser', 'r')
        xmltv_channels = xmltv.read_channels(tmp)
        tmp.close()

        xmltv_channels = sortchannels(xmltv_channels,'display-name')
        chanlist = []

        for a in xmltv_channels:
            if (a['display-name'][1][0][0].isdigit()):
                display_name = a['display-name'][0][0].encode(LOCALE, 'ignore')
                tunerid = a['display-name'][1][0].encode(LOCALE, 'ignore')
            else:
                display_name = a['display-name'][1][0].encode(LOCALE, 'ignore')
                tunerid = a['display-name'][0][0].encode(LOCALE, 'ignore')
            id = a['id'].encode(LOCALE, 'ignore')

            chanlist += [(id,display_name,int(tunerid))]

        try:
            if os.path.isfile(pname):
                os.unlink(pname)
            f = open(pname, 'w')
            cPickle.dump(chanlist, f, 1)
            f.close()
        except IOError:
            print 'Error: unable to save to cachefile %s' % pname

        for c in chanlist:
            if c[2] == 0:
                print_list = 1
                if not HELPER:
                    print 
                    print 'Error: XMLTV auto detection failed'
                    print 'Some channels in the channel list have no station id. Please add'
                    print 'it by putting the list in your local_conf.py. Start '
                    print '\'freevo tv_grab --help\' for more informations'
                    print
                break
        else:
            print 'XMTV: Auto-detected channel list'

        return chanlist
         

if TV_CHANNELS == None and plugin.is_active('tv'):
    # auto detect them
    TV_CHANNELS = detect_channels()

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

#
# delete LD_PRELOAD for all helpers, main.py does it after
# starting the display
#
if HELPER:
    os.environ['LD_PRELOAD'] = ''
    
