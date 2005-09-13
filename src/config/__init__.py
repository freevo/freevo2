# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# config.py - Handle the configuration files
# -----------------------------------------------------------------------------
# $Id$
#
# Try to find the freevo_config.py config file in the following places:
# 1) ./freevo_config.py               Defaults from the freevo dist
# 2) ~/.freevo/freevo_config.py       The user's private config
# 3) /etc/freevo/freevo_config.py     Systemwide config
# 
# Customize freevo_config.py from the freevo dist and copy it to one
# of the other places where it will not get overwritten by new
# checkouts/installs of freevo.
# 
# The format of freevo_config.py might change, in that case you'll
# have to update your customized version.
#
# Note: this file needs a huge cleanup!!!
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Krister Lagerstrom <krister-freevo@kmlager.com>
#
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
# -----------------------------------------------------------------------------

# python imports
import sys
import os
import re
import pwd
import __builtin__
import gettext
import logging
import copy

# freevo imports
import sysconfig
import version

# config imports
import setup

# input inputs variables for the input system
# and event.py (which has no more deps)
import input

import plugin_loader as plugin

# import event names (no deps)
from event import *

# get logging object
log = logging.getLogger('config')

# For Internationalization purpose
try:
    gettext.install('freevo', os.environ['FREEVO_LOCALE'], 1)
except: # unavailable, define '_' for all modules
    __builtin__.__dict__['_']= lambda m: m

# set global app name
app = os.path.splitext(os.path.basename(sys.argv[0]))[0]
__builtin__.__dict__['__freevo_app__'] = app


# XXX ************************************************************

# XXX The following code will be removed before the next release
# XXX Please do NOT use this varaibles anymore and fix code were it
# XXX is used.

# use sysconfig code
FREEVO_CACHEDIR = sysconfig.CONF.cachedir

# XXX ************************************************************

#
# Default settings
# These will be overwritten by the contents of 'freevo.conf'
#
CONF = sysconfig.CONF
if not hasattr(CONF, 'geometry'):
    CONF.geometry = '800x600'
w, h = CONF.geometry.split('x')
CONF.width, CONF.height = int(w), int(h)

if not hasattr(CONF, 'display'):
    CONF.display = 'x11'
if not hasattr(CONF, 'tv'):
    CONF.tv = 'ntsc'
if not hasattr(CONF, 'chanlist'):
    CONF.chanlist = 'us-cable'
if not hasattr(CONF, 'version'):
    CONF.version = 0


#
# TV card settup
#

class TVSettings(dict):
    def __setitem__(self, key, val):
        # FIXME: key has to end with number or we crash here
        number = key[-1]
        dict.__setitem__(self, key, val(number))
    
TV_CARDS = TVSettings()

# 
# Variable initializations to make configuring some TV settings easier
#

IVTV0_CODEC = IVTV1_CODEC = IVTV2_CODEC = IVTV3_CODEC = IVTV4_CODEC = \
IVTV5_CODEC = IVTV6_CODEC = IVTV7_CODEC = IVTV8_CODEC = IVTV9_CODEC = {}

#
# Read the environment set by the start script
#
SHARE_DIR   = os.path.abspath(os.environ['FREEVO_SHARE'])
DOC_DIR     = os.path.abspath(os.environ['FREEVO_DOC'])

SKIN_DIR  = os.path.join(SHARE_DIR, 'skins')
ICON_DIR  = os.path.join(SHARE_DIR, 'icons')
IMAGE_DIR = os.path.join(SHARE_DIR, 'images')
FONT_DIR  = os.path.join(SHARE_DIR, 'fonts')


#
# search missing programs at runtime
#
for program, valname, needed in setup.EXTERNAL_PROGRAMS:
    if not hasattr(CONF, valname) or not getattr(CONF, valname):
        setup.check_program(CONF, program, valname, needed, verbose=0)
    if not hasattr(CONF, valname) or not getattr(CONF, valname):
        setattr(CONF, valname, '')

#
# fall back to x11 if display is mga or fb and DISPLAY ist set
# or switch to fbdev if we have no DISPLAY and x11 or dga is used
#
if __freevo_app__ == 'main':
    if os.environ.has_key('DISPLAY') and os.environ['DISPLAY']:
        if CONF.display in ('mga', 'fbdev'):
            print
            print 'Warning: display is set to %s, but the environment ' % \
                  CONF.display + \
                  'has DISPLAY=%s.' % os.environ['DISPLAY']
            print 'this could mess up your X display, setting display to x11.'
            print 'If you really want to do this, start \'DISPLAY="" freevo\''
            print
            CONF.display='x11'
    else:
        if CONF.display == 'x11':
            print
            print 'Warning: display is set to %s, but the environment ' % \
                  CONF.display + \
                  'has no DISPLAY set. Setting display to fbdev.'
            print
            CONF.display='fbdev'

elif CONF.display == 'dxr3':
    # don't use dxr3 for helpers. They don't use the osd anyway, but
    # it may mess up the dxr3 output (don't ask why).
    CONF.display='fbdev'


#
# load the config file
#
execfile(os.path.join(os.path.dirname(__file__), 'configfile.py'))

#
# load additional runtime settings from the runtime configuration
#
from runtimexml import RuntimeXML
rtXML = RuntimeXML( globals() )

# set the umask
os.umask(UMASK)

#
# force fullscreen when freevo is it's own windowmanager
#
if len(sys.argv) >= 2 and sys.argv[1] == '--force-fs':
    START_FULLSCREEN_X = 1


#
# set default font
#
GUI_FONT_DEFAULT_NAME = os.path.join(FONT_DIR, GUI_FONT_DEFAULT_NAME)

#
# set list of video files to []
# (fill be filled from the plugins) 
#
VIDEO_SUFFIX = []

for v in copy.copy(globals()):
    if v.startswith('VIDEO_') and v.endswith('_SUFFIX') and v[6:-7]:
        if plugin.is_active('video.' + v[6:-7].lower()):
            for s in globals()[v]:
                if not s in VIDEO_SUFFIX:
                    VIDEO_SUFFIX.append(s)

#
# set data dirs
# if not set, set it to root and home dir
# if set, make all path names absolute
#
for type in ('video', 'audio', 'image', 'games'):
    n = '%s_ITEMS' % type.upper()
    x = eval(n)
    if x == None:
        x = []
        if os.environ.has_key('HOME') and os.environ['HOME']:
            x.append(('Home', os.environ['HOME']))
        x.append(('Root', '/'))
        exec('%s = x' % n)
        if __freevo_app__ == 'main' and plugin.is_active('mediamenu', type):
            log.warning('%s not set, set it to Home directory' % n)

    elif type == 'games':
        abs = []
        for d in x:
            pos = d[1].find(':')
            if pos == -1:
                abs.append((d[0], os.path.abspath(d[1]), d[2]))
            else:
                if pos > d[1].find('/'):                        
                    abs.append((d[0], os.path.abspath(d[1]), d[2]))
                else:
                    abs.append((d[0], d[1][0:pos+1] + \
                                os.path.abspath(d[1][pos+1:]), d[2]))
        exec ('%s = abs' % n)
    else:
        # The algorithm doesn't work for GAMES_ITEMS, so we leave it out
        abs = []
        for d in x:
            if isinstance(d, (str, unicode)):
                pos = d.find(':')
                if pos == -1:
                    abs.append(os.path.abspath(d))
                else:
                    if pos > d.find('/'):                        
                        abs.append(os.path.abspath(d))
                    else:
                        abs.append(d[0:pos+1] + os.path.abspath(d[pos+1:]))
            else:
                pos = d[1].find(':')
                if pos == -1:
                    abs.append((d[0], os.path.abspath(d[1])))
                else:
                    if pos > d[1].find('/'):                        
                        abs.append((d[0], os.path.abspath(d[1])))
                    else:
                        abs.append((d[0], d[1][0:pos+1] + \
                                    os.path.abspath(d[1][pos+1:])))
        exec ('%s = abs' % n)
            

        
if not TV_RECORD_DIR:
    TV_RECORD_DIR = VIDEO_ITEMS[0][1]
    msg = ('TV_RECORD_DIR not set\n' +
           '  Please set TV_RECORD_DIR to the directory, where recordings\n' +
           '  should be stored or remove the tv plugin. Autoset variable\n' +
           '  to %s.') % TV_RECORD_DIR
    if __freevo_app__ == 'main' and plugin.is_active('tv'):
        log.warning(msg)
        
if not VIDEO_SHOW_DATA_DIR and __freevo_app__ == 'main':
    log.warning('VIDEO_SHOW_DATA_DIR not found')
    

#
# compile the regexp
#
VIDEO_SHOW_REGEXP_MATCH = re.compile("^.*" + VIDEO_SHOW_REGEXP).match
VIDEO_SHOW_REGEXP_SPLIT = re.compile("[\.\- ]*" + \
                                     VIDEO_SHOW_REGEXP + "[\.\- ]*").split


# auto detect function
def detect(*what):
    for module in what:
        exec('import %s' % module)


# make sure USER and HOME are set
os.environ['USER'] = pwd.getpwuid(os.getuid())[0]
os.environ['HOME'] = pwd.getpwuid(os.getuid())[5]


#
# Some code for users converting from older versions of Freevo
#

try:
    LOCALE
    log.critical('LOCALE is deprecated. Set encoding in freevo.conf.')
    sys.exit(0)
except NameError, e:
    pass
    
try:
    OVERLAY_DIR
    log.critical('OVERLAY_DIR is deprecated. Set vfs_dir in freevo.conf' +\
                 '  to change the location of the virtual file system')
    sys.exit(0)
except NameError, e:
    pass


# Please do not use the variables anymore
encoding = LOCALE = sysconfig.CONF.encoding

# Some warnings used in development
REDESIGN_MAINLOOP = 'not working while mainloop redesign'
REDESIGN_BROKEN   = 'not working while gui redesign'
REDESIGN_FIXME    = 'not working since gui redesign, feel free to fix this'
REDESIGN_UNKNOWN  = 'plugin may be broken after gui redesign, please check'

