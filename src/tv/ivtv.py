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

import struct, fcntl

import v4l2

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


