
# make the command menu using the command_items array and when we call refresh with the reload arg we go back to the main menu.
command_menu = menu.Menu(_('Commands'), command_items, reload_func=menuwidget.goto_main_menu)

#make a basic menu with the string variable name for its name and items the array of choices.
mymenu = menu.Menu(name, items)
