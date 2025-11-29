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

if __name__ == '__main__':
    unittest.main()
