class CoolItem(Item):
    def __init__(self, command):
        Item.__init__(self)
        self.name = command
        self.image = util.getimage(self.cmd)

    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.runMyCommand , _('Run Command') ) ]
        return items

    def runMyCommand(self, arg=None, menuw=None):
        # do some real cool stuff..

