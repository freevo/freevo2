# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# epg_types.py - This file contains the types for the Freevo Electronic
#                Program Guide module.
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
# Revision 1.3  2004/08/09 21:19:46  dischi
# make tv guide working again (but very buggy)
#
# Revision 1.2  2004/08/05 17:16:05  dischi
# misc enhancements
#
# Revision 1.20  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.19  2004/07/01 22:49:49  rshortt
# Unicode fix.
#
# Revision 1.18  2004/06/22 01:07:49  rshortt
# Move stuff into __init__() and fix a bug for twisted's serialization.
#
# Revision 1.17  2004/03/05 20:49:11  rshortt
# Add support for searching by movies only.  This uses the date field in xmltv
# which is what tv_imdb uses and is really acurate.  I added a date property
# to TvProgram for this and updated findMatches in the record_client and
# recordserver.
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

from program import TvProgram

NO_DATA = _('no data')

class TvChannel:
    """
    Information about one channel, holding all programs
    """
    def __init__(self):
        self.id          = ''
        self.displayname = ''
        self.tunerid     = ''
        self.logo        = ''
        self.programs    = []
        self.index       = {}
        self.index_start = 0
        self.index_end   = 0

        
    def sort(self):
        """
        Sort the programs so that the earliest is first in the list
        """
        sort_function = lambda a, b: cmp(a.start, b.start)
        self.programs.sort(sort_function)
        dummy_programs = [ TvProgram(NO_DATA, 0, self.programs[0].start),
                           TvProgram(NO_DATA, self.programs[-1].stop, 2147483647) ]
        for i in range(len(self.programs)-1):
            if self.programs[i].stop + 60 < self.programs[i+1].start:
                # there is a hole in the data, fill it with dummy program
                dummy_programs.append(TvProgram(NO_DATA, self.programs[i].stop,
                                      self.programs[i+1].start))
        self.programs += dummy_programs
        self.programs.sort(sort_function)
        

    def __unicode__(self):
        """
        return as unicode for debug
        """
        s = u'CHANNEL ID   %-20s' % self.id
        
        if self.programs:
            s += u'\n'
            for program in self.programs:
                s += u'   ' + unicode(program) + u'\n'
        else:
            s += u'     NO DATA\n'
        return s


    def __str__(self):
        """
        return as string for debug
        """
        return String(self.__unicode__())
    

    def create_index(self):
        """
        create index for faster access
        """
        last     = 0
        index    = 0
        last_key = 0

        self.programs[0].index = 0
        for p in self.programs[1:]:
            index += 1
            p.index = index
            key = int(p.start) / (60 * 60 * 24)
            if not self.index_start:
                self.index_start = key
            self.index_end = key
            if not self.index.has_key(key):
                if last_key:
                    while len(self.index[last_key]) < 48:
                        self.index[last_key].append(last)
                self.index[key] = []
            pos = (int(p.start) / (60 * 30)) % (48)
            p.pos = pos
            
            if len(self.index[key]) >= pos + 1:
                last = index
                continue
            while len(self.index[key]) < pos:
                self.index[key].append(last)
            self.index[key].append(index)
            last = index
            last_key = key
        while len(self.index[key]) < 48:
            self.index[key].append(index)
            

    def __get_pos__(self, start, stop):
        """
        get internal positions for programs between start and stop
        """
        start -= 60 * 30
        key = int(start) / (60 * 60 * 24)
        if key < self.index_start:
            key = self.index_start
            pos = 0
        else:
            pos = (int(start) / (60 * 30)) % (48)

        start = max(self.index[key][pos], 0)
        
        key = int(stop) / (60 * 60 * 24)
        if key > self.index_end:
            key = self.index_end
            pos = 47
        else:
            pos = (int(stop) / (60 * 30)) % (48) + 1

        if pos >= 48:
            # next day
            key += 1
            if key > self.index_end:
                key = self.index_end
                pos = 47
            else:
                pos = 0

        stop = self.index[key][pos] + 1
        return start, stop

        
    def get(self, start, stop=0):
        """
        get programs between start and stop time or if stop=0, get
        the program running at 'start'
        """
        if not stop:
            stop = start
        start_p, stop_p = self.__get_pos__(start, stop)
        f = lambda p, a=start, b=stop: not (p.start > b or p.stop < a)
        try:
            return filter(f, self.programs[start_p:stop_p])
        except Exception, e:
            return []
                

    def next(self, prog):
        """
        return next program after 'prog'
        """
        pos  = min(len(self.programs)-1, prog.index + 1)
        prog = self.programs[pos]
        if pos < len(self.programs) and not prog.valid:
            return self.next(prog)
        return prog

    
    def prev(self, prog):
        """
        return previous program before 'prog'
        """
        pos = max(0, prog.index - 1)
        prog = self.programs[pos]
        if pos > 0 and not prog.valid:
            return self.prev(prog)
        return prog
