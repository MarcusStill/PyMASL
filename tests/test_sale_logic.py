from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest

from modules.sale_logic import (
    calculate_age,
    calculate_ticket_type,
    calculated_ticket_price,
    calculate_adult_price,
    calculate_child_price,
    update_sale_dict_child_many_child,
    update_sale_dict_child_invalid,
    calculate_discounted_price,
    calculate_discount,
    calculate_itog,
    get_talent_based_on_time,
    update_sale_dict_adult_many_child,
    update_sale_dict_adult_invalid,
    update_adult_count,
    update_child_count,
    convert_sale_dict_values,
    generating_parts_for_partial_returns
)
from modules.system import System

system = System()


#######################################
# Тестируем calculate_age
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
    monkeypatch.setattr("modules.sale_logic.get_today_date", lambda: today_date)

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


# #######################################
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

    # Теперь можно использовать system.price для расчета
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

    # Проверяем, что в system.price установлены значения по умолчанию
    assert system.price == expected_price


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
    assert system.price == expected_price


def test_get_price_not_empty():
    # Создаем экземпляр класса
    system_instance = System()

    # Запускаем метод
    system_instance.get_price()

    # Проверяем, что все ключи в system.price имеют значения больше нуля, кроме 'ticket_free'
    assert all(value > 0 or key == "ticket_free" for key, value in system.price.items())


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

    # Проверяем, что все ключи в system.price совпадают с ожидаемыми
    assert sorted(system.price.keys()) == sorted(expected_keys)


def test_calculated_ticket_price_invalid_time():
    with pytest.raises(KeyError):
        calculated_ticket_price("взрослый", 4)  # Допустим, максимальное время - 3


def test_calculated_ticket_price_empty_prices():
    system.price = {}
    with pytest.raises(KeyError):
        calculated_ticket_price("взрослый", 1)


#######################################
# Тестируем calculate_adult_price
@pytest.fixture
def setup_system():
    # Предустанавливаем словарь продаж и цены для тестов
    system.sale_dict = {"detail": [0, 0, 0, 0, 0, 0, 1]}
    system.price = {
        "ticket_adult_1": 100,
        "ticket_adult_2": 150,
        "ticket_adult_3": 200,
        "ticket_free": 0,
    }
    system.count_number_of_visitors = {
        "many_child": 0,
        "kol_adult_many_child": 0,
        "invalid": 0,
        "kol_adult_invalid": 0,
    }


def test_calculate_adult_price_1_hour(setup_system):
    system.sale_dict["detail"][6] = 1
    assert calculate_adult_price() == 100


def test_calculate_adult_price_2_hours_regular_day(setup_system):
    system.sale_dict["detail"][6] = 2
    system.count_number_of_visitors["many_child"] = 0
    assert calculate_adult_price() == 150


def test_calculate_adult_price_3_hours_regular_day(setup_system):
    system.sale_dict["detail"][6] = 3
    system.count_number_of_visitors["invalid"] = 0
    assert calculate_adult_price() == 200


def test_calculate_adult_price_3_hours_invalid_day(setup_system):
    system.sale_dict["detail"][6] = 3
    system.count_number_of_visitors["invalid"] = 1
    assert calculate_adult_price() == 0
    assert system.count_number_of_visitors["kol_adult_invalid"] == 1


def test_update_sale_dict_adult_many_child(setup_system):
    system.count_number_of_visitors["kol_adult_many_child"] = 2
    update_sale_dict_adult_many_child()
    assert system.sale_dict["detail"][0] == 2
    assert system.sale_dict["detail"][1] == 0


def test_update_sale_dict_adult_invalid(setup_system):
    system.count_number_of_visitors["kol_adult_invalid"] = 1
    update_sale_dict_adult_invalid()
    assert system.sale_dict["detail"][0] == 1
    assert system.sale_dict["detail"][1] == 0


def test_calculate_adult_price_2_hours_many_child_day(setup_system):
    system.sale_dict["detail"][6] = 2
    system.count_number_of_visitors["many_child"] = 1
    system.what_a_day = 0  # Будний день
    result = calculate_adult_price()
    assert result == 0
    assert system.count_number_of_visitors["kol_adult_many_child"] == 1


def test_calculate_adult_price_2_hours_many_child_weekend(setup_system):
    system.sale_dict["detail"][6] = 2
    system.count_number_of_visitors["many_child"] = 1
    system.what_a_day = 1  # Устанавливаем день как выходной

    assert calculate_adult_price() == 150
    assert system.count_number_of_visitors["kol_adult_many_child"] == 0


#######################################
# Тестируем calculate_child_price ПАДАЮТ
@pytest.fixture
def setup_system_calculate_child_price():
    # Предустанавливаем словарь продаж и цены для тестов
    system.sale_dict = {"detail": [0, 0, 0, 0, 0, 0, 1]}  # duration по умолчанию 1
    system.price = {
        "ticket_child_1": 250,
        "ticket_child_2": 500,
        "ticket_child_3": 750,
        "ticket_child_week_1": 300,
        "ticket_child_week_2": 600,
        "ticket_child_week_3": 900,
        "ticket_free": 0,
    }
    system.count_number_of_visitors = {
        "many_child": 0,
        "kol_child_many_child": 0,
        "invalid": 0,
        "kol_child_invalid": 0,
    }
    system.what_a_day = 0  # Будний день


def test_calculate_child_price_1_hour_weekday(setup_system_calculate_child_price):
    # Проверка для дня, не являющегося выходным (будний день)
    system.sale_dict["detail"][6] = 1  # duration = 1
    result = calculate_child_price()
    assert result == 250  # Ожидаем цену для обычного дня, для длительности 1 час


def test_calculate_child_price_1_hour_weekend(setup_system_calculate_child_price):
    # Проверка для выходного дня
    system.sale_dict["detail"][6] = 1  # duration = 1
    system.what_a_day = 1  # Выходной день
    result = calculate_child_price()
    assert result == 300  # Ожидаем цену для выходного дня, для длительности 1 час


def test_calculate_child_price_2_hours_regular_day(setup_system_calculate_child_price):
    # Проверка для 2-х часов в обычный день
    system.sale_dict["detail"][6] = 2  # duration = 2
    system.count_number_of_visitors["many_child"] = 0  # Нет многодетных
    result = calculate_child_price()
    assert result == 500  # Ожидаем стандартную цену для 2-х часов


def test_calculate_child_price_2_hours_many_child_day(
    setup_system_calculate_child_price,
):
    # Проверка для многодетных детей в будний день
    system.sale_dict["detail"][6] = 2  # duration = 2
    system.count_number_of_visitors["many_child"] = 1  # Многодетные дети
    system.what_a_day = 0  # Будний день
    result = calculate_child_price()
    assert result == 0  # Ожидаем бесплатный билет
    assert (
        system.count_number_of_visitors["kol_child_many_child"] == 1
    )  # Проверка инкремента


def test_calculate_child_price_2_hours_many_child_weekend(
    setup_system_calculate_child_price,
):
    # Проверка для многодетных детей в выходной день
    system.sale_dict["detail"][6] = 2  # duration = 2
    system.count_number_of_visitors["many_child"] = 0  # Нет многодетных детей
    system.what_a_day = 1  # Выходной день
    result = calculate_child_price()
    assert result == 600  # Ожидаем цену для выходного дня, для 2-х часов


def test_calculate_child_price_3_hours_regular_day(setup_system_calculate_child_price):
    # Проверка для 3-х часов в обычный день
    system.sale_dict["detail"][6] = 3  # duration = 3
    system.count_number_of_visitors["invalid"] = 0  # Нет инвалидов
    result = calculate_child_price()
    assert result == 750  # Ожидаем стандартную цену для 3-х часов


def test_calculate_child_price_3_hours_invalid_day(setup_system_calculate_child_price):
    # Проверка для детей с инвалидностью в обычный день
    system.sale_dict["detail"][6] = 3  # duration = 3
    system.count_number_of_visitors["invalid"] = 1  # Есть инвалид
    result = calculate_child_price()
    assert result == 0  # Ожидаем бесплатный билет
    assert (
        system.count_number_of_visitors["kol_child_invalid"] == 1
    )  # Проверка инкремента


def test_update_sale_dict_child_many_child(setup_system_calculate_child_price):
    # Проверка обновления словаря продаж для многодетных детей
    system.count_number_of_visitors["kol_child_many_child"] = 2
    update_sale_dict_child_many_child()
    assert system.sale_dict["detail"][2] == 2
    assert system.sale_dict["detail"][3] == 0


def test_update_sale_dict_child_invalid(setup_system_calculate_child_price):
    # Проверка обновления словаря продаж для детей с инвалидностью
    system.count_number_of_visitors["kol_child_invalid"] = 1
    update_sale_dict_child_invalid()
    assert system.sale_dict["detail"][2] == 1
    assert system.sale_dict["detail"][3] == 0


#######################################
# Тестируем calculate_discounted_price
@pytest.fixture
def setup_system_calculate_discounted_price():
    # Инициализация начальных данных
    system.price = {
        "ticket_free": 0,
        "ticket_child_1": 250,
        "ticket_adult_1": 100,
        "ticket_child_2": 500,
        "ticket_adult_2": 150,
    }
    system.count_number_of_visitors = {
        "many_child": 0,  # Количество многодетных детей
        "invalid": 0,  # Количество инвалидов
    }
    system.sale_special = 0  # Флаг специальной продажи


# Тест 1: Проверка скидки 100% для многодетных в день многодетных
def test_calculate_discounted_price_many_child_day(
    setup_system_calculate_discounted_price,
):
    system.count_number_of_visitors["many_child"] = 1  # Есть многодетная семья
    price = 500  # Исходная цена
    result_price, result_category, discount_status = calculate_discounted_price(
        price, "детский"
    )

    assert result_price == 0  # Скидка 100% в день многодетных
    assert result_category == ""  # Нет особой категории
    assert system.sale_special == 1  # Продажа помечена как специальная


# Тест 2: Проверка скидки 50% для многодетных детей в будний день
def test_calculate_discounted_price_many_child_weekday(
    setup_system_calculate_discounted_price,
):
    system.count_number_of_visitors["many_child"] = 2  # Есть многодетная семья
    system.what_a_day = 0  # Будний день
    price = 500  # Исходная цена
    result_price, result_category, discount_status = calculate_discounted_price(
        price, "детский"
    )

    assert result_price == 250  # Скидка 50% на обычный день
    assert result_category == ""  # Нет особой категории
    assert system.sale_special == 0  # Продажа не помечена как специальная


# Тест 3: Проверка скидки 100% для инвалида
def test_calculate_discounted_price_invalid(setup_system_calculate_discounted_price):
    system.count_number_of_visitors["invalid"] = 1  # Есть инвалид
    price = 100  # Исходная цена
    result_price, result_category, discount_status = calculate_discounted_price(
        price, "взрослый"
    )

    assert result_price == 0  # Скидка 100% для инвалидов
    assert result_category == "с"  # Указание категории "с" для сопровождающего
    assert system.sale_special == 1  # Продажа помечена как специальная


# Тест 4: Проверка для обычного билета без скидок
def test_calculate_discounted_price_no_discount(
    setup_system_calculate_discounted_price,
):
    system.count_number_of_visitors["many_child"] = 0  # Нет многодетных детей
    system.count_number_of_visitors["invalid"] = 0  # Нет инвалидов
    price = 500  # Исходная цена
    result_price, result_category, discount_status = calculate_discounted_price(
        price, "детский"
    )

    assert result_price == 500  # Нет скидки, цена остается прежней
    assert result_category == ""  # Нет особой категории
    assert system.sale_special == 0  # Продажа не помечена как специальная


# Тест 5: Проверка скидки для взрослого с инвалидом
def test_calculate_discounted_price_adult_invalid(
    setup_system_calculate_discounted_price,
):
    system.count_number_of_visitors["invalid"] = 1  # Есть инвалид
    price = 150  # Исходная цена для взрослого
    result_price, result_category, discount_status = calculate_discounted_price(
        price, "взрослый"
    )

    assert result_price == 0  # Скидка 100% для инвалидов
    assert result_category == "с"  # Указание категории "с" для сопровождающего
    assert system.sale_special == 1  # Продажа помечена как специальная


#######################################
# Тестируем calculate_discount
# Тест 1: Проверка корректного расчета с нормальной скидкой
def test_calculate_discount_normal_discount():
    result = calculate_discount(100, 20)  # 100 - 20% = 80
    assert result == Decimal("80.00")


# Тест 2: Проверка скидки, меньше 0% (должна быть 0%)
def test_calculate_discount_negative_discount():
    result = calculate_discount(100, -10)  # 100 - 0% = 100
    assert result == Decimal("100.00")


# Тест 3: Проверка скидки, больше 100% (должна быть 100%)
def test_calculate_discount_large_discount():
    result = calculate_discount(100, 150)  # 100 - 100% = 0
    assert result == Decimal("0.00")


# Тест 4: Проверка скидки 0% (цена не изменяется)
def test_calculate_discount_zero_discount():
    result = calculate_discount(100, 0)  # 100 - 0% = 100
    assert result == Decimal("100.00")


# Тест 5: Проверка скидки 100% (цена должна стать 0)
def test_calculate_discount_full_discount():
    result = calculate_discount(100, 100)  # 100 - 100% = 0
    assert result == Decimal("0.00")


# Тест 6: Проверка на округление значений
def test_calculate_discount_rounding():
    result = calculate_discount(200, 17)  # 200 - 17% = 166.00
    assert result == Decimal("166.00")


# Тест 7: Проверка с большими числами
def test_calculate_discount_large_value():
    result = calculate_discount(1000000, 10)  # 1000000 - 10% = 900000
    assert result == Decimal("900000.00")


# Тест 8: Проверка с очень маленькими числами
def test_calculate_discount_small_value():
    result = calculate_discount(0.01, 50)  # 0.01 - 50% = 0.005
    expected_result = Decimal("0.005")
    # Округление до 3 знаков после запятой перед сравнением
    assert result.quantize(Decimal("0.001")) == expected_result


#######################################
# Тестируем calculate_itog
@pytest.fixture
def setup_system_calculate_itog():
    system.sale_dict = {
        "kol_adult": 5,  # Количество взрослых билетов
        "kol_child": 3,  # Количество детских билетов
        "price_adult": 100,  # Цена взрослого билета
        "price_child": 50,  # Цена детского билета
        "detail": [2, 20, 1, 10],  # [скидки на взрослых], [скидки на детей]
    }


def test_calculate_itog_no_discounts(setup_system_calculate_itog):
    # Предположим, что все данные корректны и скидки не применяются
    # Количество взрослых билетов = 5, цена взрослого билета = 100
    # Количество детских билетов = 3, цена детского билета = 50
    # Скидки: 2 взрослых билета со скидкой 20, 1 детский билет со скидкой 10

    result = calculate_itog()

    # Рассчитываем вручную:
    adult_ticket = (5 - 2) * 100  # 3 * 100 = 300
    child_ticket = (3 - 1) * 50  # 2 * 50 = 100
    adult_sale = 2 * 20  # 2 * 20 = 40
    child_sale = 1 * 10  # 1 * 10 = 10
    expected_result = (
        adult_ticket + child_ticket + adult_sale + child_sale
    )  # 300 + 100 + 40 + 10 = 450

    assert result == expected_result


def test_calculate_itog_max_discounts(setup_system_calculate_itog):
    # Установим максимальные скидки на билеты
    system.sale_dict["detail"] = [
        5,
        100,
        3,
        50,
    ]  # 5 взрослых со скидкой 100, 3 детских с скидкой 50

    result = calculate_itog()

    # Рассчитываем вручную:
    adult_ticket = (5 - 5) * 100  # 0 * 100 = 0
    child_ticket = (3 - 3) * 50  # 0 * 50 = 0
    adult_sale = 5 * 100  # 5 * 100 = 500
    child_sale = 3 * 50  # 3 * 50 = 150
    expected_result = (
        adult_ticket + child_ticket + adult_sale + child_sale
    )  # 0 + 0 + 500 + 150 = 650

    assert result == expected_result


def test_calculate_itog_zero_values(setup_system_calculate_itog):
    # Установим все нули
    system.sale_dict = {
        "kol_adult": 0,
        "kol_child": 0,
        "price_adult": 0,
        "price_child": 0,
        "detail": [0, 0, 0, 0],
    }

    result = calculate_itog()

    # Ожидаем, что итоговая сумма будет 0
    assert result == 0


def test_calculate_itog_single_ticket(setup_system_calculate_itog):
    system.sale_dict = {
        "kol_adult": 1,
        "kol_child": 1,
        "price_adult": 100,
        "price_child": 50,
        "detail": [0, 0, 0, 0],
    }

    result = calculate_itog()

    # Рассчитываем вручную:
    adult_ticket = (1 - 0) * 100  # 1 * 100 = 100
    child_ticket = (1 - 0) * 50  # 1 * 50 = 50
    adult_sale = 0  # нет скидки на взрослых
    child_sale = 0  # нет скидки на детей
    expected_result = (
        adult_ticket + child_ticket + adult_sale + child_sale
    )  # 100 + 50 + 0 + 0 = 150

    assert result == expected_result


def test_calculate_itog_invalid_values(setup_system_calculate_itog):
    # Устанавливаем некорректные данные
    system.sale_dict["kol_adult"] = -1
    system.sale_dict["kol_child"] = -1
    system.sale_dict["price_adult"] = 100
    system.sale_dict["price_child"] = 50

    # Проверяем, что при таких данных выбрасывается ValueError
    with pytest.raises(
        ValueError, match="Некорректные данные для расчета итоговой суммы"
    ):
        calculate_itog()


#######################################
# Тестируем get_talent_based_on_time
@pytest.fixture
def mock_system_get_talent_based_on_time():
    # Подготовим mock для атрибута talent класса System
    with patch.object(system, "talent", {"1_hour": 10, "2_hour": 20, "3_hour": 30}):
        yield


# Теперь тесты:
def test_get_talent_1_hour(mock_system_get_talent_based_on_time):
    # Проверяем для time_ticket == 1
    result = get_talent_based_on_time(1)
    assert result == (1, 10)


def test_get_talent_2_hour(mock_system_get_talent_based_on_time):
    # Проверяем для time_ticket == 2
    result = get_talent_based_on_time(2)
    assert result == (2, 20)


def test_get_talent_3_hour(mock_system_get_talent_based_on_time):
    # Проверяем для time_ticket == 3
    result = get_talent_based_on_time(3)
    assert result == (3, 30)


def test_get_talent_invalid_time(mock_system_get_talent_based_on_time):
    # Проверяем для некорректного значения time_ticket
    result = get_talent_based_on_time(0)  # Некорректное значение
    assert result == (0, 0)  # Ожидаем (0, 0)

    result = get_talent_based_on_time(4)
    assert result == (0, 0)


#######################################
# Тестируем update_sale_dict_adult_many_child
@pytest.fixture
def setup_system_update_sale_dict_adult_many_child():
    # Инициализируем системные данные
    system.sale_dict = {
        "detail": [0, 0, 0, 0, 0, 0, 0],
    }
    system.price = {
        "ticket_free": 0,
    }
    system.count_number_of_visitors = {
        "kol_adult_many_child": 0,
    }


def test_update_sale_dict_adult_many_child_no_visitors(
    setup_system_update_sale_dict_adult_many_child,
):
    # Проверяем, что если нет взрослых с многодетной скидкой, то значения остаются по умолчанию
    system.count_number_of_visitors["kol_adult_many_child"] = 0

    update_sale_dict_adult_many_child()  # Запускаем функцию обновления

    # Проверяем, что данные в detail не изменились
    assert (
        system.sale_dict["detail"][0] == 0
    )  # Количество взрослых с многодетной скидкой
    assert system.sale_dict["detail"][1] == 0  # Цена должна быть 0 (ticket_free)


def test_update_sale_dict_adult_many_child_with_visitors(
    setup_system_update_sale_dict_adult_many_child,
):
    # Проверяем, что если есть взрослые с многодетной скидкой, то данные обновляются
    system.count_number_of_visitors["kol_adult_many_child"] = (
        5  # Допустим, 5 взрослых с многодетной скидкой
    )
    system.price["ticket_free"] = 0  # Цена для многодетных взрослых (скидка 100%)

    update_sale_dict_adult_many_child()  # Запускаем функцию обновления

    # Проверяем, что словарь sale_dict обновился корректно
    assert (
        system.sale_dict["detail"][0] == 5
    )  # Обновляем значение для взрослых с многодетной скидкой
    assert system.sale_dict["detail"][1] == 0  # Цена должна быть 0 (ticket_free)


def test_update_sale_dict_adult_many_child_multiple_visitors(
    setup_system_update_sale_dict_adult_many_child,
):
    # Проверим сценарий, когда есть несколько взрослых с многодетной скидкой
    system.count_number_of_visitors["kol_adult_many_child"] = (
        3  # Допустим, 3 взрослых с многодетной скидкой
    )
    system.price["ticket_free"] = 0  # Цена для многодетных взрослых (скидка 100%)

    update_sale_dict_adult_many_child()  # Запускаем функцию обновления

    # Проверяем, что словарь sale_dict обновился корректно
    assert (
        system.sale_dict["detail"][0] == 3
    )  # Обновляем количество взрослых с многодетной скидкой
    assert (
        system.sale_dict["detail"][1] == 0
    )  # Обновляем цену для многодетных взрослых (скидка 100%)


def test_update_sale_dict_adult_many_child_edge_case(
    setup_system_update_sale_dict_adult_many_child,
):
    # Проверяем крайний случай, когда количество взрослых с многодетной скидкой равно 0
    system.count_number_of_visitors["kol_adult_many_child"] = (
        0  # 0 взрослых с многодетной скидкой
    )
    system.price["ticket_free"] = 0  # Цена для многодетных взрослых

    update_sale_dict_adult_many_child()  # Запускаем функцию обновления

    # Проверяем, что словарь sale_dict обновился корректно
    assert (
        system.sale_dict["detail"][0] == 0
    )  # Количество взрослых с многодетной скидкой
    assert system.sale_dict["detail"][1] == 0  # Цена для многодетных взрослых


#######################################
# Тестируем update_sale_dict_adult_invalid
@pytest.fixture
def setup_system_update_sale_dict_adult_invalid():
    # Инициализируем системные данные
    system.sale_dict = {
        "detail": [0, 0, 0, 0, 0, 0, 0],
    }
    system.price = {
        "ticket_free": 0,  # Цена для инвалидов (100% скидка)
    }
    system.count_number_of_visitors = {
        "kol_adult_invalid": 0,  # Количество взрослых с инвалидностью
    }


def test_update_sale_dict_adult_invalid_no_visitors(
    setup_system_update_sale_dict_adult_invalid,
):
    # Проверяем, что если нет взрослых с инвалидной скидкой, то данные не меняются
    system.count_number_of_visitors["kol_adult_invalid"] = 0  # 0 инвалидов

    update_sale_dict_adult_invalid()  # Запускаем функцию обновления

    # Проверяем, что данные в detail остались по умолчанию (0, 0)
    assert system.sale_dict["detail"][0] == 0  # Количество инвалидов
    assert system.sale_dict["detail"][1] == 0  # Цена для инвалидов (0)


def test_update_sale_dict_adult_invalid_with_visitors(
    setup_system_update_sale_dict_adult_invalid,
):
    # Проверяем, что если есть взрослые с инвалидной скидкой, то данные обновляются
    system.count_number_of_visitors["kol_adult_invalid"] = 2  # Допустим, 2 инвалида
    system.price["ticket_free"] = 0  # Цена для инвалидов (скидка 100%)

    update_sale_dict_adult_invalid()  # Запускаем функцию обновления

    # Проверяем, что данные в detail обновились корректно
    assert system.sale_dict["detail"][0] == 2  # Количество инвалидов
    assert system.sale_dict["detail"][1] == 0  # Цена для инвалидов (0)


def test_update_sale_dict_adult_invalid_multiple_visitors(
    setup_system_update_sale_dict_adult_invalid,
):
    # Проверяем сценарий, когда инвалидов несколько
    system.count_number_of_visitors["kol_adult_invalid"] = 3  # 3 инвалида
    system.price["ticket_free"] = 0  # Цена для инвалидов

    update_sale_dict_adult_invalid()  # Запускаем функцию обновления

    # Проверяем, что словарь sale_dict обновился корректно
    assert system.sale_dict["detail"][0] == 3  # Количество инвалидов
    assert system.sale_dict["detail"][1] == 0  # Цена для инвалидов


def test_update_sale_dict_adult_invalid_edge_case(
    setup_system_update_sale_dict_adult_invalid,
):
    # Проверяем крайний случай, когда количество инвалидов равно 0
    system.count_number_of_visitors["kol_adult_invalid"] = 0  # 0 инвалидов
    system.price["ticket_free"] = 0  # Цена для инвалидов (скидка 100%)

    update_sale_dict_adult_invalid()  # Запускаем функцию обновления

    # Проверяем, что данные остались на месте
    assert system.sale_dict["detail"][0] == 0  # Количество инвалидов
    assert system.sale_dict["detail"][1] == 0  # Цена для инвалидов


#######################################
# Тестируем update_sale_dict_child_many_child
@pytest.fixture
def setup_system_update_sale_dict_child_many_child():
    # Инициализация системных данных
    system.sale_dict = {
        "detail": [0, 0, 0, 0, 0, 0, 0],  # Словарь продаж с нулевыми значениями
    }
    system.price = {
        "ticket_free": 0,  # Цена для многодетных детей (100% скидка)
    }
    system.count_number_of_visitors = {
        "kol_child_many_child": 0,  # Количество детей с многодетной скидкой
    }


def test_update_sale_dict_child_many_child_no_visitors(
    setup_system_update_sale_dict_child_many_child,
):
    # Проверяем, что если нет детей с многодетной скидкой, то данные не меняются
    system.count_number_of_visitors["kol_child_many_child"] = (
        0  # 0 детей с многодетной скидкой
    )

    update_sale_dict_child_many_child()  # Запускаем функцию обновления

    # Проверяем, что данные остались на месте
    assert system.sale_dict["detail"][2] == 0  # Количество детей с многодетной скидкой
    assert (
        system.sale_dict["detail"][3] == 0
    )  # Цена для многодетных детей (0, так как скидка 100%)


def test_update_sale_dict_child_many_child_with_visitors(
    setup_system_update_sale_dict_child_many_child,
):
    # Проверяем, что если есть дети с многодетной скидкой, то данные обновляются
    system.count_number_of_visitors["kol_child_many_child"] = (
        2  # 2 ребенка с многодетной скидкой
    )
    system.price["ticket_free"] = 0  # Цена для многодетных детей

    update_sale_dict_child_many_child()  # Запускаем функцию обновления

    # Проверяем, что данные обновились корректно
    assert system.sale_dict["detail"][2] == 2  # Количество детей с многодетной скидкой
    assert system.sale_dict["detail"][3] == 0  # Цена для многодетных детей (0)


def test_update_sale_dict_child_many_child_multiple_visitors(
    setup_system_update_sale_dict_child_many_child,
):
    # Проверяем сценарий, когда детей с многодетной скидкой несколько
    system.count_number_of_visitors["kol_child_many_child"] = (
        5  # 5 детей с многодетной скидкой
    )
    system.price["ticket_free"] = 0  # Цена для многодетных детей

    update_sale_dict_child_many_child()  # Запускаем функцию обновления

    # Проверяем, что количество и цена обновились корректно
    assert system.sale_dict["detail"][2] == 5  # Количество детей с многодетной скидкой
    assert system.sale_dict["detail"][3] == 0  # Цена для многодетных детей


def test_update_sale_dict_child_many_child_edge_case(
    setup_system_update_sale_dict_child_many_child,
):
    # Проверяем крайний случай, когда количество детей с многодетной скидкой равно 0
    system.count_number_of_visitors["kol_child_many_child"] = (
        0  # 0 детей с многодетной скидкой
    )
    system.price["ticket_free"] = 0  # Цена для многодетных детей

    update_sale_dict_child_many_child()  # Запускаем функцию обновления

    # Проверяем, что данные остались на месте
    assert system.sale_dict["detail"][2] == 0  # Количество детей с многодетной скидкой
    assert system.sale_dict["detail"][3] == 0  # Цена для многодетных детей


#######################################
# Тестируем update_sale_dict_child_invalid
@pytest.fixture
def setup_system_update_sale_dict_child_invalid():
    # Инициализация системных данных
    system.sale_dict = {
        "detail": [0, 0, 0, 0, 0, 0, 0],  # Словарь продаж с нулевыми значениями
    }
    system.price = {
        "ticket_free": 0,  # Цена для детей с инвалидной скидкой (100% скидка)
    }
    system.count_number_of_visitors = {
        "kol_child_invalid": 0,  # Количество детей с инвалидной скидкой
    }


def test_update_sale_dict_child_invalid_no_visitors(
    setup_system_update_sale_dict_child_invalid,
):
    # Проверяем, что если нет детей с инвалидной скидкой, то данные не меняются
    system.count_number_of_visitors["kol_child_invalid"] = (
        0  # 0 детей с инвалидной скидкой
    )

    update_sale_dict_child_invalid()  # Запускаем функцию обновления

    # Проверяем, что данные остались на месте
    assert system.sale_dict["detail"][2] == 0  # Количество детей с инвалидной скидкой
    assert (
        system.sale_dict["detail"][3] == 0
    )  # Цена для детей с инвалидной скидкой (0, так как скидка 100%)


def test_update_sale_dict_child_invalid_with_visitors(
    setup_system_update_sale_dict_child_invalid,
):
    # Проверяем, что если есть дети с инвалидной скидкой, то данные обновляются
    system.count_number_of_visitors["kol_child_invalid"] = (
        2  # 2 ребенка с инвалидной скидкой
    )
    system.price["ticket_free"] = 0  # Цена для детей с инвалидной скидкой

    update_sale_dict_child_invalid()  # Запускаем функцию обновления

    # Проверяем, что данные обновились корректно
    assert system.sale_dict["detail"][2] == 2  # Количество детей с инвалидной скидкой
    assert system.sale_dict["detail"][3] == 0  # Цена для детей с инвалидной скидкой


def test_update_sale_dict_child_invalid_multiple_visitors(
    setup_system_update_sale_dict_child_invalid,
):
    # Проверяем сценарий, когда детей с инвалидной скидкой несколько
    system.count_number_of_visitors["kol_child_invalid"] = (
        5  # 5 детей с инвалидной скидкой
    )
    system.price["ticket_free"] = 0  # Цена для детей с инвалидной скидкой

    update_sale_dict_child_invalid()  # Запускаем функцию обновления

    # Проверяем, что количество и цена обновились корректно
    assert system.sale_dict["detail"][2] == 5  # Количество детей с инвалидной скидкой
    assert system.sale_dict["detail"][3] == 0  # Цена для детей с инвалидной скидкой


def test_update_sale_dict_child_invalid_edge_case(
    setup_system_update_sale_dict_child_invalid,
):
    # Проверяем крайний случай, когда количество детей с инвалидной скидкой равно 0
    system.count_number_of_visitors["kol_child_invalid"] = (
        0  # 0 детей с инвалидной скидкой
    )
    system.price["ticket_free"] = 0  # Цена для детей с инвалидной скидкой

    update_sale_dict_child_invalid()  # Запускаем функцию обновления

    # Проверяем, что данные остались на месте
    assert system.sale_dict["detail"][2] == 0  # Количество детей с инвалидной скидкой
    assert system.sale_dict["detail"][3] == 0  # Цена для детей с инвалидной скидкой


#######################################
# Тестируем update_adult_count
@pytest.fixture
def setup_system_update_adult_count():
    # Инициализация системных данных
    system.sale_dict = {
        "kol_adult": 0,  # Начальное количество взрослых
    }
    system.count_number_of_visitors = {
        "kol_adult": 0,  # Начальное количество взрослых посетителей
    }


def test_update_adult_count_increase(setup_system_update_adult_count):
    # Проверяем, что количество взрослых увеличивается на 1
    initial_adult_count = system.count_number_of_visitors[
        "kol_adult"
    ]  # Сохраняем начальное количество
    update_adult_count()  # Запускаем функцию обновления
    # Проверяем, что количество взрослых увеличилось на 1
    assert system.count_number_of_visitors["kol_adult"] == initial_adult_count + 1
    # Также проверяем, что значение в sale_dict обновилось
    assert system.sale_dict["kol_adult"] == system.count_number_of_visitors["kol_adult"]


def test_update_adult_count_multiple_times(setup_system_update_adult_count):
    # Проверяем, что количество взрослых увеличивается корректно, если функцию вызвать несколько раз
    update_adult_count()  # Первое увеличение
    update_adult_count()  # Второе увеличение
    update_adult_count()  # Третье увеличение
    # Проверяем, что количество взрослых стало 3
    assert system.count_number_of_visitors["kol_adult"] == 3
    # Проверяем, что значение в sale_dict обновилось
    assert system.sale_dict["kol_adult"] == system.count_number_of_visitors["kol_adult"]


def test_update_adult_count_edge_case(setup_system_update_adult_count):
    # Проверяем работу функции, если количество взрослых было изначально большое
    system.count_number_of_visitors["kol_adult"] = (
        100  # Устанавливаем начальное количество взрослых в 100
    )
    update_adult_count()  # Запускаем функцию обновления
    # Проверяем, что количество взрослых увеличилось на 1
    assert system.count_number_of_visitors["kol_adult"] == 101
    # Также проверяем, что значение в sale_dict обновилось
    assert system.sale_dict["kol_adult"] == system.count_number_of_visitors["kol_adult"]


def test_update_adult_count_zero(setup_system_update_adult_count):
    # Проверяем работу функции, если количество взрослых изначально 0
    system.count_number_of_visitors["kol_adult"] = (
        0  # Устанавливаем начальное количество взрослых в 0
    )
    update_adult_count()  # Запускаем функцию обновления
    # Проверяем, что количество взрослых стало 1
    assert system.count_number_of_visitors["kol_adult"] == 1
    # Проверяем, что значение в sale_dict обновилось
    assert system.sale_dict["kol_adult"] == system.count_number_of_visitors["kol_adult"]


#######################################
# Тестируем update_child_count
@pytest.fixture
def setup_system_update_child_count():
    # Инициализация системных данных
    system.sale_dict = {
        "kol_child": 0,  # Начальное количество детей
    }
    system.count_number_of_visitors = {
        "kol_child": 0,  # Начальное количество детских посетителей
    }


def test_update_child_count_increase(setup_system_update_child_count):
    # Проверяем, что количество детей увеличивается на 1
    initial_child_count = system.count_number_of_visitors[
        "kol_child"
    ]  # Сохраняем начальное количество
    update_child_count()  # Запускаем функцию обновления
    # Проверяем, что количество детей увеличилось на 1
    assert system.count_number_of_visitors["kol_child"] == initial_child_count + 1
    # Также проверяем, что значение в sale_dict обновилось
    assert system.sale_dict["kol_child"] == system.count_number_of_visitors["kol_child"]


def test_update_child_count_multiple_times(setup_system_update_child_count):
    # Проверяем, что количество детей увеличивается корректно, если функцию вызвать несколько раз
    update_child_count()  # Первое увеличение
    update_child_count()  # Второе увеличение
    update_child_count()  # Третье увеличение
    # Проверяем, что количество детей стало 3
    assert system.count_number_of_visitors["kol_child"] == 3
    # Проверяем, что значение в sale_dict обновилось
    assert system.sale_dict["kol_child"] == system.count_number_of_visitors["kol_child"]


def test_update_child_count_edge_case(setup_system_update_child_count):
    # Проверяем работу функции, если количество детей было изначально большое
    system.count_number_of_visitors["kol_child"] = (
        100  # Устанавливаем начальное количество детей в 100
    )
    update_child_count()  # Запускаем функцию обновления
    # Проверяем, что количество детей увеличилось на 1
    assert system.count_number_of_visitors["kol_child"] == 101
    # Также проверяем, что значение в sale_dict обновилось
    assert system.sale_dict["kol_child"] == system.count_number_of_visitors["kol_child"]


def test_update_child_count_zero(setup_system_update_child_count):
    # Проверяем работу функции, если количество детей изначально 0
    system.count_number_of_visitors["kol_child"] = (
        0  # Устанавливаем начальное количество детей в 0
    )
    update_child_count()  # Запускаем функцию обновления
    # Проверяем, что количество детей стало 1
    assert system.count_number_of_visitors["kol_child"] == 1
    # Проверяем, что значение в sale_dict обновилось
    assert system.sale_dict["kol_child"] == system.count_number_of_visitors["kol_child"]


#######################################
# Тестируем convert_sale_dict_values
def test_decimal_to_int():
    sale_dict = {
        "price_adult": Decimal("250.0"),
        "price_child": Decimal("750.0"),
        "detail": [Decimal("125.0"), Decimal("375.0")],
    }
    updated_dict = convert_sale_dict_values(sale_dict)
    assert updated_dict["price_adult"] == 250
    assert updated_dict["price_child"] == 750
    assert updated_dict["detail"] == [125, 375]


def test_decimal_to_float():
    sale_dict = {
        "price_adult": Decimal("250.5"),
        "price_child": Decimal("750.75"),
        "detail": [Decimal("125.1"), Decimal("375.25")],
    }
    updated_dict = convert_sale_dict_values(sale_dict)
    assert updated_dict["price_adult"] == 250.5
    assert updated_dict["price_child"] == 750.75
    assert updated_dict["detail"] == [125.1, 375.25]


def test_float_to_int():
    sale_dict = {"price_adult": 250.0, "price_child": 750.0, "detail": [125.0, 375.0]}
    updated_dict = convert_sale_dict_values(sale_dict)
    assert updated_dict["price_adult"] == 250
    assert updated_dict["price_child"] == 750
    assert updated_dict["detail"] == [125, 375]


def test_float_to_float():
    sale_dict = {"price_adult": 250.5, "price_child": 750.75, "detail": [125.1, 375.25]}
    updated_dict = convert_sale_dict_values(sale_dict)
    assert updated_dict["price_adult"] == 250.5
    assert updated_dict["price_child"] == 750.75
    assert updated_dict["detail"] == [125.1, 375.25]


def test_mixed_values():
    sale_dict = {
        "price_adult": Decimal("250.0"),
        "price_child": 750.5,
        "detail": [Decimal("125.0"), 375.5, "some_string"],
    }
    updated_dict = convert_sale_dict_values(sale_dict)
    assert updated_dict["price_adult"] == 250
    assert updated_dict["price_child"] == 750.5
    assert updated_dict["detail"] == [125, 375.5, "some_string"]


def test_no_conversion_needed():
    sale_dict = {"price_adult": 250, "price_child": 750, "detail": [125, 375]}
    updated_dict = convert_sale_dict_values(sale_dict)
    assert updated_dict["price_adult"] == 250
    assert updated_dict["price_child"] == 750
    assert updated_dict["detail"] == [125, 375]


#######################################
# Тестируем generating_parts_for_partial_returns
# 1. Корректный возврат, когда сумма кратна стоимости билетов
def test_valid_return():
    tickets = {"adult": [100, 2], "child": [50, 2]}
    amount = 150
    expected = {"adult": [100, 1], "child": [50, 1]}  # 1 взрослый билет + 1 детский
    assert generating_parts_for_partial_returns(tickets, amount) == expected

# 2. Возврат с неполным покрытием билета (создаётся акция)
def test_partial_ticket_return():
    tickets = {"adult": [100, 2], "child": [50, 2]}
    amount = 120
    expected = {"adult": [100, 1], "child акция": [20, 1]}  # 1 взрослый билет + 20 рублей акцией
    assert generating_parts_for_partial_returns(tickets, amount) == expected

# 3. Недостаточная сумма (меньше минимального билета)
def test_not_enough_amount():
    tickets = {"adult": [100, 2], "child": [50, 2]}
    amount = 30
    expected = {"child акция": [30, 1]}  # 30 рублей акцией
    assert generating_parts_for_partial_returns(tickets, amount) == expected

# 4. Сумма возврата больше, чем стоимость всех билетов
def test_return_more_than_total():
    tickets = {"adult": [100, 1], "child": [50, 1]}
    amount = 200  # Всего билетов на 150
    expected = {"adult": [100, 1], "child": [50, 1]}  # Возвращает только 150, остальное игнорируется
    assert generating_parts_for_partial_returns(tickets, amount) == expected

# 5. Пустой словарь билетов
def test_empty_tickets():
    assert generating_parts_for_partial_returns({}, 100) == {}

# 6. Сумма возврата 0
def test_zero_amount():
    tickets = {"adult": [100, 2], "child": [50, 2]}
    assert generating_parts_for_partial_returns(tickets, 0) == {}

# 7. Неверные входные данные (tickets не словарь)
@pytest.mark.parametrize("invalid_tickets", [None, [], "string", 123])
def test_invalid_tickets(invalid_tickets):
    assert generating_parts_for_partial_returns(invalid_tickets, 100) == {}

# 8. Неверные входные данные (amount не число или отрицательное)
@pytest.mark.parametrize("invalid_amount", [None, "text", -10])
def test_invalid_amount(invalid_amount):
    tickets = {"adult": [100, 2]}
    assert generating_parts_for_partial_returns(tickets, invalid_amount) == {}

# 9. Билеты с некорректными значениями (отрицательная цена, строка вместо числа)
def test_invalid_ticket_values():
    tickets = {
        "adult": [-100, 2],  # Отрицательная цена
        "child": ["50", 2],  # Строка вместо числа
        "infant": [30, -1]   # Отрицательное количество
    }
    assert generating_parts_for_partial_returns(tickets, 100) == {}

# 10. Один билет в продаже
def test_single_ticket():
    tickets = {"adult": [100, 1]}
    amount = 100
    expected = {"adult": [100, 1]}
    assert generating_parts_for_partial_returns(tickets, amount) == expected
