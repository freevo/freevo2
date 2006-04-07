# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# machine.py - Handles machine definitions that Freevo knows about
# -----------------------------------------------------------------------------
#
# Various utilities and handling functions for different machine types.
#
# First Edition: Chris Lack <crl@lsmheatandair.com>
# Maintainer:    Chris Lack <crl@lsmheatandair.com>
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
# Please see the file doc/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import config
from emu import UserEmu


def ext(machine):
    """
    Returns a list of extensions to search for based on machine type.
    """
    extensions = { 'GB' : 'gb',
                   'GBC' : 'gbc',
                   'GBA' : 'gba',
                   'VBOY' : 'vb',
                   'NES' : 'nes',
                   'SNES' : 'smc',
                   'N64' : [ 'rom', 'z64', 'v64' ],
                   'GG' : [ 'gg' ],
                   'SG1K' : [ 'sc', 'sg' ],
                   'SMS' : [ 'sms' ],
                   'SMD' : [ 'bin', 'smd' ],
                   'LYNX' : [ 'o', 'lnx' ],
                   '2600' : 'a26',
                   '5200' : [ 'bin', 'a52' ],
                   '7800' : 'a78',
                   'JAG'  : 'jag',
                   'PCE'  : 'pce',
                   'SGX'  : 'pce'
                 }

    if machine in extensions:
        return extensions[machine]

    log.warning('Unknown machine type %s' % machine)
    return None


def title(system):
    """
    Returns the standard name for a machine type
    """
    titles = { 'GB' : 'Nintendo Gameboy (Handheld)',
               'GBC' : 'Nintendo Gameboy Color (Handheld)',
               'GBA' : 'Nintendo Gameboy Advance (Handheld)',
               'VBOY' : 'Nintendo VirtualBoy',
               'NES' : 'Nintendo Entertainment System',
               'SNES' : 'Super Nintendo',
               'N64' : 'Nintendo 64',
               'GG' : 'Sega Game Gear (Handheld)',
               'SG1K' : 'Sega SG-1000/SC-3000',
               'SMS' : 'Sega Master System',
               'SMD' : 'Sega Megadrive',
               'LYNX' : 'Atari Lynx (Handheld)',
               '2600' : 'Atari 2600',
               '5200' : 'Atari 5200',
               '7800' : 'Atari 7800',
               'JAG'  : 'Atari Jaguar',
               'PCE'  : 'NEC PC-Engine',
               'SGX'  : 'NEC Supergrafx'
             }

    if system in titles:
        return titles[system]

    log.warning('Unknown machine type %s' % system)
    return None


def emu(gameitem):
    """
    Determines which emu we're running
    """
    emus = {
             'USER' : UserEmu(gameitem),
             'GB' : UserEmu(gameitem),
             'GBC' : UserEmu(gameitem),
             'GBA' : UserEmu(gameitem),
             'VBOY' : UserEmu(gameitem),
             'NES' : UserEmu(gameitem),
             'SNES' : UserEmu(gameitem),
             'N64' : UserEmu(gameitem),
             'GG' : UserEmu(gameitem),
             'SG1K' : UserEmu(gameitem),
             'SMS' : UserEmu(gameitem),
             'SMD' : UserEmu(gameitem),
             'LYNX' : UserEmu(gameitem),
             '2600' : UserEmu(gameitem),
             '5200' : UserEmu(gameitem),
             '7800' : UserEmu(gameitem),
             'JAG'  : UserEmu(gameitem),
             'PCE'  : UserEmu(gameitem),
             'SGX'  : UserEmu(gameitem)
           }

    if config.GAMES_ITEMS[gameitem.gi_ind][0] in emus:
        return emus[config.GAMES_ITEMS[gameitem.gi_ind][0]]

    log.warning('Unknown machine type %s' % gameitem.machine)
    return None
