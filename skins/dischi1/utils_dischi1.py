# The OSD class, used to communicate with the OSD daemon
import osd
import util

# Create the OSD object
osd = osd.get_singleton()



# Draws a text based on the settings in the XML file
def DrawText(text, settings, x=-1, y=-1, align=''):
    if x == -1:
        x = settings.x
    if y == -1:
        y = settings.y
    if not align:
        align = settings.align

    if settings.shadow_visible:
        osd.drawstring(text, x+settings.shadow_pad_x, y+settings.shadow_pad_y,
                       settings.shadow_color, None, settings.font,
                       settings.size, align)
    osd.drawstring(text, x, y, settings.color, None, settings.font,
                   settings.size, align)


# Draws a text inside a frame based on the settings in the XML file
def DrawTextFramed(text, settings, x=-1, y=-1, width=-1, height=-1):
    if x == -1:
        x = settings.x
    if y == -1:
        y = settings.y

    if width == -1:
        width = settings.width

    if settings.shadow_visible:
        osd.drawstringframed(text, x+settings.shadow_pad_x, y+settings.shadow_pad_y,
                             width, height, settings.shadow_color, None,
                             font=settings.font, ptsize=settings.size,
                             align_h=settings.align, align_v=settings.valign)
    osd.drawstringframed(text, x, y, width, height, settings.color, None,
                         font=settings.font, ptsize=settings.size,
                         align_h=settings.align, align_v=settings.valign)


def DrawLogo(settings):
    if settings.image and settings.visible:
        if settings.width and settings.height:
            osd.drawbitmap(util.resize(settings.image, settings.width, settings.height),
                           settings.x, settings.y)
        else:
            osd.drawbitmap(settings.image, settings.x, settings.y)
    
