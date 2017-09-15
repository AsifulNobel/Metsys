import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        r = func(*args, **kwargs)
        end = time.perf_counter()
        logger.debug('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
        return r
    return wrapper
