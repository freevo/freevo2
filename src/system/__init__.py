import config
import cache
import xine

cache = cache.Cache()

for key in cache.keys():
    setattr(config, key, cache[key])

xine.probe(cache)

cache.save()
