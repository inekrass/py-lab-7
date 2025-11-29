#!/usr/bin/env python3
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

    # Ошибка типов
    for name, value in zip(("a", "b", "c"), (a, b, c)):
        if not isinstance(value, (int, float)):
            logging.critical(f"Parameter '{name}' must be a number, got: {value}")
            raise TypeError(f"Coefficient '{name}' must be numeric")

    # Ошибка: a = 0
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


if __name__ == "__main__":

    print("=== Демонстрация логирования квадратных уравнений ===\n")

    print("1. Два корня (a=1, b=-5, c=6):")
    try:
        result = solve_quadratic(1, -5, 6)
        print(f"   Результат: {result}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    print()

    print("2. Нет действительных корней (a=1, b=2, c=5):")
    try:
        result = solve_quadratic(1, 2, 5)
        print(f"   Результат: {result}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    print()

    print("3. Некорректные данные (a='abc', b=2, c=3):")
    try:
        result = solve_quadratic("abc", 2, 3)
        print(f"   Результат: {result}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    print()

    # Случай 4: CRITICAL - a = 0
    print("4. Критическая ошибка (a=0, b=0, c=3):")
    try:
        result = solve_quadratic(0, 0, 3)
        print(f"   Результат: {result}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    print()

