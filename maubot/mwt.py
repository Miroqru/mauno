# Source: http://code.activestate.com/recipes/325905-memoize-decorator-with-timeout/#c1

import time


class MWT(object):
    """Memoize With Timeout."""

    _cache = {}
    _timeouts = {}

    def __init__(self,timeout=2):
        self.timeout = timeout

    def collect(self):
        """Clear cache of results which have timed out."""
        for fn in self._cache:
            cache = {}
            for key in self._cache[fn]:
                if (time.time() - self._cache[fn][key][1]) < self._timeouts[fn]:
                    cache[key] = self._cache[fn][key]
            self._cache[fn] = cache

    def __call__(self, f):
        self.cache = self._cache[f] = {}
        self._timeouts[f] = self.timeout

        def func(*args, **kwargs):
            kw = sorted(kwargs.items())
            key = (args, tuple(kw))
            try:
                v = self.cache[key]
                print("cache")
                if (time.time() - v[1]) > self.timeout:
                    raise KeyError
            except KeyError:
                print("new")
                v = self.cache[key] = f(*args,**kwargs),time.time()
            return v[0]
        func.func_name = f.__name__

        return func