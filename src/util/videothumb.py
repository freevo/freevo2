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
# Revision 1.11  2004/06/23 21:09:29  dischi
# handle mplayer TS, PES problems
#
# Revision 1.10  2004/05/02 09:21:57  dischi
# better python code
#
# Revision 1.9  2004/02/09 20:04:33  dischi
# better error handling
#
# Revision 1.8  2004/02/08 12:16:27  dischi
# chdir to tmp to call mplayer
#
# Revision 1.7  2004/02/08 12:09:01  dischi
# o let mplayer keep the aspect of the movie
# o add bars/resize to fit 4:3 so all thumbnails have the same geometry
#
# Revision 1.6  2004/02/01 17:05:28  dischi
# popup support
#
# Revision 1.5  2004/01/10 18:45:23  dischi
# always use thumbnail
#
# Revision 1.4  2004/01/10 04:12:02  outlyer
# Take a snapshot/thumbnail after a file is recorded...
#
# Revision 1.3  2004/01/04 17:19:57  dischi
# store image as .raw file if no filename is given
#
# Revision 1.2  2004/01/04 13:07:14  dischi
# make image max 300x300
#
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

import sys, os, mmpython, glob, shutil
from stat import *

def snapshot(videofile, imagefile=None, pos=None, update=True, popup=None):
    """
    make a snapshot of the videofile at position pos to imagefile
    """
    import config
    import popen3
    import Image
    import util
    import vfs
    import gui.PopupBox
    import osd
    
    if not imagefile:
        imagefile = vfs.getoverlay(videofile + '.raw')

    if not update and os.path.isfile(imagefile) and \
           os.stat(videofile)[ST_MTIME] <= os.stat(imagefile)[ST_MTIME]:
        return

    if popup:
        pop = gui.PopupBox(text='Creating thumbnail for \'%s\'...' % \
                           os.path.basename(videofile),
                           width=osd.get_singleton().width-config.OSD_OVERSCAN_X*2-80)
        pop.show()
        
    args = [ config.MPLAYER_CMD, videofile, imagefile ]

    if pos != None:
        args.append(str(pos))

    out = popen3.stdout([os.environ['FREEVO_SCRIPT'], 'execute',
                         os.path.abspath(__file__) ] + args)
    if out:
        for line in out:
            print line
    if vfs.isfile(imagefile):
        try:
            image = Image.open(imagefile)
            image.thumbnail((300,300), Image.ANTIALIAS)
            if image.size[0] * 3 > image.size[1] * 4:
                # fix image with blank bars to be 4:3
                ni = Image.new('RGB', (image.size[0], (image.size[0]*3)/4))
                ni.paste(image, (0,(((image.size[0]*3)/4)-image.size[1])/2))
                image = ni
            elif image.size[0] * 3 < image.size[1] * 4:
                # strange aspect, let's guess it's 4:3
                image = Image.open(imagefile).resize((image.size[0], (image.size[0]*3)/4),
                                                     Image.ANTIALIAS)
            if image.mode == 'P':
                image = image.convert('RGB')
            # crob some pixels, looks better that way
            image = image.crop((4, 3, image.size[0]-8, image.size[1]-6))
            if imagefile.endswith('.raw'):
                data = (image.tostring(), image.size, image.mode)
                util.save_pickle(data, imagefile)
            else:
                image.save(imagefile)
        except (OSError, IOError), e:
            print e
    else:
        print 'no imagefile found'
        
    if popup:
        pop.destroy()
        
#
# main function, will be called when this file is executed, not imported
# args: mplayer, videofile, imagefile, [ pos ]
#

if __name__ == "__main__":
    import config
    import popen2
    import vfs
    
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
            # else arbitrary consider that file is 1Mbps and grab position at 10%
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
            shutil.copy(capture, vfs.getoverlay(imagefile[1:]))
    else:
        print "error creating capture for %s" % filename

    for capture in captures:
        try:
            os.remove(capture)
        except:
            print "error removing temporary captures for %s" % filename
