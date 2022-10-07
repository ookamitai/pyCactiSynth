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
            logging.error(
                f"An error occurred when calling {func.__name__}.\nType: {type(e).__name__}\nException: {e}"
            )

    return wrapper
