# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# program.py - A program class for the epg
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/08/10 19:35:45  dischi
# o better index generation
# o split into different files
# o support for other parsers than xmltv
# o internal caching
#
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


import time
import config

NO_DATA = _('no data')

class TvProgram:
    """
    All information about one TV program
    """
    def __init__(self, title='', start=0, stop=0):
        self.channel_id = ''
        self.title      = title
        self.desc       = ''
        self.sub_title  = ''
        self.start      = start
        self.stop       = stop
        self.ratings    = {}
        self.advisories = []
        self.categories = []
        self.date       = None
        self.pos        = None
        if title == NO_DATA:
            self.valid = False
        else:
            self.valid = True
        
        # Due to problems with Twisted's marmalade this should not be changed
        # to a boolean type. 
        self.scheduled  = 0


    def __unicode__(self):
        """
        return as unicode for debug
        """
        bt = time.localtime(self.start)   # Beginning time tuple
        et = time.localtime(self.stop)    # End time tuple
        begins = '%s-%02d-%02d %02d:%02d' % (bt[0], bt[1], bt[2], bt[3], bt[4])
        ends   = '%s-%02d-%02d %02d:%02d' % (et[0], et[1], et[2], et[3], et[4])
        return u'%s to %s  %3s ' % (begins, ends, self.channel_id) + \
                   self.title + u' (%s)' % self.pos


    def __str__(self):
        """
        return as string for debug
        """
        return String(self.__unicode__())

    
    def __cmp__(self, other):
        """
        compare function, return 0 if the objects are identical, 1 otherwise
        """
        if not other:
            return 1
        return self.title != other.title or \
               self.start != other.start or \
               self.stop  != other.stop or \
               self.channel_id != other.channel_id


    def getattr(self, attr):
        """
        return the specific attribute as string or an empty string
        """
        if attr == 'start':
            return Unicode(time.strftime(config.TV_TIMEFORMAT, time.localtime(self.start)))
        if attr == 'stop':
            return Unicode(time.strftime(config.TV_TIMEFORMAT, time.localtime(self.stop)))
        if attr == 'date':
            return Unicode(time.strftime(config.TV_DATEFORMAT, time.localtime(self.start)))
        if attr == 'time':
            return self.getattr('start') + u' - ' + self.getattr('stop')
        if hasattr(self, attr):
            return getattr(self,attr)
        return ''



