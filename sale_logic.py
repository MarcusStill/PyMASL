import logging
from datetime import date
from decimal import Decimal

from system import System

logger = logging.getLogger(__name__)

# Возраст посетителей
age_client: dict = {"min": 5, "max": 15}


def calculate_age(birth_date: date) -> int:
    """
    Функция вычисляет возраст посетителя.

    Параметры:
        born (date): Дата рождения.

    Возвращаемое значение:
        int: Возраст.
    """
    today = get_today_date()  # Используем функцию get_today_date для получения текущей даты
    return (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


def get_today_date():
    """Функция для получения текущей даты (можно подменить в тестах)."""
    return date.today()


def calculate_ticket_type(age: int) -> str:
    """
    Функция определяет тип входного билета.

    Параметры:
        age (int): Возраст посетителя.

    Возвращаемое значение:
        str: Тип билета (бесплатный, детский, взрослый).
    """
    result: str = ""
    if age < age_client["min"]:
        result = "бесплатный"
    elif age_client["min"] <= age < age_client["max"]:
        result = "детский"
    elif age >= age_client["max"]:
        result = "взрослый"
    return result


def calculated_ticket_price(type_ticket: str, time: int) -> int:
    """
    Функция определяет стоимость входного билета.

    Параметры:
        type_ticket (str): Тип билета.
        time(int): Время пребывания.

    Возвращаемое значение:
        str: Тип билета (бесплатный, детский, взрослый).
    """
    try:
        if type_ticket == "бесплатный":
            return System.price["ticket_free"]
        elif type_ticket == "взрослый":
            key = f"ticket_adult_{time}"
            return System.price[key]
        else:
            key = f"ticket_child_{time}"
            return System.price[key]
    except KeyError as e:
        raise KeyError(f"Не найден ключ для типа билета {type_ticket} на {time} час. Ошибка: {e}")

def calculate_adult_price() -> int:
    """
    Считает цену взрослого билета в зависимости от продолжительности и категорий.

    Параметры:
        None

    Возвращаемое значение:
        int: Цена взрослого билета.
    """
    duration = System.sale_dict["detail"][6]
    # Если продолжительность посещения 1 час
    if duration == 1:
        return System.price["ticket_adult_1"]
    elif duration == 2:
        # Если день многодетных
        if System.count_number_of_visitors["many_child"] == 1:
            System.count_number_of_visitors["kol_adult_many_child"] += 1
            # Изменяем цену и записываем размер скидки
            update_sale_dict_adult_many_child()
            return System.price["ticket_free"]
        # Если обычный день
        else:
            return System.price["ticket_adult_2"]
    else:
        # Если продолжительность 3 часа
        # Если в продаже инвалид
        if System.count_number_of_visitors["invalid"] == 1:
            System.count_number_of_visitors["kol_adult_invalid"] += 1
            update_sale_dict_adult_invalid()
            return System.price["ticket_free"]
        return System.price["ticket_adult_3"]


def calculate_child_price() -> int:
    """
    Считает цену взрослого билета в зависимости от продолжительности и категорий.

    Параметры:
        None

    Возвращаемое значение:
        int: Цена взрослого билета.
    """
    duration = System.sale_dict["detail"][6]
    is_weekend = System.what_a_day != 0
    if duration == 1:
        return (
            System.price["ticket_child_week_1"]
            if is_weekend
            else System.price["ticket_child_1"]
        )
    elif duration == 2:
        if System.count_number_of_visitors["many_child"] == 1:
            System.count_number_of_visitors["kol_child_many_child"] += 1
            update_sale_dict_child_many_child()
            return System.price["ticket_free"]
        return (
            System.price["ticket_child_week_2"]
            if is_weekend
            else System.price["ticket_child_2"]
        )
    else:
        if System.count_number_of_visitors["invalid"] == 1:
            System.count_number_of_visitors["kol_child_invalid"] += 1
            update_sale_dict_child_invalid()
            return System.price["ticket_free"]
        return (
            System.price["ticket_child_week_3"]
            if is_weekend
            else System.price["ticket_child_3"]
        )


def calculate_discounted_price(price: int, type_ticket: str):
    """
    Рассчитывает итоговую цену с учетом скидок и специальных условий.

    Параметры:
        price (int): Цена до применения скидок.
        type_ticket (str): Тип билета (взрослый или детский).

    Возвращает:
        tuple[int, bool, str]: Итоговая цена, флаг особой продажи, категория билета.
    """
    new_price = price
    category = ""
    discount_status = False
    # В день многодетных
    if System.count_number_of_visitors["many_child"] == 1:
        logger.info("Скидка 100% в день многодетных")
        # Помечаем продажу как "особенную"
        System.sale_special = 1
        new_price = System.price["ticket_free"]
    # Скидка 50% в будни
    elif System.count_number_of_visitors["many_child"] == 2:
        logger.info("Скидка 50% многодетным в будни")
        new_price: int = round(price * 0.5)
    # Скидка инвалидам
    elif System.count_number_of_visitors["invalid"] == 1:
        logger.info("Скидка 100% инвалидам")
        # Помечаем продажу как "особенную"
        System.sale_special = 1
        new_price = System.price["ticket_free"]
        if type_ticket == "взрослый":
            category = "с"  # сопровождающий
    return new_price, category, discount_status


def calculate_discount(value_1, value_2) -> Decimal:
    """
    Вычисляет новую цену после применения скидки.

    Параметры:
        value_1 (int): Исходная цена.
        value_2 (int): Размер скидки в процентах.

    Возвращаемое значение:
        Decimal: Новая цена после применения скидки.
    """
    # Проверка на корректность скидки: 0 ≤ value_2 ≤ 100
    price = Decimal(value_1)
    sale_discount = Decimal(max(0, min(value_2, 100)))
    return price - (price * sale_discount / Decimal(100))


def calculate_itog() -> int:
    """
    Функция рассчитывает итоговую сумму заказа.

    Параметры:
        None

    Возвращаемое значение:
        None: Функция не возвращает значений, вставляет фамилию в поле формы.
    """
    logger.info("Запуск функцию calculate_itog")
    adult_ticket: int = (
        System.sale_dict["kol_adult"] - System.sale_dict["detail"][0]
    ) * System.sale_dict["price_adult"]
    child_ticket: int = (
        System.sale_dict["kol_child"] - System.sale_dict["detail"][2]
    ) * System.sale_dict["price_child"]
    adult_sale: int = System.sale_dict["detail"][0] * System.sale_dict["detail"][1]
    child_sale: int = System.sale_dict["detail"][2] * System.sale_dict["detail"][3]
    # Вычисляем итоговую сумму
    result: int = adult_ticket + child_ticket + adult_sale + child_sale
    return result


def get_talent_based_on_time(time_ticket: int):
    """Возвращает количество талантов в зависимости от времени.

    Параметры:
        time_ticket (int): Время в часах.

    Возвращаемое значение:
        tuple[int, int]: Количество талантов и соответствующее значение таланта из системы.
    """
    if time_ticket == 1:
        return 1, System.talent["1_hour"]
    elif time_ticket == 2:
        return 2, System.talent["2_hour"]
    elif time_ticket == 3:
        return 3, System.talent["3_hour"]
    return 0, 0


def update_sale_dict_adult_many_child() -> None:
    """
    Обновляет словарь продаж для взрослого с многодетной скидкой.

    Параметры:
        None

    Возвращаемое значение:
        None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
    """
    logger.debug("Добавляем взрослого многодетного в sale_dict[detail]")
    System.sale_dict["detail"][0] = System.count_number_of_visitors[
        "kol_adult_many_child"
    ]
    System.sale_dict["detail"][1] = System.price["ticket_free"]


def update_sale_dict_adult_invalid() -> None:
    """
    Обновляет словарь продаж для взрослого с инвалидной скидкой.

    Параметры:
        None

    Возвращаемое значение:
        None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
    """
    System.sale_dict["detail"][0] = System.count_number_of_visitors["kol_adult_invalid"]
    System.sale_dict["detail"][1] = System.price["ticket_free"]


def update_sale_dict_child_many_child() -> None:
    """
    Обновляет словарь продаж для ребенка с многодетной скидкой.

    Параметры:
        None

    Возвращаемое значение:
        None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
    """
    System.sale_dict["detail"][2] = System.count_number_of_visitors[
        "kol_child_many_child"
    ]
    System.sale_dict["detail"][3] = System.price["ticket_free"]


def update_sale_dict_child_invalid() -> None:
    """
    Обновляет словарь продаж для ребенка с инвалидной скидкой.

    Параметры:
        None

    Возвращаемое значение:
        None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
    """
    System.sale_dict["detail"][2] = System.count_number_of_visitors["kol_child_invalid"]
    System.sale_dict["detail"][3] = System.price["ticket_free"]


def update_adult_count() -> None:
    """
    Обновляет счетчик взрослых посетителей.

    Параметры:
        None

    Возвращаемое значение:
        None: Функция не возвращает значений, вставляет фамилию в поле формы.
    """
    System.count_number_of_visitors["kol_adult"] += 1
    System.sale_dict["kol_adult"] = System.count_number_of_visitors["kol_adult"]


def update_child_count() -> None:
    """
    Обновляет счетчик детских билетов.

    Параметры:
        None

    Возвращаемое значение:
        None: Функция не возвращает значений, вставляет фамилию в поле формы.
    """
    System.count_number_of_visitors["kol_child"] += 1
    System.sale_dict["kol_child"] = System.count_number_of_visitors["kol_child"]
