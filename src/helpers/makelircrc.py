#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# makelircrc.py - helper to generate lircrc
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/07/10 12:33:39  dischi
# header cleanup
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


import re
import config
import sys
import os

if len(sys.argv)>1 and sys.argv[1] == '--help':
    print 'script to write the freevo lircrc file'
    print 'usage: makelircrc [-w] [button=comand]'
    print
    print 'The -w will write the settings to %s' % config.LIRCRC
    print 'If this is not the file the informations should be written to, set'
    print 'LIRCRC in your local_conf.py to the correct filename. If the file'
    print 'exists, it will be overwritten.'
    print
    print 'If started with no options, this script will print the suggested mapping'
    print 'and a list of buttons not used right now and a list of events in Freevo'
    print 'without a button. You can either change EVENTS in local_conf.py or define'
    print 'a mapping on your own.'
    print
    sys.exit(0)


iscode = re.compile('^[ \t]*([^ #\t]*)[ \t]*(0x[0-9A-Fa-f]*)').match

needed  = []
mapping = []
unused  = []

alternatives = {
    'QUIT': 'EXIT',
    'OSD' : 'DISPLAY',
    'FF'  : 'FFWD',
    'REV' : 'REW',
    'PREV': 'CH-',
    'NEXT': 'CH+'
    }

for type in config.EVENTS:
    for button in config.EVENTS[type]:
        if not button in needed:
            needed.append(button)

write_option = False

for arg in sys.argv:
    if arg == '-w':
        write_option = True
    if arg.find('=') > 0:
        alternatives[arg[:arg.find('=')]] = arg[arg.find('=')+1:]
        
if os.path.exists('/etc/lircd.conf'): x = open('/etc/lircd.conf')
elif os.path.exists('/etc/lirc/lircd.conf'): x = open ('/etc/lirc/lircd.conf')

pos = 0
for line in x.readlines():
    if line.find('begin codes') != -1:
        pos = 1
    if pos > 0:
        if iscode(line):
            button = iscode(line).groups()[0]
            if button.upper() in needed:
                needed.remove(button.upper())
                mapping.append((button.upper(), button))
            
            elif alternatives.has_key(button.upper()) and \
                     alternatives[button.upper()] in needed:
                needed.remove(alternatives[button.upper()])
                mapping.append((alternatives[button.upper()], button))
            else:
                unused.append(button)
                mapping.append((button.upper(), button))
x.close()

if write_option:
    out = open(config.LIRCRC, 'w')
    for event, button in mapping:
        out.write('begin\n')
        out.write('    prog   = freevo\n')
        out.write('    button = %s\n' % button)
        out.write('    config = %s\n' % event)
        out.write('end\n')
    out.close()
    sys.exit(0)

print 'Mapping:'
print
for event, button in mapping:
    print '  %-10s: %-10s' % (button, event)
print
if unused:
    print 'The following buttons are not used by Freevo.'
    print 'You may want to enhance EVENTS in local_conf.py to make use of the buttons'
    print
    for i in unused:
        print '  %s' % i
    print
if needed:
    print 'The following buttons are needed for Freevo and not defined yet.'
    if unused:
        print 'Since you have unused buttons, you may want to set a button to a missing one'
        print 'Right now, the output file will have an unused mapping for %s. You' % unused[0]
        print 'could assign this button by calling this script with the extra parameter'+\
              '\'%s=%s\'.' % (unused[0], needed[0])
        print 'You can add this parameter as often as needed.'
        print 'Please send good mappings to missing buttons to the Freevo developers to add'
        print 'them into this script.'
    else:
        print 'Since there are no unused buttons anymore, you need to change EVENTS in'
        print 'local_conf.py'
    print
    for i in needed:
        print '  %s' % i
    print
    
