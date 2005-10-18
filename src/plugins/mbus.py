# kaa imports
from kaa.notifier import EventHandler, Timer

# freevo core imports
from freevo import mcomm

# freevo ui imports
import plugin
import application
import event

class PluginInterface(plugin.Plugin, mcomm.RPCServer):
    def __init__(self):
        plugin.Plugin.__init__(self)
        mcomm.RPCServer.__init__(self)
        self.__events = EventHandler(self.eventhandler)
        self.__timer = Timer(self.update_idle_time)
        self.idle_time = 0
        
    def plugin_activate(self):
        """
        Execute on activation of the plugin.
        """
        plugin.Plugin.plugin_activate(self)
        self.idle_time = 0
        self.__events.register()
        self.__timer.start(60)
        
        
    def __rpc_play__(self, addr, val):
        file = self.parse_parameter(val, ( str, ))

        app = application.get_active()
        if not app or app.get_name() != 'menu':
            return mcomm.RPCError('freevo not in menu mode')

        for p in plugin.mimetype(None):
            i = p.get(None, [ file ] )
            if i and hasattr(i[0], 'play'):
                i[0].play()
                return mcomm.RPCReturn()

        return mcomm.RPCError('no player found')


    def __rpc_stop__(self, addr, val):
        event.STOP.post()
        return mcomm.RPCReturn()


    def __rpc_status__(self, addr, val):
        """
        Send status on rpc status request.
        """
        app = application.get_active()
        if not app or app.get_name() != 'menu':
            self.idle_time = 0
        status = { 'idle': self.idle_time }
        return mcomm.RPCReturn(status)


    def eventhandler(self, event):
        # each event resets the idle time
        self.idle_time = 0
        return True


    def update_idle_time(self):
        self.idle_time += 1
        return True
