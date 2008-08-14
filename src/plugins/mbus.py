# kaa imports
import kaa
import kaa.beacon

# freevo core imports
import freevo.ipc
from freevo import plugin

# freevo ui imports
from freevo.ui import application
from freevo.ui.event import PLAY_START, PLAY_END
from freevo.ui.directory import DirItem
from freevo.ui.menu import MediaPlugin

import logging
log = logging.getLogger('mbus')

class PluginInterface(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)
        self.__events = kaa.EventHandler(self.eventhandler)
        self.__timer = kaa.Timer(self.update_idle_time)
        self.idle_time = 0

        mbus = freevo.ipc.Instance()
        mbus.connect(self)
        mbus.connect('freevo.ipc.status')

        self.status = mbus.status
        self.status.set('idle', 0)
        self.status.set('playing', '')

        self.__events.register()
        self.__timer.start(60)

        
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


    @freevo.ipc.expose('home-theatre.play')
    @kaa.coroutine()
    def play(self, file, type=None):
        log.info('play %s with %s', file, type)
        app = application.get_active()
        if not app or app.get_name() != 'menu':
            raise RuntimeError('freevo not in menu mode')

        listing = (yield kaa.beacon.query(filename=kaa.unicode_to_str(file))).get(filter='extmap')

        # normal file
        for p in MediaPlugin.plugins(type):
            i = p.get(None, listing)
            if i and hasattr(i[0], 'play'):
                i[0].play()
                yield []

        # directory
        for i in listing.get_dir():
            pl = DirItem(i, None, type=type)
            pl.play()
            # Now this is ugly. If we do nothing 'pl' will be deleted by the
            # garbage collector, so we have to store it somehow
            self.__pl_for_gc = pl
            yield []

        raise RuntimeError('no player found')


    @freevo.ipc.expose('home-theatre.stop')
    def stop(self):
        log.info('stop')
        STOP.post()
        return []

    @freevo.ipc.expose('home-theatre.message')
    def message(self, msg):
        OSD_MESSAGE.post(msg)
        return []
