# kaa imports
from kaa.notifier import EventHandler, Timer

# freevo core imports
import freevo.ipc

# freevo ui imports
import plugin
import application
from event import *

class PluginInterface(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)
        self.__events = EventHandler(self.eventhandler)
        self.__timer = Timer(self.update_idle_time)
        self.idle_time = 0

        mbus = freevo.ipc.Instance()
        mbus.connect('freevo.ipc.status')
        mbus.connect_rpc(self.play, 'home-theatre.play')
        mbus.connect_rpc(self.stop, 'home-theatre.stop')
        mbus.connect_rpc(self.status, 'home-theatre.status')

        self.status = mbus.status
        self.status.set('idle', 0)
        self.status.set('playing', '')

        
    def plugin_activate(self):
        """
        Execute on activation of the plugin.
        """
        plugin.Plugin.plugin_activate(self)
        self.idle_time = 0
        self.__events.register()
        self.__timer.start(60)

        
    def play(self, file):
        app = application.get_active()
        if not app or app.get_name() != 'menu':
            raise RuntimeError('freevo not in menu mode')

        for p in plugin.mimetype(None):
            i = p.get(None, [ file ] )
            if i and hasattr(i[0], 'play'):
                i[0].play()
                return []
            
        raise RuntimeError('no player found')


    def stop(self):
        STOP.post()
        return []


    def status(self):
        """
        Send status on rpc status request.
        """
        app = application.get_active()
        if not app or app.get_name() != 'menu':
            self.idle_time = 0
        status = { 'idle': self.idle_time }
        return status


    def eventhandler(self, event):
        # each event resets the idle time
        if event == PLAY_START and event.arg and hasattr(event.arg, 'url'):
            self.status.set('playing', event.arg.url)
        if event == PLAY_END:
            self.status.set('playing', '')
        self.idle_time = 0
        return True


    def update_idle_time(self):
        app = application.get_active()
        if app and app.get_name() == 'menu':
            self.idle_time += 1
            self.status.set('idle', self.idle_time)
        return True
