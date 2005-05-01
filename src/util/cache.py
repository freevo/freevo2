# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# cache.py - Cache functions and classes
# -----------------------------------------------------------------------------
# $Id$
#
# This module provides two helper functions to store python objects to a
# cachefile using pickle and loading it again. It can also handle version
# informations to make sure the data is valid for the current version of the
# software using it. The class 'Cache' is a mix between a dict, a cache using
# the pickle load and save functions and a way to add variabkes to a module.
#
# This module has no dependencies to Freevo.
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

__all__ = [ 'load', 'save', 'Cache' ]

import os
import sys
import pickle
import cPickle

if float(sys.version[0:3]) < 2.3:
    PICKLE_PROTOCOL = 1
else:
    PICKLE_PROTOCOL = pickle.HIGHEST_PROTOCOL

def load(file, version=None):
    """
    Load a cache from disc. If version is given, the version field in the
    cachefile is checked and the function will return None if the field
    doesn't match. Notice: if a file is saved using a version field, this
    version must also be given on loading.
    """
    try:
        f = open(file, 'r')
        try:
            data = cPickle.load(f)
        except:
            data = pickle.load(f)
        f.close()
        if version and data[0] == version:
            return data[1]
        elif version == None:
            return data
        return None
    except:
        return None


def save(file, data, version=None):
    """
    Save the data to the given file. If version is given, this information will
    also be stored in the cachefile. Notice: when using a version here, the
    version parameter must also be used when loading the data again.
    """
    try:
        f = open(file, 'w')
    except (OSError, IOError):
        if os.path.isfile(file):
            os.unlink(file)
        try:
            f = open(file, 'w')
        except (OSError, IOError), e:
            try:
                os.makedirs(os.path.dirname(file))
                f = open(file, 'w')
            except (OSError, IOError), e:
                print 'cache.save: %s' % e
                return
    if version:
        cPickle.dump((version, data), f, PICKLE_PROTOCOL)
    else:
        cPickle.dump(data, f, PICKLE_PROTOCOL)
    f.close()



class Cache:
    """
    Class to cache data from a given module to a file. This is usefull when
    using the freevo config or sysconfig module as 'module' to store data.
    After loading, all key-value pairs added to this dict like class will
    also be added as variable to module in upper case.
    """
    def __init__(self, filename, module=None, version=None):
        self.cachefile = filename
        self.module = module
        self.version = version
        self.data = load(filename, version)
        if not self.data:
            self.data = {}
        for key in self.data:
            if self.module and not key.startswith('_'):
                setattr(self.module, key, self.data[key])


    def __getitem__(self, key):
        """
        Return the value for key from the internal data. Return None if the
        key is not found.
        """
        if self.data.has_key(key):
            return self.data[key]
        return None


    def __setitem__(self, key, value):
        """
        Set key to value and store it to the internal data for caching and
        add it to the given module.
        """
        self.data[key] = value
        if self.module and not key.startswith('_'):
            setattr(self.module, key, value)


    def save(self):
        """
        Store the internal data to the cachefile
        """
        save(self.cachefile, self.data, self.version)


    def keys(self):
        """
        Return all valid keys from the internal data
        """
        return filter(lambda x: not x.startswith('_'), self.data.keys())


