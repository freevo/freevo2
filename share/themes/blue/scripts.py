import kaa

@kaa.coroutine()
def menu(prev, next):
    if prev.type == 'main':
        next.opacity = 0
        c = prev.get_widget('content')
        yield c.animate('EASE_OUT_QUAD', 0.3, x=(c.x - c.width))
        next.animate('EASE_OUT_CUBIC', 0.2, opacity=255)
        yield None
    if next.type == 'main':
        next.x = next.x - next.width
        yield prev.animate('EASE_OUT_CUBIC', 0.2, opacity=0)
        # FIXME: size too large
        next.animate('EASE_OUT_CUBIC', 0.3, x=(next.x + next.width))
        yield None
    # default fade
    yield prev.animate('EASE_OUT_CUBIC', 0.3, opacity=0)

@kaa.coroutine()
def fade(prev, next):
    next.opacity = 0
    next.animate('EASE_IN_QUAD', 0.2, opacity=255)
    yield prev.animate('EASE_OUT_QUAD', 0.2, opacity=0)
