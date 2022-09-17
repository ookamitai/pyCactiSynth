import logging


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
            logging.error(e)
    return wrapper
