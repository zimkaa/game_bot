from time import perf_counter

from loguru import logger


def timing_decorator(func):
    def wrapper(*args, **kwargs):
        logger.critical(f"start {func.__name__=}")
        logger.debug(f"{kwargs=}")
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        logger.critical(f"timing_decorator {func.__name__=} - {end_time - start_time:.5f} seconds")
        return result

    return wrapper
