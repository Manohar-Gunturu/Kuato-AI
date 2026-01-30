import logging
import time

def timeit(fn):
    def wrapper(self, *args, **kwargs):
        logger = getattr(self, "logger", logging.getLogger(__name__))
        start = time.perf_counter()
        logger.info(f"{fn.__name__} started")
        try:
            return fn(self, *args, **kwargs)
        finally:
            end = time.perf_counter()
            logger.info(f"{fn.__name__} finished in {(end - start):.3f}s")
    return wrapper