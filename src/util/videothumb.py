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
import mmpython
import glob
import shutil
import Image
import popen2

from stat import *

_runqueue = []

# do not import freevo stuff when running this file
if __name__ != "__main__":
    import childapp
    import config
    import vfs

    class MplayerThumbnail(childapp.Instance):
        """
        Mplayer thumbnailing childapp
        """
        def __init__( self, app, imagefile):
            self.imagefile = imagefile
            childapp.Instance.__init__(self, app, stop_osd=0)

        def stdout_cb(self, line):
            if line[:-1]:
                print '>>', line[:-1]

        def stderr_cb(self, line):
            if line[:-1]:
                print '>>', line[:-1]

        def finished(self):
            global _runqueue
            _runqueue = _runqueue[1:]

            if vfs.isfile(self.imagefile):
                imagefile = self.imagefile
                try:
                    image = Image.open(imagefile)
                    if image.size[0] > 255 or image.size[1] > 255:
                        image.thumbnail((255,255), Image.ANTIALIAS)

                    if image.mode == 'P':
                        image = image.convert('RGB')

                    if image.size[0] * 3 > image.size[1] * 4:
                        # fix image with blank bars to be 4:3
                        ni = Image.new('RGB', (image.size[0],
                                               (image.size[0]*3)/4))
                        ni.paste(image, (0,(((image.size[0]*3)/4)-\
                                            image.size[1])/2))
                        image = ni
                    elif image.size[0] * 3 < image.size[1] * 4:
                        # strange aspect, let's guess it's 4:3
                        new_size = (image.size[0], (image.size[0]*3)/4)
                        image = Image.open(imagefile).resize(new_size,
                                                             Image.ANTIALIAS)

                    # crob some pixels, looks better that way
                    image = image.crop((4, 3, image.size[0]-8,
                                        image.size[1]-6))
                    if imagefile.endswith('.raw.tmp'):
                        f = vfs.open(imagefile[:-4], 'w')
                        f.write('FRI%s%s%5s' % (chr(image.size[0]),
                                                chr(image.size[1]),
                                                image.mode))
                        f.write(image.tostring())
                        f.close()
                        os.unlink(imagefile)
                    else:
                        image.save(imagefile)
                except (OSError, IOError), e:
                    _debug_(e, 0)
            else:
                _debug_('no imagefile found', 0)
            if _runqueue:
                MplayerThumbnail(*_runqueue[0])
            



def snapshot(videofile, imagefile=None, pos=None, update=True):
    """
    make a snapshot of the videofile at position pos to imagefile
    """
    global _runqueue
    if not imagefile:
        imagefile = vfs.getoverlay(videofile + '.raw')

    if not update and os.path.isfile(imagefile) and \
           os.stat(videofile)[ST_MTIME] <= os.stat(imagefile)[ST_MTIME]:
        return

    if imagefile.endswith('.raw'):
        imagefile += '.tmp'

    for r, r_image in _runqueue:
        if r_image == imagefile:
            return
    
    print 'generate', imagefile
    args = [ config.MPLAYER_CMD, videofile, imagefile ]

    if pos != None:
        args.append(str(pos))

    _runqueue.append((([os.environ['FREEVO_SCRIPT'], 'execute',
                        os.path.abspath(__file__) ] + args), imagefile))
    if len(_runqueue) == 1:
        MplayerThumbnail(*_runqueue[0])
        


        
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
            mminfo = mmpython.parse(filename)
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
    os.chdir('/tmp')

    # call mplayer to get the image
    child = popen2.Popen3((mplayer, '-nosound', '-vo', 'png', '-frames', '8',
                           '-ss', position, '-zoom', filename), 1, 100)
    while(1):
        data = child.fromchild.readline()
        if not data:
            break
    child.wait()
    child.fromchild.close()
    child.childerr.close()
    child.tochild.close()
    # store the correct thumbnail
    captures = glob.glob('000000??.png')
    if captures:
        capture = captures[-1]
        try:
            shutil.copy(capture, imagefile)
        except:
            try:
                import config
                import vfs
                shutil.copy(capture, vfs.getoverlay(imagefile[1:]))
            except:
                print 'unable to write file'
    else:
        print "error creating capture for %s" % filename

    for capture in captures:
        try:
            os.remove(capture)
        except:
            print "error removing temporary captures for %s" % filename
