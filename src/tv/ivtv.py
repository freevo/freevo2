#if 0 /*
# -----------------------------------------------------------------------
# ivtv.py - Python interface to ivtv based capture cards.
# -----------------------------------------------------------------------
# $Id$
#
# Notes: http://ivtv.sf.net
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2003/08/02 12:56:41  rshortt
# Increase the sleep time because 0.3 was too short for some people.
#
# Revision 1.7  2003/07/30 23:04:01  rshortt
# Work around an msp3400 bug where it will lose sound when doing a few things,
# one of which is setting the video standard.  Right now it calls the newly added
# mspSetMatrix() method with no args -- it is possible the default input and
# output values here are not valid for some users.  This should be fixed in
# the driver soon but I will make these values configurable if it becomes a
# problem for users in the meantime.
#
# Revision 1.6  2003/07/24 00:57:30  rshortt
# Remove framespergop setting for now.  We don't want to hardcode an NTSC
# setting for anyone in PAL or SECAM land.
#
# Revision 1.5  2003/07/14 17:08:45  rshortt
# Remove setting the framerate and rely on the card's initialized defaults instead.
#
# Revision 1.4  2003/07/14 11:44:42  rshortt
# Add some init and print methods to Videodev and IVTV.
#
# Revision 1.3  2003/07/11 00:27:23  rshortt
# Added a mspSetMatrix which is currently not used by anything.
#
# This was previously needed to correct an audio problem that is now fixed
# by specifying standard as a msp3400 modprobe option.
#
# Revision 1.2  2003/07/07 01:59:06  rshortt
# Updating for current ivtv CVS, added bitrate_mode and use constant bitrate
# by default.
#
# Revision 1.1  2003/06/01 16:05:40  rshortt
# Further suport for ivtv based cards.  Now you can set the bitrate to encode at or the stream type to use.
#
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

import string, struct, fcntl, time

import v4l2, config

# ioctls
IVTV_IOC_G_CODEC = 0xFFEE7703
IVTV_IOC_S_CODEC = 0xFFEE7704
MSP_SET_MATRIX =   0x40086D11

# Stream types 
IVTV_STREAM_PS     = 0
IVTV_STREAM_TS     = 1
IVTV_STREAM_MPEG1  = 2
IVTV_STREAM_PES_AV = 3
IVTV_STREAM_PES_V  = 5
IVTV_STREAM_PES_A  = 7
IVTV_STREAM_DVD    = 10

# structs
CODEC_ST = '15I'
MSP_MATRIX_ST = '2i'


class IVTV(v4l2.Videodev):

    def __init__(self, device):
        v4l2.Videodev.__init__(self, device)


    def setCodecInfo(self, codec):
        val = struct.pack( CODEC_ST, 
                           codec.aspect,
                           codec.audio_bitmask,
                           codec.bframes,
                           codec.bitrate_mode,
                           codec.bitrate,
                           codec.bitrate_peak,
                           codec.dnr_mode,
                           codec.dnr_spatial,
                           codec.dnr_temporal,
                           codec.dnr_type,
                           codec.framerate,
                           codec.framespergop,
                           codec.gop_closure,
                           codec.pulldown,
                           codec.stream_type)
        r = fcntl.ioctl(self.device, IVTV_IOC_S_CODEC, val)


    def setstd(self, value):
        v4l2.Videodev.setstd(self, value)
        time.sleep(1)
        self.mspSetMatrix()


    def getCodecInfo(self):
        val = struct.pack( CODEC_ST, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 )
        r = fcntl.ioctl(self.device, IVTV_IOC_G_CODEC, val)
        codec_list = struct.unpack(CODEC_ST, r)
        return IVTVCodec(codec_list)


    def mspSetMatrix(self, input=None, output=None):
        if not input: input = 3
        if not output: output = 1

        val = struct.pack(MSP_MATRIX_ST, input, output)
        r = fcntl.ioctl(self.device, MSP_SET_MATRIX, val)


    def init_settings(self, opts=None):
        if not opts:
            opts = config.IVTV_OPTIONS

        v4l2.Videodev.init_settings(self)

        self.setinput(opts['input'])

        (width, height) = string.split(opts['resolution'], 'x')
        self.setfmt(int(width), int(height))

        codec = self.getCodecInfo()

        codec.aspect        = opts['aspect']
        codec.audio_bitmask = opts['audio_bitmask']
        codec.bframes       = opts['bframes']
        codec.bitrate_mode  = opts['bitrate_mode']
        codec.bitrate       = opts['bitrate']
        codec.bitrate_peak  = opts['bitrate_peak']
        codec.dnr_mode      = opts['dnr_mode']
        codec.dnr_spatial   = opts['dnr_spatial']
        codec.dnr_temporal  = opts['dnr_temporal']
        codec.dnr_type      = opts['dnr_type']
        # XXX: Ignore framerate for now, use the card's initialized default.
        # codec.framerate     = opts['framerate']
        # XXX: Ignore framespergop for now, use the card's initialized default.
        # codec.framespergop  = opts['framespergop']
        codec.gop_closure   = opts['gop_closure']
        codec.pulldown      = opts['pulldown']
        codec.stream_type   = opts['stream_type']

        self.setCodecInfo(codec)


    def print_settings(self):
        v4l2.Videodev.print_settings(self)

        codec = self.getCodecInfo()

        print 'CODEC::aspect: %s' % codec.aspect
        print 'CODEC::audio_bitmask: %s' % codec.audio_bitmask
        print 'CODEC::bfrmes: %s' % codec.bframes
        print 'CODEC::bitrate_mode: %s' % codec.bitrate_mode
        print 'CODEC::bitrate: %s' % codec.bitrate
        print 'CODEC::bitrate_peak: %s' % codec.bitrate_peak
        print 'CODEC::dnr_mode: %s' % codec.dnr_mode
        print 'CODEC::dnr_spatial: %s' % codec.dnr_spatial
        print 'CODEC::dnr_temporal: %s' % codec.dnr_temporal
        print 'CODEC::dnr_type: %s' % codec.dnr_type
        print 'CODEC::framerate: %s' % codec.framerate
        print 'CODEC::framespergop: %s' % codec.framespergop
        print 'CODEC::gop_closure: %s' % codec.gop_closure
        print 'CODEC::pulldown: %s' % codec.pulldown
        print 'CODEC::stream_type: %s' % codec.stream_type


class IVTVCodec:
    def __init__(self, args):
        self.aspect        = args[0]
        self.audio_bitmask = args[1]
        self.bframes       = args[2]
        self.bitrate_mode  = args[3]
        self.bitrate       = args[4]
        self.bitrate_peak  = args[5]
        self.dnr_mode      = args[6]
        self.dnr_spatial   = args[7]
        self.dnr_temporal  = args[8]
        self.dnr_type      = args[9]
        self.framerate     = args[10]
        self.framespergop  = args[11]
        self.gop_closure   = args[12]
        self.pulldown      = args[13]
        self.stream_type   = args[14]


