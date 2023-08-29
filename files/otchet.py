from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, letter
from reportlab.lib.units import mm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from files.logger import *


def generate_saved_tickets(values):
    logger.info("Запуск функции generate_saved_tickets")
    client_in_sale = values
    type_ticket = None
    img_file = 'files/qr-code.jpg'
    path = "./ticket.pdf"
    logger.info("Устанавливаем параметры макета билета")
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'files/DejaVuSerif.ttf'))
    c = canvas.Canvas(path, pagesize=(landscape(letter)))
    logger.debug("Сохраняем билеты")
    for i in range(len(client_in_sale)):
        age = int(client_in_sale[i][6])
        not_go = client_in_sale[i][4]
        if age < 5:
            type_ticket = 'бесплатный'
        elif 5 <= age < 15:
            type_ticket = 'детский'
        elif age >= 15:
            type_ticket = 'взрослый'
        if type_ticket != 'бесплатный' and not_go != 'н':
            date_time = str(client_in_sale[i][9])
            """Сохраняем макет билета"""
            c.setFont('DejaVuSerif', 12)
            # имя
            c.drawString(
                75 * mm,
                182 * mm,
                str(client_in_sale[i][1]).replace("'", "").replace("[", "").replace("]", "")
            )
            # фамилия
            c.drawString(
                75 * mm,
                177 * mm,
                str(client_in_sale[i][0]).replace("'", "").replace("[", "").replace("]", "")
            )
            # возраст
            c.drawString(
                160 * mm,
                182 * mm,
                str(age).replace("'", "").replace("[", "").replace("]", "")
            )
            # продолжительность
            c.drawString(
                80 * mm,
                167 * mm,
                f'{client_in_sale[i][7]} ч. пребывания'.replace("'", "").replace("[", "").replace("]", "")
            )
            # дата и время билета
            c.drawString(
                160 * mm,
                167 * mm,
                str(date_time[0:10]).replace("'", "").replace("[", "").replace("]", "")
            )
            c.drawString(160 * mm, 177 * mm, "гость")
            c.drawString(130 * mm, 157 * mm, "БЕЛГОРОД")
            c.drawString(120 * mm, 152 * mm, "МАСТЕРСЛАВЛЬ")
            # цена
            c.drawString(
                190 * mm,
                155 * mm,
                f'{client_in_sale[i][3]} руб.'.replace("'", "").replace("[", "").replace("]", "")
            )
            # тип билета
            c.drawString(
                101 * mm,
                138 * mm,
                str(type_ticket).replace("'", "").replace("[", "").replace("]", "")
            )
            # доп.отметки
            c.drawString(170 * mm, 138 * mm, str(client_in_sale[i][4]))
            # таланты
            # печатаем их только для детских билетов
            c.setFont('DejaVuSerif', 24)
            if type_ticket == 'взрослый':
                c.drawString(
                    225 * mm,
                    168 * mm,
                    "0".replace("'", "").replace("[", "").replace("]", "")
                )
            else:
                c.drawString(
                    225 * mm,
                    168 * mm,
                    str(client_in_sale[i][8]).replace("'", "").replace("[", "").replace("]", "")
                )
            c.drawImage(img_file, 170, 370, height=80, width=80, preserveAspectRatio=True, mask='auto')
            c.showPage()
    c.save()


def otchet_administratora(date_1, date_2, values):
    """Формирование отчета администратора"""
    logger.info("Запуск функции otchet_administratora")
    path = "./otchet.pdf"
    dt1, dt2, data = date_1, date_2, values
    logger.debug("values %s" % data)
    c = canvas.Canvas(path, pagesize=A4)
    c.setLineWidth(.3)
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'files/DejaVuSerif.ttf'))
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
    t = Table(data, 9 * [1.2 * inch], 19 * [0.3 * inch])
    t.setStyle(TableStyle([("FONT", (0, 0), (9, 19), "DejaVuSerif", 8),
                           ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                           ("BOX", (0, 0), (-1, -1), 0.25, colors.black)]))
    # wrap the table to this width, height in case it spills
    t.wrapOn(c, 100 * mm, 180 * mm)
    # draw it on our pdf at x,y
    t.drawOn(c, 20 * mm, 60 * mm)
    # отчет сдал
    c.drawString(30, 150, "Отчет сдал:")
    c.drawString(30, 130, "Кассир")
    c.setLineWidth(1)
    c.line(150, 130, 240, 130)
    c.setFont("DejaVuSerif", 8)
    c.drawString(165, 120, "Подпись")
    c.line(300, 130, 390, 130)
    c.setFont("DejaVuSerif", 8)
    c.drawString(315, 120, "Расшифровка")
    # отчет принял
    c.drawString(30, 80, "Отчет принял:")
    c.setLineWidth(1)
    c.line(150, 65, 240, 65)
    c.setFont("DejaVuSerif", 8)
    c.drawString(175, 58, "Подпись")
    c.line(300, 65, 390, 65)
    c.setFont("DejaVuSerif", 8)
    c.drawString(325, 58, "Расшифровка")
    c.showPage()
    c.save()


def otchet_kassira(val, date1, date2, kassir):
    """Формирование отчета кассира"""
    logger.info("Запуск функции otchet_kassira")
    path = "./otchet.pdf"
    values, dt1, dt2, user = val, date1, date2, kassir
    c = canvas.Canvas(path, pagesize=A4)
    c.setLineWidth(.3)
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'files/DejaVuSerif.ttf'))
    c.setFont('DejaVuSerif', 12)
    c.drawString(30, 800, 'Организация')
    c.drawString(30, 785, 'АО "Мастерславль-Белгород"')
    c.drawString(450, 800, "Приложение №1")
    c.drawString(255, 685, 'Отчет кассира')
    c.drawString(255, 670, 'по оказанным услугам')
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
    c.setFont('DejaVuSerif', 8)
    c.drawString(255, 610, 'ФИО кассира')
    data = [['№ п/п', 'Тип\nпродажи', 'Сумма, руб.'],
            ['1', 'Банковская карта', values[0]],
            ['2', 'Наличные', values[1]],
            ['3', 'Итого', int(values[0]) + int(values[1])]]
    t = Table(data, 4 * [1.2 * inch], 4 * [0.3 * inch])
    t.setStyle(TableStyle([('FONT', (0, 0), (4, 4), 'DejaVuSerif', 8),
                           ('INNERGRID', (0, 0), (-1, -1), 0.2, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.2, colors.black)]))
    # wrap the table to this width, height in case it spills
    t.wrapOn(c, 100 * mm, 180 * mm)
    # draw it on our pdf at x,y
    t.drawOn(c, 20 * mm, 170 * mm)
    # отчет сдал
    c.drawString(30, 310, 'Отчет сдал:')
    c.drawString(30, 290, 'Кассир')
    c.setLineWidth(1)
    c.line(150, 290, 240, 290)
    c.setFont('DejaVuSerif', 8)
    c.drawString(165, 282, 'Подпись')
    c.line(300, 290, 390, 290)
    c.setFont('DejaVuSerif', 8)
    c.drawString(315, 282, 'Расшифровка')
    # отчет принял
    c.drawString(30, 210, 'Отчет принял:')
    c.drawString(30, 190, 'Старший администратор')
    c.setLineWidth(1)
    c.line(150, 190, 240, 190)
    c.setFont('DejaVuSerif', 8)
    c.drawString(175, 182, 'Подпись')
    c.line(300, 190, 390, 190)
    c.setFont('DejaVuSerif', 8)
    c.drawString(325, 182, 'Расшифровка')
    c.showPage()
    c.save()
