# you would then create a menu like normal and then push it onto the stack
command_items += [menu.MenuItem(_('No Commands found'), menuwidget.goto_prev_page, 0)]

# generic item use for things that are simple
# you would then create a menu like normal and then push it onto the stack
if item.info.has_key('audio'):
    items.append(menu.MenuItem(_('Audio selection'), audio_selection_menu, item))
if item.info.has_key('subtitles'):
    items.append(menu.MenuItem(_('Subtitle selection'), subtitle_selection_menu, item))
if item.info.has_key('chapters'):
    items.append(menu.MenuItem(_('Chapter selection'), chapter_selection_menu, item))                                                                                
