# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# ioctl.py - A modules to make ioctl's in python easier.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/11/13 16:07:54  dischi
# fix ioctl future warning for now
#
# Revision 1.2  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.1  2003/10/11 11:54:22  rshortt
# A class to make using ioctls much easier.
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


import sys
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
    # FIXME: this is a very bad hack to avoid the future warning for
    # the next python version. The real code is nd = dir << _IOC_DIRSHIFT
    # but for dir > 1 this shifts the first 1 bit to position 32 which will
    # result in an overflow with sign changing. And I have no idea if this is
    # working in 2.4 or if it works on other machines than i386
    if dir == 1:
        nd = dir << _IOC_DIRSHIFT
    if dir == 2:
        nd = -2147483648
    if dir == 3:
        nd = -1073741824
    return (nd | (ord(type) << _IOC_TYPESHIFT) | 
            (nr << _IOC_NRSHIFT) | (size << _IOC_SIZESHIFT))

def IO(type,nr): return _IOC(_IOC_NONE,(type),(nr),0)
def IOR(type,nr,size): return _IOC(_IOC_READ,(type),(nr),struct.calcsize(size))
def IOW(type,nr,size): return _IOC(_IOC_WRITE,(type),(nr),struct.calcsize(size))
def IOWR(type,nr,size): return _IOC(_IOC_READ|_IOC_WRITE,(type),(nr),struct.calcsize(size))

# used to decode ioctl numbers..
def IOC_DIR(nr): return (((nr) >> _IOC_DIRSHIFT) & _IOC_DIRMASK)
def IOC_TYPE(nr): return (((nr) >> _IOC_TYPESHIFT) & _IOC_TYPEMASK)
def IOC_NR(nr): return (((nr) >> _IOC_NRSHIFT) & _IOC_NRMASK)
def IOC_SIZE(nr): return (((nr) >> _IOC_SIZESHIFT) & _IOC_SIZEMASK)

ioctl  = fcntl.ioctl
pack   = struct.pack
unpack = struct.unpack
