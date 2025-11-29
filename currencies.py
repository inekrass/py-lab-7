import requests
import sys
from logger_decorator import logger


@logger(handle=sys.stdout)
def get_currencies(currency_codes: list, url="https://www.cbr-xml-daily.ru/daily_json.js") -> dict:
    """
    Получает курсы валют с API ЦБ РФ.

    Args:
        currency_codes: Список кодов валют для получения курсов
        url: URL API ЦБ РФ

    Returns:
        Словарь с курсами валют в формате {"USD": 93.25, "EUR": 101.7}

    Raises:
        ConnectionError: Если API недоступен
        ValueError: Если получен некорректный JSON
        KeyError: Если нет ключа "Valute" или отсутствует валюта в данных
        TypeError: Если курс валюты имеет неверный тип
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"API недоступен: {e}")

    try:
        data = response.json()
    except ValueError as e:
        raise ValueError(f"Некорректный JSON: {e}")

    if "Valute" not in data:
        raise KeyError("Нет ключа 'Valute' в ответе API")

    valute_data = data["Valute"]
    result = {}

    for currency_code in currency_codes:
        if currency_code not in valute_data:
            raise KeyError(f"Валюта {currency_code} отсутствует в данных")

        currency_info = valute_data[currency_code]

        if "Value" not in currency_info:
            raise KeyError(f"Нет ключа 'Value' для валюты {currency_code}")

        rate = currency_info["Value"]

        if not isinstance(rate, (int, float)):
            raise TypeError(f"Курс валюты {currency_code} имеет неверный тип: {type(rate).__name__}")

        result[currency_code] = rate

    return result
