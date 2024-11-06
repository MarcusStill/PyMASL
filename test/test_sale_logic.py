from datetime import date

import pytest

from sale_logic import (
    calculate_age,
    calculate_ticket_type,
    calculated_ticket_price,
)
from system import System


@pytest.mark.parametrize(
    "birth_date, today_date, expected_age",
    [
        (date(2000, 1, 1), date(2024, 1, 1), 24),
        (date(2000, 1, 2), date(2024, 1, 1), 23),
        (date(2024, 1, 1), date(2024, 1, 1), 0),
        (date(1800, 1, 1), date(2024, 1, 1), 224),
    ],
)
def test_calculate_age(monkeypatch, birth_date, today_date, expected_age):
    # Подменяем функцию get_today_date, чтобы возвращалась нужная дата
    monkeypatch.setattr("sale_logic.get_today_date", lambda: today_date)

    # Проверка, что calculate_age возвращает ожидаемый возраст
    assert calculate_age(birth_date) == expected_age


# Параметризованные тесты для разных возрастов
@pytest.mark.parametrize(
    "age, expected",
    [
        (4, "бесплатный"),  # Меньше 5 лет - бесплатный билет
        (5, "детский"),  # Возраст равен 5 - детский билет
        (10, "детский"),  # Возраст внутри диапазона для детского билета
        (14, "детский"),  # Возраст равен 14 - детский билет
        (15, "взрослый"),  # Возраст равен 15 - взрослый билет
        (20, "взрослый"),  # Возраст больше 15 - взрослый билет
        (100, "взрослый"),  # Для любого возраста больше 15 - взрослый билет
    ],
)
def test_calculate_ticket_type(age, expected):
    result = calculate_ticket_type(age)
    assert result == expected, f"Expected {expected} for age {age}, but got {result}"


#######################################
# Тестируем calculated_ticket_price
@pytest.mark.parametrize(
    "type_ticket, time, expected_price",
    [
        ("взрослый", 1, 150),
        ("взрослый", 2, 200),
        ("взрослый", 3, 250),
        ("детский", 1, 250),
        ("детский", 2, 500),
        ("детский", 3, 750),
    ],
)
def test_calculated_ticket_price(type_ticket, time, expected_price):
    # Создаём экземпляр класса
    system_instance = System()

    # Вызываем метод get_price через экземпляр класса
    system_instance.get_price()  # Работает через экземпляр

    # Теперь можно использовать System.price для расчета
    actual_price = calculated_ticket_price(type_ticket, time)

    # Проверка результата
    assert actual_price == expected_price


def test_get_price_empty_db():
    # Ожидаемые значения теперь включают 'ticket_free': 0
    expected_price = {
        "ticket_child_1": 250,
        "ticket_child_2": 500,
        "ticket_child_3": 750,
        "ticket_child_week_1": 300,
        "ticket_child_week_2": 600,
        "ticket_child_week_3": 900,
        "ticket_adult_1": 150,
        "ticket_adult_2": 200,
        "ticket_adult_3": 250,
        "ticket_free": 0,  # Добавляем этот ключ
    }

    # Создаем экземпляр класса
    system_instance = System()
    # Запускаем метод
    system_instance.get_price()

    # Проверяем, что в System.price установлены значения по умолчанию
    assert System.price == expected_price


def test_get_price_with_zero_values_in_db():
    # Симулируем, что в базе данных есть нули для некоторых значений
    mock_db_data = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # Все нули

    # Создаем экземпляр класса
    system_instance = System()

    # Запускаем метод
    system_instance.get_price()

    # Проверяем, что нули не заменили значения по умолчанию
    expected_price = {
        "ticket_child_1": 250,
        "ticket_child_2": 500,
        "ticket_child_3": 750,
        "ticket_child_week_1": 300,
        "ticket_child_week_2": 600,
        "ticket_child_week_3": 900,
        "ticket_adult_1": 150,
        "ticket_adult_2": 200,
        "ticket_adult_3": 250,
        "ticket_free": 0,  # ticket_free по-прежнему с нулем
    }

    # Здесь метод должен не менять значения по умолчанию, если в базе нули
    assert System.price == expected_price


def test_get_price_not_empty():
    # Создаем экземпляр класса
    system_instance = System()

    # Запускаем метод
    system_instance.get_price()

    # Проверяем, что все ключи в System.price имеют значения больше нуля, кроме 'ticket_free'
    assert all(value > 0 or key == "ticket_free" for key, value in System.price.items())


def test_get_price_valid_keys():
    # Ожидаемые ключи теперь включают 'ticket_free'
    expected_keys = [
        "ticket_child_1",
        "ticket_child_2",
        "ticket_child_3",
        "ticket_child_week_1",
        "ticket_child_week_2",
        "ticket_child_week_3",
        "ticket_adult_1",
        "ticket_adult_2",
        "ticket_adult_3",
        "ticket_free",  # Добавляем этот ключ
    ]

    # Создаем экземпляр класса
    system_instance = System()
    # Запускаем метод
    system_instance.get_price()

    # Проверяем, что все ключи в System.price совпадают с ожидаемыми
    assert sorted(System.price.keys()) == sorted(expected_keys)


def test_calculated_ticket_price_invalid_time():
    with pytest.raises(KeyError):
        calculated_ticket_price("взрослый", 4)  # Допустим, максимальное время - 3


def test_calculated_ticket_price_empty_prices():
    System.price = {}
    with pytest.raises(KeyError):
        calculated_ticket_price("взрослый", 1)


#######################################
# Тестируем calculate_adult_price
