from plugin import MainMenuPlugin

import config
import skin
import os

skin = skin.get_singleton()

from item import Item


TRUE  = 1
FALSE = 0


class ShutdownItem(Item):
    """
    Item for shutdown
    """
    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.shutdown_freevo, 'Shutdown Freevo' ),
                  ( self.shutdown_system, 'Shutdown system' ) ]
        if config.ENABLE_SHUTDOWN_SYS:
            items.reverse()
        return items


    def shutdown_freevo(self, arg=None, menuw=None):
        """
        shutdown freevo, don't shutdown the system
        """
        import main
        main.shutdown(menuw=menuw, arg=FALSE)

        
    def shutdown_system(self, arg=None, menuw=None):
        """
        shutdown the complete system
        """
        import main
        main.shutdown(menuw=menuw, arg=TRUE)
    


#
# the plugins defined here
#

class shutdown(MainMenuPlugin):
    def __init__(self):
        pass

    def desc(self):
        return 'the shutdown plugin'

    def parameter(self):
        return 'None'
    
    def items(self, parent):
        menu_items = skin.settings.mainmenu.items

        item = ShutdownItem()
        item.name = menu_items['shutdown'].name
        if menu_items['shutdown'].icon:
            item.icon = os.path.join(skin.settings.icon_dir, menu_items['shutdown'].icon)
        if menu_items['shutdown'].image:
            item.image = menu_items['shutdown'].image
        item.parent = parent
        
        return [ item ]


