import functools

from loguru import logger


def logger_wraps(
    *,
    entry: bool = True,
    exit: bool = True,
    level: str = "DEBUG",
    catch_exceptions: bool = True
):
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(
                    level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs
                )
            try:
                result = func(*args, **kwargs)
                if exit:
                    logger_.log(level, "Exiting '{}' (result={})", name, result)
                return result
            except Exception as e:
                if catch_exceptions:
                    logger_.error("Exception in '{}': {}", name, str(e))
                raise  # Повторно выбрасываем исключение, чтобы оно могло быть обработано вызывающим кодом

        return wrapped

    return wrapper


# Экспортируем logger для дальнейшего использования
__all__ = ["logger", "logger_wraps"]
