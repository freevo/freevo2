# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# configfile.py - read the freevo config file
# -----------------------------------------------------------------------------
# $Id$
#
# This file needs to be called from __init__ with execfile because
# it needs to globals() and locals() from the basic module
#
# Note: depending on execfile is a bad
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Krister Lagerstrom <krister-freevo@kmlager.com>
#
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
# -----------------------------------------------------------------------------

import sys
import freevo.conf

def print_config_changes(conf_version, file_version, changelist):
    """
    print changes made between version on the screen
    """
    ver_old = float(file_version)
    ver_new = float(conf_version)
    if ver_old == ver_new:
        return
    print
    print 'You are using version %s, changes since then:' % file_version
    changed = [(cv, cd) for (cv, cd) in changelist if cv > ver_old]
    if not changed:
        print 'The changelist has not been updated'
        print 'Please notify the developers!'
    else:
        for change_ver, change_desc in changed:
            print 'Version %s:' % change_ver
            for line in change_desc.split('\n'):
                print '    ', line.strip()
            print
    print
            

#
# Config file handling
#
cfgfilepath = [ '.', os.path.expanduser('~/.freevo'), '/etc/freevo',
                '/usr/local/etc/freevo' ]


#
# Check that freevo_config.py is not found in the config file dirs
#
for dirname in cfgfilepath[1:]:
    freevoconf = dirname + '/freevo_config.py'
    if os.path.isfile(freevoconf):
        log.critical(('freevo_config.py found in %s, please remove it ' +
                      'and use local_conf.py instead!') % freevoconf)
        sys.exit(1)
        
#
# Load freevo_config.py:
#
FREEVO_CONFIG = os.path.join(freevo.conf.SHAREDIR, 'freevo_config.py')
if os.path.isfile(FREEVO_CONFIG):
    log.info('Loading cfg: %s' % FREEVO_CONFIG)
    execfile(FREEVO_CONFIG, globals(), locals())
    
else:
    log.critical("Error: %s: no such file" % FREEVO_CONFIG)
    sys.exit(1)


#
# Search for local_conf.py:
#

has_config = False
for a in sys.argv:
    if has_config == True:
        has_config = a
    if a == '-c':
        has_config = True
    
for dirname in cfgfilepath:
    if isinstance(has_config, str):
        overridefile = has_config
    else:
        overridefile = dirname + '/local_conf.py'
    if os.path.isfile(overridefile):
        log.info('Loading cfg overrides: %s' % overridefile)
        execfile(overridefile, globals(), locals())

        try:
            CONFIG_VERSION
        except NameError:
            print
            print 'Error: your local_config.py file has no version information'
            print 'Please check freevo_config.py for changes and set'
            print 'CONFIG_VERSION in %s to %s' % \
                  (overridefile, LOCAL_CONF_VERSION)
            print
            sys.exit(1)

        if int(str(CONFIG_VERSION).split('.')[0]) < 5:
            print
            print 'Error: You local_conf.py is too old, too much has changed.'
            print 'Please check freevo_config.py for changes and set'
            print 'CONFIG_VERSION in %s to %s' % \
                  (overridefile, LOCAL_CONF_VERSION)
            print
            sys.exit(1)
            
        if int(str(CONFIG_VERSION).split('.')[0]) != \
           int(str(LOCAL_CONF_VERSION).split('.')[0]):
            print
            print 'Error: The version information in freevo_config.py doesn\'t'
            print 'match the version in your local_config.py.'
            print 'Please check freevo_config.py for changes and set'
            print 'CONFIG_VERSION in %s to %s' % \
                  (overridefile, LOCAL_CONF_VERSION)
            print_config_changes(LOCAL_CONF_VERSION, CONFIG_VERSION,
                                  LOCAL_CONF_CHANGES)
            sys.exit(1)

        if int(str(CONFIG_VERSION).split('.')[1]) != \
           int(str(LOCAL_CONF_VERSION).split('.')[1]):
            log.warning('freevo_config.py was changed.\n' +
                        'Please check your local_config.py')
            print_config_changes(LOCAL_CONF_VERSION, CONFIG_VERSION, 
                                 LOCAL_CONF_CHANGES)
        break

else:
    locations = ''
    for dirname in cfgfilepath:
        locations += '  %s\n' % dirname
    log.critical("""local_conf.py not found
Freevo is not completely configured to start

The configuration is based on three files. This may sound oversized, but this
way it's easier to configure. First Freevo loads a file called 'freevo.conf'.
This file will be generated by 'freevo setup'. Use 'freevo setup --help' to get
information about the parameter. Based on the informations in that file, Freevo
will guess some settings for your system. This takes place in a file called
'freevo_config.py'. Since this file may change from time to time, you should
not edit this file. After freevo_config.py is loaded, Freevo will look for a
file called 'local_conf.py'. You can overwrite the variables from
'freevo_config.py' in here. There is an example for 'local_conf.py' called
'local_conf.py.example' in the Freevo distribution.
    
The location of freevo_config.py is %s
Freevo searches for freevo.conf and local_conf.py in the following locations:
%s

Since it's highly unlikly you want to start Freevo without further
configuration, Freevo will exit now.
"""  % (FREEVO_CONFIG, locations))
    sys.exit(0)

