#!/usr/bin/python

import sys, cgi, time
import html_util as fv

so = sys.stdout
sys.stdout = sys.stderr

import rec_interface as ri

TRUE = 1
FALSE = 0

form = cgi.FieldStorage()

find = fv.formValue(form, 'find')

progs = ri.findMatches(find)

recordings = ri.getScheduledRecordings()
rec_progs = recordings.getProgramList()

sys.stdout = so

fv.printContentType()
fv.printHeader('Search Results', 'styles/main.css')

fv.tableOpen('border=0 cellpadding=4 cellspacing=1 width="100%"')
fv.tableRowOpen('class="chanrow"')
fv.tableCell('<img src="images/logo_200x100.png">', 'align=left')
fv.tableCell('Search Results', 'class="heading" align="left"')
fv.tableRowClose()
fv.tableClose()

fv.tableOpen('border=0 cellpadding=4 cellspacing=1 width="100%"')
fv.tableRowOpen('class="chanrow"')
fv.tableCell('Start Time', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Stop Time', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Channel', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Title', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Program Description', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Actions', 'class="guidehead" align="center" colspan="1"')
fv.tableRowClose()

for prog in progs:

    status = 'basic'
    for rp in rec_progs.values():
        if rp.start == prog.start and rp.channel_id == prog.channel_id:
            status = 'scheduled'
            try:
                if rp.isRecording == TRUE:
                    status = 'recording'
            except:
                sys.stderr.write('isRecording not set')

    fv.tableRowOpen('class="chanrow"')
    fv.tableCell(time.strftime('%b %d %H:%M', time.localtime(prog.start)), 'class="'+status+'" align="left" colspan="1"')
    fv.tableCell(time.strftime('%b %d %H:%M', time.localtime(prog.stop)), 'class="'+status+'" align="left" colspan="1"')
    fv.tableCell(prog.channel_id, 'class="'+status+'" align="left" colspan="1"')
    fv.tableCell(prog.title, 'class="'+status+'" align="left" colspan="1"')

    if prog.desc == '':
        cell = 'Sorry, the program description for "%s" is unavailable.' % prog.title
    else:
        cell = prog.desc
    fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')

    if status == 'scheduled':
        cell = '<a href="record.cgi?chan=%s&start=%s&action=remove">Remove</a>' % (prog.channel_id, prog.start)
    elif status == 'recording':
        cell = '<a href="record.cgi?chan=%s&start=%s">Record</a>' % (prog.channel_id, prog.start)
    else:
        cell = '<a href="record.cgi?chan=%s&start=%s">Record</a>' % (prog.channel_id, prog.start)

    fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')

    fv.tableRowClose()

fv.tableClose()

fv.printSearchForm()

fv.printLinks()

fv.printFooter()
