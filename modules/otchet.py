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


def generate_saved_tickets(values):
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
        age = int(client_in_sale[i][6])
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


def otchet_administratora(date_1, date_2, values):
    """Формирование отчета администратора"""
    logger.info("Запуск функции otchet_administratora")
    path = "./otchet.pdf"
    dt1, dt2, data = date_1, date_2, values
    c = canvas.Canvas(path, pagesize=A4)
    c.setLineWidth(0.3)
    pdfmetrics.registerFont(TTFont("DejaVuSerif", "files/DejaVuSerif.ttf"))
    c.setFont("DejaVuSerif", 12)
    c.drawString(30, 800, "Организация")
    c.drawString(30, 785, 'АО "Мастерславль-Белгород"')
    c.drawString(450, 800, "Приложение №2")
    c.drawString(255, 685, "Отчет администратора")
    c.drawString(255, 670, "по оказанным услугам")
    if dt1 == dt2:
        c.drawString(255, 655, f"за {dt1}")
    else:
        c.drawString(255, 655, f"за {dt1} - {dt2}")
    # рисуем линию
    c.setLineWidth(1)
    c.line(275, 652, 430, 652)
    # ФИО персонала
    # c.drawString(255, 623, f"{System.user[0]} {System.user[1]}")
    c.setLineWidth(1)
    c.line(100, 621, 500, 621)
    c.setFont("DejaVuSerif", 8)
    c.drawString(255, 610, "ФИО Администратора")
    # Ширины столбцов
    custom_widths = [
        10 * mm,  # 1-й столбец (№ п/п)
        135 * mm,  # 2-й столбец (Тип билета), остаток ширины
        15 * mm,  # 3-й столбец (Цена, руб.)
        25 * mm,  # 4-й столбец (Количество, шт.)
        25 * mm,  # 5-й столбец (Стоимость, руб.)
    ]
    # Рассчитаем x-координату для размещения таблицы
    page_width = 210 * mm  # Ширина листа A4
    left_margin = 20 * mm  # Отступ слева
    right_margin = 10 * mm  # Отступ справа
    table_width = sum(custom_widths)  # Общая ширина таблицы
    # Позиция таблицы с учётом отступа слева и справа
    left_position = left_margin
    right_position = page_width - right_margin  # Правый отступ
    # Если общая ширина таблицы превышает доступную ширину с учетом отступов, подгоняем её
    if table_width > (right_position - left_position):
        # Подгоняем 2-й столбец для оставшейся ширины
        remaining_width = right_position - left_position - (sum(custom_widths) - custom_widths[1])
        custom_widths[1] = remaining_width
    # Теперь создаём таблицу с заданными ширинами
    t = Table(data, colWidths=custom_widths, rowHeights=len(data) * [0.3 * inch])
    t.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (9, 19), "DejaVuSerif", 8),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )
    # wrap the table to this width, height in case it spills
    t.wrapOn(c, left_position, 180 * mm)
    # draw it on our pdf at x,y
    t.drawOn(c, left_position, 60 * mm)
    # отчет сдал
    c.drawString(30, 130, "Отчет сдал:")
    c.drawString(30, 110, "Кассир")
    c.setLineWidth(1)
    c.line(150, 110, 240, 110)
    c.setFont("DejaVuSerif", 8)
    c.drawString(175, 98, "Подпись")
    c.line(300, 110, 390, 110)
    c.setFont("DejaVuSerif", 8)
    c.drawString(325, 98, "Расшифровка")
    # отчет принял
    c.drawString(30, 50, "Отчет принял:")
    c.setLineWidth(1)
    c.line(150, 35, 240, 35)
    c.setFont("DejaVuSerif", 8)
    c.drawString(175, 26, "Подпись")
    c.line(300, 35, 390, 35)
    c.setFont("DejaVuSerif", 8)
    c.drawString(325, 26, "Расшифровка")
    c.showPage()
    c.save()


def otchet_kassira(val, date1, date2, kassir):
    """Формирование отчета кассира"""
    logger.info("Запуск функции otchet_kassira")
    path = "./otchet.pdf"
    values, dt1, dt2, user = val, date1, date2, kassir
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
    data = [
        ["№ п/п", "Тип продажи", "Сумма, руб."],
        ["1", "Банковская карта", values[0]],
        ["2", "Наличные", values[1]],
        ["3", "Итого", int(values[0]) + int(values[1])],
        ["", "Тип возврата", ""],
        ["4", "Банковская карта", values[2]],
        ["5", "Наличные", values[3]],
        ["6", "Итого", int(values[2]) + int(values[3])],
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

def calculate_ticket_statistics(table: list[str], system) -> list[list]:
    """
    Выполняет расчеты по типам билетов и возвращает таблицу данных для отчета.
    """
    logger.info("Запуск функции calculate_ticket_statistics")
    def calculate_total(prices, counts):
        return sum(price * int(count) for price, count in zip(prices, counts))

    type_ticket = [
        "Взрослый, 1 ч.", "Взрослый, 2 ч.", "Взрослый, 3 ч.",
        "Детский, 1 ч.", "Детский, 2 ч.", "Детский, 3 ч.",
        "Многодетный взрослый, 1 ч.", "Многодетный взрослый, 2 ч.", "Многодетный взрослый, 3 ч.",
        "Многодетный детский, 1 ч.", "Многодетный детский, 2 ч.", "Многодетный детский, 3 ч.",
        "Инвалид, 3 ч.", "Сопровождающий, 3 ч.",
    ]

    adult_prices = [
        system.price["ticket_adult_1"],
        system.price["ticket_adult_2"],
        system.price["ticket_adult_3"],
    ]
    child_prices = [
        system.price["ticket_child_1"],
        system.price["ticket_child_2"],
        system.price["ticket_child_3"],
    ]
    many_adult_prices = [round(price / 2) for price in adult_prices]
    many_child_prices = [round(price / 2) for price in child_prices]

    adult_counts = table[:3]
    child_counts = table[3:6]
    many_adult_counts = table[6:9]
    many_child_counts = table[9:12]
    disabled_counts = table[12]
    maintainer_counts = table[13]

    sum_adult = calculate_total(adult_prices, adult_counts)
    sum_child = calculate_total(child_prices, child_counts)
    sum_many_adult = calculate_total(many_adult_prices, many_adult_counts)
    sum_many_child = calculate_total(many_child_prices, many_child_counts)

    kol_adult = sum(int(count) for count in adult_counts)
    kol_child = sum(int(count) for count in child_counts)
    kol_many_adult = sum(int(count) for count in many_adult_counts)
    kol_many_child = sum(int(count) for count in many_child_counts)
    kol_disabled = int(disabled_counts) if disabled_counts else 0
    kol_maintainer = int(maintainer_counts) if maintainer_counts else 0

    data = [
        ["№\n п/п", "Тип\nбилета", "Цена,\n руб.", "Количество,\n шт.", "Стоимость,\n руб."],
        *[
            [str(i + 1), type_ticket[i], adult_prices[i], adult_counts[i], adult_prices[i] * int(adult_counts[i])]
            for i in range(3)
        ],
        ["4", "Всего взрослых билетов", "", kol_adult, sum_adult],
        *[
            [str(i + 5), type_ticket[i + 3], child_prices[i], child_counts[i], child_prices[i] * int(child_counts[i])]
            for i in range(3)
        ],
        ["8", "Всего детских билетов", "", kol_child, sum_child],
        *[
            [str(i + 9), type_ticket[i + 6], many_adult_prices[i], many_adult_counts[i], many_adult_prices[i] * int(many_adult_counts[i])]
            for i in range(3)
        ],
        ["12", "Всего многодетных взрослых билетов", "", kol_many_adult, sum_many_adult],
        *[
            [str(i + 13), type_ticket[i + 9], many_child_prices[i], many_child_counts[i], many_child_prices[i] * int(many_child_counts[i])]
            for i in range(3)
        ],
        ["16", "Всего многодетных детских билетов", "", kol_many_child, sum_many_child],
        ["17", type_ticket[12], "-", disabled_counts, "-"],
        ["18", type_ticket[13], "-", maintainer_counts, "-"],
        ["", "Итого билетов", "",
         kol_adult + kol_child + kol_many_adult + kol_many_child + kol_disabled + kol_maintainer,
         sum_adult + sum_child + sum_many_adult + sum_many_child + kol_disabled + kol_maintainer],
    ]
    return data
