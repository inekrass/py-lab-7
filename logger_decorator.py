import sys
import functools
import logging
from datetime import datetime


def logger(func=None, *, handle=sys.stdout):
    """
    Параметризуемый декоратор для логирования вызовов функций.

    Args:
        func: Декорируемая функция (None при параметризованном вызове)
        handle: Поток вывода для логирования (по умолчанию sys.stdout) или объект logging.Logger
    """
    def log_message(message):
        """Универсальная функция для записи сообщений в лог"""
        if isinstance(handle, logging.Logger):
            message = message.rstrip('\n')
            if message:
                handle.info(message)
        else:
            handle.write(message)

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            args_str = ', '.join(repr(arg) for arg in args)
            kwargs_str = ', '.join(f'{k}={repr(v)}' for k, v in kwargs.items())

            if args_str and kwargs_str:
                all_args = f"{args_str}, {kwargs_str}"
            elif args_str:
                all_args = args_str
            elif kwargs_str:
                all_args = kwargs_str
            else:
                all_args = ""

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_message(f"[{timestamp}] INFO: Вызов функции {f.__name__}({all_args})\n")

            try:
                result = f(*args, **kwargs)

                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_message(f"[{timestamp}] INFO: Функция {f.__name__} успешно завершена. Результат: {repr(result)}\n")

                return result

            except Exception as e:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_message(f"[{timestamp}] ERROR: В функции {f.__name__} произошло исключение {type(e).__name__}: {str(e)}\n")

                raise

        return wrapper

    # Если декоратор вызван без параметров (@logger)
    if func is not None:
        return decorator(func)

    # Если декоратор вызван с параметрами (@logger(...))
    return decorator