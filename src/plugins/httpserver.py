import logging
import kaa
from kaa.base.net.httpserver import HTTPServer

import json

# freevo imports
from .. import core as freevo

log = logging.getLogger('freevo')

class PluginInterface( freevo.Plugin ):
    """
    """

    application = None
    last_view = 0, ''

    __signals_connected = False

    def __init__(self):
        """
        """
        super(PluginInterface, self).__init__()
        self.signals = kaa.Signals('update')
        port = freevo.config.plugin.httpserver.port
        self.server = HTTPServer(("", port))
        self.server.serve_forever()
        self.server.add_handler('/event/', self.event)
        self.server.add_handler('/view', self.view)
        self.server.add_handler('/select/', self.select)
        self.server.add_static('/', freevo.FREEVO_SHARE_DIR + '/httpserver/simple.html')
        self.server.add_static('/jquery', freevo.FREEVO_SHARE_DIR + '/httpserver/jquery')
        freevo.signals['application-change'].connect(self.application_change)

    def application_change(self, app):
        self.application = app
        if app.name == 'menu' and not self.__signals_connected:
            freevo.signals['application-change'].connect(self.signals['update'].emit)
            self.application.signals['refresh'].connect(self.signals['update'].emit)
            self.__signals_connected = True
            
    def _get_view(self):
        if self.application and self.application.name == 'menu':
            items = []
            for pos, item in enumerate(self.application.current.choices):
                items.append({'name': item.name, 'id': pos})
            return { 'type': 'menu', 'menu': items }
        if self.application and self.application.name == 'audioplayer':
            properties = self.application.item.properties
            return { 'type': 'audioplayer', 'title': properties.title, 'artist': properties.artist, 'album': properties.album }
        return { 'type': 'unknown' }

    @kaa.coroutine()
    def view(self, path, known=None, **attributes):
        while True:
            result = self._get_view()
            if not known or known != str(self.last_view[0]):
                result['status'] = self.last_view[0]
                yield "application/json", json.dumps(result)
            # we need to wait for an update
            yield kaa.inprogress(self.signals['update'])
            result = str(self._get_view())
            if result != self.last_view[1]:
                self.last_view = self.last_view[0] + 1, result

    @kaa.coroutine()
    def select(self, path, **attributes):
        if self.application and self.application.name == 'menu':
            menu = self.application.current
            if path.lower() == 'back':
                self.application.back_one_menu()
            elif path.lower() == 'home':
                self.application.back_to_menu(self.application[0])
            elif path.lower() == 'submenu':
                pass
            else:
                menu.select(menu.choices[int(path)])
                self.application.refresh()
                yield kaa.delay(0.2)
                actions = menu.selected._get_actions()
                if actions:
                    actions[0]()
        yield "application/json", "{}"

    def event(self, path, **attributes):
        freevo.Event(path).post()
        yield "application/json", "{}"

