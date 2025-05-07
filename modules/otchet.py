from datetime import datetime
from typing import Any, Dict, List, Tuple, Union

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, letter
from reportlab.lib.units import mm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from modules.config import Config
from modules.logger import *
from modules.system import System

system = System()
config = Config()


def generate_saved_tickets(values: List[List[Any]]) -> None:
    """
    Функция генерирует PDF-файл с билетами на основе переданных данных о клиентах.

    Параметры:
        values (list): Список клиентов, для каждого из которых указываются данные в формате:
            [
                [Фамилия, Имя, ..., Цена, Признак "не идет", ..., Возраст, Продолжительность, Таланты, Дата/время],
                ...
            ]

    Описание работы:
        - Определяет тип билета (взрослый, детский, бесплатный) на основе возраста.
        - Пропускает генерацию билета для бесплатных клиентов и тех, у кого признак "не идет" равен "н".
        - Загружает координаты элементов билета из конфигурационного файла.
        - Создает PDF-файл `ticket.pdf`, размещая на каждой странице информацию о клиенте:
            ФИО, возраст, дата, продолжительность пребывания, тип билета, цена, таланты, QR-код и др.
        - Использует шрифт DejaVuSerif и фоновые изображения (например, QR-код).

    Возвращаемое значение:
        None: Функция сохраняет PDF-файл и не возвращает значения.
    """
    logger.info("Запуск функции generate_saved_tickets")
    client_in_sale = values
    type_ticket = None
    img_file = "files/qr-code.jpg"
    path = "./ticket.pdf"
    coordinates = system.load_coordinates(
        config
    )  # Путь к файлу координат берется из Config
    pdfmetrics.registerFont(TTFont("DejaVuSerif", "files/DejaVuSerif.ttf"))
    c = canvas.Canvas(path, pagesize=(landscape(letter)))
    for i in range(len(client_in_sale)):
        age_str = client_in_sale[i][6]
        age = int(age_str) if age_str.isdigit() else 0
        not_go = client_in_sale[i][4]
        if age < 5:
            type_ticket = "бесплатный"
        elif 5 <= age < 15:
            type_ticket = "детский"
        elif age >= 15:
            type_ticket = "взрослый"
        if type_ticket != "бесплатный" and not_go != "н":
            date_time = str(client_in_sale[i][9])

            c.setFont("DejaVuSerif", 12)
            # Имя
            # x - расстояние мм от левого края страницы
            # y - расстояние мм от нижнего края страницы
            c.drawString(
                coordinates["name"]["x"] * mm,
                coordinates["name"]["y"] * mm,
                str(client_in_sale[i][1])
                .replace("'", "")
                .replace("[", "")
                .replace("]", ""),
            )
            # Фамилия
            c.drawString(
                coordinates["surname"]["x"] * mm,
                coordinates["surname"]["y"] * mm,
                str(client_in_sale[i][0])
                .replace("'", "")
                .replace("[", "")
                .replace("]", ""),
            )
            # Возраст
            c.drawString(
                coordinates["age"]["x"] * mm,
                coordinates["age"]["y"] * mm,
                str(age).replace("'", "").replace("[", "").replace("]", ""),
            )
            # Продолжительность
            duration_text = f"{client_in_sale[i][7]} ч. пребывания"
            if client_in_sale[i][7] == 3:
                duration_text += "-весь день"
            c.drawString(
                coordinates["duration"]["x"] * mm,
                coordinates["duration"]["y"] * mm,
                duration_text.replace("'", "").replace("[", "").replace("]", ""),
            )
            # Дата и время билета
            c.drawString(
                coordinates["date"]["x"] * mm,
                coordinates["date"]["y"] * mm,
                str(date_time[0:10]).replace("'", "").replace("[", "").replace("]", ""),
            )
            c.drawString(
                coordinates["guest"]["x"] * mm, coordinates["guest"]["y"] * mm, "гость"
            )
            c.drawString(
                coordinates["city"]["x"] * mm, coordinates["city"]["y"] * mm, "БЕЛГОРОД"
            )
            c.drawString(
                coordinates["place"]["x"] * mm,
                coordinates["place"]["y"] * mm,
                "МАСТЕРСЛАВЛЬ",
            )
            # Цена
            c.drawString(
                coordinates["price"]["x"] * mm,
                coordinates["price"]["y"] * mm,
                f"{client_in_sale[i][3]} руб.".replace("'", "")
                .replace("[", "")
                .replace("]", ""),
            )
            # Тип билета
            c.drawString(
                coordinates["ticket_type"]["x"] * mm,
                coordinates["ticket_type"]["y"] * mm,
                str(type_ticket).replace("'", "").replace("[", "").replace("]", ""),
            )
            # Доп.отметки
            c.drawString(
                coordinates["notes"]["x"] * mm,
                coordinates["notes"]["y"] * mm,
                str(client_in_sale[i][4]),
            )
            # Таланты
            c.setFont("DejaVuSerif", 24)
            if type_ticket == "взрослый":
                c.drawString(
                    coordinates["talents"]["x"] * mm,
                    coordinates["talents"]["y"] * mm,
                    "0".replace("'", "").replace("[", "").replace("]", ""),
                )
            else:
                c.drawString(
                    coordinates["talents"]["x"] * mm,
                    coordinates["talents"]["y"] * mm,
                    str(client_in_sale[i][8])
                    .replace("'", "")
                    .replace("[", "")
                    .replace("]", ""),
                )
            c.drawImage(
                img_file,
                coordinates["qr_code"]["x"],
                coordinates["qr_code"]["y"],
                height=80,
                width=80,
                preserveAspectRatio=True,
                mask="auto",
            )

            c.showPage()
    c.save()


def generate_ticket_report_table(ticket_summary: dict) -> list[list]:
    """
    Формирует таблицу отчета по билетам, включая агрегированные строки, используя данные из ticket_summary.
    Отсутствующие категории заполняются нулями.

    Параметры:
        ticket_summary: dict
            Словарь с данными о типах билетов, где ключами являются названия типов билетов,
            а значениями - словари с ценами, количеством и суммой для каждого билета.

    Возвращаемое значение:
        list[list]:
            Список строк, представляющих таблицу отчета. Каждая строка содержит информацию о типе билета,
            его цене, количестве и сумме. Также в таблице присутствуют агрегированные строки для каждого
            типа билета (взрослые, детские, многодетные и т.д.).

    Примечания:
        - В таблице присутствуют следующие типы билетов: взрослый, детский, многодетный, инвалид и сопровождающий.
        - В случае отсутствия данных для какого-либо типа билета, в таблицу добавляется строка с нулями.
        - В конце таблицы добавляются строки с агрегацией по количеству и сумме для разных типов билетов.
    """
    logger.info("Запуск функции generate_ticket_report_table")
    type_ticket = [
        "Взрослый, 1 ч.", "Взрослый, 2 ч.", "Взрослый, 3 ч.",
        "Детский, 1 ч.", "Детский, 2 ч.", "Детский, 3 ч.",
        "Многодетный взрослый, 1 ч.", "Многодетный взрослый, 2 ч.", "Многодетный взрослый, 3 ч.",
        "Многодетный детский, 1 ч.", "Многодетный детский, 2 ч.", "Многодетный детский, 3 ч.",
        "Инвалид, 3 ч.", "Сопровождающий, 3 ч.",
    ]
    data = [["№\n п/п", "Тип\nбилета", "Цена,\n руб.", "Количество,\n шт.", "Стоимость,\n руб."]]
    # Счётчики для агрегатов
    total = {
        "adult": {"count": 0, "sum": 0},
        "child": {"count": 0, "sum": 0},
        "many_adult": {"count": 0, "sum": 0},
        "many_child": {"count": 0, "sum": 0},
        "disabled": {"count": 0},
        "maintainer": {"count": 0},
    }
    row_num = 1
    for i, ticket_type in enumerate(type_ticket):
        prices = ticket_summary.get(ticket_type, {})
        if prices:
            for price, details in prices.items():
                count = details["count"]
                total_price = details["total_price"]
                data.append([str(row_num), ticket_type, price, count, total_price])
                row_num += 1
                if "Взрослый" in ticket_type and "Многодетный" not in ticket_type:
                    total["adult"]["count"] += count
                    total["adult"]["sum"] += total_price
                elif "Детский" in ticket_type and "Многодетный" not in ticket_type:
                    total["child"]["count"] += count
                    total["child"]["sum"] += total_price
                elif "Многодетный взрослый" in ticket_type:
                    total["many_adult"]["count"] += count
                    total["many_adult"]["sum"] += total_price
                elif "Многодетный детский" in ticket_type:
                    total["many_child"]["count"] += count
                    total["many_child"]["sum"] += total_price
                elif "Инвалид" in ticket_type:
                    total["disabled"]["count"] += count
                elif "Сопровождающий" in ticket_type:
                    total["maintainer"]["count"] += count
        else:
            # Пустая категория
            data.append([str(row_num), ticket_type, "-", 0, 0])
            row_num += 1

    # Агрегированные строки
    data += [
        ["", "Всего взрослых билетов", "", total["adult"]["count"], total["adult"]["sum"]],
        ["", "Всего детских билетов", "", total["child"]["count"], total["child"]["sum"]],
        ["", "Всего многодетных взрослых билетов", "", total["many_adult"]["count"], total["many_adult"]["sum"]],
        ["", "Всего многодетных детских билетов", "", total["many_child"]["count"], total["many_child"]["sum"]],
        ["", "Инвалид, 3 ч.", "", total["disabled"]["count"], "0"],
        ["", "Сопровождающий, 3 ч.", "", total["maintainer"]["count"], "0"],
        ["", "Итого билетов", "",
         total["adult"]["count"] + total["child"]["count"] +
         total["many_adult"]["count"] + total["many_child"]["count"] +
         total["disabled"]["count"] + total["maintainer"]["count"],
         total["adult"]["sum"] + total["child"]["sum"] +
         total["many_adult"]["sum"] + total["many_child"]["sum"]],
    ]

    return data

def otchet_administratora(date_1: str, date_2: str, values: Dict) -> None:
    """
    Функция формирует отчет администратора в формате PDF.

    Параметры:
        date_1: str
            Дата начала отчетного периода в формате "yyyy-MM-dd HH:mm:ss".

        date_2: str
            Дата конца отчетного периода в формате "yyyy-MM-dd HH:mm:ss".

        values: dict
            Словарь значений для таблицы отчета, включающий типы билетов, цены, количество и суммы.

    Возвращаемое значение:
        None: Функция не возвращает значений, генерирует отчет в формате PDF по указанным данным.
    """
    logger.info("Запуск функции otchet_administratora")
    path = "./otchet.pdf"
    dt1, dt2 = format_date_range(date_1, date_2)
    data = generate_ticket_report_table(values)
    c = canvas.Canvas(path, pagesize=A4)
    c.setLineWidth(0.3)
    pdfmetrics.registerFont(TTFont("DejaVuSerif", "files/DejaVuSerif.ttf"))
    c.setFont("DejaVuSerif", 12)
    c.drawString(30, 800, "Организация")
    c.drawString(30, 785, 'АО "Мастерславль-Белгород"')
    c.drawString(450, 800, "Приложение №2")
    c.drawString(255, 730, "Отчет администратора")
    c.drawString(255, 715, "по оказанным услугам")
    if dt1 == dt2:
        c.drawString(255, 700, f"за {dt1}")
    else:
        c.drawString(255, 700, f"за {dt1} - {dt2}")
    # Линия под датой
    c.setLineWidth(1)
    c.line(275, 697, 350, 697)
    # Линия под ФИО
    c.line(100, 666, 500, 666)
    c.setFont("DejaVuSerif", 8)
    c.drawString(255, 655, "ФИО Администратора")
    # Настройка ширины таблицы
    custom_widths = [
        10 * mm,  # № п/п
        135 * mm,  # Тип билета
        15 * mm,  # Цена
        25 * mm,  # Кол-во
        25 * mm,  # Сумма
    ]
    page_width = 210 * mm
    left_margin = 20 * mm
    right_margin = 10 * mm
    table_width = sum(custom_widths)
    if table_width > (page_width - left_margin - right_margin):
        # Корректировка ширины второго столбца
        remaining_width = page_width - left_margin - right_margin - (sum(custom_widths) - custom_widths[1])
        custom_widths[1] = remaining_width
    t = Table(data, colWidths=custom_widths, rowHeights=[0.3 * inch] * len(data))
    t.setStyle(
        TableStyle([
            ("FONT", (0, 0), (-1, -1), "DejaVuSerif", 8),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
        ])
    )
    t.wrapOn(c, left_margin, 180 * mm)
    t.drawOn(c, left_margin, 60 * mm)
    # Подписи
    c.drawString(30, 130, "Отчет сдал:")
    c.drawString(30, 110, "Кассир")
    c.line(150, 110, 240, 110)
    c.setFont("DejaVuSerif", 8)
    c.drawString(175, 98, "Подпись")
    c.line(300, 110, 390, 110)
    c.drawString(325, 98, "Расшифровка")
    c.drawString(30, 50, "Отчет принял:")
    c.line(150, 35, 240, 35)
    c.drawString(175, 26, "Подпись")
    c.line(300, 35, 390, 35)
    c.drawString(325, 26, "Расшифровка")
    c.showPage()
    c.save()

def safe_int(value: Any) -> int:
    """
    Преобразует значение в целое число, если это возможно. Если значение None, строка 'None',
    или невозможно преобразовать (например, строка с текстом), возвращает 0.

    Параметры:
        value (Any): Входное значение, которое нужно попытаться преобразовать в целое число.

    Возвращаемое значение:
        int: Целое число, полученное в результате преобразования, либо 0 при ошибке.
    """
    if isinstance(value, (list, dict, set, tuple)):  # Проверка на неподобающие типы
        return 0
    try:
        if value not in [None, 'None']:
            return int(float(value))  # Преобразование строки с плавающей точкой в целое число
        else:
            return 0
    except (ValueError, TypeError):  # Обработка ошибок для некорректных значений
        return 0

def format_date_range(date1_str: str, date2_str: str, input_format: str = "%Y-%m-%d %H:%M:%S", output_format: str = "%d-%m-%Y") -> Tuple[str, str]:
    """
    Преобразует строки с датами из одного формата в другой и возвращает кортеж из двух отформатированных строк.

    Параметры:
        date1_str (str): Первая дата в виде строки в формате input_format.
        date2_str (str): Вторая дата в виде строки в формате input_format.
        input_format (str, по умолчанию "%Y-%m-%d %H:%M:%S"): Формат, в котором переданы входные строки дат.
        output_format (str, по умолчанию "%d-%m-%Y"): Формат, в который нужно преобразовать даты.

    Возвращаемое значение:
        Tuple[str, str]: Кортеж из двух строк, представляющих отформатированные даты.
    """
    date_1 = datetime.strptime(date1_str, input_format)
    date_2 = datetime.strptime(date2_str, input_format)
    dt1 = date_1.strftime(output_format)
    dt2 = date_2.strftime(output_format)
    return dt1, dt2

def otchet_kassira(val: List[int], date1: str, date2: str, kassir: Any) -> None:
    """
    Формирует PDF-отчет кассира за указанный период с разбивкой по типам оплат и возвратов.

    Функция создает PDF-файл `otchet.pdf`, в котором отображается следующая информация:
    - Даты начала и окончания отчетного периода;
    - Фамилия, имя и отчество кассира;
    - Суммы продаж и возвратов по типам оплаты: банковская карта и наличные;
    - Итоговые суммы;
    - Место для подписей кассира и администратора.

    Параметры:
        val (List[int]): Список из 4 чисел:
                         [сумма по карте, сумма наличными, возврат по карте, возврат наличными].
        date1 (str): Начальная дата периода в формате "%Y-%m-%d %H:%M:%S".
        date2 (str): Конечная дата периода в том же формате.
        kassir (object): Объект кассира, содержащий атрибуты `last_name`, `first_name`, `middle_name`.

    Возвращаемое значение:
        None: Функция не возвращает значений. Результатом выполнения является сформированный PDF-файл.
    """
    logger.info("Запуск функции otchet_kassira")
    # Проверка на пустой список или недостаточное количество элементов
    if not val or len(val) < 4:
        logger.error("Некорректные данные для отчета: данные не переданы или их недостаточно.")
        # Завершаем функцию, если данных недостаточно или они пустые
        return
    path = "./otchet.pdf"
    values, user = val, kassir
    dt1, dt2 = format_date_range(date1, date2)
    c = canvas.Canvas(path, pagesize=A4)
    c.setLineWidth(0.3)
    pdfmetrics.registerFont(TTFont("DejaVuSerif", "files/DejaVuSerif.ttf"))
    c.setFont("DejaVuSerif", 12)
    c.drawString(30, 800, "Организация")
    c.drawString(30, 785, 'АО "Мастерславль-Белгород"')
    c.drawString(450, 800, "Приложение №1")
    c.drawString(255, 685, "Отчет кассира")
    c.drawString(255, 670, "по оказанным услугам")
    if dt1 == dt2:
        c.drawString(255, 655, f"за {dt1}")
    else:
        c.drawString(255, 655, f"за {dt1} - {dt2}")
    # рисуем линию
    c.setLineWidth(1)
    c.line(275, 652, 430, 652)
    # ФИО персонала
    c.drawString(255, 623, f"{user.last_name} {user.first_name} {user.middle_name}")
    c.setLineWidth(1)
    c.line(100, 621, 500, 621)
    c.setFont("DejaVuSerif", 8)
    c.drawString(255, 610, "ФИО кассира")
    # Преобразуем все значения в целые числа, если они корректные
    values = [safe_int(v) for v in values]
    # Формируем таблицу данных
    data = [
        ["№ п/п", "Тип продажи", "Сумма, руб."],
        ["1", "Банковская карта", values[0]],
        ["2", "Наличные", values[1]],
        ["3", "Итого", values[0] + values[1]],
        ["", "Тип возврата", ""],
        ["4", "Банковская карта", values[2]],
        ["5", "Наличные", values[3]],
        ["6", "Итого", values[2] + values[3]],
    ]
    t = Table(data, 4 * [1.2 * inch], 8 * [0.3 * inch])
    t.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (4, 8), "DejaVuSerif", 8),
                ("INNERGRID", (0, 0), (-1, -1), 0.2, colors.black),
                ("BOX", (0, 0), (-1, -1), 0.2, colors.black),
            ]
        )
    )
    # wrap the table to this width, height in case it spills
    t.wrapOn(c, 100 * mm, 180 * mm)
    # draw it on our pdf at x,y
    t.drawOn(c, 20 * mm, 140 * mm)
    # отчет сдал
    c.drawString(30, 310, "Отчет сдал:")
    c.drawString(30, 290, "Кассир")
    c.setLineWidth(1)
    c.line(150, 290, 240, 290)
    c.setFont("DejaVuSerif", 8)
    c.drawString(165, 282, "Подпись")
    c.line(300, 290, 390, 290)
    c.setFont("DejaVuSerif", 8)
    c.drawString(315, 282, "Расшифровка")
    # отчет принял
    c.drawString(30, 210, "Отчет принял:")
    c.drawString(30, 190, "Старший администратор")
    c.setLineWidth(1)
    c.line(150, 190, 240, 190)
    c.setFont("DejaVuSerif", 8)
    c.drawString(175, 182, "Подпись")
    c.line(300, 190, 390, 190)
    c.setFont("DejaVuSerif", 8)
    c.drawString(325, 182, "Расшифровка")
    c.showPage()
    c.save()

def process_sales_and_returns(
    sales: List[Tuple[str, int, Union[int, float]]],
    sales_return: List[Tuple[str, int, Union[int, float], int]]
) -> List[Tuple[Union[str, None], Union[int, float, None], Union[int, float, None], Union[int, float, None], Union[int, float, None], Union[int, float, None], Union[int, float]]]:
    """
    Обрабатывает продажи и возвраты, агрегируя информацию по каждому кассовому аппарату.
    Функция вычисляет суммы по картам и наличным, а также учитывает возвраты по каждому типу:
    полный, частичный и возврат за второй раз. Итоговая информация формируется по каждому аппарату
    и общей сумме для всех.

    Параметры:
        sales: list[tuple]
            Список кортежей, представляющих продажи. Каждый кортеж содержит имя кассового аппарата,
            тип оплаты (1 - карта, 2 - наличные) и сумму продажи.

        sales_return: list[tuple]
            Список кортежей, представляющих возвраты. Каждый кортеж содержит имя кассового аппарата,
            тип возврата (2 - обычный возврат, 4 - возврат второй раз, 6 - частичный возврат), тип оплаты
            (1 - карта, 2 - наличные) и сумму возврата.

    Возвращаемое значение:
        list[tuple]:
            Список кортежей с агрегированными данными по каждому кассовому аппарату. Каждый кортеж включает:
            - имя кассового аппарата,
            - сумму продаж по картам,
            - сумму продаж по наличным,
            - общую сумму продаж,
            - сумму возвратов по картам,
            - сумму возвратов по наличным,
            - общую сумму возвратов.

    Примечания:
        - Функция учитывает несколько типов возвратов (полный, частичный, возврат за второй раз).
        - Если кассовый аппарат отсутствует в данных о продажах или возвратах, он игнорируется.
        - В конце добавляется строка с итоговой информацией по всем кассовым аппаратам.
    """
    logger.info("Запуск функции process_sales_and_returns")
    pcs = {
        name: {
            "card": 0, "cash": 0,
            "return": 0, "return_again": 0,
            "return_partial": 0,
            "return_card": 0, "return_cash": 0,
        }
        for name in system.pcs
    }

    type_rm = [1, 2]  # 1 - карта, 2 - наличные
    RETURN_FIELDS = {2: "return", 4: "return_again", 6: "return_partial"}

    for sale in sales:
        pc_name = sale[0]
        if pc_name not in pcs:
            continue
        if sale[1] == type_rm[0]:
            pcs[pc_name]["card"] += sale[2]
        else:
            pcs[pc_name]["cash"] += sale[2]

    for sale in sales_return:
        return_type = sale[3]
        if return_type not in RETURN_FIELDS:
            continue
        pc_name = sale[0]
        if pc_name in pcs:
            return_type = sale[3]
            if return_type in RETURN_FIELDS:
                pcs[pc_name][RETURN_FIELDS[return_type]] += 1
                if sale[1] == 1:
                    pcs[pc_name]["return_card"] += sale[2]
                else:
                    pcs[pc_name]["return_cash"] += sale[2]

    data = []
    for name in system.pcs:
        stats = pcs[name]
        data.append((
            name,
            stats["card"],
            stats["cash"],
            None,
            stats["return_card"],
            stats["return_cash"],
            stats["return_card"] + stats["return_cash"]
        ))

    total_card = sum(pc["card"] for pc in pcs.values())
    total_cash = sum(pc["cash"] for pc in pcs.values())
    total_return = sum(pc["return_card"] + pc["return_cash"] for pc in pcs.values())

    data.append((
        "Итого",
        total_card,
        total_cash,
        total_card + total_cash,
        None,
        None,
        total_return
    ))
    system.sales_data_summary = data
    return data

def process_ticket_stats(tickets: List[Tuple[int, int, str, object, object, int]]) -> List[Tuple[str, Dict[str, int]]]:
    """
    Обрабатывает информацию о билетах, суммируя количество и стоимость проданных билетов по категориям
    и времени пребывания. Возвращает данные, которые могут быть использованы для отображения статистики
    по типам билетов, а также сводку по ценам и количествам для каждой категории.

    Параметры:
        tickets: list[tuple]
            Список кортежей, каждый из которых содержит информацию о типе билета, времени пребывания,
            описании, цене и других данных о продаже.

    Возвращаемое значение:
        list[tuple]:
            Список кортежей, каждый из которых представляет собой пару: название категории билета
            и словарь с данными о количестве и стоимости билетов для каждой цены в данной категории.
            Также сохраняется информация о количестве и распределении билетов по времени пребывания.

    Примечания:
        - Функция поддерживает несколько типов билетов (взрослый, детский, многодетный и т. д.).
        - Каждая категория билетов имеет различные временные интервалы (1 ч., 2 ч., 3 ч.).
        - Функция поддерживает несколько типов возвратов и их учет по категориям.
    """
    logger.info("Запуск функции process_ticket_stats")
    a, c, m_c, m_a, i_, i_m = (
        {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0} for _ in range(6)
    )

    TICKET_TYPE_MAP = {
        (0, 1): "Взрослый, 1 ч.", (0, 2): "Взрослый, 2 ч.", (0, 3): "Взрослый, 3 ч.",
        (1, 1): "Детский, 1 ч.", (1, 2): "Детский, 2 ч.", (1, 3): "Детский, 3 ч.",
        (2, 1): "Многодетный взрослый, 1 ч.", (2, 2): "Многодетный взрослый, 2 ч.", (2, 3): "Многодетный взрослый, 3 ч.",
        (3, 1): "Многодетный детский, 1 ч.", (3, 2): "Многодетный детский, 2 ч.", (3, 3): "Многодетный детский, 3 ч.",
        (4, 3): "Инвалид, 3 ч.",
        (5, 3): "Сопровождающий, 3 ч.",
    }

    # Здесь будут цены и кол-во проданных билетов по ним
    ticket_price_summary: dict[str, dict[int, dict[str, int]]] = {}

    for ticket_type, arrival_time, description, _, _, price in tickets:
        # Определяем ключ категории для сводки
        if description == "-":
            key = (ticket_type, arrival_time)
        elif description == "м":
            key = (ticket_type + 2, arrival_time)
        elif description == "и":
            key = (4, 3)
        elif description == "с":
            key = (5, 3)
        else:
            continue

        if key not in TICKET_TYPE_MAP:
            continue

        category_name = TICKET_TYPE_MAP[key]

        # Инициализация вложенного словаря
        if category_name not in ticket_price_summary:
            ticket_price_summary[category_name] = {}
        if price not in ticket_price_summary[category_name]:
            ticket_price_summary[category_name][price] = {"count": 0, "total_price": 0}

        ticket_price_summary[category_name][price]["count"] += 1
        ticket_price_summary[category_name][price]["total_price"] += price

        # Для таблицы (по категориям)
        if description == "-":
            target = a if ticket_type == 0 else c
        elif description == "м":
            target = m_a if ticket_type == 0 else m_c
        elif description == "и":
            target = i_
        elif description == "с":
            target = i_m
        else:
            continue

        target["sum"] += 1
        if arrival_time == 1:
            target["t_1"] += 1
        elif arrival_time == 2:
            target["t_2"] += 1
        elif arrival_time == 3:
            target["t_3"] += 1

    ticket_data = [
        ("взрослый", a),
        ("детский", c),
        ("многодетный взр.", m_a),
        ("многодетный дет.", m_c),
        ("инвалид", i_),
        ("сопровождающий", i_m),
    ]
    system.ticket_price_summary = ticket_price_summary
    return ticket_data
