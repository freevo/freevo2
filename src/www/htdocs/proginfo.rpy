#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# proginfo.rpy - Dynamically update program info popup box.
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
#endif

import sys, string
import time

from www.web_types import HTMLResource, FreevoResource
from twisted.web.woven import page

import util.tv_util as tv_util
import util
import config 
import tv.record_client as ri
from twisted.web import static

MAX_DESCRIPTION_CHAR = 1000

class ProgInfoResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        form = request.args
        id = fv.formValue(form, 'id')
        chanid = id[:id.find(":")]
        starttime = int( id[id.find(":")+1:] )

        t0=time.time()
        guide = tv_util.get_guide()
        t1=time.time()
        (got_schedule, schedule) = ri.getScheduledRecordings()
        if got_schedule:
            schedule = schedule.getProgramList()

        chan = guide.chan_dict[chanid]
        for prog in chan.programs:
            if prog.start == starttime:
                break

        if prog.desc == '':
            desc = (_('Sorry, the program description for ' \
                      '%s is unavailable.')) % ('<b>'+prog.title+'</b>')
        else:
            desc = prog.desc
                                                                                                                                   
        desc = desc.lstrip()
        if MAX_DESCRIPTION_CHAR and len(desc) > MAX_DESCRIPTION_CHAR:
            desc=desc[:desc[:MAX_DESCRIPTION_CHAR].rfind('.')] + '. [...]'

        if prog.sub_title:
            desc = '"%s"<br/>%s' % (prog.sub_title,desc)

        fv.res += (
           u"<script>\n" \
           u"var doc = parent.top.document;\n" \
           u"doc.getElementById('program-title').innerHTML = '%s';\n"\
           u"doc.getElementById('program-desc').innerHTML = '%s';\n"\
           u"doc.getElementById('program-start').innerHTML = '%s';\n"
           u"doc.getElementById('program-end').innerHTML = '%s';\n"\
           u"doc.getElementById('program-runtime').innerHTML = '%s';\n"\
           u"doc.getElementById('program-record-button').onclick = %s;\n"\
           u"doc.getElementById('program-favorites-button').onclick = %s;\n"\
           u"doc.getElementById('program-waiting').style.display = 'none';\n" \
           u"doc.getElementById('program-info').style.visibility = 'visible';\n" \
           u"</script>\n"
        ) % ( prog.title.replace("'", "\\'") , desc.replace("'", "\\'"),
              time.strftime(config.TV_TIMEFORMAT,
                            time.localtime( prog.start ) ),
              time.strftime(config.TV_TIMEFORMAT,
                            time.localtime( prog.stop ) ),
              int( ( prog.stop - prog.start ) / 60 ),
              "function() { doc.location=\"record.rpy?chan=%s&start=%s&action=add\"; }" % (chanid, starttime),
              "function() { doc.location=\"edit_favorite.rpy?chan=%s&start=%s&action=add\"; }" % (chanid, starttime),

        )

        return String( fv.res )

resource = ProgInfoResource()
