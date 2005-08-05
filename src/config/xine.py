# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# xine.py - auto detect xine
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2005/08/05 17:50:30  dischi
# fix fbxine version detection
#
# Revision 1.1  2004/11/28 17:31:24  dischi
# merge system/ and config.py into config/, needs more cleanup
#
# Revision 1.3  2004/11/21 10:12:47  dischi
# improve system detect, use config.detect now
#
# Revision 1.2  2004/10/25 16:30:05  rshortt
# Fix crash if freevo.conf entries exist but aren't valid.
# Maybe we should also print a warning?
#
# Revision 1.1  2004/09/28 18:30:24  dischi
# add autodetect system settings module
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

import popen2
import os
import stat

import sysconfig
import config
import util.cache

cache = util.cache.Cache(sysconfig.cachefile('xine', True), config, 1)

if config.CONF.xine and os.path.exists(config.CONF.xine):
    timestamp = os.stat(config.CONF.xine)[stat.ST_MTIME]
    if timestamp != cache['_XINE_TIMESTAMP']:
        cache['XINE_USE_LIRC'] = 0
        cache['XINE_VERSION']  = ''
        child = popen2.Popen3([config.CONF.xine, '--help'])
        for line in child.fromchild.readlines():
            if line.find('--no-lirc') > 0:
                cache['XINE_USE_LIRC'] = 1
        child.wait()

        child = popen2.Popen3([config.CONF.xine, '--version'])
        for line in child.fromchild.readlines():
            if line.find('X11 gui') > 0 and line.rfind(' v') > 0:
                cache['XINE_VERSION'] = line[line.rfind(' v')+2:-2]
        child.wait()
        cache['_XINE_TIMESTAMP'] = timestamp

if config.CONF.fbxine and os.path.exists(config.CONF.fbxine):
    timestamp = os.stat(config.CONF.fbxine)[stat.ST_MTIME]
    if timestamp != cache['_FBXINE_TIMESTAMP']:
        cache['FBXINE_USE_LIRC'] = 0
        cache['FBXINE_VERSION']  = ''
        child = popen2.Popen3([config.CONF.fbxine, '--help'])
        for line in child.fromchild.readlines():
            if line.find('--no-lirc') > 0:
                cache['FBXINE_USE_LIRC'] = 1
            if line.startswith('fbxine '):
                cache['FBXINE_VERSION'] = line[7:line[8:].find(' ')+8]
        child.wait()
        if not cache['FBXINE_VERSION']:
            child = popen2.Popen3([config.CONF.fbxine, '--version'])
            for line in child.fromchild.readlines():
                if line.startswith('fbxine '):
                    cache['FBXINE_VERSION'] = line[7:line[8:].find(' ')+8]
            child.wait()
        cache['_FBXINE_TIMESTAMP'] = timestamp

cache.save()
