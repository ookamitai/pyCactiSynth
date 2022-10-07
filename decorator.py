import logging
from time import time

def catch_exception(func):
    """
    Catch exceptions and log them

    :param func: Function to decorate
    :return: Decorated function
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(
                f"An error occurred when calling {func.__name__!r}.\nType: {type(e).__name__}\nException: {e}"
            )

    return wrapper


def timer_func(func):
    def wrapper(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Function {func.__name__!r} executed in {(t2 - t1):.4f}s')
        return result

    return wrapper
