
import time
import kaa
import kaa.candy

from plugin import IdleBarPlugin

class PluginInterface(IdleBarPlugin):
    """
    Shows the current time.
    """
    def __init__(self, format=''):
        IdleBarPlugin.__init__(self)
        if format == '':
            if time.strftime('%P') =='':
                format ='%a %H:%M'
            else:
                format ='%a %I:%M %P'
        self.format = format

    def connect(self, idlebar):
        self.widget = kaa.candy.Label(None, ('100%', '50%'), 0xffffff, 'Vera')
        self.widget.xalign=self.widget.ALIGN_RIGHT
        self.widget.yalign=self.widget.ALIGN_CENTER
        self.widget.text = time.strftime(self.format)
        idlebar.add(self.widget)
        kaa.Timer(self.update).start(10)

    def update(self):
        self.widget.text = time.strftime(self.format)
