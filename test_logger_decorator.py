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
