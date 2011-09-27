import kaa.candy

kaa.candy.Eventhandler.signatures['widget-show'] = 'self'
kaa.candy.Eventhandler.signatures['widget-hide'] = 'self'

class WidgetStyles(kaa.candy.candyxml.Styles):
    """
    """
    candyxml_name = 'widget'

    def get(self, name):
        """
        Get the given widget class or return the default.
        """
        if not name in self:
            name = None
        return super(WidgetStyles, self).get(name)

    def candyxml_parse(self, element):
        """
        Parse and return the class based on the given xml element.
        """
        return self.get(element.name)


class Widget(kaa.candy.Group):
    candyxml_name = 'widget'

    __visible = False

    class __template__(kaa.candy.AbstractGroup.__template__):
        @classmethod
        def candyxml_get_class(cls, element):
            return kaa.candy.candyxml.get_class(element.node, element.name)

    @property
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, visible):
        if self.__visible == visible:
            return
        self.__visible = visible
        if visible:
            self.show()
        else:
            self.hide()

    def show(self):
        return self.emit('widget-show', self)

    def hide(self):
        return self.emit('widget-hide', self)

    @kaa.coroutine()
    def destroy(self):
        hiding = self.hide()
        if isinstance(hiding, kaa.InProgress):
            yield hiding
        self.parent = None
