# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# font.py - Freevo font module
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
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

__all__ = [ 'get' ]

# python imports
import logging
import kaa.mevas

# freevo imports
from freevo.ui import config

# get logging object
log = logging.getLogger('gui')

# list of fonts already known to be not found
font_warning = []

class Font(object):
    """
    Freevo GUI font object based on the mevas font.
    """
    def __init__(self, name, ptsize):
        self.font   = self.__getfont(name, ptsize)
        self.height = self.font.get_text_size('')[3]
        self.chars  = {}
        self.name   = name
        self.ptsize = ptsize


    def charsize(self, c):
        """
        Return the width of the given char.
        """
        try:
            return self.chars[c]
        except:
            w = self.font.get_text_size(c)[0]
            self.chars[c] = w
            return w


    def stringsize(self, s):
        """
        Return the width of the given string.
        """
        s = self.font.get_text_size(s)
        return max(s[0], s[2])


    def __getfont(self, name, ptsize):
        """
        Load font into this object.
        """
        log.debug('Loading font "%s:%s"' % (name, ptsize))
        try:
            return kaa.mevas.imagelib.load_font(name, ptsize)
        except IOError:
            log.debug('Couldn\'t load font "%s"' % name)

            # Ok, see if there is an alternate font to use
            if name in config.GUI_FONT_ALIASES:
                alt_fname = config.GUI_FONT_ALIASES[name]
                log.debug('trying alternate: %s' % alt_fname)
                try:
                    return kaa.mevas.imagelib.load_font(alt_fname, ptsize)
                except IOError:
                    # not good
                    if not name in font_warning:
                        print 'WARNING: No alternate found in the alias list!'
                        print 'Falling back to default font, this looks ugly'
                        font_warning.append(name)
                    name = config.GUI_FONT_DEFAULT_NAME
                    return kaa.mevas.imagelib.load_font(name, ptsize)


# init mevas font (imlib2)
kaa.mevas.imagelib.add_font_path(config.FONT_DIR)

# the font cache object for 'get'
font_info_cache = {}

def get(font, ptsize):
    """
    Return the (cached) font
    """
    key = (font, ptsize)
    try:
        return font_info_cache[key]
    except:
        fi = Font(font, ptsize)
        font_info_cache[key] = fi
        return fi
