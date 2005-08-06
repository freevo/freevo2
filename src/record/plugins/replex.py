# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# replex.py - replex ts recordings
# -----------------------------------------------------------------------------
# $Id$
#
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

# python imports
import os
import kaa.metadata
import logging

# kaa imports
import kaa.notifier

# freevo imports
from util.fileops import find_file_in_path
from record.plugins import Plugin
from record.record_types import *

# get logging object
log = logging.getLogger('record')


class PluginInterface(Plugin):
    """
    Plugin to replex mpeg ts into dvd mpegs
    """
    def __init__(self):
        self.replex = find_file_in_path( 'replex' )
        self.nice = find_file_in_path( 'nice' )
        if not self.replex:
            self.reason = 'replex not found'
            return
        if not self.nice:
            self.reason = 'nice not found'
            return
        Plugin.__init__(self)
        log.info('add replex plugin')


    def replex_stop(self, source, dest):
        """
        The replex program has stopped, check the result.
        """
        # get length of both files
        srcinfo = kaa.metadata.parse(source)
        if not srcinfo:
            # this shoudln't happen
            log.error('unable to parse %s' % source)
            # set slen to something unrealistic
            slen = -1000
        else:
            slen = srcinfo.length

        destinfo = kaa.metadata.parse(dest)
        if not destinfo:
            # replex didn't work
            log.error('unable to parse %s' % dest)
            dlen = 0
        else:
            # get dest file length
            dlen = destinfo.length

        log.info('%s finished' % String(dest))

        if slen - 10 > dlen:
            # different length, looks something went wrong, keep
            # ts and remove mpg file
            log.error('replex failed, remove replex file')
            if os.path.isfile(dest):
                os.unlink(dest)
            return

        # delete ts
        os.unlink(source)
        fxd = os.path.splitext(source)[0] + '.fxd'
        if not os.path.isfile(fxd):
            # fxd file must be in real not in overlay dir, without
            # that, replex couldn't even store the file
            log.info('no fxd file to change')
            return

        log.info('changing fxd file %s' % String(fxd))

        # read fxd file
        f = open(fxd)
        data = f.readlines()
        f.close()

        source = os.path.basename(source) + '</file>'
        dest = os.path.basename(dest) + '</file>'

        # write fxd file with source replaced with dest
        f = open(fxd, 'w')
        for line in data:
            f.write(line.replace(source, dest))
        f.close()



    def stop_recording(self, recording):
        """
        Replex mpeg ts into dvd mpegs
        """
        source = recording.url[5:]
        if recording.status != SAVED:
            log.info('%s is failed' % String(source))
            return
        if not recording.url.startswith('file:'):
            log.info('%s is no file' % String(source))
            return
        if not source.endswith('.ts'):
            log.info('%s is no mpeg ts' % String(source))
            return

        if not kaa.metadata.parse(source):
            log.info('%s is failed' % String(source))
            return
        
        dest = os.path.splitext(source)[0] + '.mpg'
        log.info('replex %s' % String(source))
        app = [ self.nice, '-n', '19', self.replex, '-x', '-k',
                '-t', 'DVD', '--of', dest, source ]
        child = kaa.notifier.Process(app)
        child.signals["completed"].connect(self.replex_stop, source, dest)
        child.start()
