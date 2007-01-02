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
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Krister Lagerstrom <krister-freevo@kmlager.com>
#
# Please see the file doc/CREDITS for a complete list of authors.
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
import logging
import copy

import kaa.strutils
import kaa.popcorn

import freevo.conf

# freevo imports
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

#
# freevo.conf parser
#

class struct(object):
    pass

CONF = struct()
CONF.geometry = '800x600'
CONF.display = 'x11'
CONF.tv = 'ntsc'
CONF.chanlist = 'us-cable'
CONF.version = 0

for dirname in freevo.conf.cfgfilepath:
    conffile = os.path.join(dirname, 'freevo.conf')
    if os.path.isfile(conffile):
        c = open(conffile)
        for line in c.readlines():
            if line.startswith('#'):
                continue
            if line.find('=') == -1:
                continue
            vals = line.strip().split('=')
            if not len(vals) == 2:
                print 'invalid config entry: %s' % line
                continue
            name, val = vals[0].strip(), vals[1].strip()
            CONF.__dict__[name] = val

        c.close()
        break
else:
    log.critical('freevo.conf not found, please run \'freevo setup\'')
    sys.exit(1)
    
kaa.popcorn.config.load('/etc/freevo/player.conf')
# if started as user add personal config file
if os.getuid() > 0:
    cfgdir = os.path.expanduser('~/.freevo')
    kaa.popcorn.config.load(os.path.join(cfgdir, 'player.conf'))

# save the file again in case it did not exist or the variables changed
kaa.popcorn.config.save()

w, h = CONF.geometry.split('x')
CONF.width, CONF.height = int(w), int(h)

#
# Read the environment set by the start script
#
SHARE_DIR = freevo.conf.SHAREDIR
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


#
# load the config file
#
execfile(os.path.join(os.path.dirname(__file__), 'configfile.py'))

# set the umask
os.umask(UMASK)

#
# force fullscreen when freevo is it's own windowmanager
#
if len(sys.argv) >= 2 and sys.argv[1] == '--force-fs':
    GUI_FULLSCREEN = 1


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
        if plugin.is_active('mediamenu', type):
            log.warning('%s not set, set it to Home directory' % n)

    elif type == 'games':
        abs = []
        for d in x:
            dirs = []

            for p in d[2]:
                pos = p.find(':')

                if pos == -1:
                    dirs.append(os.path.abspath(p))
                else:
                    if pos > p.find('/'):
                        dirs.append(os.path.abspath(p))
                    else:
                        dirs.append(p[0:pos + 1] + os.path.abspath(p[pos + 1:]))

            abs.append(( d[0], d[1], dirs, d[3], d[4], d[5] ))

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
    if plugin.is_active('tv'):
        log.warning(msg)
        
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
    log.critical('LOCALE is deprecated.')
    sys.exit(0)
except NameError, e:
    pass
    
try:
    OVERLAY_DIR
    log.critical('OVERLAY_DIR is deprecated. Set overlay dir on beacon' +\
                 '  startup to change the location of the virtual file system')
    sys.exit(0)
except NameError, e:
    pass
