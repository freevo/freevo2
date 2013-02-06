import kaa

@kaa.coroutine()
def image_osd(widget, event):
    if event != 'TOGGLE_OSD':
        yield None
    visible = getattr(widget, 'image_osd_status', False)
    if not visible:
        widget.get_widget('player').animate('EASE_IN_QUAD', 0.2, scale_x=0.7, scale_y=0.7,
                  x=30 * widget.osd.scale_x, y=120 * widget.osd.scale_y)
        yield kaa.delay(0.2)
        idlebar = widget.stage.get_widget('idlebar')
        if idlebar:
            idlebar.show()
        widget.osd.show('listing')
        widget.osd.show('info')
    else:
        idlebar = widget.stage.get_widget('idlebar')
        if idlebar:
            idlebar.hide()
        widget.osd.hide('listing')
        yield widget.osd.hide('info')
        widget.get_widget('player').animate('EASE_IN_QUAD', 0.2, scale_x=1.0, scale_y=1.0, x=0, y=0)
    widget.image_osd_status = not visible
