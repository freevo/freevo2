import os

from kaa.utils import property
import kaa.imlib2
import kaa.candy

class Thumbnail(kaa.candy.Thumbnail):
    candyxml_style = 'mimetype'

    __item = __item_eval = None

    def __init__(self, pos, size, item, context=None):
        super(Thumbnail,self).__init__(pos, size, context=context)
        self.item = item

    def _candy_context_sync(self, context):
        super(Thumbnail, self)._candy_context_sync(context)
        self.item = self.__item

    @property
    def item(self):
        return self.__item_eval

    @item.setter
    def item(self, item):
        self.__item = item
        if isinstance(item, (str, unicode)):
            if self.context:
                item = self.context.get(item)
            else:
                item = None
        if self.__item_eval == item:
            return
        self.__item_eval = item
        if not item:
            return
        self.set_thumbnail(item.get('thumbnail'))
        if not self.has_image():
            self._load_mimetype(item)

    def _try_mimetype(self, name):
        for ext in ('.png', '.jpg'):
            fname = os.path.join(self.theme.icons, 'mimetypes', name + ext)
            if os.path.isfile(fname):
                self.set_image(fname)
                return True
        return False

    def _load_mimetype(self, item):
        if item.type == 'dir':
            if self._try_mimetype('folder_%s' % item.media_type):
                return
            return self._try_mimetype('folder')
        if item.type == 'playlist':
            if item.parent and self._try_mimetype('playlist_%s' % item.parent.media_type):
                return
            return self._try_mimetype('playlist')
        try:
            if self._try_mimetype(item.info['mime'].replace('/', '_')):
                return
        except:
            pass
        if item.type and self._try_mimetype(item.type):
            return
        if self._try_mimetype('unknown'):
            return

    @classmethod
    def candyxml_parse(cls, element):
        """
        """
        return kaa.candy.Imlib2Texture.candyxml_parse(element).update(
            item=element.item)


class Icon(kaa.candy.Image):

    candyxml_style = 'icon'

    __name = __name_eval = None

    def __init__(self, pos, size, name, context=None):
        super(Icon, self).__init__(pos, size, context=context)
        if name and name.startswith('$'):
            self.add_dependency(name)
            name = self.context.get(name)
        if not name:
            return
        for ext in ('.png', '.jpg'):
            fname = os.path.join(self.theme.icons, name + ext)
            if os.path.isfile(fname):
                self.set_image(fname)
                return

    @classmethod
    def candyxml_parse(cls, element):
        """
        """
        return kaa.candy.Imlib2Texture.candyxml_parse(element).update(
            name=element.name)


class MediaImage(kaa.candy.Image):

    candyxml_style = 'media'

    __name = __name_eval = None

    def __init__(self, pos, size, folder, context=None):
        super(MediaImage, self).__init__(pos, size, context=context)
        self.add_dependency('item.media_type')
        name = self.context.get('item.media_type') or 'default'
        for name in (name, 'default'):
            for ext in ('.png', '.jpg'):
                fname = os.path.join(self.theme.icons, folder, name + ext)
                if os.path.isfile(fname):
                    self.set_image(fname)
                    return

    @classmethod
    def candyxml_parse(cls, element):
        """
        """
        return kaa.candy.Imlib2Texture.candyxml_parse(element).update(
            folder=element.folder)
