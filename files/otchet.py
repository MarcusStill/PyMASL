from reportlab.lib.units import mm, inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape, letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


def generate_saved_tickets(values):
    client_in_sale = values
    adult_talent = 0
    img_file = 'files/qr-code.jpg'
    path = "./ticket.pdf"
    """Устанавливаем параметры макета билета"""
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'files/DejaVuSerif.ttf'))
    c = canvas.Canvas(path, pagesize=(landscape(letter)))
    c.setFillColorRGB(200, 50, 100)
    c.setFont('DejaVuSerif', 12)
    """Сохраняем билеты"""
    for i in range(len(client_in_sale)):
        age = int(client_in_sale[i][8])
        if age < 5:
            type_ticket = 'бесплатный'
        if 5 <= age < 15:
            type_ticket = 'детский'
        elif age >= 15:
            type_ticket = 'взрослый'
        # если взрослый отсутствовал в чеке - не печатаем ему билет
        # if not (int(client_in_sale[i][6]) >= 15 and client_in_sale[i][2]) == 'бесплатный':
        if type_ticket != 'бесплатный':
            date_time = str(client_in_sale[i][11])
            """Сохраняем макет билета"""
            c.setFont('DejaVuSerif', 12)
            c.drawImage(img_file, 170, 370, height=80, width=80, preserveAspectRatio=True, mask='auto')
            # имя
            c.drawString(
                75 * mm, 182 * mm,
                str(client_in_sale[i][0]).replace("'",
                                                  "").replace("[",
                                                              "").replace("]",
                                                                          ""))
            # фамилия
            c.drawString(
                75 * mm, 177 * mm,
                str(client_in_sale[i][1]).replace("'",
                                                  "").replace("[",
                                                              "").replace("]",
                                                                          ""))
            # возраст
            c.drawString(
                160 * mm, 182 * mm,
                str(age).replace("'",
                                                  "").replace("[",
                                                              "").replace("]",
                                                                          ""))
            # продолжительность
            c.drawString(
                80 * mm, 167 * mm,
                (f'{client_in_sale[i][9]} ч. пребывания').replace("'",
                                                  "").replace("[",
                                                              "").replace("]",
                                                                          ""))
            # дата и время билета
            c.drawString(
                160 * mm, 167 * mm,
                str(date_time[0:10]).replace("'",
                                             "").replace("[",
                                                         "").replace("]",
                                                                     ""))
            c.drawString(160 * mm, 177 * mm, "гость")
            c.drawString(130 * mm, 157 * mm, "БЕЛГОРОД")
            c.drawString(120 * mm, 152 * mm, "МАСТЕРСЛАВЛЬ")
            # цена
            c.drawString(
                190 * mm, 155 * mm,
                (f'{client_in_sale[i][4]} руб.').replace("'",
                                                  "").replace("[",
                                                              "").replace("]",
                                                                          ""))
            # тип билета
            c.drawString(101 * mm, 138 * mm,
                         str(type_ticket).replace("'",
                                           "").replace("[",
                                                       "").replace("]", ""))
            # доп.отметки
            c.drawString(170 * mm, 138 * mm, str(client_in_sale[i][5]))
            # c.drawString(90 * mm, 13 * mm, str(client_in_sale[i][5]))
            # таланты
            # печатаем их только для детских билетов
            c.setFont('DejaVuSerif', 24)
            if type_ticket == 'взрослый':
                c.drawString(
                    225 * mm, 168 * mm,
                    str(adult_talent).replace("'",
                                                       "").replace("[",
                                                                   "").replace("]",
                                                                               ""))
            else:
                c.drawString(
                    225 * mm, 168 * mm,
                    str(client_in_sale[i][10]).replace("'",
                                                       "").replace("[",
                                                                   "").replace("]",
                                                                               ""))
            c.showPage()
    c.save()


def otchet_administratora(date_1, date_2, values):
    """Формирование отчета администратора"""
    print("Inside the function def otchet_kassira")
    path = "./otchet.pdf"
    dt1, dt2, data = date_1, date_2, values
    print('values', data)
    c = canvas.Canvas(path, pagesize=A4)
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


def otchet_kassira(val, date1, date2, kassir):
    """Формирование отчета кассира"""
    print("Inside the function def otchet_kassira")
    path = "./otchet.pdf"
    values, dt1, dt2, user = val, date1, date2, kassir
    print('values', values)
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
