#!/usr/bin/env python3
from logger_decorator import logger
from currencies import get_currencies


@logger
def get_currency_rates(codes):
    """Получает курсы валют с логированием."""
    return get_currencies(codes)


if __name__ == "__main__":
    try:
        rates = get_currency_rates(["USD", "EUR"])
        print(f"Курсы валют: {rates}")
    except Exception as e:
        print(f"Ошибка: {e}")
