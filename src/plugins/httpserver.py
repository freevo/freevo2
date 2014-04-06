import os
import logging
import hashlib

import kaa
import kaa.beacon
from kaa.base.net.httpserver import HTTPServer

# freevo imports
from .. import core as freevo
from input.plugin import InputPlugin

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
        self.image_cache_images = { None: None }
        self.image_cache_hashes = { None: None }
        port = freevo.config.plugin.httpserver.port
        self.server = HTTPServer(("", port))
        self.server.serve_forever()
        self.server.add_json_handler('/event/', self.event)
        self.server.add_json_handler('/key/', self.key)
        self.server.add_json_handler('/view', self.view)
        self.server.add_json_handler('/select/', self.select)
        self.server.add_handler('/images/', self.images)
        self.server.add_static('/', freevo.FREEVO_SHARE_DIR + '/httpserver/simple.html')
        self.server.add_static('/jquery', freevo.FREEVO_SHARE_DIR + '/httpserver/jquery')
        freevo.signals['application-change'].connect(self.application_change)
        self.post_key = InputPlugin().post_key

    def application_change(self, app):
        self.application = app
        if app.name == 'menu' and not self.__signals_connected:
            self.application.signals['refresh'].connect(self.signals['update'].emit)
            self.__signals_connected = True
        self.signals['update'].emit()

    def register_image(self, image):
        original = image
        if isinstance(image, kaa.beacon.Thumbnail):
            image = image.name
        if image not in self.image_cache_images:
            hash = hashlib.md5(image).hexdigest() + os.path.splitext(image)[1]
            self.image_cache_images[image] = '/images/' + hash
            self.image_cache_hashes[hash] = original
        return self.image_cache_images[image]

    @kaa.coroutine()
    def view(self, path, known=None, **attributes):
        result = self.application.get_json(self)
        result['type'] = self.application.name
        if str(result) != self.last_view[1]:
            self.last_view = self.last_view[0] + 1, str(result)
        while True:
            if not known or known != str(self.last_view[0]):
                result = self.application.get_json(self)
                result['type'] = self.application.name
                result['status'] = self.last_view[0]
                yield result
            # we need to wait for an update
            yield kaa.inprogress(self.signals['update'])
            result = self.application.get_json(self)
            result['type'] = self.application.name
            if str(result) != self.last_view[1]:
                self.last_view = self.last_view[0] + 1, str(result)

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
                if menu.selected.type == 'video':
                    items = menu.selected.subitems
                    self.application.pushmenu(freevo.Menu(menu.selected.name, items, type='submenu'))
                else:
                    actions = menu.selected._get_actions()
                    if actions:
                        actions[0]()
        yield {}

    def event(self, path, **attributes):
        freevo.Event(path).post()
        return {}

    def key(self, path, **attributes):
        self.post_key(path)
        return {}

    @kaa.coroutine()
    def images(self, path, **attributes):
        if path in self.image_cache_hashes:
            image = self.image_cache_hashes[path]
            if isinstance(image, kaa.beacon.Thumbnail):
                if image.needs_update or 1:
                    yield kaa.inprogress(image.create(priority=kaa.beacon.Thumbnail.PRIORITY_HIGH))
                if attributes.get('size', '') == 'small':
                    image = image.normal
                elif attributes.get('size', '') == 'normal':
                    image = image.large
                else:
                    image = image.name
            if image:
                yield open(image).read(), None, None

