import functools
import cyclone.web
from twisted.internet import defer

def dbsafe(method):
    @defer.inlineCallbacks
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            result = yield defer.maybeDeferred(method, self, *args, **kwargs)
        except Exception, e:
            print("MySQL error: " + str(e))
        else:
            defer.returnValue(result)
    return wrapper

