# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# sysconfig.py - Basic configuration for some utils used in Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# Most modules in the util directory doesn't need Freevo. So it is possible
# to use them in a different project (licence is GPL). But the modules need
# a very simple configuration, like were to store cache files and some need
# the virtual filesystem (util.vfs) to work and this has it's own data
# directory. A different problem is the python encoding handling. It is
# fixed to 'ascii' (you can change it in site.py, but that doesn't always
# work and is a bad solution). 
#
# This module provides some basic settings to solve that problems. It reads
# a config file and stores everything in a struct. It will create necessary
# directories for vfs and caching and provides helper functions Unicode
# and String to solve the encoding problem.
#
# If you want to use an util module in a different project, you may also
# need this file. The name freevo in the config file can be changed at the
# beginning of this file.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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

# Application name. This name is used to locate the config file.
# Possible locations are ., ~/application, /etc/application and
# /usr/local/etc/application. The name of the config file is
# application.conf. It not defined, the variables vfs, encoding and
# cachedir are added to the resulting struct to have all needed informations.
application = 'freevo'

# Should the sysconfig module prepare the application for the use of the
# vfs util?
use_vfs = True


# That's it, you shouldn't need to make changes after this point

__all__ = [ 'CONF', 'Unicode', 'String', 'getvar', 'cachefile', 'datafile' ]

# Python imports
import os
import sys
import locale
import __builtin__
import logging

# Directories were to search the config file
_cfgfilepath = [ '.', os.path.expanduser('~/.' + application),
                 '/etc/' + application, '/usr/local/etc/' + application]

# Dummy class for the CONF
class struct:
    pass

CONF = struct()

# Removable media list. This is used by the vfs and should be filled
# with objects after startup. If not, the vfs will have no support
# for removable media.
REMOVABLE_MEDIA = []

# find the currect encoding
try:
    CONF.default_encoding = locale.getdefaultlocale()[1]
    ''.encode(CONF.default_encoding)
except:
    CONF.default_encoding = 'latin-1'

CONF.encoding = CONF.default_encoding

# set default vfs dir
if use_vfs:
    CONF.vfs_dir = os.path.expanduser('~/.' + application + '/vfs')

# set default cachedir
if os.uname()[0] == 'FreeBSD':
    OS_CACHEDIR = '/var/db'
else:
    OS_CACHEDIR = '/var/cache'

CONF.cachedir = OS_CACHEDIR + '/' + application
CONF.datadir  = '/var/lib/' + application
CONF.logdir   = '/var/log/' + application

# read the config file, if no file is found, the default values
# are used.
for dirname in _cfgfilepath:
    conf = os.path.join(dirname, application + '.conf')
    if os.path.isfile(conf):
        c = open(conf)
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


# create the vfs
if use_vfs:
    if not CONF.vfs_dir or CONF.vfs_dir == '/':
        print
        print 'ERROR: bad vfs dir.'
        print 'Set vfs dir it to a directory on the local filesystem.'
        print 'Make sure this partition has about 100 MB free space'
        sys.exit(0)
    
    # Make sure CONF.vfs_dir doesn't ends with a slash
    # With that, we don't need to use os.path.join, normal string
    # concat is much faster
    if CONF.vfs_dir.endswith('/'):
        CONF.vfs_dir = CONF.vfs_dir[:-1]

    if not os.path.isdir(CONF.vfs_dir):
        os.makedirs(CONF.vfs_dir)
    
    if not os.path.isdir(CONF.vfs_dir + '/disc'):
        os.makedirs(CONF.vfs_dir + '/disc')
    
    if not os.path.isdir(CONF.vfs_dir + '/disc/metadata'):
        os.makedirs(CONF.vfs_dir + '/disc/metadata')
    
    if not os.path.isdir(CONF.vfs_dir + '/disc-set'):
        os.makedirs(CONF.vfs_dir + '/disc-set')

# create cachedir
if not os.path.isdir(CONF.cachedir):
    try:
        os.makedirs(CONF.cachedir)
    except OSError:
        CONF.cachedir = os.path.expanduser('~/.' + application + '/cache')
        if not os.path.isdir(CONF.cachedir):
            os.makedirs(CONF.cachedir)

# create datadir
if not os.path.isdir(CONF.datadir):
    try:
        os.makedirs(CONF.datadir)
    except OSError:
        CONF.datadir = os.path.expanduser('~/.' + application + '/lib')
        if not os.path.isdir(CONF.datadir):
            os.makedirs(CONF.datadir)

# create logdir
if not os.path.isdir(CONF.logdir):
    try:
        os.makedirs(CONF.logdir)
    except OSError:
        CONF.logdir = os.path.expanduser('~/.' + application + '/log')
        if not os.path.isdir(CONF.logdir):
            os.makedirs(CONF.logdir)

# add everything in CONF to the module variable list (but in upper
# case, so CONF.vfs_dir is VFS_DIR, too
for key in CONF.__dict__:
    exec('%s = CONF.%s' % (key.upper(), key))


# create and setup the root logger object.
# using logging.getLogger() gives the root logger, calling
# logging.getLogger('foo') returns a new logger with the same default
# settings.
logger = logging.getLogger()

# set stdout logging
# TODO: find a way to shut down that logger later when the user
# wants to visible debug in the terminal
formatter = logging.Formatter('%(levelname)s %(module)s'+\
                              '(%(lineno)s): %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# set file logger
formatter = logging.Formatter('%(asctime)s %(levelname)-8s [%(name)6s] '+\
                              '%(filename)s %(lineno)s: '+\
                              '%(message)s')
fname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
fname = '%s/%s-%s' % (CONF.logdir, fname, os.getuid())
handler = logging.FileHandler(fname)
handler.setFormatter(formatter)
logger.addHandler(handler)

# set log level
logger.setLevel(logging.WARNING)


# encoding helper functions

def Unicode(string, encoding=None):
    """
    Convert an object to unicode using the sysconfig encoding as
    fallback instead of ascii
    """
    if not encoding:
        encoding = CONF.encoding
    if string.__class__ == str:
        try:
            return unicode(string, encoding)
        except UnicodeDecodeError:
            pass
        try:
            return unicode(string, CONF.default_encoding)
        except UnicodeDecodeError:
            pass
        try:
            return unicode(string, 'UTF-8')
        except UnicodeDecodeError:
            pass
        return unicode(string, encoding, 'replace')

    if string.__class__ == unicode:
        return string
    return Unicode(str(string), encoding)


def String(string, encoding=None):
    """
    Convert an object to string using the sysconfig encoding as
    fallback instead of ascii
    """
    if not encoding:
        encoding = CONF.encoding
    if string.__class__ == unicode:
        return string.encode(encoding, 'replace')
    if string.__class__ == str:
        return Unicode(string, encoding).encode(encoding, 'replace')
    try:
        return str(string)
    except:
        return unicode(string).encode(encoding, 'replace')


# add Unicode and String to the global scope
__builtin__.__dict__['Unicode'] = Unicode
__builtin__.__dict__['String']  = String


def getvar(variable):
    """
    Get a variable from CONF, return None if not found
    """
    if hasattr(CONF, variable):
        return CONF.variable
    return None


def cachefile(name, uid=False):
    """
    Return a cachefile based on the name. The result is an absolute path.
    If uid is True, the uid will be added to the name.
    """
    if uid:
        return os.path.join(CONF.cachedir, name + '-' + str(os.getuid()))
    else:
        return os.path.join(CONF.cachedir, name)


def datafile(name):
    """
    Return a datafile based on the name. The result is an absolute path.
    """
    return os.path.join(CONF.datadir, name)


def logfile(name):
    """
    Return a datafile based on the name. The result is an absolute path.
    """
    return os.path.join(CONF.logdir, name)
