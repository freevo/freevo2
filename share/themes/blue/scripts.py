import kaa

@kaa.coroutine()
def menu(prev, next):
    logo = next.stage.get_widget('idlebar').get_widget('logo')
    next.opacity = 0
    if prev.type == 'main':
        prev.animate('EASE_IN_QUAD', 0.4, scale_x=10, scale_y=10, opacity=0)
        yield kaa.delay(0.2)
        next.animate('EASE_OUT_CUBIC', 0.2, opacity=255)
        yield logo.animate('EASE_OUT_CUBIC', 0.2, opacity=255)
        yield None
    if next.type == 'main':
        next.scale_x = 10
        next.scale_y = 10
        logo.animate('EASE_IN_CUBIC', 0.2, opacity=0)
        prev.animate('EASE_IN_CUBIC', 0.2, opacity=0)
        yield next.animate('EASE_OUT_QUAD', 0.4, scale_x=1, scale_y=1, opacity=255)
        yield None
    # default fade
    next.animate('EASE_OUT_CUBIC', 0.3, opacity=255)
    yield prev.animate('EASE_IN_CUBIC', 0.3, opacity=0)

@kaa.coroutine()
def fade(prev, next):
    next.opacity = 0
    next.animate('EASE_IN_QUAD', 0.2, opacity=255)
    yield prev.animate('EASE_OUT_QUAD', 0.2, opacity=0)
