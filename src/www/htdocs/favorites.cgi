#!/usr/bin/python

import sys, cgi, time
import html_util as fv

so = sys.stdout
sys.stdout = sys.stderr

import rec_interface as ri
import rec_favorites as rf

TRUE = 1
FALSE = 0

form = cgi.FieldStorage()

action = fv.formValue(form, 'action')
oldname = fv.formValue(form, 'oldname')
name = fv.formValue(form, 'name')
title = fv.formValue(form, 'title')
chan = fv.formValue(form, 'chan')
dow = fv.formValue(form, 'dow')
mod = fv.formValue(form, 'mod')
priority = fv.formValue(form, 'priority')



if action == 'remove':
    rf.removeFavorite(name)
    pass
elif action == 'add':
    rf.addEditedFavorite(name, title, chan, dow, mod, priority)
    pass
elif action == 'edit':
    rf.removeFavorite(oldname)
    rf.addEditedFavorite(name, title, chan, dow, mod, priority)
elif action == 'bump':
    rf.adjustPriority(name, priority)
else:
    pass

favorites = rf.getFavorites()

sys.stdout = so

days = {
    '0' : 'Monday',
    '1' : 'Tuesday',
    '2' : 'Wednesday',
    '3' : 'Thursday',
    '4' : 'Friday',
    '5' : 'Saturday',
    '6' : 'Sunday'
}

fv.printContentType()
fv.printHeader('Favorites', 'styles/main.css')

fv.tableOpen('border=0 cellpadding=4 cellspacing=1 width="100%"')
fv.tableRowOpen('class="chanrow"')
fv.tableCell('<img src="images/logo_200x100.png">', 'align=left')
fv.tableCell('Favorites', 'class="heading" align="left"')
fv.tableRowClose()
fv.tableClose()

fv.tableOpen('border=0 cellpadding=4 cellspacing=1 width="100%"')
fv.tableRowOpen('class="chanrow"')
fv.tableCell('Favorite Name', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Program', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Channel', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Day of week', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Time of day', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Actions', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Priority', 'class="guidehead" align="center" colspan="1"')
fv.tableRowClose()

f = lambda a, b: cmp(a.priority, b.priority)
favs = favorites.values()
favs.sort(f)
for fav in favs:
    status = 'favorite'

    fv.tableRowOpen('class="chanrow"')
    fv.tableCell(fav.name, 'class="'+status+'" align="left" colspan="1"')
    fv.tableCell(fav.title, 'class="'+status+'" align="left" colspan="1"')
    fv.tableCell(fav.channel_id, 'class="'+status+'" align="left" colspan="1"')

    if fav.dow != 'ANY':
        # cell = time.strftime('%b %d %H:%M', time.localtime(fav.start))
        cell = '%s' % days[fav.dow]
    else:
        cell = 'ANY'
    fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')

    if fav.mod != 'ANY':
        # cell = time.strftime('%b %d %H:%M', time.localtime(fav.start))
        cell = '%s' % ri.minToTOD(fav.mod)
    else:
        cell = 'ANY'
    fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')

    # cell = '<input type="hidden" name="action" value="%s">' % action
    cell = '<a href="edit_favorite.cgi?action=edit&name=%s">Edit</a>, ' % fav.name
    cell += '<a href="favorites.cgi?action=remove&name=%s">Remove</a>' % fav.name
    fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')

    cell = ''

    if favs.index(fav) != 0:
        tmp_prio = int(fav.priority) - 1
        cell += '<a href="favorites.cgi?action=bump&name=%s&priority=-1">Higher</a>' % fav.name

    if favs.index(fav) != 0 and favs.index(fav) != len(favs)-1:
        cell += ' | '

    if favs.index(fav) != len(favs)-1:
        tmp_prio = int(fav.priority) + 1
        cell += '<a href="favorites.cgi?action=bump&name=%s&priority=1">Lower</a>' % fav.name

    fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')

    fv.tableRowClose()

fv.tableClose()

fv.printSearchForm()

fv.printLinks()

fv.printFooter()
