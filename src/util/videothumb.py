# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# videothumb - create a thumbnail for video files
# -----------------------------------------------------------------------------
# $Id$
#
# This file provides a function to create video thumbnails in the background.
# It will start a mplayer childapp to create the thumbnail. It uses the
# notifier loop to do this without blocking.
#
# Loosly based on videothumb.py commited to the freevo wiki
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
import sys
import os
import kaa.metadata
import glob
import tempfile
import logging
import popen2

from stat import *

# kaa imports
import kaa.notifier
from kaa import mevas

# freevo imports
import vfs

# get logging object
log = logging.getLogger()

# internal thumbnail queue
_runqueue = []

# do not import freevo stuff when running this file
if __name__ != "__main__":
    import config

    class MplayerThumbnail(kaa.notifier.Process):
        """
        Mplayer thumbnailing process
        """
        def __init__( self, app, imagefile):
            self.imagefile = imagefile
            kaa.notifier.Process.__init__(self, app)
            self.signals["stdout"].connect(self.stdout_cb)
            self.signals["stderr"].connect(self.stderr_cb)
            self.signals["completed"].connect(self.finished)


        def stdout_cb(self, line):
            """
            print debug from child as warning
            """
            line.strip(' \t\n')
            if line:
                log.warning('>> %s' % line)


        def stderr_cb(self, line):
            """
            print debug from child as warning
            """
            line.strip(' \t\n')
            if line:
                log.warning('>> %s' % line)


        def finished(self, exit_code):
            """
            Job finished, run next if there is more
            """
            global _runqueue
            _runqueue = _runqueue[1:]

            if not vfs.isfile(self.imagefile):
                log.warning('no imagefile found')
            if _runqueue:
                MplayerThumbnail(*_runqueue[0]).start()
            


    def snapshot(videofile, imagefile=None, pos=None, update=True):
        """
        make a snapshot of the videofile at position pos to imagefile
        """
        global _runqueue
        if not imagefile:
            imagefile = os.path.splitext(videofile)[0] + '.jpg'

        if not update and os.path.isfile(imagefile) and \
               os.stat(videofile)[ST_MTIME] <= os.stat(imagefile)[ST_MTIME]:
            return

        for r, r_image in _runqueue:
            if r_image == imagefile:
                return

        log.info('generate %s' % imagefile)
        args = [ config.MPLAYER_CMD, videofile, imagefile ]

        if pos != None:
            args.append(str(pos))

        job = (([os.environ['FREEVO_SCRIPT'], 'execute',
                 os.path.abspath(__file__) ] + args), imagefile)
        _runqueue.append(job)
        if len(_runqueue) == 1:
            MplayerThumbnail(*_runqueue[0]).start()

        
#
# main function, will be called when this file is executed, not imported
# args: mplayer, videofile, imagefile, [ pos ]
#

if __name__ == "__main__":
    mplayer   = os.path.abspath(sys.argv[1])
    filename  = os.path.abspath(sys.argv[2])
    imagefile = os.path.abspath(sys.argv[3])

    try:
        position = sys.argv[4]
    except IndexError:
        try:
            mminfo = kaa.metadata.parse(filename)
            position = str(int(mminfo.video[0].length / 2.0))
            if hasattr(mminfo, 'type'):
                if mminfo.type in ('MPEG-TS', 'MPEG-PES'):
                    position = str(int(mminfo.video[0].length / 20.0))
        except:
            # else arbitrary consider that file is 1Mbps and grab position
            # at 10%
            position = os.stat(filename)[ST_SIZE]/1024/1024/10.0
            if position < 10:
                position = '10'
            else:
                position = str(int(position))

    # chdir to tmp so we have write access
    tmpdir = tempfile.mkdtemp('tmp', 'videothumb', '/tmp/')
    os.chdir(tmpdir)

    # call mplayer to get the image
    child = popen2.Popen3((mplayer, '-nosound', '-vo', 'png', '-frames', '8',
                           '-ss', position, '-zoom', filename), 1, 100)
    child_output = ''
    while(1):
        data = child.fromchild.readline()
        if not data:
            break
        child_output += data
    for line in child.childerr.readlines():
        child_output += line

    child.wait()
    child.fromchild.close()
    child.childerr.close()
    child.tochild.close()

    # store the correct thumbnail
    captures = glob.glob('000000??.png')
    if not captures:
        # strange, print debug to find the problem
        print "error creating capture for %s" % filename
        print child_output
        os.chdir('/')
        os.rmdir(tmpdir)
        sys.exit(1)
    
    capture = captures[-1]

    try:
        image = mevas.imagelib.open(capture)
        if image.width > 255 or image.height > 255:
            image.scale_preserve_aspect((255,255))
        if image.width * 3 > image.height * 4:
            # fix image with blank bars to be 4:3
            nh = (image.width*3)/4
            ni = mevas.imagelib.new((image.width, nh))
            ni.blend(image, (0,(nh- image.height) / 2))
            image = ni
        elif image.width * 3 < image.height * 4:
            # strange aspect, let's guess it's 4:3
            new_size = (image.width, (image.width*3)/4)
            image.scale((new_size))
        try:
            image.save(imagefile)
        except:
            # unable to save image, try vfs dir
            imagefile = vfs.getoverlay(imagefile)
            try:
                if not os.path.isdir(os.path.dirname(imagefile)):
                    os.makedirs(os.path.dirname(imagefile))
                image.save(imagefile)
            except Exception, e:
                # strange, print debug to find the problem
                print 'unable to write file %s: %s' % \
                      (vfs.getoverlay(imagefile), e)

    except (OSError, IOError), e:
        # strange, print debug to find the problem
        print 'error saving image %s: %s' % (imagefile, e)

    for capture in captures:
        try:
            os.remove(capture)
        except:
            print "error removing temporary captures for %s" % filename

    os.chdir('/')
    os.rmdir(tmpdir)
    sys.exit(0)
