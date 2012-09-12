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

    def __init__(self):
        """
        """
        super(PluginInterface, self).__init__()
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

    def event(self, path):
        freevo.Event(path).post()
        return "text/plain", "OK"

    def _get_menu(self):
        items = []
        for pos, item in enumerate(self.application.current.choices):
            items.append({'name': item.name, 'id': pos})
        return { 'type': 'menu', 'menu': items }

    @kaa.coroutine()
    def view(self, path, known=None, **attributes):
        if self.application and self.application.name == 'menu':
            while True:
                result = self._get_menu()
                if not known or known != str(self.last_view[0]):
                    result['status'] = self.last_view[0]
                    yield "application/json", json.dumps(result)
                # we need to wait for a menu update
                yield kaa.inprogress(self.application.signals['refresh'])
                result = str(self._get_menu())
                if result != self.last_view[1]:
                    self.last_view = self.last_view[0] + 1, result
        yield "application/json", ""

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
        yield "text/plain", ""
