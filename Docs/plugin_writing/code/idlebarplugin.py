import random
from plugins.idlebar import IdleBarPlugin

# for a simple example put in a file called YeaNay.py in
# /usr/local/freevo/src/plugins/idlebar/
class PluginInterface(IdleBarPlugin):
    """
    Shows Yea or Nay randomly as text in the idlebar
                                                                                
    Activate with:
    plugin.activate('idlebar.YeaNay',   level=45)
    """
    def __init__(self):
        IdleBarPlugin.__init__(self)
        if ( random.randrange(2) ):
            self.yeanay = 'yea'
        else:
            self.yeanay = 'nay'
                                                                        
    def draw(self, (type, object), x, osd):
        font  = osd.get_font('clock')
        idlebar_height = 60
        w = font.font.stringsize( self.yeanay )
        h = font.font.height
        if h > idlebar_height:
            h = idlebar_height
        osd.write_text( self.yeanay, font, None,
                        ( x + 5 ),
                        ( osd.y + ( idlebar_height - h ) / 2 ),
                        ( w + 1 ), h , 'right', 'center')
        return 0

