class DaemonPlugin(Plugin):

    # Variables:
    self.poll_interval  = 1
    self.poll_menu_only = True
    self.event_listener = False

    # Functions
    def __init__(self):
        pass
    
    def poll(self):
        pass
    
    def draw(self(type, object), osd):
        pass

    def eventhandler(self, event, menuw=None):
        return False
    
    def shutdown(self):
        pass
    
