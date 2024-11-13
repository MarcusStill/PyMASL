import logging
from datetime import date
from decimal import Decimal

from modules.system import System

system = System()

logger = logging.getLogger(__name__)


def calculate_age(birth_date: date) -> int:
    """
    Функция вычисляет возраст посетителя.

    Параметры:
        born (date): Дата рождения.

    Возвращаемое значение:
        int: Возраст.
    """
    logger.info("Запуск функцию calculate_age")
    # Используем функцию get_today_date для получения текущей даты
    today = get_today_date()
    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


def get_today_date():
    """Функция для получения текущей даты (можно подменить в тестах)."""
    logger.info("Запуск функцию get_today_date")
    return date.today()


def calculate_ticket_type(age: int) -> str:
    """
    Функция определяет тип входного билета.

    Параметры:
        age (int): Возраст посетителя.

    Возвращаемое значение:
        str: Тип билета (бесплатный, детский, взрослый).
    """
    logger.info("Запуск функцию calculate_ticket_type")
    result: str = ""
    if age < system.age["min"]:
        result = "бесплатный"
    elif system.age["min"] <= age < system.age["max"]:
        result = "детский"
    elif age >= system.age["max"]:
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
    logger.info("Запуск функцию calculated_ticket_price")
    try:
        if type_ticket == "бесплатный":
            return system.price["ticket_free"]
        elif type_ticket == "взрослый":
            key = f"ticket_adult_{time}"
            return system.price[key]
        else:
            key = f"ticket_child_{time}"
            return system.price[key]
    except KeyError as e:
        raise KeyError(
            f"Не найден ключ для типа билета {type_ticket} на {time} час. Ошибка: {e}"
        )


def calculate_adult_price() -> int:
    """
    Считает цену взрослого билета в зависимости от продолжительности и категорий.

    Параметры:
        None

    Возвращаемое значение:
        int: Цена взрослого билета.
    """
    logger.info("Запуск функцию calculate_adult_price")
    duration = system.sale_dict["detail"][6]
    # Если продолжительность посещения 1 час
    if duration == 1:
        return system.price["ticket_adult_1"]
    elif duration == 2:
        # Проверка многодетной скидки только в будний день
        if (
            system.count_number_of_visitors["many_child"] == 1
            and system.what_a_day == 0
        ):
            system.count_number_of_visitors["kol_adult_many_child"] += 1
            # Изменяем цену и записываем размер скидки
            update_sale_dict_adult_many_child()
            return system.price["ticket_free"]
        # Если обычный день
        else:
            return system.price["ticket_adult_2"]
    else:
        # Если продолжительность 3 часа
        # Если в продаже инвалид
        if system.count_number_of_visitors["invalid"] == 1:
            system.count_number_of_visitors["kol_adult_invalid"] += 1
            update_sale_dict_adult_invalid()
            return system.price["ticket_free"]
        return system.price["ticket_adult_3"]


def calculate_child_price() -> int:
    """
    Считает цену взрослого билета в зависимости от продолжительности и категорий.

    Параметры:
        None

    Возвращаемое значение:
        int: Цена взрослого билета.
    """
    logger.info("Запуск функцию calculate_child_price")
    duration = system.sale_dict["detail"][6]
    is_weekend = system.what_a_day != 0
    if duration == 1:
        return (
            system.price["ticket_child_week_1"]
            if is_weekend
            else system.price["ticket_child_1"]
        )
    elif duration == 2:
        if system.count_number_of_visitors["many_child"] == 1:
            system.count_number_of_visitors["kol_child_many_child"] += 1
            update_sale_dict_child_many_child()
            return system.price["ticket_free"]
        return (
            system.price["ticket_child_week_2"]
            if is_weekend
            else system.price["ticket_child_2"]
        )
    else:
        if system.count_number_of_visitors["invalid"] == 1:
            system.count_number_of_visitors["kol_child_invalid"] += 1
            update_sale_dict_child_invalid()
            return system.price["ticket_free"]
        return (
            system.price["ticket_child_week_3"]
            if is_weekend
            else system.price["ticket_child_3"]
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
    logger.info("Запуск функцию calculate_discounted_price")
    new_price = price
    category = ""
    discount_status = False
    # В день многодетных
    if system.count_number_of_visitors["many_child"] == 1:
        logger.info("Скидка 100% в день многодетных")
        # Помечаем продажу как "особенную"
        system.sale_special = 1
        new_price = system.price["ticket_free"]
    # Скидка 50% в будни
    elif system.count_number_of_visitors["many_child"] == 2:
        logger.info("Скидка 50% многодетным в будни")
        new_price: int = round(price * 0.5)
    # Скидка инвалидам
    elif system.count_number_of_visitors["invalid"] == 1:
        logger.info("Скидка 100% инвалидам")
        # Помечаем продажу как "особенную"
        system.sale_special = 1
        new_price = system.price["ticket_free"]
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
    logger.info("Запуск функцию calculate_discount")
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
    # Проверка на корректность данных (например, отрицательные значения)
    if (
        system.sale_dict["kol_adult"] < 0
        or system.sale_dict["kol_child"] < 0
        or system.sale_dict["price_adult"] < 0
        or system.sale_dict["price_child"] < 0
    ):
        raise ValueError("Некорректные данные для расчета итоговой суммы")

    adult_ticket: int = (
        system.sale_dict["kol_adult"] - system.sale_dict["detail"][0]
    ) * system.sale_dict["price_adult"]
    child_ticket: int = (
        system.sale_dict["kol_child"] - system.sale_dict["detail"][2]
    ) * system.sale_dict["price_child"]
    adult_sale: int = system.sale_dict["detail"][0] * system.sale_dict["detail"][1]
    child_sale: int = system.sale_dict["detail"][2] * system.sale_dict["detail"][3]
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
    logger.info("Запуск функцию get_talent_based_on_time")
    if time_ticket == 1:
        return 1, system.talent["1_hour"]
    elif time_ticket == 2:
        return 2, system.talent["2_hour"]
    elif time_ticket == 3:
        return 3, system.talent["3_hour"]
    return 0, 0


def update_sale_dict_adult_many_child() -> None:
    """
    Обновляет словарь продаж для взрослого с многодетной скидкой.

    Параметры:
        None

    Возвращаемое значение:
        None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
    """
    logger.info("Запуск функцию update_sale_dict_adult_many_child")
    logger.debug("Добавляем взрослого многодетного в sale_dict[detail]")
    system.sale_dict["detail"][0] = system.count_number_of_visitors[
        "kol_adult_many_child"
    ]
    system.sale_dict["detail"][1] = system.price["ticket_free"]


def update_sale_dict_adult_invalid() -> None:
    """
    Обновляет словарь продаж для взрослого с инвалидной скидкой.

    Параметры:
        None

    Возвращаемое значение:
        None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
    """
    logger.info("Запуск функцию update_sale_dict_adult_invalid")
    system.sale_dict["detail"][0] = system.count_number_of_visitors["kol_adult_invalid"]
    system.sale_dict["detail"][1] = system.price["ticket_free"]


def update_sale_dict_child_many_child() -> None:
    """
    Обновляет словарь продаж для ребенка с многодетной скидкой.

    Параметры:
        None

    Возвращаемое значение:
        None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
    """
    logger.info("Запуск функцию update_sale_dict_child_many_child")
    system.sale_dict["detail"][2] = system.count_number_of_visitors[
        "kol_child_many_child"
    ]
    system.sale_dict["detail"][3] = system.price["ticket_free"]


def update_sale_dict_child_invalid() -> None:
    """
    Обновляет словарь продаж для ребенка с инвалидной скидкой.

    Параметры:
        None

    Возвращаемое значение:
        None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
    """
    logger.info("Запуск функцию update_sale_dict_child_invalid")
    system.sale_dict["detail"][2] = system.count_number_of_visitors["kol_child_invalid"]
    system.sale_dict["detail"][3] = system.price["ticket_free"]


def update_adult_count() -> None:
    """
    Обновляет счетчик взрослых посетителей.

    Параметры:
        None

    Возвращаемое значение:
        None: Функция не возвращает значений, вставляет фамилию в поле формы.
    """
    logger.info("Запуск функцию update_adult_count")
    system.count_number_of_visitors["kol_adult"] += 1
    system.sale_dict["kol_adult"] = system.count_number_of_visitors["kol_adult"]


def update_child_count() -> None:
    """
    Обновляет счетчик детских билетов.

    Параметры:
        None

    Возвращаемое значение:
        None: Функция не возвращает значений, вставляет фамилию в поле формы.
    """
    logger.info("Запуск функцию update_child_count")
    system.count_number_of_visitors["kol_child"] += 1
    system.sale_dict["kol_child"] = system.count_number_of_visitors["kol_child"]


def convert_sale_dict_values(sale_dict):
    """
    Преобразует значения в словаре sale_dict в правильные типы данных (int или float).
    Применяется в конце расчетов перед записью в базу данных.

    :param sale_dict: Словарь с данными продажи.
    :return: Обновленный словарь с корректными типами данных.
    """
    for key, value in sale_dict.items():
        if isinstance(value, list):
            # Если значение - это список, проходим по его элементам
            for i in range(len(value)):
                # Проверяем, является ли значение Decimal или float
                if isinstance(value[i], Decimal):
                    # Если значение Decimal целое (например, Decimal(10.0)), преобразуем в int
                    value[i] = int(value[i]) if value[i] == value[i].to_integral_value() else float(value[i])
                elif isinstance(value[i], float):
                    # Если значение float целое (например, 10.0), преобразуем в int
                    value[i] = int(value[i]) if value[i].is_integer() else value[i]
        elif isinstance(value, Decimal):
            # Преобразуем Decimal в int или float
            sale_dict[key] = int(value) if value == value.to_integral_value() else float(value)
        elif isinstance(value, float):
            # Если значение float целое (например, 10.0), преобразуем в int
            sale_dict[key] = int(value) if value.is_integer() else value

    return sale_dict
