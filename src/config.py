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
# Revision 1.56  2003/09/22 20:17:04  dischi
# do not use dxr3 output for helpers
#
# Revision 1.55  2003/09/20 15:21:08  dischi
# bugfix
#
# Revision 1.54  2003/09/20 15:08:25  dischi
# some adjustments to the missing testfiles
#
# Revision 1.53  2003/09/20 14:10:17  dischi
# move version info into a python file
#
# Revision 1.52  2003/09/20 12:58:11  dischi
# add VERSION
#
# Revision 1.51  2003/09/19 18:57:43  dischi
# fixed TRUE/FALSE problems
#
# Revision 1.50  2003/09/14 20:47:48  outlyer
# * TRUE/FALSE wasn't working in Python 2.3...
# * Wrapped the tagging function in a try: except because it failed on a data
#    track and Freevo needed to be restarted to rip another CD.
#
# Revision 1.49  2003/09/14 20:08:11  dischi
# o add TRUE and FALSE to the buildin objects for Python < 2.3
# o add a _debug_ function to buildin. All files can use _debug_ to write
#   debug messages. Even with DEBUG=0, debugs will be made to the logfile
#   (but not stdout)
#
# Revision 1.48  2003/09/11 15:50:25  dischi
# delete LD_PRELOADS after startup
#
# Revision 1.47  2003/09/08 19:43:14  dischi
# added some internal help messages and a tv grab helper
#
# Revision 1.46  2003/09/05 20:09:30  dischi
# add function to auto detect channels and some help messages
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

VERSION = version.__version__

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
    

def error(message, *desc):
    """
    Small helper function to print out errors so that they fit on a
    normal terminal screen (80 chars)
    """
    print
    print 'ERROR: %s' % message
    message = ''
    for line in desc:
        message += line
    for line in message.split('\n'):
        while(line):
            if len(line) > 80:
                print line[:line[:80].rfind(' ')]
                line = line[line[:80].rfind(' ')+1:]
            else:
                print line
                line = ''
    print

    
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
            

#
# get information about what is started here:
# helper = some script from src/helpers or is webserver or recordserver
#
HELPER          = 0
IS_RECORDSERVER = 0
IS_WEBSERVER    = 0

if sys.argv[0].find('main.py') == -1:
    HELPER=1
elif sys.argv[0].find('recordserver.py') == -1:
    IS_RECORDSERVER = 1
elif sys.argv[0].find('webserver.py') == -1:
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

# add True and False to __builtin__ for older python versions
if float(sys.version[0:3]) < 2.3:
    __builtin__.__dict__['True']  = 1
    __builtin__.__dict__['False'] = 0

# temp solution until this is fixed to True and False
# in all freevo modules
__builtin__.__dict__['TRUE']  = 1
__builtin__.__dict__['FALSE'] = 0

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
    if DEBUG > 0:
        # add the current trace to the string
        where =  traceback.extract_stack(limit = 2)[0]
        s = '%s (%s): %s' % (where[0][where[0].rfind('/')+1:], where[1], s)
    if DEBUG >= level:
        print s
    elif DEBUG == 0 and level == 1:
        if isinstance(sys.stderr, Logger):
            sys.stderr.log(s+'\n')
            
__builtin__.__dict__['_debug_']= _debug_function_


#
# Config file handling
#
cfgfilepath = [ '.', os.path.expanduser('~/.freevo'), '/etc/freevo' ]


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
for dirname in [os.path.expanduser('~/.freevo'), '/etc/freevo']:
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
        if DEBUG:
            print 'Loading configure settings: %s' % freevoconf

        c = open(freevoconf)
        for line in c.readlines():
            vals = line.strip().split()
            if DEBUG: print 'Cfg file data: "%s"' % line.strip()
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
    error('Error', 'freevo.conf not found', 'Freevo needs a basic configuration to guess ',
          'the best settings for your system. Please run \'freevo setup\' first')
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
            print 'Warning: display is set to %s, but the environment ' % CONF.display + \
                  'has DISPLAY=%s.' % os.environ['DISPLAY']
            print 'this could mess up your X display, setting display to x11.'
            print 'If you really want to do this, start \'DISPLAY="" freevo\''
            CONF.display='x11'
    else:
        if CONF.display == 'x11':
            print 'Warning: display is set to %s, but the environment ' % CONF.display + \
                  'has no DISPLAY set.'
            print 'Setting display to fbdev.'
            CONF.display='fbdev'
elif CONF.display == 'dxr3':
    # don't use dxr3 for helpers. They don't use the osd anyway, but
    # it may mess up the dxr3 output (don't ask why).
    CONF.display='fbdev'
    
#
# Load freevo_config.py:
#
if os.path.isfile(os.environ['FREEVO_CONFIG']):
    if DEBUG:
        print 'Loading cfg: %s' % os.environ['FREEVO_CONFIG']
    execfile(os.environ['FREEVO_CONFIG'], globals(), locals())
    
else:
    print "\nERROR: %s: no such file" % os.environ['FREEVO_CONFIG']
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
    error('local_conf.py not found', 'Freevo can be configured with a file called ',
          'local_conf.py. It\'s possible to override variables from freevo_config.py ',
          'in this file. Freevo searched for local_conf.py in the following locations:')
    for dirname in cfgfilepath:
        print dirname + '/local_conf.py'
    print
    print 'the location of freevo_config.py is %s' % os.environ['FREEVO_CONFIG']
    print


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
# set data dirs
#
if not DIR_MOVIES:
    ONLY_SCAN_DATADIR = True
    DIR_MOVIES = [ ('Root', '/') ]
    if os.environ.has_key('HOME') and os.environ['HOME']:
        DIR_MOVIES = [ ('Home', os.environ['HOME']) ] + DIR_MOVIES
    if not HELPER and plugin.is_active('mediamenu', 'video'):
            error('DIR_MOVIES not set', 'set it to default Home directory')

if not DIR_AUDIO:
    DIR_AUDIO = [ ('Root', '/') ]
    if os.environ.has_key('HOME') and os.environ['HOME']:
        DIR_AUDIO = [ ('Home', os.environ['HOME']) ] + DIR_AUDIO
    if not HELPER and plugin.is_active('mediamenu', 'audio'):
        error('DIR_AUDIO not set', 'set it to default Home directory')

if not DIR_IMAGES:
    DIR_IMAGES = [ ('Root', '/') ]
    if os.environ.has_key('HOME') and os.environ['HOME']:
        DIR_IMAGES = [ ('Home', os.environ['HOME']) ] + DIR_IMAGES
    if not HELPER and plugin.is_active('mediamenu', ('image', True)):
        error('DIR_IMAGES not set', 'set it to default Home directory')

if not DIR_GAMES:
    DIR_GAMES = [ ('Root', '/') ]
    if os.environ.has_key('HOME') and os.environ['HOME']:
        DIR_GAMES = [ ('Home', os.environ['HOME']) ] + DIR_GAMES
    if not HELPER and plugin.is_active('mediamenu', 'games'):
        error('DIR_GAMES not set', 'set it to default Home directory')

if not DIR_RECORD:
    DIR_RECORD = '/tmp/'
    if not HELPER and plugin.is_active('tv'):
        error('DIR_RECORD not set', 'Please set DIR_RECORD to the directory ',
              'where recordings should be stored or remove the tv plugin. ',
              'Autoset variable to /tmp.')

if not TV_SHOW_DATA_DIR and not HELPER:
    error('TV_SHOW_DATA_DIR not found')
    
if not COVER_DIR and not HELPER:
    error('COVER_DIR not found')
    
if not MOVIE_DATA_DIR and not HELPER:
    error('MOVIE_DATA_DIR not found')
    
#
# Autodetect the CD/DVD drives in the system if not given in local_conf.py
#
if not ROM_DRIVES:
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
            error('can\'t find %s' % file,
                  'Use xmltv to create this file or when you don\'t want ',
                  'to use the tv module at all, add TV_CHANNELS = [] and ',
                  'plugin.remove(\'tv\') to your local_conf.py\n',
                  'TVguide is deactivated now.')
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
            error('unable to read cachefile %s' % pname)
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
                display_name = a['display-name'][0][0]
                tunerid = a['display-name'][1][0]
            else:
                display_name = a['display-name'][1][0]
                tunerid = a['display-name'][0][0]
            id = a['id']

            chanlist += [(id,display_name,int(tunerid))]

        try:
            if os.path.isfile(pname):
                os.unlink(pname)
            f = open(pname, 'w')
            cPickle.dump(chanlist, f, 1)
            f.close()
        except IOError:
            error('unable to save to cachefile %s' % pname)

        for c in chanlist:
            if c[2] == 0:
                print_list = 1
                if not HELPER:
                    error('XMLTV auto detection failed', 'Some channels in the channel ',
                          'list have no station id. Please add it by putting the list '
                          'in your local_conf.py. Start \'freevo tv_grab --help\' for ',
                          'more informations')
                break
        else:
            print 'XMTV: Auto-detected channel list'

        return chanlist
         

if TV_CHANNELS == None:
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
    
