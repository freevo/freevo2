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
# directories for caching.
#
# If you want to use an util module in a different project, you may also
# need this file. The name freevo in the config file can be changed at the
# beginning of this file.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
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

# Application name. This name is used to locate the config file.
# Possible locations are ., ~/application, /etc/application and
# /usr/local/etc/application. The name of the config file is
# application.conf.
application = 'freevo'


# That's it, you shouldn't need to make changes after this point

__all__ = [ 'datafile', 'SHAREDIR', 'LOGDIR', 'cfgfilepath' ]

# Python imports
import os
import stat
import md5
import sys
import locale
import logging
from logging.handlers import RotatingFileHandler
import gettext
import gc

# kaa imports
import kaa

# set basic env variables
if not os.environ.has_key('HOME') or not os.environ['HOME'] or os.environ['HOME'] == '/':
    os.environ['HOME'] = '/root'
if not os.environ.has_key('USER') or not os.environ['USER']:
    os.environ['USER'] = 'root'

# Directories were to search the config file
cfgfilepath = [ '.', os.path.expanduser('~/.' + application), '/etc/' + application ]

# directory for 'share' files
base = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../../..'))
SHAREDIR = os.path.abspath(os.path.join(base, 'share', application + '2'))

# get path with translations
i18npath = os.path.join(base, 'share/locale')
try:
    # try translation file based on application name
    i18n = gettext.translation(os.path.basename(sys.argv[0]), i18npath, fallback=False)
except IOError:
    # try freevo translation file and use fallback to avoid crashing
    i18n = gettext.translation('freevo', i18npath, fallback=True)

i18n.install(unicode=True)

# create needed directories.
DATADIR = '/var/lib/' + application
if os.getuid():
    DATADIR = os.path.expanduser('~/.' + application + '/data')
if not os.path.isdir(DATADIR):
    os.makedirs(DATADIR)

# create and setup the root logger object.
# using logging.getLogger() gives the root logger, calling
# logging.getLogger('foo') returns a new logger with the same default
# settings.
logger = logging.getLogger()

# remove handler, we want to set the look and avoid
# duplicate handlers
for l in logger.handlers[:]:
    logger.removeHandler(l)

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
if sys.argv[0]:
    logfiletmpl = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if logfiletmpl.startswith('freevo-'):
        logfiletmpl = logfiletmpl[7:]
else:
    logfiletmpl = 'python'
    
try:
    LOGDIR = '/var/log/' + application
    logfile = '%s/%s-%s' % (LOGDIR, logfiletmpl, os.getuid())
    if not os.path.isdir(LOGDIR):
        os.makedirs(LOGDIR)
    handler = RotatingFileHandler(logfile, maxBytes=1000000, backupCount=2)
except (OSError, IOError):
    LOGDIR = os.path.expanduser('~/.' + application + '/log')
    logfile = '%s/%s' % (LOGDIR, logfiletmpl)
    if not os.path.isdir(LOGDIR):
        os.makedirs(LOGDIR)
    handler = RotatingFileHandler(logfile, maxBytes=1000000, backupCount=2)
handler.setFormatter(formatter)
logger.addHandler(handler)

# set log level
logger.setLevel(logging.WARNING)

def garbage_collect():
    """
    Run garbage collector. It is not nice that we have to do this,
    but without we have a memory leak.
    """
    # run gc
    gc.collect()
    for g in gc.garbage:
        # print information about garbage gc can't collect
        logger.warning('Unable to free %s' % g)


# start garbage_collect every 5 seconds
kaa.Timer(garbage_collect).start(5)


def datafile(name):
    """
    Return a datafile based on the name. The result is an absolute path.
    """
    return os.path.join(DATADIR, name)
