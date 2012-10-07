__all__ = [ 'Widget', 'WidgetStyles' ]

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

    # This variable can be False (not visible), True (visible) and
    # 'showing' and 'hiding' for the transitions. The later translate
    # to True in the visible property to make sure kaa.candy does not
    # delete the item because the flag is False and we need a way to
    # determain if we are about to be visisble or hidden.
    __visible = False

    class __template__(kaa.candy.AbstractGroup.__template__):
        @classmethod
        def candyxml_get_class(cls, element):
            return kaa.candy.candyxml.get_class(element.node, element.name)

    def __init__(self, pos=None, size=None, widgets=[], layer=None, context=None):
        super(Widget, self).__init__(pos, size, widgets, context)
        self.layer = layer

    @property
    def visible(self):
        return bool(self.__visible)

    @visible.setter
    def visible(self, visible):
        if bool(self.__visible) == visible:
            return
        if visible:
            self.show()
        else:
            self.hide()

    @kaa.coroutine()
    def show(self):
        if self.__visible in ('showing', True):
            yield None
        self.__visible = 'showing'
        showing = self.emit('widget-show', self)
        if isinstance(showing, kaa.InProgress):
            yield showing
        self.__visible = True

    @kaa.coroutine()
    def hide(self):
        if self.__visible in ('hiding', False):
            yield None
        self.__visible = 'hiding'
        hiding = self.emit('widget-hide', self)
        if isinstance(hiding, kaa.InProgress):
            yield hiding
        self.__visible = False

    @kaa.coroutine()
    def destroy(self):
        hiding = self.hide()
        if isinstance(hiding, kaa.InProgress):
            yield hiding
        self.parent = None

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the candyxml element for parameter to create the widget.
        """
        return super(Widget, cls).candyxml_parse(element).update(layer=element.layer)
