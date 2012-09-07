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

    def __init__(self):
        """
        """
        super(PluginInterface, self).__init__()
        port = freevo.config.plugin.httpserver.port
        self.server = HTTPServer(("", port))
        self.server.serve_forever()
        self.server.add_handler('/event/', self.event)
        self.server.add_handler('/ui', self.ui)
        self.server.add_handler('/select/', self.select)
        freevo.signals['application-change'].connect(self.application_change)

    def application_change(self, app):
        self.application = app

    def event(self, path):
        freevo.Event(path).post()
        return "text/plain", "OK"

    def ui(self, path):
        if self.application and self.application.name == 'menu':
            items = []
            for pos, item in enumerate(self.application.current.choices):
                items.append({'name': item.name, 'id': pos})
            result = [ 'menu', items ]
            return "application/json", json.dumps(result)
        return "application/json", ""

    @kaa.coroutine()
    def select(self, path):
        yield kaa.delay(2)
        if self.application and self.application.name == 'menu':
            menu = self.application.current
            menu.select(menu.choices[int(path)])
            self.application.refresh()
            yield kaa.delay(0.2)
            actions = menu.selected._get_actions()
            if actions:
                actions[0]()
        yield "text/plain", ""
