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
# Revision 1.4  2004/11/14 19:20:59  dischi
# fix future warning
#
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

def unsiged(x):
    if x > sys.maxint:
        return int(~(-x % sys.maxint) - 1)
    return int(x)

def lshift(x, y):
    return unsiged(long(x) << y)

def _IOC(dir,type,nr,size):
    # Note: this functions uses lshift to avoid future warnings. It
    # may not work every time and is more or less a bad hack
    return (lshift(dir, _IOC_DIRSHIFT) | (ord(type) << _IOC_TYPESHIFT) | 
            (nr << _IOC_NRSHIFT) | (size << _IOC_SIZESHIFT))

def IO(type,nr):
    return _IOC(_IOC_NONE,(type),(nr),0)

def IOR(type,nr,size):
    return _IOC(_IOC_READ,(type),(nr),struct.calcsize(size))

def IOW(type,nr,size):
    return _IOC(_IOC_WRITE,(type),(nr),struct.calcsize(size))

def IOWR(type,nr,size):
    return _IOC(_IOC_READ|_IOC_WRITE,(type),(nr),struct.calcsize(size))

# used to decode ioctl numbers..
def IOC_DIR(nr): return (((nr) >> _IOC_DIRSHIFT) & _IOC_DIRMASK)
def IOC_TYPE(nr): return (((nr) >> _IOC_TYPESHIFT) & _IOC_TYPEMASK)
def IOC_NR(nr): return (((nr) >> _IOC_NRSHIFT) & _IOC_NRMASK)
def IOC_SIZE(nr): return (((nr) >> _IOC_SIZESHIFT) & _IOC_SIZEMASK)

ioctl  = fcntl.ioctl
pack   = struct.pack
unpack = struct.unpack
