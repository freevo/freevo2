#if 0 /*
# -----------------------------------------------------------------------
# videothumb - create a thumbnail for video files
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This is a bad hack. It creates a new process to make the
#        images with mplayer and than copy it to the location
#
#        Based on videothumb.py commited to the freevo wiki
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/01/04 11:16:32  dischi
# add function to create a thumbnail from videofiles
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
#endif

import sys, os, mmpython, glob
from stat import *
import shutil

import config
import popen3


def snapshot(videofile, imagefile, pos=None):
    """
    make a snapshot of the videofile at position pos to imagefile
    """
    args = [ videofile, imagefile ]
    if pos != None:
        args.append(str(pos))

    out = popen3.stdout([os.environ['FREEVO_SCRIPT'], 'execute',
                         os.path.abspath(__file__) ] + args)
    if out:
        print out



#
# main function, will be called when this file is executed, not imported
# args: videofile, imagefile, [ pos ]
#

if __name__ == "__main__":
    filename  = os.path.abspath(sys.argv[1])
    imagefile = os.path.abspath(sys.argv[2])

    try:
        position = sys.argv[3]
    except IndexError:
        try:
            position = str(mmpython.parse(filename).video[0].length / 2.0)
        except:
            # else arbitrary consider that file is 1Mbps and grab position at 10%
            position = os.stat(filename)[ST_SIZE]/1024/1024/10.0
            if position < 10:
                position = '10'
            else:
                position = str(int(position))

    popen3.stdout((config.MPLAYER_CMD, '-nosound', '-vo', 'png', '-frames', '8',
                   '-ss', position, filename))

    captures = glob.glob('000000??.png')
    if captures:
        capture = captures[-1:][0]
        try:
            shutil.copy(capture, imagefile)
        except:
            shutil.copy(capture, os.path.join(config.OVERLAY_DIR, imagefile[1:]))
    else:
        print "error creating capture for %s" % filename

    for capture in captures:
        try:
            os.remove(capture)
        except:
            print "error removing temporary captures for %s" % filename
