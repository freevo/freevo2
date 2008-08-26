import os

import kaa.imlib2
import kaa.candy

class Thumbnail(kaa.candy.Thumbnail):
    candyxml_style = 'mimetype'

    def __init__(self, pos, size, item, context=None):
        super(Thumbnail,self).__init__(pos, size, context=context)
        if isinstance(item, (str, unicode)):
            if context:
                item = self.eval_context(item)
            else:
                item = None
        self.item = item
        if not item:
            return
        self.set_thumbnail(item.get('thumbnail'))
        if not self.has_image():
            self.load_mimetype(item)

    def _try_mimetype(self, name):
        for ext in ('.png', '.jpg'):
            fname = os.path.join(self.theme.icons, 'mimetypes', name + ext)
            if os.path.isfile(fname):
                self.set_image(fname)
                return True
        return False

    def load_mimetype(self, item):
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
        if self._try_mimetype(item.type):
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

    def __init__(self, pos, size, name, context=None):
        super(Icon, self).__init__(pos, size, context=context)
        if name and name.startswith('$'):
            # variable from the context, e.g. $varname
            name = self.eval_context(name[1:])
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


Thumbnail.candyxml_register()
Icon.candyxml_register()
