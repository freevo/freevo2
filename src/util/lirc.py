# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# util/lirc.py - A module to help with some lirc tasks.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2005/06/25 08:52:29  dischi
# switch to new style python classes
#
# Revision 1.2  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.1  2003/10/11 11:57:11  rshortt
# A new module to help with lirc.  This contains a lircd.conf file parser which
# I will be using for some infrared transmitting modules.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al. 
# Please see the file doc/CREDITS for a complete list of authors.
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


import string, os, re


def parse_lircd(conf):
    remotes = {}
    remote = None
    input_codes = 0

    try:
        lircd = open(conf, 'r')
    except:
        print 'Unable to open %s.' % conf
        return

    for line in lircd.readlines():
        line = string.strip(line)
        if not line or line[0] == '#':  continue

        data = line.split()
        if len(data) < 2:  continue

        if data[0].lower() == 'begin' and data[1].lower() == 'remote':
            remote = LircRemote()
            continue

        if remote:
            if input_codes:
                if data[0].lower() == 'end' and data[1].lower() == 'codes':
                    input_codes = 0
                    continue

                #remote.codes[data[0]] = long(data[1])
                remote.codes[data[0]] = data[1]
                continue

            if data[0].lower() == 'name':
                remote.name = data[1]

            elif data[0].lower() == 'bits':
                remote.bits = int(data[1])

            elif data[0].lower() == 'flags':
                remote.flags = data[1]

            elif data[0].lower() == 'eps':
                remote.eps = int(data[1])

            elif data[0].lower() == 'aeps':
                remote.aeps = int(data[1])

            elif data[0].lower() == 'one':
                remote.one[0] = int(data[1])
                remote.one[1] = int(data[2])

            elif data[0].lower() == 'zero':
                remote.zero[0] = int(data[1])
                remote.zero[1] = int(data[2])

            elif data[0].lower() == 'plead':
                remote.plead = int(data[1])

            elif data[0].lower() == 'gap':
                remote.gap = int(data[1])

            elif data[0].lower() == 'toggle_bit':
                remote.toggle_bit = int(data[1])

            elif data[0].lower() == 'begin' and data[1].lower() == 'codes':
                input_codes = 1
                continue

        if data[0].lower() == 'end' and data[1].lower() == 'remote':
            remotes[remote.name] = remote

    return remotes


            
def dump_remotes(remotes):
    for remote in remotes.values():
        print 'Remote: %s' % remote.name
        print '        bits: %d' % remote.bits
        print '        flags: %s' % remote.flags
        print '        eps: %d' % remote.eps
        print '        aeps: %d' % remote.aeps
        print '        one: %d %d' % (remote.one[0], remote.one[1])
        print '        zero: %d %d' % (remote.zero[0], remote.zero[1])
        print '        plead: %d' % remote.plead
        print '        gap: %d' % remote.gap
        print '        toggle_bit: %d' % remote.toggle_bit
        print '        Codes:'
        for code in remote.codes.keys():
            print '               %s: %s' % (code, remote.codes[code])


class LircRemote(object):

    def __init__(self):
        self.name = 'undefined'
        self.bits = 0
        self.flags = None
        self.eps = 0
        self.aeps = 0
        self.one = [0, 0]
        self.zero = [0, 0]
        self.plead = 0
        self.gap = 0
        self.toggle_bit = 0
        self.codes = {}

# dump_remotes(parse_lircd('/etc/lircd.conf'))
