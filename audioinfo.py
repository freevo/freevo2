# ----------------------------------------------------------------------
# audioinfo - Getting info about mp3 files
# ----------------------------------------------------------------------
# $Id$
#
# Authors: Thomas Malt <thomas@malt.no>
#	   Aubin Paul <aubin@debian.org>
#          Scott Hassan (afaik)
# Notes:   - Lot of code taken from an mp3 module by Scott Hassan
#          - From now on ogg.vorbis is an optional dependency.
#          - The code for calculating elapsed time and stuff is not 
#            really accurate. We don't get any info from mplayer about
#            how far we've really gotten, we just hope the timeskew
#            isn't to bad.
# Todo:    - Write doc.
#          * Add support for Ogg-Vorbis
# ----------------------------------------------------------------------
# $Log$
# Revision 1.6  2002/08/01 00:38:26  outlyer
# More VBR fixes.
#
# Revision 1.5  2002/07/31 14:28:28  outlyer
# Added sampling frequency '9' as '44100' to cope with a (possibly broken) VBR
# mp3 file I had. This prevents an indexerror/crash.
#
# Revision 1.4  2002/07/31 00:59:09  outlyer
# Patch from Thomas Malt <tm@false.linpro.no>
# 1) When paused the timer for the audio did not pause, so when
#    you continued to play the statusbar and stuff would leap forward.
#    fixed.
# 2) On some ogg files with corrupted info I found that audioinfo.py
#    would crash throwing an UnicodeError. Added code to catch the
#    exception, but it doesn't do anything smart to resolve yet.
#
# Revision 1.3  2002/07/29 06:25:29  outlyer
# Added imghdr.what() call back to verify the image is actually an image
# and not lying via the extension. That of course, would make for a crash.
#
# Revision 1.2  2002/07/29 06:21:27  outlyer
# Fixed a minor regression. Added code to get the cover image, as per
# previous behaviour. I've noticed that the mplayer mp3 player takes remarkably
# little CPU on my Celeron 400; less than 1%, so it definitely smokes mpg123
# and mpg321.
#
# Revision 1.1  2002/07/29 05:24:35  outlyer
# Lots and lots of changes for new mplayer-based audio playing code.
# o You'll need to modify your config file, as well as setup the new mplayer
#   module by editing main.py
# o This change includes Ogg Support, but that requires the ogg.vorbis
#   module. If you don't want it, just don't install ogg.vorbis :)
#
# ----------------------------------------------------------------------
# 
# Copyright (C) 2002 Krister Lagerstrom
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
# ----------------------------------------------------------------------
#
"""Module for providing information about MP3-files

Usage: audioinfo.MP3Info( 'filename' )
"""

import os
import sys
import string
import time
import re
import mp3_id3
import skin
import imghdr

DEBUG=1

class AudioInfo:
    """
    This is the common class to get information about audiofiles.
    """
    __pause_timer = 0 # Private variable to store time for pause.
    __lastupdate  = 0.0
    
    def __init__( self, file, drawall=0 ):
        self.drawall    = drawall
        self.filename   = file
        self.album      = ''
        self.artist     = ''
        self.length     = 0
        self.title      = 0
        self.track      = 0
        self.year       = 0
        self.start      = 0
        self.elapsed    = 0
        self.remain     = 0
        self.done       = 0.0
        self.image      = ''
        self.pause      = 0

        # XXX This is really not a very smart way to do it. We should be
        # XXX able to handle files with messed up extentions.
        if self.is_ogg():
            if DEBUG: print "Got ogg..."
            self.set_info_ogg( self.filename )

        elif self.is_mp3():
            if DEBUG: print "Got mp3..."
            self.set_info_mp3( self.filename )
        else:
            if DEBUG: print "Got something else..."

	temp = self.get_cover_image ( self.filename )
        if DEBUG:
            print "DEBUG:"
            print "  Album: " + str(self.album)
            print " Artist: " + str(self.artist)
            print "  Title: " + str(self.title)
            print "  Track: " + str(self.track)
            print "   Year: " + str(self.year)
            print " Length: " + str(self.length)
	    print "  Image: " + str(temp)

    def get_cover_image( self, filename ):
    	cover_logo = os.path.dirname(filename)
	cover_logo += '/cover.png'
	print cover_logo
	# Only draw the cover if the file exists. We'll
	# use the standard imghdr function to check if
	# it's a real png, and not a lying one :)
	if os.path.isfile(cover_logo) and imghdr.what(cover_logo):
		self.image = cover_logo
	# Allow per mp3 covers. As per Chris' request ;)
	if os.path.isfile(os.path.splitext(filename)[0] + '.png'):
	        self.image = os.path.splitext(filename)[0] + '.png'
        return self.image

    def set_cover_image( self, str ):
        self.image = str

    def toggle_pause( self ):
        if self.pause:
            self.pause = 0
            self.start = self.start + (time.time()-self.__pause_timer)
            self.__pause_timer = 0
        else:
            self.pause = 1
            self.__pause_timer = time.time()
            
    def set_info_ogg( self, file ):
        """
        Sets all the info variables with useful info from the oggfile.

        Arguments: Filename of file to get info from
        Returns:   1 if success.
        """
	try:
		import ogg.vorbis
	except ImportError:
		return None
        try: 
            vf = ogg.vorbis.VorbisFile( file )
            vc = vf.comment()
        except ogg.vorbis.VorbisError:
            if DEBUG: print "Got VorbisError.. not an ogg file."
            return 0
        
        try:
            if 'ALBUM' in vc.keys():
                self.album  = vc['ALBUM'][0]
            else:
                self.album  = ''
                
            if 'ARTIST' in vc.keys():
                self.artist = vc['ARTIST'][0]
            else:
                self.artist = ''
                
            if 'TITLE' in vc.keys():
                self.title  = vc['TITLE'][0]
            else:
                self.title  = ''
                
            if 'TRACK' in vc.keys():
                self.track  = vc['TRACK'][0]
            elif 'TRACKNUMBER' in vc.keys():
                self.track  = vc['TRACKNUMBER'][0]
            else:
                self.track  = ''
                
            if 'YEAR' in vc.keys():
                self.year = vc['YEAR'][0]
            else:
                self.year = ''
        except UnicodeError:
            if DEBUG: print "Oops, got UnicodeError"

        self.length = vf.time_total( -1 )
        return 1

    def set_info_mp3( self, file ):
        """
        Sets the info variables with info from the mp3

        Arguments: filename
          Returns: 1 if success
        """
        id3 = mp3_id3.ID3( file )
        tmp = mp3info( file )

        self.album  = id3.album
        self.artist = id3.artist
        self.length = (tmp['MM']*60)+tmp['SS']
        self.title  = id3.title
        if not self.title:
            self.title = ''
        self.track  = id3.track
        self.year   = id3.year
        return 1

    def yes( self ):
        return 1

    def is_ogg( self ):
        if re.match( '.*[oO][gG]{2}$', self.filename ):
            return 1        
        return 0

    def is_mp3( self ):
        if re.match( '.*[mM][pP]3$', self.filename ):
            return 1
        return 0
            
    def get_elapsed( self ):
        if self.pause:
            return self.elapsed
        return (time.time() - self.start)

    def get_remain( self ):
        if( self.elapsed > self.length ):
            self.elapsed = self.length
        return (self.length - self.elapsed)

    def get_done( self ):
        if( self.elapsed > self.length ):
            self.elapsed = self.length
        return ((self.elapsed/self.length)*100.0)

    def ffwd( self, len=0 ):
        # Hm.. funny timetravel stuff here :)
        self.start = self.start-len
        
    def rwd( self, len=0 ):
        # and here.
        self.start = self.start+len
        if self.start > time.time():
            self.start = time.time()
            
    def draw( self ):
        """
        Give information to the skin..
        """
        # XXX Let's wait a whole second :)
        if time.time() > (self.__lastupdate + 0.5):
            # print "Doing update of audio GUI..."
            self.elapsed = self.get_elapsed()
            self.remain  = self.get_remain()
            self.done    = self.get_done()
            self.__lastupdate = time.time()
            skin.DrawMP3( self )

        return

# ======================================================================
# End of AudioInfo class
# ======================================================================



t_bitrate = [
  [
    [0,32,48,56,64,80,96,112,128,144,160,176,192,224,256],
    [0,8,16,24,32,40,48,56,64,80,96,112,128,144,160],
    [0,8,16,24,32,40,48,56,64,80,96,112,128,144,160]
    ],
  [
    [0,32,64,96,128,160,192,224,256,288,320,352,384,416,448],
    [0,32,48,56,64,80,96,112,128,160,192,224,256,320,384],
    [0,32,40,48,56,64,80,96,112,128,160,192,224,256,320]
    ]
  ]
        
t_sampling_freq = [
  [22050, 24000, 16000],
  [44100, 48000, 32000]
  ]

frequency_tbl = {0:22050,1:24000,2:16000,3:44100,4:48000,5:32000,6:64000}


def getword(fp, off):
    fp.seek(off, 0)
    word = fp.read(4)
    return word

def get_l4 (s):
    return reduce (lambda a,b: ((a<<8) + b), map (long, map (ord, s)))

def get_xing_header (f):
    where = f.tell()
    try:
        f.seek(0)
        b = f.read(8192)
        i = string.find (b, 'Xing')
        if i > 0:
            # 32-bit fields; "Xing", flags, frames, bytes, 100 toc
            i = i + 4
            flags	= get_l4 (b[i:i+4]); i = i + 4
            frames	= get_l4 (b[i:i+4]); i = i + 4
            bytes	= get_l4 (b[i:i+4]); i = i + 4
            return flags, frames, bytes
        else:
            return None
    finally:
        f.seek (where)

MPG_MD_STEREO           = 0
MPG_MD_JOINT_STEREO     = 1
MPG_MD_DUAL_CHANNEL     = 2
MPG_MD_MONO             = 3

def get_newhead (word):
  word = get_l4 (word)
  if (word & (1<<20)):
    if (word & (1<<19)):
      lsf = 0
    else:
      lsf = 1
    mpeg25 = 0
  else:
    lsf = 1
    mpeg25 = 1
  lay = 4 - ((word>>17)&3)
  if mpeg25:
    sampling_frequency = 6 + ((word>>10) & 3)
  else:
    sampling_frequency = ((word>>10)&3) + (lsf * 3)
  error_protection 	= ((word>>16)&1) ^ 1
  bitrate_index 	= (word>>12) & 0xf
  padding 		= ((word >> 9) & 0x1)
  extension 		= ((word >> 8) & 0x1)
  mode	 		= ((word >> 6) & 0x3)
  mode_ext 		= ((word >> 4) & 0x3)
  copyright 		= ((word >> 3) & 0x1)
  original 		= ((word >> 2) & 0x1)
  emphasis 		= word & 0x3

  if mode == MPG_MD_MONO:
    stereo = 1
  else:
    stereo = 2


  return locals()
  import pprint
  pprint.pprint (locals())
  
def get_head(word):
    if len(word) != 4:
        return {}
    
    l = ord(word[0])<<24|ord(word[1])<<16|ord(word[2])<<8|ord(word[3])

    id             = (l>>19) & 1
    layer          = (l>>17) & 3
    protection_bit = (l>>16) & 1
    bitrate_index  = (l>>12) & 15
    sampling_freq  = (l>>10) & 3
    padding_bit    = (l>>9) & 1
    private_bit    = (l>>8) & 1
    mode           = (l>>6) & 3
    mode_extension = (l>>4) & 3
    copyright      = (l>>3) & 1
    original       = (l>>2) & 1
    emphasis       = (l>>0) & 1
    version_index  = (l>>19) & 3
    bytes          = l


    try:
        bitrate = t_bitrate[id][3-layer][bitrate_index]
    except IndexError:
        bitrate = 0

    try:
        fs = t_sampling_freq[id][sampling_freq]
    except IndexError:
        fs = 0

    return vars()


def is_mp3(h):
    #if h['bytes'] == -1: return 0
    if not (h['bitrate_index'] == 0 or \
            h['version_index'] == 1 or \
            ((h['bytes'] & 0xFFE00000) != 0xFFE00000) or \
            (not h['fs']) or \
            (not h['bitrate'])):
        return 1
    return 0

def get_v2head(fp):
    fp.seek(0,0)
    word = fp.read(3)
    if word != "ID3": return 0

    bytes = fp.read(2)
    major_version = ord(bytes[0])
    minor_version = ord(bytes[1])

    version = "ID3v2.%d.%d" % (major_version, minor_version)
    bytes = fp.read(1)
    unsync = (ord(bytes)>>7) & 1
    ext_header = (ord(bytes)>>6) & 1
    experimental = (ord(bytes)>>5) & 1

    bytes = fp.read(4)
    tagsize = 0

    for i in range(4):
        tagsize = tagsize + ord(bytes[3-i])*128*i

    if ext_header:
        ext_header_size = ext_header_size + 10
        bytes = fp.read(4)

    return vars()

def mp3info(fn):
    off = 0
    eof = 0
    h   = 0
    i   = 0
    tot = 4096

    if os.stat(fn)[6] == 0:
        return {}

    fp   = open(fn)
    word = getword(fp, off)

    if off==0:
        id3v2 = get_v2head(fp)
        if id3v2:
            off  = off + id3v2['tagsize']
            tot  = tot + off
            word = getword(fp, off)

    nh   = get_newhead( word )

    while 1:
        h = get_head(word)
        if not h: break
        off=off+1
        word = getword(fp, off)
        if off>tot: 
            print "BAD FILE", fn, os.stat(fn)[6]
            #os.unlink(fn)
            return {}

        if is_mp3(h): break


    fp.seek(0, 2)
    eof = fp.tell()

    try:
        fp.seek(-128, 2)
    except IOError, reason:
        return {}

	vbr = 0
    xh = get_xing_header (fp)
    if xh:
    	# Override the bitrate if a Xing header is present
        flags, xing_frames, xing_bytes = xh
	if DEBUG: 
		print "Flags: "+ flags
		print "Xing Frames: " + xing_frames
		print "Xing Byttes: " + xing_bytes
	if (flags & 0x08):
		if DEBUG:
			print "Sampling Index: " + nh['sampling_frequency']
		tpf = float([0,384,1152,1152,576][int(nh['lay'])])
		tpf = tpf / ([44100, 48000, 32000, 22050, 24000, 16000, 22050, 12000, 8000, 44100][int(nh['sampling_frequency'])] << nh['lsf'])
		h['bitrate'] = (xing_bytes * 8.) / (tpf * xing_frames * 1000)
		if DEBUG: 
			print "VBR: " + h['bitrate']

    if h['id']:
        h['mean_frame_size'] = (144000. * h['bitrate']) / h['fs']
    else:
        h['mean_frame_size'] = (72000. * h['bitrate']) / h['fs']

    h['layer'] = h['mode']
    h['freq_idx'] = 3*h['id'] + h['sampling_freq']

    h['length'] = ((1.0*eof-off) / h['mean_frame_size']) * ((115200./2)*(1.+h['id']))/(1.0*h['fs'])
    h['secs'] = int(h['length'] / 100);
  

    i = {}
    i['VERSION'] = h['id']
    i['MM'] = int(h['secs']/60)
    i['SS'] = h['secs']%60
    i['STEREO'] = not(h['mode'] == 3)
    if h['layer'] >= 0:
        if h['layer'] == 3:
            i['LAYER'] = 2
        else:
            i['LAYER'] = 3
    else:
        i['LAYER'] = ''
    i['MODE'] = h['mode']
    i['COPYRIGHT'] = h['copyright']
    if h['bitrate'] >=0:
        i['BITRATE'] = h['bitrate']
    else:
        i['BITRATE'] = ''
    if h['freq_idx'] >= 0:
        i['FREQUENCY'] = frequency_tbl[h['freq_idx']]
    else:
        i['FREQUENCY'] = ''

    return i
			    
