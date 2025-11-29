# Отчёт по лабораторной работе №7: Логирование и обработка ошибок в Python
# Некрасов Богдан P4150

## 1. Исходный код декоратора с параметрами

```python
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
```

## 2. Исходный код ```get_currencies```(без логирования)

```python
import requests


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
```

## 3. Демонстрационный пример (квадратное уравнение)

```python
import logging
import math
from logger_decorator import logger

# Настройка логирования
logging.basicConfig(
    filename="quadratic.log",
    level=logging.DEBUG,
    format="%(levelname)s: %(message)s"
)

@logger
def solve_quadratic(a, b, c):
    """
    Решает квадратное уравнение ax² + bx + c = 0

    Args:
        a, b, c: Коэффициенты квадратного уравнения

    Returns:
        tuple: Корни уравнения или None

    Raises:
        TypeError: Если параметры не являются числами
        ValueError: Если a = 0
    """
    logging.info(f"Solving equation: {a}x² + {b}x + {c} = 0")

    # Проверка типов
    for name, value in zip(("a", "b", "c"), (a, b, c)):
        if not isinstance(value, (int, float)):
            logging.critical(f"Parameter '{name}' must be a number, got: {value}")
            raise TypeError(f"Coefficient '{name}' must be numeric")

    # Проверка a = 0
    if a == 0:
        logging.error("Coefficient 'a' cannot be zero")
        raise ValueError("a cannot be zero")

    d = b*b - 4*a*c
    logging.debug(f"Discriminant: {d}")

    if d < 0:
        logging.warning("Discriminant < 0: no real roots")
        return None

    if d == 0:
        x = -b / (2*a)
        logging.info("One real root")
        return (x,)

    root1 = (-b + math.sqrt(d)) / (2*a)
    root2 = (-b - math.sqrt(d)) / (2*a)
    logging.info("Two real roots computed")
    return root1, root2
```

## 4. Фрагменты логов

### 4.1```quadratic_demo.py```:

```
=== Демонстрация логирования квадратных уравнений ===

1. Два корня (a=1, b=-5, c=6):
[2025-11-30 01:38:00] INFO: Вызов функции solve_quadratic(1, -5, 6)
[2025-11-30 01:38:00] INFO: Функция solve_quadratic успешно завершена. Результат: (3.0, 2.0)
   Результат: (3.0, 2.0)

2. Нет действительных корней (a=1, b=2, c=5):
[2025-11-30 01:38:00] INFO: Вызов функции solve_quadratic(1, 2, 5)
[2025-11-30 01:38:00] INFO: Функция solve_quadratic успешно завершена. Результат: None
   Результат: None

3. Некорректные данные (a='abc', b=2, c=3):
[2025-11-30 01:38:00] INFO: Вызов функции solve_quadratic('abc', 2, 3)
[2025-11-30 01:38:00] ERROR: В функции solve_quadratic произошло исключение TypeError: Coefficient 'a' must be numeric
   Ошибка: Coefficient 'a' must be numeric

4. Критическая ошибка (a=0, b=0, c=3):
[2025-11-30 01:38:00] INFO: Вызов функции solve_quadratic(0, 0, 3)
[2025-11-30 01:38:00] ERROR: В функции solve_quadratic произошло исключение ValueError: a cannot be zero
   Ошибка: a cannot be zero
```

### 4.2```quadratic.log```:

```
INFO: Solving equation: 1x² + -5x + 6 = 0
DEBUG: Discriminant: 1
INFO: Two real roots computed
INFO: Solving equation: 1x² + 2x + 5 = 0
DEBUG: Discriminant: -16
WARNING: Discriminant < 0: no real roots
INFO: Solving equation: abcx² + 2x + 3 = 0
CRITICAL: Parameter 'a' must be a number, got: abc
INFO: Solving equation: 0x² + 0x + 3 = 0
ERROR: Coefficient 'a' cannot be zero
```

### 4.3```main.py```:

```
[2025-11-30 01:37:04] INFO: Вызов функции get_currency_rates(['USD', 'EUR'])
[2025-11-30 01:37:04] INFO: Функция get_currency_rates успешно завершена. Результат: {'USD': 78.2284, 'EUR': 90.819}
Курсы валют: {'USD': 78.2284, 'EUR': 90.819}
```

### 4.4```currencies.log```:

```
[2025-11-30 01:36:56] INFO: Вызов функции get_currencies(['USD', 'EUR'])
[2025-11-30 01:36:56] INFO: Функция get_currencies успешно завершена. Результат: {'USD': 93.25, 'EUR': 101.7}
[2025-11-30 01:36:56] INFO: Вызов функции get_currencies(['USD'])
[2025-11-30 01:36:56] ERROR: В функции get_currencies произошло исключение ValueError: Некорректный JSON: Invalid JSON
[2025-11-30 01:37:04] INFO: Вызов функции get_currencies(['USD', 'EUR'])
```

## 5. Тесты

### 5.1 Тесты функции get_currencies (test_currencies.py)

```python
import unittest
import requests
from unittest.mock import patch, Mock
from currencies import get_currencies


class TestGetCurrencies(unittest.TestCase):
    """Тесты для функции get_currencies"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.valid_currency_codes = ["USD", "EUR", "GBP"]
        self.valid_api_response = {
            "Date": "2023-11-30T11:30:00+03:00",
            "Valute": {
                "USD": {
                    "ID": "R01235",
                    "NumCode": "840",
                    "CharCode": "USD",
                    "Nominal": 1,
                    "Name": "Доллар США",
                    "Value": 93.25,
                    "Previous": 92.80
                },
                "EUR": {
                    "ID": "R01239",
                    "NumCode": "978",
                    "CharCode": "EUR",
                    "Nominal": 1,
                    "Name": "Евро",
                    "Value": 101.7,
                    "Previous": 101.2
                },
                "GBP": {
                    "ID": "R01035",
                    "NumCode": "826",
                    "CharCode": "GBP",
                    "Nominal": 1,
                    "Name": "Фунт стерлингов Соединенного королевства",
                    "Value": 117.5,
                    "Previous": 116.8
                }
            }
        }

    def test_successful_currency_retrieval(self):
        """Тест корректного возврата реальных курсов валют"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = self.valid_api_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_currencies(["USD", "EUR"])

            expected = {"USD": 93.25, "EUR": 101.7}
            self.assertEqual(result, expected)

            mock_get.assert_called_once_with("https://www.cbr-xml-daily.ru/daily_json.js")

    def test_connection_error_request_exception(self):
        """Тест выброса ConnectionError при RequestException"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Connection failed")

            with self.assertRaises(ConnectionError) as context:
                get_currencies(["USD"])

            self.assertIn("API недоступен", str(context.exception))
            self.assertIn("Connection failed", str(context.exception))

    def test_value_error_invalid_json(self):
        """Тест выброса ValueError при некорректном JSON"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            with self.assertRaises(ValueError) as context:
                get_currencies(["USD"])

            self.assertIn("Некорректный JSON", str(context.exception))
            self.assertIn("Invalid JSON", str(context.exception))

    def test_key_error_missing_valute_key(self):
        """Тест выброса KeyError при отсутствии ключа 'Valute'"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"Date": "2023-11-30", "Data": {}}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            with self.assertRaises(KeyError) as context:
                get_currencies(["USD"])

            self.assertIn("Нет ключа 'Valute' в ответе API", str(context.exception))

    def test_key_error_missing_currency(self):
        """Тест выброса KeyError при отсутствии запрашиваемой валюты"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            response_data = {
                "Valute": {
                    "USD": {
                        "Value": 93.25
                    }
                }
            }
            mock_response.json.return_value = response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            with self.assertRaises(KeyError) as context:
                get_currencies(["JPY"])

            self.assertIn("Валюта JPY отсутствует в данных", str(context.exception))
```

**Результат выполнения тестов функции:**
```
.....
----------------------------------------------------------------------
Ran 5 tests in 0.002s

OK
```

### 5.2 Тесты декоратора (test_logger_decorator.py)

```python
import unittest
import io
from logger_decorator import logger


class TestLoggerDecorator(unittest.TestCase):
    """Тесты для декоратора логгера"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.stream = io.StringIO()

    def test_successful_execution_logs(self):
        """Тест логирования при успешном выполнении функции"""
        @logger(handle=self.stream)
        def test_function(x):
            return x * 2

        result = test_function(5)

        self.assertEqual(result, 10)

        log_output = self.stream.getvalue()

        # Проверяем наличие сообщения о старте (INFO)
        self.assertRegex(log_output, r"\[.*\] INFO: Вызов функции test_function\(5\)")

        # Проверяем наличие сообщения об окончании (INFO)
        self.assertRegex(log_output, r"\[.*\] INFO: Функция test_function успешно завершена\. Результат: 10")

        # Проверяем, что аргументы записаны
        self.assertIn("test_function(5)", log_output)

        # Проверяем, что возвращаемое значение записано
        self.assertIn("Результат: 10", log_output)

    def test_error_execution_logs(self):
        """Тест логирования при ошибке в функции"""
        @logger(handle=self.stream)
        def failing_function(x):
            if x == 0:
                raise ValueError("Нельзя делить на ноль")
            return 10 / x

        # Проверяем, что исключение проброшено
        with self.assertRaises(ValueError) as context:
            failing_function(0)

        self.assertEqual(str(context.exception), "Нельзя делить на ноль")

        log_output = self.stream.getvalue()

        # Проверяем наличие ERROR лога
        self.assertRegex(log_output, "ERROR")

        self.assertRegex(log_output, r"В функции failing_function произошло исключение ValueError: Нельзя делить на ноль")

        self.assertRegex(log_output, r"INFO: Вызов функции failing_function\(0\)")


if __name__ == '__main__':
    unittest.main()
```

**Результат выполнения тестов декоратора:**
```
..
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

### 5.3 Работа с StringIO

```python
def setUp(self):
    """Настройка перед каждым тестом"""
    self.stream = io.StringIO()

@logger(handle=self.stream)
def test_function(x):
    return x * 2

result = test_function(5)
log_output = self.stream.getvalue()  # Получаем логи из StringIO
```
