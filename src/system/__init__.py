import config
import cache
import xine
import tvcards

cache = cache.Cache()

for key in cache.keys():
    setattr(config, key, cache[key])

# TODO: move into detect()
xine.probe(cache)

cache.save()


# TODO: datect() should take **kwargs or a list
def detect(what):
    eval(what).detect()

