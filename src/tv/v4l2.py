#if 0 /*
# -----------------------------------------------------------------------
# v4l2.py - V4L2 python interface.
# -----------------------------------------------------------------------
# $Id$
#
# Notes: http://bytesex.org/v4l/spec/
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/05/29 12:08:45  rshortt
# Make sure we close the device when done.
#
# Revision 1.1  2003/05/28 23:32:50  rshortt
# V4L device control by Thomas Schueppel.
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

import freq
import os
import struct
import fcntl

_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2

_IOC_NRMASK = ((1 << _IOC_NRBITS)-1)
_IOC_TYPEMASK = ((1 << _IOC_TYPEBITS)-1)
_IOC_SIZEMASK = ((1 << _IOC_SIZEBITS)-1)
_IOC_DIRMASK = ((1 << _IOC_DIRBITS)-1)

_IOC_NRSHIFT = 0 
_IOC_TYPESHIFT = (_IOC_NRSHIFT+_IOC_NRBITS)
_IOC_SIZESHIFT = (_IOC_TYPESHIFT+_IOC_TYPEBITS)
_IOC_DIRSHIFT = (_IOC_SIZESHIFT+_IOC_SIZEBITS)

# Direction bits.
_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ = 2

def _IOC(dir,type,nr,size):
    return (((dir)  << _IOC_DIRSHIFT) | \
           (ord(type) << _IOC_TYPESHIFT) | \
           ((nr)   << _IOC_NRSHIFT) | \
           ((size) << _IOC_SIZESHIFT))

def _IO(type,nr): return _IOC(_IOC_NONE,(type),(nr),0)
def _IOR(type,nr,size): return _IOC(_IOC_READ,(type),(nr),struct.calcsize(size))
def _IOW(type,nr,size): return _IOC(_IOC_WRITE,(type),(nr),struct.calcsize(size))
def _IOWR(type,nr,size): return _IOC(_IOC_READ|_IOC_WRITE,(type),(nr),struct.calcsize(size))

# used to decode ioctl numbers..
def _IOC_DIR(nr): return (((nr) >> _IOC_DIRSHIFT) & _IOC_DIRMASK)
def _IOC_TYPE(nr): return (((nr) >> _IOC_TYPESHIFT) & _IOC_TYPEMASK)
def _IOC_NR(nr): return (((nr) >> _IOC_NRSHIFT) & _IOC_NRMASK)
def _IOC_SIZE(nr): return (((nr) >> _IOC_SIZESHIFT) & _IOC_SIZEMASK)

FREQUENCY_ST = "III32x"
GETFREQ_NO   = _IOWR('V', 56, FREQUENCY_ST)
SETFREQ_NO   = _IOW('V', 57, FREQUENCY_ST)

SETFREQ_NO_V4L = _IOW('v', 15, "L")

QUERYCAP_ST  = "16s32s32sLL16x"
QUERYCAP_NO  = _IOR('V',  0, QUERYCAP_ST)

ENUMSTD_ST   = "LQ24s2LL16x"
ENUMSTD_NO   = _IOWR('V', 25, ENUMSTD_ST)

STANDARD_ST  = "Q"
GETSTD_NO    = _IOR('V', 23, STANDARD_ST)
SETSTD_NO    = _IOW('V', 24, STANDARD_ST)

ENUMINPUT_ST = "L32sLLLQL16x"
ENUMINPUT_NO = _IOWR('V', 26, ENUMINPUT_ST)

INPUT_ST  = "L";
GETINPUT_NO  = _IOR('V', 38, INPUT_ST)
SETINPUT_NO  = _IOWR('V', 39, INPUT_ST)

FMT_ST = "L7L4x168x"
GET_FMT_NO = _IOWR ('V',  4, FMT_ST)
SET_FMT_NO = _IOWR ('V',  5, FMT_ST)

TUNER_ST = "L32sLLLLLLll16x"
GET_TUNER_NO = _IOWR ('V', 29, TUNER_ST)
SET_TUNER_NO = _IOW  ('V', 30, TUNER_ST)

AUDIO_ST = "L32sLL8x"
GET_AUDIO_NO = _IOWR ('V', 33, AUDIO_ST)
SET_AUDIO_NO = _IOW  ('V', 34, AUDIO_ST)

class Videodev:
  def __init__(self, device):
      self.chanlist = None
      self.chanlistName = ""
      self.device = os.open (device, os.O_TRUNC)
      if self.device < 0:
          sys.exit("Error: %d\n" %self.device)
      else:
          print "Video Opened at %s" % device


  def close(self):
      os.close(self.device)


  def setchanlist(self, chanlist):
      self.chanlistName = chanlist
      self.chanlist = freq.CHANLIST[chanlist]

  def getfreq(self):
      val = struct.pack( FREQUENCY_ST, 0,0,0 )
      r = fcntl.ioctl(self.device, long(GETFREQ_NO), val)
      (junk,junk, freq, ) = struct.unpack(FREQUENCY_ST, r)
      return freq

  def setchannel(self, channel):
      freq = (self.chanlist[channel]*16)/1000
      try:
          self.setfreq(freq)
      except:
          self.setfreq_old(freq)
      
  def setfreq_old(self, freq):
      val = struct.pack( "L", freq)
      r = fcntl.ioctl(self.device, long(SETFREQ_NO_V4L), val)        

  def setfreq(self, freq):
      val = struct.pack( FREQUENCY_ST, long(0), long(0), freq)
      r = fcntl.ioctl(self.device, long(SETFREQ_NO), val)

  def getinput(self):
      r = fcntl.ioctl(self.device, GETINPUT_NO, struct.pack(INPUT_ST,0))
      return struct.unpack(INPUT_ST,r)[0]
  
  def setinput(self,value):
      r = fcntl.ioctl(self.device, SETINPUT_NO, struct.pack(INPUT_ST,value))


  def querycap(self):
      val = struct.pack( QUERYCAP_ST, "", "", "", 0, 0 )
      r = fcntl.ioctl(self.device, long(QUERYCAP_NO), val)
      return struct.unpack( QUERYCAP_ST, r )

  def enumstd(self, no):
      val = struct.pack( ENUMSTD_ST, no, 0, "", 0, 0, 0)
      r = fcntl.ioctl(self.device,ENUMSTD_NO,val)
      return struct.unpack( ENUMSTD_ST, r )

  def getstd(self):
      val = struct.pack( STANDARD_ST, 0 )
      r = fcntl.ioctl(self.device,GETSTD_NO, val)
      return struct.unpack( STANDARD_ST, r )[0]

  def setstd(self, value):
      val = struct.pack( STANDARD_ST, value )
      r = fcntl.ioctl(self.device,SETSTD_NO, val)

  def enuminput(self,index):
      val = struct.pack( ENUMINPUT_ST, index, "", 0,0,0,0,0)
      r = fcntl.ioctl(self.device,ENUMINPUT_NO,val)
      return struct.unpack( ENUMINPUT_ST, r )

  def getfmt(self):  
      val = struct.pack( FMT_ST, 0,0,0,0,0,0,0,0)
      r = fcntl.ioctl(self.device,GET_FMT_NO,val)
      return struct.unpack( FMT_ST, r )

  def setfmt(self, width, height):
      val = struct.pack( FMT_ST, 1L, width, height, 0L, 4L, 0L, 131072L, 0L)
      r = fcntl.ioctl(self.device,SET_FMT_NO,val)

  def gettuner(self,index):
      val = struct.pack( TUNER_ST, index, "", 0,0,0,0,0,0,0,0)
      r = fcntl.ioctl(self.device,GET_TUNER_NO,val)
      return struct.unpack( TUNER_ST, r )

  def settuner(self,index,audmode):
      val = struct.pack( TUNER_ST, index, "", 0,0,0,0,0,audmode,0,0)
      r = fcntl.ioctl(self.device,SET_TUNER_NO,val)

  def getaudio(self,index):
      val = struct.pack( AUDIO_ST, index, "", 0,0)
      r = fcntl.ioctl(self.device,GET_AUDIO_NO,val)
      return struct.unpack( AUDIO_ST, r )

  def setaudio(self,index,mode):
      val = struct.pack( AUDIO_ST, index, "", mode, 0)
      r = fcntl.ioctl(self.device,SET_AUDIO_NO,val)



