_backend = None

def set_backend(name):
    exec "from %s_backend import *"  % name in globals()
    global _backend
    _backend = name


def get_current_backend():
    return _backend


def get_backend(name):
    try:
        backend = __import__(name + "_backend", globals())
    except ImportError:
        return None
    return backend


# Set default backend
try:
    set_backend("imlib2")
except ImportError:
    pass

if _backend == None:
    raise "No supported image library could be found."


def convert(image, target = None):
    if target == None:
        target = get_current_backend()

    target_backend = get_backend(target)
    if isinstance(image, target_backend.Image):
        return image
