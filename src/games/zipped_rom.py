# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# zipped_rom.py - Handles game roms that are zipped
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.1  2004/01/10 21:25:01  mikeruelle
# zipped rom support for snes and genesis
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


from zipfile import *
import os.path
from string import rfind, lower

def unzip_rom(file, ext_list):
    """
    Unzips a zipped ROM and returns the name of the unzipped file
    which is placed in /tmp, or returns simply the 'file' argument if it is not
    zipped. ext_list is a list of extensions that ROMS can use.
    Returns the name of the unzipped ROM, or None.
    """
    if is_zipfile(file):
        zip_file = ZipFile(file)
        info = zip_file.namelist()
        for f in info:
             ext_pos = rfind(f, '.')
             if ext_pos > -1:
                 ext = f[ext_pos+1:]
                 if lower(ext) in ext_list:
                     tmp_file = os.path.join('/tmp', os.path.basename(f))
                     content = zip_file.read(f)
                     unzipped_file = open(os.path.join('/tmp', tmp_file), 'w')
                     unzipped_file.write(content)
                     unzipped_file.close()
                     return tmp_file
    return None

