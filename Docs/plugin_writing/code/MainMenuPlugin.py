import os
import config
import plugin
import menu
import rc

from item import Item
from image.imageitem import ImageItem

# In addition to these two classes you might need a specialized subclass
# of Item to put in your menu. Here i used ImageItem for brevity.

# This is the item that does most of the action. It builds the menu
# that happens after clicking on the module.
class CoolMainMenuItem(Item):
    def __init__(self, parent, neededargument):
        Item.__init__(self, parent, skin_type='image')
        self.name = _( 'APOD' )
        self.importantData = neededargument

    # this is what happens when you click on the module in the menu
    def actions(self):
        return [ ( self.create_cool_menu , 'Show Cool Module' ) ]

    # creates a submenu with two choices
    def create_cool_menu(self, arg=None, menuw=None):
        myitems = []
	myitems += [menu.MenuItem(_('Cool Choice1'), action=self.doChoice1)]
	myitems += [menu.MenuItem(_('Cool Choice2'), action=self.doChoice2)]
        cool_menu = menu.Menu( _( 'Cool Menu' ), myitems)
        rc.app(None)
        menuw.pushmenu(cool_menu)
        menuw.refresh()

    # create a submenu again this time with image items
    def doChoice1(self, arg=None, menuw=None):
        mylistofitems = []
        mylistofobjects = some_func_that_returns_you_list()

        for myobject in mylistofobjects:
            img_item = ImageItem(myobject, self)
            mylistofitems += [ img_item ]

        if (len(mylistofitems) == 0):
            mylistofitems += [menu.MenuItem(_('No Objects found'),
                              menuw.back_one_menu, 0)]

        myobjectmenu = menu.Menu(_('My Image Objects'), mylistofitems,
                                 reload_func=menuw.back_one_menu )

        rc.app(None)
        menuw.pushmenu(myobjectmenu)
        menuw.refresh()

    # display an image if we select this option in the menu
    def doChoice2(self, arg=None, menuw=None):
        imgitem = ImageItem(self.importantData, self)
	imgitem.view(menuw=menuw)

# This class basically only exists to give the item to the main menu and
# to setup variables to pass to the real meat of the plugin above. The
# reason for this setup is that plugins generally don't have eventhandlers
# and mimetype stuff needed for menus so we create a shell for an Item to take
# over and do the cool stuff.
class PluginInterface(plugin.MainMenuPlugin):
    """
    Put your description of your cool plugin here.

    plugin.activate('cool', args=('/tmp/cool.jpg',))

    """
    def __init__(self, cooldata=None):
        if not cooldata:
            self.reason = _('Need an arg to display.')
            return
	
	if not os.path.isfile(cooldata):
	    self.reason = _('%s does not exist.') % cooldata
            return

	self.importantData = cooldata

        # init the plugin
        plugin.MainMenuPlugin.__init__(self)

    def items(self, parent):
            return [ CoolMainMenuItem(parent, self.importantData) ]
	                                                                                    


