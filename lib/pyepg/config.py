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
application = 'pyepg'

# That's it, you shouldn't need to make changes after this point

__all__ = [ 'CONF', 'Unicode', 'String' ]

# Python imports
import os
import sys
import locale
import __builtin__

# Dummy class for the CONF
class struct(object):
    pass

CONF = struct()

# find the currect encoding
try:
    CONF.default_encoding = locale.getdefaultlocale()[1]
    ''.encode(CONF.default_encoding)
except:
    CONF.default_encoding = 'latin-1'

CONF.encoding = CONF.default_encoding

# add everything in CONF to the module variable list (but in upper
# case, so CONF.vfs_dir is VFS_DIR, too
for key in CONF.__dict__:
    exec('%s = CONF.%s' % (key.upper(), key))

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
