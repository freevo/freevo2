# list of items to go in the menu
mylistofitems = []

# a call to a function that returns an array of objects you would create
# your menu from. for example a call to os.listdir to return a list of strings
# containing filenames
mylistofobjects = some_func_that_returns_you_list()

# loop through our object list and add each item to the list for the menu 
for myobject in mylistofobjects:
    img_item = ImageItem(myobject, self)
    mylistofitems += [ img_item ]

# handle the no objects found case if we get an empty list
# this uses a single menu item
if (len(mylistofitems) == 0):
    mylistofitems += [menu.MenuItem(_('No Objects found'),
                      menuw.back_one_menu, 0)]

# create the menu using your menu list 
myobjectmenu = menu.Menu(_('My Image Objects'), mylistofitems,
                         reload_func=menuw.back_one_menu )

# tells freevo to give rc control to the menu
rc.app(None)

# now we push our menu on the top of the stack and tell it to display
menuw.pushmenu(myobjectmenu)
menuw.refresh()

