# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# passwd.py - Freevo helper to generate passwords for Freevo usage.
# -----------------------------------------------------------------------------
# $Id$
#
# Notes:
#   Right now we only have WWW_USERS but in the future we can support
#   these username / password pairs in other parts of Freevo.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rshortt@users.sf.net>
# Maintainer:    Rob Shortt <rshortt@users.sf.net>
#
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
# -----------------------------------------------------------------------------

import crypt
import sys
from optparse import OptionParser

import config


def main():
    parser = OptionParser()

    parser.add_option('-u', '--username', dest='username', default=None,
                      help='The username to generate a WWW password for.')
    parser.add_option('-p', '--password', dest='password', default=None,
                      help='The password to encrypt.')

    (options, args) = parser.parse_args()


    if not options.username or not options.password:
        parser.print_help()
        sys.exit(0)

    newcryptpass = crypt.crypt(options.password, 'WW')

    config.WWW_USERS[options.username] = newcryptpass

    print 'Here is a new WWW_USERS that you may use in local_conf.py:\n'
    print 'WWW_USERS = {'
    for u,p in config.WWW_USERS.items():
        print '    "%s" : "%s",' % (u, p)
    print '}'


if __name__ == '__main__':
    main()

