import kaa.candy

# get config
from ... import config
guicfg = config.gui

class Idlebar(kaa.candy.Container):
    candyxml_name = 'idlebar'

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the XML element for parameter to create the widget.
        """
        for c in element:
            if c.ignore_overscan:
                # the idlebar background. Expand by overscan
                c._attrs['x'] = c._attrs.get('x', 0) - guicfg.display.overscan.x
                c._attrs['y'] = c._attrs.get('y', 0) - guicfg.display.overscan.y
                default = guicfg.display.width - 2 * guicfg.display.overscan.x
                value = float(c._attrs.get('width', default))
                factor = value / default
                c._attrs['width'] = int(value + factor * 2 * guicfg.display.overscan.x)
                c._attrs['height'] +=  guicfg.display.overscan.y
        return super(Idlebar, cls).candyxml_parse(element)

Idlebar.candyxml_register()
