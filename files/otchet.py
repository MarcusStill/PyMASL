from reportlab.lib.units import mm, inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


def generate_saved_tickets(values):
    client_in_sale = values
    """Устанавливаем параметры макета билета"""
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'files/DejaVuSerif.ttf'))
    c = canvas.Canvas("ticket.pdf", pagesize=(21 * cm, 8 * cm))
    c.setFont('DejaVuSerif', 12)
    """Сохраняем билеты"""
    for i in range(len(client_in_sale)):
        if int(client_in_sale[i][4]) >= 14:
            type = 'взрослый'
        else:
            type = 'детский'
        date_time = str(client_in_sale[i][11])
        """Сохраняем макет билета"""
        c.setFont('DejaVuSerif', 12)
        # имя
        c.drawString(
            20 * mm, 53 * mm,
            str(client_in_sale[i][0]).replace("'",
                                              "").replace("[",
                                                          "").replace("]",
                                                                      ""))
        # фамилия
        c.drawString(
            20 * mm, 47 * mm,
            str(client_in_sale[i][1]).replace("'",
                                              "").replace("[",
                                                          "").replace("]",
                                                                      ""))
        # возраст
        c.drawString(
            95 * mm, 53 * mm,
            str(client_in_sale[i][8]).replace("'",
                                              "").replace("[",
                                                          "").replace("]",
                                                                      ""))
        # продолжительность
        c.drawString(
            20 * mm, 41 * mm,
            str(client_in_sale[i][9]).replace("'",
                                              "").replace("[",
                                                          "").replace("]",
                                                                      ""))
        # дата и время билета
        c.drawString(
            95 * mm, 41 * mm,
            str(date_time[0:10]).replace("'",
                                         "").replace("[",
                                                     "").replace("]",
                                                                 ""))
        c.drawString(70 * mm, 30 * mm, "БЕЛГОРОД")
        c.drawString(70 * mm, 23 * mm, "МАСТЕРСЛАВЛЬ")
        # цена
        c.drawString(
            121 * mm, 30 * mm,
            str(client_in_sale[i][4]).replace("'",
                                              "").replace("[",
                                                          "").replace("]",
                                                                      ""))
        # тип билета
        c.drawString(31 * mm, 13 * mm,
                     str(type).replace("'",
                                       "").replace("[",
                                                   "").replace("]", ""))
        # доп.отметки
        c.drawString(90 * mm, 13 * mm, str(client_in_sale[i][5]))
        # c.drawString(90 * mm, 13 * mm, str(client_in_sale[i][5]))
        # таланты
        c.drawString(
            153 * mm, 40 * mm,
            str(client_in_sale[i][10]).replace("'",
                                               "").replace("[",
                                                           "").replace("]",
                                                                       ""))
        c.showPage()
    c.save()


def otchet_administratora(date_1, date_2, values):
    """Формирование отчета администратора"""
    dt1, dt2, data = date_1, date_2, values
    c = canvas.Canvas("otchet.pdf", pagesize=A4)
    c.setLineWidth(.3)
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'files/DejaVuSerif.ttf'))
    c.setFont('DejaVuSerif', 12)
    c.drawString(30, 800, 'Организация')
    c.drawString(30, 785, 'АО "Мастерславль-Белгород"')
    c.drawString(450, 800, "Приложение №2")
    c.drawString(255, 685, 'Отчет администратора')
    c.drawString(255, 670, 'по оказанным услугам')
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
    c.setFont('DejaVuSerif', 8)
    c.drawString(255, 610, 'ФИО Администратора')
    t = Table(data, 9 * [1.2 * inch], 9 * [0.3 * inch])
    t.setStyle(TableStyle([('FONT', (0, 0), (9, 9), 'DejaVuSerif', 8),
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
    # wrap the table to this width, height in case it spills
    t.wrapOn(c, 100 * mm, 180 * mm)
    # draw it on our pdf at x,y
    t.drawOn(c, 20 * mm, 140 * mm)
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
    # c.drawString(30, 190, 'Старший администратор')
    c.setLineWidth(1)
    c.line(150, 190, 240, 190)
    c.setFont('DejaVuSerif', 8)
    c.drawString(175, 182, 'Подпись')
    c.line(300, 190, 390, 190)
    c.setFont('DejaVuSerif', 8)
    c.drawString(325, 182, 'Расшифровка')
    c.showPage()
    c.save()


def otchet_kassira(values, date1, date2, kassir):
    """Формирование отчета кассира"""
    values, dt1, dt2, user = values, date1, date2, kassir

    c = canvas.Canvas("otchet.pdf", pagesize=A4)
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
    c.drawString(255, 623, f"{user[0]} {user[1]}")
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
