#!/usr/bin/python

import sys
import time

import html_util as fv
import web

so = sys.stdout
sys.stdout = sys.stderr

import config 
import xmltv
import epg_xmltv 
import rec_interface as ri
import rec_favorites as rf

# Set to 1 for debug output
DEBUG = 0

TRUE = 1
FALSE = 0

INTERVAL = web.INTERVAL
n_cols = web.n_cols

guide = epg_xmltv.get_guide()
schedule = ri.getScheduledRecordings().getProgramList()
favs = rf.getFavorites()


sys.stdout = so

fv.printContentType()
fv.printHeader('Freevo TV Guide', web.STYLESHEET, web.JAVASCRIPT)

fv.tableOpen('border=0 cellpadding=4 cellspacing=1 width="100%"')
fv.tableRowOpen('class="chanrow"')
fv.tableCell('<img src="images/logo_200x100.png">', 'align=left')
fv.tableCell('TV Guide', 'class="heading" align="left"')
fv.tableRowClose()
fv.tableClose()

print('<HR>\n')

pops = ''
desc = ''

fv.tableOpen('border=0 cellpadding=4 cellspacing=1')

fv.tableRowOpen('class="chanrow"')
fv.tableCell(time.strftime('%b %d'), 'class="guidehead"')
now = int(time.time() / INTERVAL) * INTERVAL
for i in range(n_cols):
    fv.tableCell(time.strftime('%H:%M', time.localtime(now)), 'class="guidehead"')
    now += INTERVAL
fv.tableRowClose()

for chan in guide.chan_list:
    now = time.time()
    fv.tableRowOpen('class="chanrow"')
    fv.tableCell(chan.displayname, 'class="channel"')
    c_left = n_cols

    if not chan.programs:
        fv.tableCell('<< NO DATA >>', 'class="program" colspan=%s' % n_cols)

    for prog in chan.programs:
        if c_left > 0:

            status = 'program'

            if ri.isProgScheduled(prog, schedule):
                status = 'scheduled'
                really_now = time.time()
                if prog.start <= really_now and prog.stop >= really_now:
                    # in the future we should REALLY see if it is 
                    # recording instead of just guessing
                    status = 'recording'

            if prog.start <= now and prog.stop >= now:
                cell = ""
                if prog.start <= now - INTERVAL:
                    # show started earlier than the guide start,
                    # insert left arrows
                    cell += '<< '
                showtime_left = int(prog.stop - now)
                intervals = showtime_left / INTERVAL
                colspan = intervals + 1
                cell += '%s' % prog.title
                if colspan > c_left:
                    # show extends past visible range,
                    # insert right arrows
                    cell += '  >>'
                    colspan = c_left
                popid = '%s:%s' % (prog.channel_id, prog.start)
                pops += '<div id="%s"  class="proginfo" >\n' % popid
                pops += '  <div class="move" onmouseover="focusPop(\'%s\');" onmouseout="unfocusPop(\'%s\');" style="cursor:move">%s</div>\n' % (popid, popid, prog.title)
                if prog.desc == '':
                    desc = 'Sorry, the program description for "%s" is unavailable.' % prog.title
                else:
                    desc = prog.desc
                pops += '  <div class="progdesc"><br><font color=black>%s</font><br><br></div>\n' % desc
                pops += '  <div class="poplinks" style="cursor:hand">\n' 
                pops += '    <table width="100%" border=0 cellpadding=4 cellspacing=0>\n'
                pops += '      <tr>\n'
                pops += '        <td class="popbottom" '
                pops += 'onClick="document.location=\'record.cgi?chan=%s&start=%s\'">Record</td>\n' % (prog.channel_id, prog.start)
                pops += '        <td class="popbottom" '
                pops += 'onClick="document.location=\'edit_favorite.cgi?chan=%s&start=%s&action=add\'">Add to Favorites</td>\n' % (prog.channel_id, prog.start)
                pops += '        <td class="popbottom" '
                pops += 'onClick="javascript:closePop(\'%s\');">Close Window</td>\n' % popid
                pops += '      </tr>\n'
                pops += '    </table>\n'
                pops += '  </div>\n'
                pops += '</div>\n'
                fv.tableCell(cell, 'class="'+status+'" onclick="showPop(\'%s\', this)" colspan=%s' % (popid, colspan))
                now += INTERVAL*colspan
                c_left -= colspan
    fv.tableRowClose()
fv.tableClose()

print pops

fv.printSearchForm()

fv.printLinks()

fv.printFooter()

