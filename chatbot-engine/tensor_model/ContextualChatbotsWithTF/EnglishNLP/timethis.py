import time
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

def timethis(what):
    @contextmanager
    def benchmark():
        start = time.time()
        yield
        end = time.time()
        logger.debug("%s : %0.3f seconds" % (what, end-start))
    if hasattr(what,"__call__"):
        def timed(*args,**kwargs):
            with benchmark():
                return what(*args,**kwargs)
        return timed
    else:
        return benchmark()
