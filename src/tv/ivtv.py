# -*- coding: iso-8859-1 -*-
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
# Revision 1.19  2005/06/25 08:52:28  dischi
# switch to new style python classes
#
# Revision 1.18  2004/12/05 13:01:12  dischi
# delete old tv variables, rename some and fix detection
#
# Revision 1.17  2004/11/15 22:57:32  rshortt
# -use util.ioctl for what we can
# -calculate ioctl numbers instead of hardcoding them, this gets rid of future warnings
# -add more stream types: IVTV_STREAM_VCD, IVTV_STREAM_SVCD, IVTV_STREAM_DVD_S1, IVTV_STREAM_DVD_S2.
#
# Revision 1.16  2004/08/13 16:17:33  rshortt
# More work on tv settings, configuration of v4l2 devices based on TV_CARDS.
#
# Revision 1.15  2004/08/13 15:25:28  rshortt
# Remove TV_IVTV_OPTIONS in favour of new TV_CARDS.
#
# Revision 1.14  2004/08/12 16:52:49  rshortt
# Work on autodetecting tv cards.
#
# Revision 1.13  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.12  2003/12/31 16:05:34  rshortt
# No longer override setstd because the mspSetMatrix() call was only to work
# around a (fixed) ivtv bug.  Also removed the setinput call because that is
# now taken care of by the VideoGroup and channels.py.
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


import string, struct, fcntl, time
from util.ioctl import ioctl, IOR, IOW, IOWR

import tv.v4l2, config


# Stream types 
IVTV_STREAM_PS     =  0
IVTV_STREAM_TS     =  1
IVTV_STREAM_MPEG1  =  2
IVTV_STREAM_PES_AV =  3
IVTV_STREAM_PES_V  =  5
IVTV_STREAM_PES_A  =  7
IVTV_STREAM_DVD    = 10
IVTV_STREAM_VCD    = 11
IVTV_STREAM_SVCD   = 12
IVTV_STREAM_DVD_S1 = 13
IVTV_STREAM_DVD_S2 = 14


# structs and ioctls

CODEC_ST = '15I'
IVTV_IOC_G_CODEC = IOR('@', 48, CODEC_ST)
IVTV_IOC_S_CODEC = IOW('@', 49, CODEC_ST)

MSP_MATRIX_ST = '2i'
IVTV_IOC_S_MSP_MATRIX = IOW('@', 210, MSP_MATRIX_ST)


class IVTV(tv.v4l2.Videodev):

    def __init__(self, which=None, device=None):
        tv.v4l2.Videodev.__init__(self, which, device)


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
        r = ioctl(self.devfd, IVTV_IOC_S_CODEC, val)


    def getCodecInfo(self):
        val = struct.pack( CODEC_ST, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 )
        r = ioctl(self.devfd, IVTV_IOC_G_CODEC, val)
        codec_list = struct.unpack(CODEC_ST, r)
        return IVTVCodec(codec_list)


    def mspSetMatrix(self, input=None, output=None):
        if not input: input = 3
        if not output: output = 1

        val = struct.pack(MSP_MATRIX_ST, input, output)
        r = ioctl(self.devfd, IVTV_IOC_S_MSP_MATRIX, val)


    def init_settings(self):
        tv.v4l2.Videodev.init_settings(self)

        if not self.settings:
            return


        (width, height) = string.split(self.settings.resolution, 'x')
        self.setfmt(int(width), int(height))

        codec = self.getCodecInfo()

        codec.aspect        = self.settings.aspect
        codec.audio_bitmask = self.settings.audio_bitmask
        codec.bframes       = self.settings.bframes
        codec.bitrate_mode  = self.settings.bitrate_mode
        codec.bitrate       = self.settings.bitrate
        codec.bitrate_peak  = self.settings.bitrate_peak
        codec.dnr_mode      = self.settings.dnr_mode
        codec.dnr_spatial   = self.settings.dnr_spatial
        codec.dnr_temporal  = self.settings.dnr_temporal
        codec.dnr_type      = self.settings.dnr_type
        codec.framerate     = self.settings.framerate
        codec.framespergop  = self.settings.framespergop
        codec.gop_closure   = self.settings.gop_closure
        codec.pulldown      = self.settings.pulldown
        codec.stream_type   = self.settings.stream_type

        self.setCodecInfo(codec)


    def print_settings(self):
        tv.v4l2.Videodev.print_settings(self)

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


class IVTVCodec(object):
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


