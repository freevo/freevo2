import plugin

class FooReceiverPlugin(plugin.DaemonPlugin):
    """
    Counting foo
    """
    def __init__(self):
        DaemonPlugin.__init__(self)
        self.foo = 0

    def eventhandler(self, event, menuw=None):
        if event == 'foo':
            self.foo += 1
            return True
        return False

