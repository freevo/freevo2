import plugin
import rc
from event import *

class FooSenderPlugin(plugin.DaemonPlugin):
    """
    Sending foo events
    """
    def __init__(self):
        DaemonPlugin.__init__(self)
        self.poll_interval  = 100

    def poll(self):
        rc.post_event(Event('foo'))
        
