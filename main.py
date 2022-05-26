import calendar
import os
import socket
import subprocess
import sys
from configparser import ConfigParser
from datetime import date, timedelta

import datetime as dt

from PySide6 import QtCore, QtSql, QtWidgets
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QCheckBox, QDialog, QHBoxLayout
from PySide6.QtWidgets import QMainWindow, QTableWidgetItem, QWidget
from sqlalchemy import and_, create_engine, update
from sqlalchemy.orm import sessionmaker

from db.models import Client
from db.models import Holiday
from db.models import Sale
from db.models import Ticket
from db.models import Workday
from db.models.user import User
from files.logger import *
from files import kkt
from files import otchet
from files import windows
from forms.authorization import Ui_Dialog
from forms.client import Ui_Dialog_Client
from forms.main_form import Ui_MainWindow
from forms.pay import Ui_Dialog_Pay
from forms.sale import Ui_Dialog_Sale

# Чтение параметров из файла конфигурации
config = ConfigParser()
config.read('config.ini')
host = config.get("DATABASE", "host")
port = config.get("DATABASE", "port")
database = config.get("DATABASE", "database")
user = config.get("DATABASE", "user")
pswrd = config.get("DATABASE", "password")
software_version = config.get("OTHER", "version")
log_file = config.get("OTHER", "log_file")
kol_pc = config.get("PC", "kol")
pc_1 = config.get("PC", "pc_1")
pc_2 = config.get("PC", "pc_2")

engine = create_engine("postgresql://postgres:"
                       + pswrd + "@" + host + ":"
                       + port + "/" + database, echo=True)
Session = sessionmaker(engine)
logger.add(log_file, rotation="1 MB")


class MainWindow(QMainWindow):
    """Главная форма"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        """Открыть окно добавления нового клиента"""
        self.ui.pushButton_2.clicked.connect(self.open_client)
        """Отображение всех клиентов"""
        self.ui.pushButton_8.clicked.connect(kkt.get_info)
        self.ui.pushButton_11.clicked.connect(kkt.last_document)
        self.ui.pushButton_9.clicked.connect(kkt.get_time)
        self.ui.pushButton_5.clicked.connect(kkt.report_x)
        self.ui.pushButton_6.clicked.connect(lambda: kkt.smena_close(System.user))
        self.ui.pushButton_7.clicked.connect(kkt.get_status_obmena)
        self.ui.pushButton_15.clicked.connect(kkt.continue_print)
        self.ui.pushButton_10.clicked.connect(kkt.smena_info)
        self.ui.pushButton_16.clicked.connect(kkt.terminal_check_itog_window)
        self.ui.pushButton_21.clicked.connect(kkt.terminal_svod_check)
        self.ui.pushButton_22.clicked.connect(kkt.terminal_control_lenta)
        self.ui.pushButton_23.clicked.connect(self.open_sale)
        self.ui.pushButton_13.clicked.connect(self.button_all_sales)
        self.ui.pushButton_18.clicked.connect(self.otchet_kassira)
        self.ui.pushButton_19.clicked.connect(self.otchet_administratora)
        self.ui.tableWidget_2.doubleClicked.connect(self.search_selected_sale)
        self.ui.pushButton_17.clicked.connect(self.get_statistic)
        self.ui.pushButton_3.clicked.connect(self.click_in_client_view)
        self.ui.tableView.clicked.connect(self.click_in_client_view)
        self.ui.dateEdit.setDate(date.today())
        self.ui.dateEdit_2.setDate(date.today())
        # tableView с клиентами
        self.model = QtSql.QSqlTableModel()
        self.ui.tableView.setModel(self.model)
        grid = QtWidgets.QGridLayout(self)
        grid.addWidget(self.ui.lineEdit_2, 0, 0)
        grid.addWidget(self.ui.comboBox_2, 0, 1)
        grid.addWidget(self.ui.tableView, 1, 0, 1, 2)
        self.model.setTable("client")
        self.model.select()
        type_col = QtCore.Qt.Horizontal
        # скрываем столбец с номерами строк
        self.ui.tableView.verticalHeader().setVisible(False)
        # адаптированный для пользователя фильтр к модели
        self.ui.comboBox_3.currentTextChanged.connect(self.main_check_filter_update)
        self.ui.comboBox_2.clear()
        # скрываем comboBox_2
        self.ui.comboBox_2.hide()
        for i in range(self.model.columnCount()):
            self.ui.comboBox_2.addItem(self.model.headerData(i, type_col))
        self.ui.lineEdit_2.textChanged.connect(self.filter_table_client)
        headers_view = ["N", "Фамилия", "Имя", "Отчество", "Дата рожд.",
                        "Пол", "Телефон", "Email", "Категория"]
        for i in range(len(headers_view)):
            self.model.setHeaderData(i, Qt.Horizontal, headers_view[i])

    def main_check_filter_update(self):
        """Передаем значение пользовательского
        фильтра в модель QSqlTableModel"""
        logger.info("Inside the function def main_check_filter_update ")
        # вычисляем индекс значения
        index = self.ui.comboBox_3.currentIndex()
        # передаем значение в comboBox_2
        if index == 0:
            self.ui.comboBox_2.setCurrentIndex(1)
            self.ui.lineEdit_2.clear()
        elif index == 1:
            self.ui.comboBox_2.setCurrentIndex(2)
            self.ui.lineEdit_2.clear()
        elif index == 2:
            self.ui.comboBox_2.setCurrentIndex(6)
            self.ui.lineEdit_2.clear()
        elif index == 3:
            self.ui.comboBox_2.setCurrentIndex(8)
            self.ui.lineEdit_2.setText('и')
        elif index == 4:
            self.ui.comboBox_2.setCurrentIndex(8)
            self.ui.lineEdit_2.setText('м')

    def filter_table_client(self, text):
        filter = (" {} LIKE '%{}%'".format(self.ui.comboBox_2.currentText(),
                                           text) if text else text)
        self.model.setFilter(filter)

    def click_in_client_view(self):
        """Поиск выделенной строки в таблице клиентов
                 и открытие формы с найденными данными
        """
        # ищем индекс и значение ячейки
        index = (self.ui.tableView.selectionModel().currentIndex())
        # ! исправить передавать в index всегда первый столбец
        value = index.sibling(index.row(), index.column()).data()
        if type(value) == int:
            session = Session()
            search_client = session.query(Client).filter_by(id=(value)).first()
            session.close()
            # сохраняем id клиента
            System.client_id = search_client.id
            """Передаем в форму данные клиента"""
            client = ClientForm()
            client.ui.lineEdit.setText(search_client.last_name)
            client.ui.lineEdit_2.setText(search_client.first_name)
            client.ui.lineEdit_3.setText(search_client.middle_name)
            client.ui.dateEdit.setDate(search_client.birth_date)
            """Поиск значения для установки в ComboBox gender"""
            index_gender = client.ui.comboBox.findText(
                search_client.gender, Qt.MatchFixedString)
            if index_gender >= 0:
                client.ui.comboBox.setCurrentIndex(index_gender)
            client.ui.lineEdit_4.setText(search_client.phone)
            client.ui.lineEdit_5.setText(search_client.email)
            """Поиск значения для установки в ComboBox privilege"""
            index_privilege = client.ui.comboBox.findText(
                search_client.privilege, Qt.MatchFixedString)
            if index_privilege >= 0:
                client.ui.comboBox_2.setCurrentIndex(index_privilege)
            """bug Запись сохраняется с новым id"""
            client.show()
            # сохраняем параметры данных об уже существующем клиенте
            System.client_update = 1
            logger.info('System.client_update %s' % (System.client_update))
            logger.info('System.client_id %s' % (System.client_id))
            client.exec_()

    def search_selected_sale(self):
        """Поиск выделенной строки в таблице продаж
        и открытие формы с найденными данными
        """
        logger.info("Inside the function def search_selected_sale")
        kol_adult = 0
        kol_child = 0
        sum = 0
        for idx in self.ui.tableWidget_2.selectionModel().selectedIndexes():
            """Номер строки найден"""
            row_number = idx.row()
            """Получаем содержимое ячейки"""
            sale_number = self.ui.tableWidget_2.item(row_number, 0).text()
            session = Session()
            client_in_sale = session.query(Client.first_name,
                                           Client.last_name,
                                           Client.middle_name,
                                           Ticket.ticket_type,
                                           Ticket.price,
                                           Ticket.description,
                                           Client.id,
                                           Ticket.print,
                                           Ticket.client_age,
                                           Ticket.arrival_time,
                                           Ticket.talent,
                                           Ticket.datetime).join(
                Ticket).filter(and_(Client.id == Ticket.id_client,
                                    Ticket.id_sale == sale_number)).all()
            print('client_in_sale', client_in_sale)
            # запрашиваем статус продажи
            sale_status = (session.query(Sale.status).filter(
                Sale.id == sale_number).one())._asdict()
            """Передаем в форму данные клиента"""
            sale = SaleForm()
            sale.ui.tableWidget_2.setRowCount(0)
            sale.ui.dateEdit.setDate(client_in_sale[0][11])
            sale.ui.dateEdit.setEnabled(False)
            sale.ui.comboBox.setCurrentText(str(client_in_sale[0][9]))
            sale.ui.comboBox.setEnabled(False)
            # sale.ui.checkBox.setEnabled(False)
            # если продажа оплачена
            if sale_status.get('status') == 1:
                sale.ui.pushButton_3.setEnabled(False)
                sale.ui.pushButton_5.setEnabled(False)
            # если продажа не оплачена
            elif sale_status.get('status') == 0:
                sale.ui.pushButton_5.setEnabled(True)
            for search_client in client_in_sale:
                logger.debug(search_client)
                row = sale.ui.tableWidget_2.rowCount()
                if search_client[8] >= 14:
                    type_ticket = 'взрослый'
                    kol_adult += 1
                else:
                    type_ticket = 'детский'
                    kol_child += 1
                sale.ui.tableWidget_2.insertRow(row)
                # имя
                sale.ui.tableWidget_2.setItem(
                    row, 0, QTableWidgetItem(f"{search_client[1]}"))
                # фамилия
                sale.ui.tableWidget_2.setItem(
                    row, 1, QTableWidgetItem(f"{search_client[0]}"))
                # отчество
                sale.ui.tableWidget_2.setItem(
                    row, 2, QTableWidgetItem(f"{search_client[2]}"))
                # тип билета
                sale.ui.tableWidget_2.setItem(
                    row, 3, QTableWidgetItem(type_ticket))
                # цена
                sale.ui.tableWidget_2.setItem(
                    row, 4, QTableWidgetItem(f"{search_client[4]}"))
                # примечание
                sale.ui.tableWidget_2.setItem(
                    row, 5, QTableWidgetItem(f"{search_client[5]}"))
                # id клиента
                sale.ui.tableWidget_2.setItem(
                    row, 6, QTableWidgetItem(f"{search_client[6]}"))
                # sale.ui.tableWidget_2.setColumnHidden(6, True)
                # печать - время пребывания
                sale.ui.tableWidget_2.setItem(
                    row, 7, QTableWidgetItem(f"{search_client[7]}"))
                # возраст
                sale.ui.tableWidget_2.setItem(
                    row, 8, QTableWidgetItem(f"{search_client[8]}"))
                # sale.ui.tableWidget_2.setColumnHidden(8, True)
                sum += int(search_client[4])
            session.close()
            sale.ui.label_5.setText(str(kol_adult))
            sale.ui.label_7.setText(str(kol_child))
            sale.ui.label_8.setText(str(sum))
            sale.show()
            # передаем сведения о сохраненной продаже
            System.sale_status = 1
            logger.warning("System.sale_status %s" % (System.sale_status))
            System.sale_id = sale_number
            System.sale_tickets = client_in_sale
            logger.warning('selected sale')
            logger.debug(System.sale_tickets)
            # возвращаем model для tableView
            self.model = QtSql.QSqlTableModel()
            self.ui.tableView.setModel(self.model)
            self.model.setTable("client")
            self.model.select()
            sale.exec_()

    def button_all_sales(self):
        """Показ всех продаж в tableWidget"""
        logger.info("Inside the function def button_all_sales")
        filter_day = 0
        self.ui.tableWidget_2.setRowCount(0)
        """Фильтр продаж за 1, 3 и 7 дней"""
        if self.ui.radioButton.isChecked():
            filter_day = dt.datetime(dt.datetime.today().year,
                                     dt.datetime.today().month,
                                     dt.datetime.today().day)
        elif self.ui.radioButton_2.isChecked():
            filter_day = dt.datetime.today() - timedelta(days=3)
        elif self.ui.radioButton_3.isChecked():
            filter_day = dt.datetime.today() - timedelta(days=7)
        try:
            session = Session()
            sales = session.query(Sale).filter(Sale.datetime >=
                                               filter_day).order_by(Sale.id)
            if sales:
                for sale in sales:
                    row = self.ui.tableWidget_2.rowCount()
                    self.ui.tableWidget_2.insertRow(row)
                    self.ui.tableWidget_2.setItem(
                        row, 0, QTableWidgetItem(f"{sale.id}"))
                    self.ui.tableWidget_2.setItem(
                        row, 1, QTableWidgetItem(f"{sale.id_client}"))
                    self.ui.tableWidget_2.setItem(
                        row, 2, QTableWidgetItem(f"{sale.price}"))
                    self.ui.tableWidget_2.setItem(
                        row, 3, QTableWidgetItem(f"{sale.datetime}"))
                    if sale.status == 0:
                        status_type = 'создана'
                    elif sale.status == 1:
                        status_type = 'оплачена'
                    else:
                        status_type = 'возврат'
                    self.ui.tableWidget_2.setItem(
                        row, 4, QTableWidgetItem(f"{status_type}"))
                    self.ui.tableWidget_2.setItem(
                        row, 5, QTableWidgetItem(f"{sale.discount}"))
                    self.ui.tableWidget_2.setItem(
                        row, 6, QTableWidgetItem(f"{sale.pc_name}"))
                    if sale.payment_type == 1:
                        payment_type = 'карта'
                    elif sale.payment_type == 2:
                        payment_type = 'наличные'
                    else:
                        payment_type = '-'
                    self.ui.tableWidget_2.setItem(
                        row, 7, QTableWidgetItem(f"{payment_type}"))
            session.close()
        except Exception as e:
            logger.warning("Продаж не было")

    @logger_wraps()
    def open_client(self):
        """Открываем форму с данными клиента"""
        logger.info("Inside the function def open_client")
        client = ClientForm()
        client.show()
        client.exec_()

    @logger_wraps()
    def open_sale(self):
        """Открываем форму с продажей"""
        logger.info("Inside the function def open_sale")
        sale = SaleForm()
        sale.show()
        sale.exec_()
        System.sale_discount = 0

    @logger_wraps()
    def get_statistic(self):
        """Генерация сводной информации о продажах и билетах"""
        logger.info("Inside the function def get_statistic")
        # считаем выручку
        start_time = ' 00:00:00'
        end_time = ' 23:59:59'
        dt1 = self.ui.dateEdit_2.date().toString("yyyy-MM-dd") + start_time
        dt2 = self.ui.dateEdit.date().toString("yyyy-MM-dd") + end_time
        session = Session()
        sales = session.query(Sale.pc_name,
                              Sale.payment_type,
                              Sale.price
                              ).filter(Sale.datetime.between(dt1,
                                                             dt2)).all()
        session.close()
        logger.info('sales')
        logger.info(sales)
        # предполагаем что кассовых РМ два
        pc_1 = {'Name PC': f'{System.pc_1}', 'card': 0, 'cashe': 0}
        pc_2 = {'Name PC': f'{System.pc_2}', 'card': 0, 'cashe': 0}
        type = [1, 2]
        for i in range(len(sales)):
            if sales[i][0] in pc_1.values():
                if sales[i][1] == type[1]:
                    pc_1['card'] += sales[i][2]
                else:
                    pc_1['cashe'] += sales[i][2]
            else:
                if sales[i][1] == type[1]:
                    pc_2['card'] += sales[i][2]
                else:
                    pc_2['cashe'] += sales[i][2]
        logger.info('pc_1')
        logger.debug(pc_1)
        logger.info('pc_2')
        logger.debug(pc_2)
        card = int(pc_1['card']) + int(pc_2['card'])
        cashe = int(pc_1['cashe']) + int(pc_2['cashe'])
        sum = card + cashe
        self.ui.tableWidget_4.setRowCount(0)
        self.ui.tableWidget_4.insertRow(0)
        self.ui.tableWidget_4.setItem(0, 0,
                                      QTableWidgetItem(f"{pc_1['Name PC']}"))
        self.ui.tableWidget_4.setItem(0, 1,
                                      QTableWidgetItem(f"{pc_1['card']}"))
        self.ui.tableWidget_4.setItem(0, 2,
                                      QTableWidgetItem(f"{pc_1['cashe']}"))
        self.ui.tableWidget_4.insertRow(1)
        self.ui.tableWidget_4.setItem(1, 0,
                                      QTableWidgetItem(f"{pc_2['Name PC']}"))
        self.ui.tableWidget_4.setItem(1, 1,
                                      QTableWidgetItem(f"{pc_2['card']}"))
        self.ui.tableWidget_4.setItem(1, 2,
                                      QTableWidgetItem(f"{pc_2['cashe']}"))
        self.ui.tableWidget_4.insertRow(2)
        self.ui.tableWidget_4.setItem(2, 0,
                                      QTableWidgetItem(f"{'Итого'}"))
        self.ui.tableWidget_4.setItem(2, 1,
                                      QTableWidgetItem(f"{card}"))
        self.ui.tableWidget_4.setItem(2, 2,
                                      QTableWidgetItem(f"{cashe}"))
        self.ui.tableWidget_4.setItem(2, 3,
                                      QTableWidgetItem(f"{sum}"))
        # считаем билеты
        session = Session()
        tickets = session.query(Ticket.ticket_type,
                                Ticket.arrival_time,
                                Ticket.description,
                                ).filter(Ticket.datetime.between(dt1,
                                                                 dt2)).all()
        session.close()
        logger.info('tickets')
        logger.info(tickets)
        logger.debug((len(tickets)))
        type_tickets = [0, 1, 'м', 'и', '-']
        # 0-взролый, 1-детский, 2-многодетный, 3-инвалид
        time_arrival = [1, 2, 3]
        # child
        c = {'sum': 0, 't_1': 0, 't_2': 0, 't_3': 0}
        # adult
        a = {'sum': 0, 't_1': 0, 't_2': 0, 't_3': 0}
        # many_child
        m = {'sum': 0, 't_1': 0, 't_2': 0, 't_3': 0}
        # invalid
        i_ = {'sum': 0, 't_1': 0, 't_2': 0, 't_3': 0}
        # считаем количество билетов
        for i in range(len(tickets)):
            # обычный билет - '-'
            if tickets[i][2] == type_tickets[4]:
                # взрослый?
                if tickets[i][0] == type_tickets[0]:
                    a['sum'] += 1
                    # проверяем продолжительность времени
                    if tickets[i][1] == time_arrival[0]:
                        a['t_1'] += 1
                    elif tickets[i][1] == time_arrival[1]:
                        a['t_2'] += 1
                    elif tickets[i][1] == time_arrival[2]:
                        a['t_3'] += 1
                # детский?
                elif tickets[i][0] == type_tickets[1]:
                    c['sum'] += 1
                    # проверяем продолжительность времени
                    if tickets[i][1] == time_arrival[0]:
                        c['t_1'] += 1
                    elif tickets[i][1] == time_arrival[1]:
                        c['t_2'] += 1
                    elif tickets[i][1] == time_arrival[2]:
                        c['t_3'] += 1
            # многодетный?
            elif tickets[i][2] == type_tickets[2]:
                m['sum'] += 1
                if tickets[i][1] == time_arrival[0]:
                    m['t_1'] += 1
                elif tickets[i][1] == time_arrival[1]:
                    m['t_2'] += 1
                elif tickets[i][1] == time_arrival[2]:
                    m['t_3'] += 1
                # a['price'] += tickets[i][3]
            # инвалид?
            elif tickets[i][2] == type_tickets[3]:
                i_['sum'] += 1
                if tickets[i][1] == time_arrival[0]:
                    i_['t_1'] += 1
                elif tickets[i][1] == time_arrival[1]:
                    i_['t_2'] += 1
                elif tickets[i][1] == time_arrival[2]:
                    i_['t_3'] += 1
        # выводим обобщенную информаци юв таблицу
        self.ui.tableWidget_3.setRowCount(0)
        self.ui.tableWidget_3.insertRow(0)
        self.ui.tableWidget_3.setItem(0, 0, QTableWidgetItem('взрослый'))
        self.ui.tableWidget_3.setItem(0, 1, QTableWidgetItem(f"{a['sum']}"))
        self.ui.tableWidget_3.setItem(0, 2, QTableWidgetItem(f"{a['t_1']}"))
        self.ui.tableWidget_3.setItem(0, 3, QTableWidgetItem(f"{a['t_2']}"))
        self.ui.tableWidget_3.setItem(0, 4, QTableWidgetItem(f"{a['t_3']}"))
        self.ui.tableWidget_3.insertRow(1)
        self.ui.tableWidget_3.setItem(1, 0, QTableWidgetItem('детский'))
        self.ui.tableWidget_3.setItem(1, 1, QTableWidgetItem(f"{c['sum']}"))
        self.ui.tableWidget_3.setItem(1, 2, QTableWidgetItem(f"{c['t_1']}"))
        self.ui.tableWidget_3.setItem(1, 3, QTableWidgetItem(f"{c['t_2']}"))
        self.ui.tableWidget_3.setItem(1, 4, QTableWidgetItem(f"{c['t_3']}"))
        self.ui.tableWidget_3.insertRow(2)
        self.ui.tableWidget_3.setItem(2, 0, QTableWidgetItem('многодетный'))
        self.ui.tableWidget_3.setItem(2, 1, QTableWidgetItem(f"{m['sum']}"))
        self.ui.tableWidget_3.setItem(2, 2, QTableWidgetItem(f"{m['t_1']}"))
        self.ui.tableWidget_3.setItem(2, 3, QTableWidgetItem(f"{m['t_2']}"))
        self.ui.tableWidget_3.setItem(2, 4, QTableWidgetItem(f"{m['t_3']}"))
        self.ui.tableWidget_3.insertRow(3)
        self.ui.tableWidget_3.setItem(3, 0, QTableWidgetItem('инвалид'))
        self.ui.tableWidget_3.setItem(3, 1, QTableWidgetItem(f"{i_['sum']}"))
        self.ui.tableWidget_3.setItem(3, 2, QTableWidgetItem(f"{i_['t_1']}"))
        self.ui.tableWidget_3.setItem(3, 3, QTableWidgetItem(f"{i_['t_2']}"))
        self.ui.tableWidget_3.setItem(4, 4, QTableWidgetItem(f"{i_['t_3']}"))

    @logger_wraps()
    def otchet_administratora(self):
        """Формирование отчета администратора"""
        logger.info("Inside the function def otchet_administratora")
        path = "./otchet.pdf"
        path = os.path.realpath(path)
        row = self.ui.tableWidget_3.rowCount()
        if row >= 1:
            type = ['Взрослый, 1 ч.', 'Взрослый, 2 ч.', 'Взрослый, 3 ч.',
                    'Детский, 1 ч.', 'Детский, 2 ч.', 'Детский, 3 ч.',
                    'Многодетный', 'Инвалид']
            table = [self.ui.tableWidget_3.item(0, 2).text(),
                     self.ui.tableWidget_3.item(0, 3).text(),
                     self.ui.tableWidget_3.item(0, 4).text(),
                     self.ui.tableWidget_3.item(1, 2).text(),
                     self.ui.tableWidget_3.item(1, 3).text(),
                     self.ui.tableWidget_3.item(1, 4).text(),
                     self.ui.tableWidget_3.item(2, 1).text(),
                     self.ui.tableWidget_3.item(3, 1).text()]
            """Удаляем предыдущий файл"""
            os.system("TASKKILL /F /IM SumatraPDF.exe")
            if os.path.exists(path):
                os.remove(path)
            dt1 = self.ui.dateEdit_2.date().toString("dd-MM-yyyy")
            dt2 = self.ui.dateEdit.date().toString("dd-MM-yyyy")
            # формируем данные
            data = [['№ п/п', 'Тип\nбилета', 'Цена, руб.',
                     'Количество, шт.', 'Стоимость, руб.'],
                    ['1', type[0], System.ticket_adult_1, table[0],
                     int(System.ticket_adult_1) * int(table[0])],
                    ['2', type[1], System.ticket_adult_2, table[1],
                     int(System.ticket_adult_2) * int(table[1])],
                    ['3', type[2], System.ticket_adult_3, table[2],
                     int(System.ticket_adult_3) * int(table[2])],
                    ['4', type[3], System.ticket_child_1, table[3],
                     int(System.ticket_child_1) * int(table[3])],
                    ['5', type[4], System.ticket_child_2, table[4],
                     int(System.ticket_child_2) * int(table[4])],
                    ['6', type[5], System.ticket_child_3, table[5],
                     int(System.ticket_child_3) * int(table[5])],
                    ['7', type[6], '-', table[6], '-'],
                    ['8', type[7], '-', table[7], '-']]
            logger.info(data)
            otchet.otchet_administratora(dt1, dt2, data)
            os.startfile(path)

    @logger_wraps()
    def otchet_kassira(self):
        """Формирование отчета кассира"""
        logger.info("Inside the function def otchet_kassira")
        path = "./otchet.pdf"
        path = os.path.realpath(path)
        """Удаляем предыдущий файл"""
        row_tab_1 = self.ui.tableWidget_3.rowCount()
        row_tab_2 = self.ui.tableWidget_4.rowCount()
        if row_tab_1 >= 1 and row_tab_2 >= 1:
            os.system("TASKKILL /F /IM SumatraPDF.exe")
            if os.path.exists(path):
                os.remove(path)
            dt1 = self.ui.dateEdit_2.date().toString("dd-MM-yyyy")
            dt2 = self.ui.dateEdit.date().toString("dd-MM-yyyy")
            # формируем данные
            logger.info(self.ui.tableWidget_3.item(0, 0).text())
            logger.info(System.pc_name)
            if System.pc_name == self.ui.tableWidget_4.item(0, 0).text():
                values = [self.ui.tableWidget_4.item(0, 1).text(),
                          self.ui.tableWidget_4.item(0, 2).text()]
            else:
                values = [self.ui.tableWidget_4.item(1, 1).text(),
                          self.ui.tableWidget_4.item(1, 2).text()]
            logger.info(values)
            otchet.otchet_kassira(values, dt1, dt2, System.user)
            os.startfile(path)


class AuthForm(QDialog):
    """Форма авторизации"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        """Добавляем логотип на форму"""
        pixmap = QPixmap('pylogo.png')
        self.ui.label_4.setPixmap(pixmap)
        self.ui.label_7.setText(software_version)
        self.ui.pushButton.clicked.connect(self.logincheck)
        self.ui.pushButton_2.clicked.connect(self.close)

    def logincheck(self):
        """Проверяем есть ли в таблице user запись с указанными полями"""
        logger.info("Inside the function def logincheck")
        login = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()
        kassir = System.check_login(self, login, password)
        if kassir == 1:
            """После закрытия окна авторизации открываем главную форму"""
            auth.close()
            window = MainWindow()
            window.setWindowTitle('PyMasl ver. ' + software_version +
                                  '. Пользователь: ' +
                                  System.user[0] + ' ' + System.user[1])
            # отображаем все продажи при запуске
            window.button_all_sales()
            # устанавливаем по-умолчанию фильтр по фамилии
            window.ui.comboBox_2.setCurrentIndex(1)
            # проверяем статус текущего дня
            day_today = System.check_day(self)
            logger.info('day_today %s' % (day_today))
            if day_today == 0:
                System.what_a_day = 0
                logger.info("System.what_a_day %s" % (System.what_a_day))
            elif day_today == 1:
                System.what_a_day = 1
                sun, num_of_week = System.check_one_sunday(self)
                # проверяем если номер дня недели равен 7 и дата <= 7
                System.sunday = sun
                logger.info("System.sunday %s" % (System.sunday))
                System.num_of_week = num_of_week
                logger.info("System.num_of_week %s" % (System.num_of_week))
            # else:
            #     System.what_a_day = 0  # надо ли??
            # считываем количество РМ и имена
            System.kol_pc = kol_pc
            System.pc_1 = pc_1
            System.pc_2 = pc_2
            window.show()
            window.exec_()
        else:
            windows.info_window(
                'Пользователь не найден',
                'Проверьте правильность ввода логина и пароля.', '')


class ClientForm(QDialog):
    """Форма с данными клиента"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_Client()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.client_save)
        self.ui.pushButton_2.clicked.connect(self.close)

    def client_save(self):
        """Сохраняем информацию о новом клиенте"""
        logger.info("Inside the function def client_save")
        System.add_new_client_in_sale = 0
        if System.client_update != 1:
            # добавляем нового клиента
            with Session.begin() as session:
                logger.info('добавляем нового клиента')
                client_index = session.query(Client).count()
                add_client = Client(id=client_index + 1,
                                    last_name=str(
                                        self.ui.lineEdit.text()),
                                    first_name=str(
                                        self.ui.lineEdit_2.text()),
                                    middle_name=str(
                                        self.ui.lineEdit_3.text()),
                                    birth_date=(self.ui.dateEdit.date().
                                                toString("yyyy-MM-dd")),
                                    gender=str(
                                        self.ui.comboBox.currentText()),
                                    phone=self.ui.lineEdit_4.text(),
                                    email=self.ui.lineEdit_5.text(),
                                    privilege=str(
                                        self.ui.comboBox_2.currentText()))
                session.add(add_client)
            # сохраняем id нового клиента
            System.id_new_client_in_sale = client_index + 1
            self.close()
        elif System.client_update == 1:
            # обновляем информацию о клиенте
            with Session.begin() as session:
                logger.info('обновляем информацию о клиенте')
                session.execute(update(Client).where(
                    Client.id == System.client_id).values(
                    id=System.client_id,
                    last_name=str(self.ui.lineEdit.text()),
                    first_name=str(self.ui.lineEdit_2.text()),
                    middle_name=str(self.ui.lineEdit_3.text()),
                    birth_date=self.ui.dateEdit.date().toString(
                        "yyyy-MM-dd"),
                    gender=str(self.ui.comboBox.currentText()),
                    phone=self.ui.lineEdit_4.text(),
                    email=self.ui.lineEdit_5.text(),
                    privilege=str((self.ui.comboBox_2.
                                   currentText()))))
            System.client_update = None
            System.client_id = None
            self.close()


class SaleForm(QDialog):
    """Форма с данными клиента"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_Sale()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.search_clients_to_sale)
        self.ui.pushButton_2.clicked.connect(lambda: MainWindow.open_client(self))
        self.ui.pushButton_3.clicked.connect(self.sale_save)
        self.ui.pushButton_4.clicked.connect(self.close)
        self.ui.pushButton_5.clicked.connect(
            lambda: self.open_pay(self.ui.label_8.text()))
        self.ui.pushButton_6.clicked.connect(self.sale_return)
        self.ui.pushButton_7.clicked.connect(self.generate_saved_tickets)
        self.ui.tableWidget.doubleClicked.connect(self.add_client_to_sale)
        cur_today = date.today()
        self.ui.dateEdit.setDate(cur_today)
        self.ui.dateEdit.dateChanged.connect(self.calendar_color_change)
        self.ui.comboBox.currentTextChanged.connect(self.edit_sale)
        self.ui.checkBox_2.stateChanged.connect(self.check_sale_enabled)
        self.ui.comboBox_2.currentTextChanged.connect(self.edit_sale)
        # адаптированный для пользователя фильтр
        self.ui.comboBox_4.currentTextChanged.connect(self.sale_check_filter_update)
        # KeyPressEvent
        self.ui.tableWidget_2.keyPressEvent = self.key_pressed
        self.ui.pushButton_9.clicked.connect(self.add_new_client)
        self.ui.pushButton_10.clicked.connect(self.edit_sale)
        self.ui.tableWidget_3.doubleClicked.connect(self.add_client_to_sale_2)
    def add_new_client(self):
        """Добавляем в окно продажи только что созданного клиента"""
        logger.info("Inside the function def add_new_client")
        type_ticket = ''
        """Запрашиваем id нового клиента"""
        session = Session()
        search_client = session.query(Client).filter_by(id=(System.id_new_client_in_sale)).first()
        session.close()
        print('search_client', search_client)
        """Вычисляем возраст клиента"""
        today = date.today()
        age = (today.year - search_client.birth_date.year -
               ((today.month, today.day) < (search_client.birth_date.month,
                                            search_client.birth_date.day)))
        """Определяем тип билета и цену"""
        if 5 <= age < 14:
            type_ticket = 'детский'
        elif age >= 14:
            type_ticket = 'взрослый'
        """Определяем тип билета и цену"""
        time = int(self.ui.comboBox.currentText())
        if type == 'взрослый':
            if time == 1:
                price = System.ticket_adult_1
            elif time == 2:
                price = System.ticket_adult_2
            else:
                price = System.ticket_adult_3
        else:
            if time == 1:
                price = System.ticket_child_1
            elif time == 2:
                price = System.ticket_child_2
            else:
                price = System.ticket_child_3
        """Создаем виджет checkbox"""
        widget = QWidget()
        checkbox = QCheckBox()
        checkbox.setCheckState(Qt.Unchecked)
        layoutH = QHBoxLayout(widget)
        layoutH.addWidget(checkbox)
        layoutH.setAlignment(Qt.AlignCenter)
        layoutH.setContentsMargins(0, 0, 0, 0)
        row = self.ui.tableWidget_2.rowCount()
        self.ui.tableWidget_2.insertRow(row)
        """добавляем checkbox"""
        self.ui.tableWidget_2.setCellWidget(row, 7, widget)
        """Передаем в таблицу заказа данные клиента"""
        self.ui.tableWidget_2.setItem(
            row, 0, QTableWidgetItem(f"{search_client.last_name}"))
        self.ui.tableWidget_2.setItem(
            row, 1, QTableWidgetItem(f"{search_client.first_name}"))
        self.ui.tableWidget_2.setItem(
            row, 2, QTableWidgetItem(f"{type_ticket}"))
        self.ui.tableWidget_2.setItem(
            row, 3, QTableWidgetItem(f"{price}"))
        self.ui.tableWidget_2.setItem(
            row, 4, QTableWidgetItem(f"{search_client.privilege}"))
        self.ui.tableWidget_2.setItem(
            row, 5, QTableWidgetItem(f"{search_client.id}"))
        self.ui.tableWidget_2.setColumnHidden(5, True)
        self.ui.tableWidget_2.setItem(row, 6, QTableWidgetItem(f"{age}"))
        self.ui.tableWidget_2.setColumnHidden(6, True)

    def key_pressed(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.del_selected_item()
        elif event.key() == QtCore.Qt.Key_Backspace:
            self.del_selected_item()
        elif event.key() == QtCore.Qt.Key_Space:
            self.edit_sale()

    def del_selected_item(self):
        """Удаляем запись из таблицы при нажатии кнопки в key_press_event"""
        logger.info("Inside the function def del_selected_item")
        if self.ui.tableWidget_2.rowCount() > 0:
            currentrow = self.ui.tableWidget_2.currentRow()
            # перед удаление записи обновляем sale_dictt
            type = self.ui.tableWidget_2.item(currentrow, 2).text()
            # если checkbox в tableWidget_2 активирован, то обновляем details
            if type == 'взрослый':
                if self.ui.tableWidget_2.cellWidget(currentrow, 7).findChild(QCheckBox).isChecked():
                    System.sale_dict['detail'][0] -= 1
                else:
                    System.sale_dict['kol_adult'] -= 1
            else:
                if self.ui.tableWidget_2.cellWidget(currentrow, 7).findChild(QCheckBox).isChecked():
                    System.sale_dict['detail'][2] -= 1
                else:
                    System.sale_dict['kol_child'] -= 1
            self.ui.tableWidget_2.removeRow(currentrow)
            self.check_field_update()
            self.edit_sale()
        row = self.ui.tableWidget_2.rowCount()
        # если таблица заказа пустая
        if row == 0:
            # отменяем скидку 100%
            # ! работает только при двойном нажатии кнопок "del", "backspace"
            self.ui.comboBox_2.setCurrentIndex(0)
            System.sale_discount = 0
            self.edit_sale()
            # Обновляем System.sale_dict
            System.sale_dict['kol_adult'] = 0
            System.sale_dict['kol_child'] = 0
            System.sale_dict['detail'][5] = 0
            System.sale_dict['detail'][6] = 0
            System.sale_dict['detail'][7] = 0

    def sale_check_filter_update(self):
        """Передаем значение пользовательского
        фильтра в модель QSqlTableModel"""
        logger.info("Inside the function def sale_check_filter_update ")
        self.ui.lineEdit.clear()

    def calendar_color_change(self):
        logger.info("Inside the function def calendar_color_change")
        logger.warning(self.ui.dateEdit.date())
        date = str(self.ui.dateEdit.date())
        date_slice = date[21:(len(date) - 1)]
        logger.debug(date_slice)
        date = date_slice.replace(', ', '-')
        logger.debug(date)
        if System.check_day(self, date) == 1:
            self.ui.dateEdit.setStyleSheet('background-color: red;')
            logger.debug(self.ui.dateEdit.date)
        else:
            self.ui.dateEdit.setStyleSheet('background-color: white;')
            logger.debug(self.ui.dateEdit.date)

    def check_sale_enabled(self):
        logger.info("Inside the function def check_sale_enabled")
        if self.ui.checkBox_2.isChecked():
            self.ui.comboBox_2.setEnabled(True)
        else:
            self.ui.comboBox_2.setEnabled(False)

    @logger_wraps()
    def search_clients_to_sale(self):
        """Выводим в tableWidget новой продажи список найденных клиентов"""
        logger.info("Inside the function def button_all_clients_to_sale")
        today = date.today()
        if System.what_a_day == 1:
            self.ui.dateEdit.setStyleSheet('background-color: red;')
        # вычисляем индекс значения
        index = self.ui.comboBox_4.currentIndex()
        if index == 2:
            """Поиск по номеру телефона"""
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.phone.like(
                '%' + self.ui.lineEdit.text() + '%')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(
                    row, 0, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(
                    row, 1, QTableWidgetItem(f"{client.first_name}"))
                """Вычисляем возраст клиента"""
                age = (today.year - client.birth_date.year -
                       ((today.month, today.day) < (client.birth_date.month,
                                                    client.birth_date.day)))
                self.ui.tableWidget.setItem(
                    row, 2, QTableWidgetItem(f"{age}"))
                self.ui.tableWidget.setItem(
                    row, 3, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 4, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(5, True)
            session.close()
        elif index == 1:
            """Поиск по фамилии"""
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.last_name.ilike(
                '%' + self.ui.lineEdit.text() + '%')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(
                    row, 0, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(
                    row, 1, QTableWidgetItem(f"{client.first_name}"))
                """Вычисляем возраст клиента"""
                age = (today.year - client.birth_date.year -
                       ((today.month, today.day) < (client.birth_date.month,
                                                    client.birth_date.day)))
                self.ui.tableWidget.setItem(
                    row, 2, QTableWidgetItem(f"{age}"))
                self.ui.tableWidget.setItem(
                    row, 3, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 4, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(5, True)
            session.close()
        elif index == 0:
            """Поиск по фамилии и имени"""
            self.ui.tableWidget.setRowCount(0)
            search = self.ui.lineEdit.text().title()
            print('search', search)
            lst = search.split()
            print('lst', lst)
            print('len(lst)', len(lst))
            if len(lst) == 2:
                session = Session()
                search = session.query(Client).filter(and_(Client.first_name.ilike(
                    lst[1] + '%'), Client.last_name.ilike(
                    lst[0] + '%'))).all()
            else:
                windows.info_window('Внимание',
                                    'Задайте условие для поиска правильно', '')
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(
                    row, 0, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(
                    row, 1, QTableWidgetItem(f"{client.first_name}"))
                """Вычисляем возраст клиента"""
                age = (today.year - client.birth_date.year -
                       ((today.month, today.day) < (client.birth_date.month,
                                                    client.birth_date.day)))
                self.ui.tableWidget.setItem(
                    row, 2, QTableWidgetItem(f"{age}"))
                self.ui.tableWidget.setItem(
                    row, 3, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 4, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(5, True)
            session.close()
        elif index == 3:
            """Поиск инвалидов"""
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.privilege.ilike(
                '%' + 'и')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(
                    row, 0, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(
                    row, 1, QTableWidgetItem(f"{client.first_name}"))
                """Вычисляем возраст клиента"""
                age = (today.year - client.birth_date.year -
                       ((today.month, today.day) < (client.birth_date.month,
                                                    client.birth_date.day)))
                self.ui.tableWidget.setItem(
                    row, 2, QTableWidgetItem(f"{age}"))
                self.ui.tableWidget.setItem(
                    row, 3, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 4, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(5, True)
            session.close()
        elif index == 4:
            """Поиск многодетных"""
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.privilege.ilike(
                '%' + 'м')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(
                    row, 0, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(
                    row, 1, QTableWidgetItem(f"{client.first_name}"))
                """Вычисляем возраст клиента"""
                age = (today.year - client.birth_date.year -
                       ((today.month, today.day) < (client.birth_date.month,
                                                    client.birth_date.day)))
                self.ui.tableWidget.setItem(
                    row, 2, QTableWidgetItem(f"{age}"))
                self.ui.tableWidget.setItem(
                    row, 3, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 4, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(5, True)
            session.close()

    @logger_wraps()
    def add_client_to_sale(self, *args, **kwargs):
        """Поиск выделенной строки в таблице клиентов
        и передача ее в таблицу заказа
        """
        """изменяем ширину столбцов"""
        self.ui.tableWidget_2.setColumnWidth(3, 5)
        self.ui.tableWidget_2.setColumnWidth(4, 5)
        logger.info("Inside the function def add_client_to_sale")
        type_ticket = ''
        today = date.today()
        # если продажа новая - обновляем статус
        System.sale_status = 0
        logger.warning("status_sale %s" % (System.sale_status))
        for idx in self.ui.tableWidget.selectionModel().selectedIndexes():
            """Номер строки найден"""
            row_number = idx.row()
            """Получаем содержимое ячейки"""
            res = self.ui.tableWidget.item(row_number, 5).text()
            session = Session()
            """Находим выделенного в таблице клиента"""
            search_client = session.query(Client).filter_by(id=(res)).first()
            session.close()
            # print('search_client', search_client)
            """Вычисляем возраст клиента"""
            age = int(self.ui.tableWidget.item(row_number, 2).text())
            """Определяем тип билета и цену"""
            if 5 <= age < 14:
                type_ticket = 'детский'
            elif age >= 14:
                type_ticket = 'взрослый'
            """Создаем виджет checkbox"""
            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            layoutH = QHBoxLayout(widget)
            layoutH.addWidget(checkbox)
            layoutH.setAlignment(Qt.AlignCenter)
            layoutH.setContentsMargins(0, 0, 0, 0)
            row = self.ui.tableWidget_2.rowCount()
            self.ui.tableWidget_2.insertRow(row)
            """добавляем checkbox"""
            self.ui.tableWidget_2.setCellWidget(row, 7, widget)
            """Передаем в таблицу заказа данные клиента"""
            self.ui.tableWidget_2.setItem(
                row, 0, QTableWidgetItem(f"{search_client.last_name}"))
            self.ui.tableWidget_2.setItem(
                row, 1, QTableWidgetItem(f"{search_client.first_name}"))
            self.ui.tableWidget_2.setItem(
                row, 2, QTableWidgetItem(f"{type_ticket}"))
            # цена
            self.ui.tableWidget_2.setItem(
                row, 3, QTableWidgetItem(f"{0}"))
            self.ui.tableWidget_2.setItem(
                row, 4, QTableWidgetItem(f"{search_client.privilege}"))
            self.ui.tableWidget_2.setItem(
                row, 5, QTableWidgetItem(f"{search_client.id}"))
            self.ui.tableWidget_2.setColumnHidden(5, True)
            self.ui.tableWidget_2.setItem(row, 6, QTableWidgetItem(f"{age}"))
            # self.ui.tableWidget_2.setColumnHidden(6, True)
            self.edit_sale()
            """Очищаем tableWidget_3"""
            while self.ui.tableWidget_3.rowCount() > 0:
                self.ui.tableWidget_3.removeRow(0)
                """изменяем ширину столбцов"""
            self.ui.tableWidget_3.setColumnWidth(2, 10)
            self.ui.tableWidget_3.setColumnWidth(3, 5)
            """Ищем продажи, в которых он был ранее"""
            session = Session()
            sales = session.query(Client.id, Ticket.id, Ticket.id_sale).filter(
                and_(Client.id == search_client.id, Ticket.id_client == search_client.id))
            for client_in_sales in sales:
                if client_in_sales:
                    """Находим других клиентов, которые были в этих продажах"""
                    search_sale = session.query(Ticket.id_sale, Ticket.id_client).filter(
                        Ticket.id_sale == client_in_sales[2])
                    for search_cl in search_sale:
                        """Запрашиваем информацию об этих клиентах"""
                        search_client_in_sale = session.query(Client).filter_by(id=search_cl[1]).first()
                        row = self.ui.tableWidget_3.rowCount()
                        self.ui.tableWidget_3.insertRow(row)
                        self.ui.tableWidget_3.setItem(
                            row, 0, QTableWidgetItem(f"{search_client_in_sale.last_name}"))
                        self.ui.tableWidget_3.setItem(
                            row, 1, QTableWidgetItem(f"{search_client_in_sale.first_name}"))
                        """Вычисляем возраст клиента"""
                        age = (today.year - search_client_in_sale.birth_date.year -
                               ((today.month, today.day) < (search_client_in_sale.birth_date.month,
                                                            search_client_in_sale.birth_date.day)))
                        self.ui.tableWidget_3.setItem(
                            row, 2, QTableWidgetItem(f"{age}"))
                        self.ui.tableWidget_3.setItem(
                            row, 3, QTableWidgetItem(f"{search_client_in_sale.privilege}"))
                        self.ui.tableWidget_3.setItem(
                            row, 4, QTableWidgetItem(f"{search_client_in_sale.id}"))
                        self.ui.tableWidget_3.setColumnHidden(4, True)
            session.close()

    @logger_wraps()
    def add_client_to_sale_2(self, *args, **kwargs):
        """Поиск выделенной строки в таблице клиентов
        и передача ее в таблицу заказа
        """
        logger.info("Inside the function def add_client_to_sale 2")
        for idx in self.ui.tableWidget_3.selectionModel().selectedIndexes():
            """Номер строки найден"""
            row_number = idx.row()
            """Получаем содержимое ячейки"""
            res = self.ui.tableWidget_3.item(row_number, 4).text()
            age = int(self.ui.tableWidget_3.item(row_number, 2).text())
            session = Session()
            """Находим выделенного в таблице клиента"""
            search_client = session.query(Client).filter_by(id=(res)).first()
            session.close()
            """Определяем тип билета и цену"""
            if 5 <= age < 14:
                type_ticket = 'детский'
            elif age >= 14:
                type_ticket = 'взрослый'
            """Определяем тип билета и цену"""
            """Создаем виджет checkbox"""
            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            layoutH = QHBoxLayout(widget)
            layoutH.addWidget(checkbox)
            layoutH.setAlignment(Qt.AlignCenter)
            layoutH.setContentsMargins(0, 0, 0, 0)
            row = self.ui.tableWidget_2.rowCount()
            self.ui.tableWidget_2.insertRow(row)
            """добавляем checkbox"""
            self.ui.tableWidget_2.setCellWidget(row, 7, widget)
            """Передаем в таблицу заказа данные клиента"""
            self.ui.tableWidget_2.setItem(
                row, 0, QTableWidgetItem(f"{search_client.last_name}"))
            self.ui.tableWidget_2.setItem(
                row, 1, QTableWidgetItem(f"{search_client.first_name}"))
            # self.ui.tableWidget_2.setItem(
            #     row, 2, QTableWidgetItem(f"{search_client.middle_name}"))
            self.ui.tableWidget_2.setItem(
                row, 2, QTableWidgetItem(f"{type_ticket}"))
            # цена
            self.ui.tableWidget_2.setItem(
                row, 3, QTableWidgetItem(f"{0}"))
            self.ui.tableWidget_2.setItem(
                row, 4, QTableWidgetItem(f"{search_client.privilege}"))
            self.ui.tableWidget_2.setItem(
                row, 5, QTableWidgetItem(f"{search_client.id}"))
            self.ui.tableWidget_2.setColumnHidden(5, True)
            self.ui.tableWidget_2.setItem(row, 6, QTableWidgetItem(f"{age}"))
            # self.ui.tableWidget_2.setColumnHidden(6, True)
            self.edit_sale()

    def check_field_update(self):
        """Определяем статус продажи: обычная
        или продление билетов для многодетных"""
        logger.info("Inside the function def check_field_update")
        # если сегодня не первое воскресенье месяца
        if self.ui.checkBox_3.isChecked():
            logger.info('продление многодетным')
            # отменяем скидку 100%
            self.ui.checkBox_2.setEnabled(True)
            self.ui.comboBox_2.setCurrentIndex(0)
            self.extension_many_child()
        else:
            logger.info('обычная продажа')
            self.edit_sale()

    def edit_sale(self):
        """Обновляем таблицу заказа и генерируем информацию
        о продаже и список билетов
        """
        logger.info("Inside the function def edit_sale")
        logger.info('system what_a_day', System.what_a_day)
        kol_adult = 0
        kol_child = 0
        kol_sale_adult = 0
        kol_sale_child = 0
        new_price = 0
        kol_adult_many_child = 0
        kol_child_many_child = 0
        id_adult = 0
        time = 0
        time_ticket = self.ui.comboBox.currentText()
        sale = 0
        tickets = []
        many_child = 0
        invalid = 0
        talent = 0
        '''устанавливаем время и количество талантов'''
        if (int(time_ticket)) == 1:
            time = 1
            talent = System.talent_1
        elif (int(time_ticket)) == 2:
            time = 2
            talent = System.talent_2
        elif (int(time_ticket)) == 3:
            time = 3
            talent = System.talent_3
        System.sale_dict['detail'][6] = time
        date_time = self.ui.dateEdit.date().toString("yyyy-MM-dd")
        """считаем общую сумму"""
        rows = self.ui.tableWidget_2.rowCount()
        for row in range(rows):
            """Акция день многодетных?"""
            logger.info('system day', System.sunday)
            # проверяем категорию посетителя
            # если многодетный
            if self.ui.tableWidget_2.item(row, 4).text() == 'м':
                # проверяем если номер дня недели равен 7 и дата <= 7
                if System.sunday == 1:
                    many_child = 1
                    # устанавливаем продолжительность посещения
                    self.ui.comboBox.setCurrentIndex(1)
                    self.ui.checkBox_2.setEnabled(False)
                    logger.info('день многодетных')
                # применяем скидку 50%
                elif System.num_of_week <= 5:
                    many_child = 2
            # если инвалид
            elif self.ui.tableWidget_2.item(row, 4).text() == 'и':
                invalid = 1
            """Считаем общее количество позиций и берем цену"""
            type = self.ui.tableWidget_2.item(row, 2).text()
            # считаем взрослые билеты
            if type == 'взрослый':
                if time == 1:
                    price = System.ticket_adult_1
                elif time == 2:
                    # если обычный день
                    if many_child == 0:
                        price = System.ticket_adult_2
                    else:
                        # цена = 0
                        price = System.ticket_many_child
                        kol_adult_many_child += 1
                else:
                    # если продолжительность 3 часа
                    price = System.ticket_adult_3
                """Привязываем продажу ко взрослому"""
                if id_adult == 0:
                    id_adult = self.ui.tableWidget_2.item(row, 5).text()
                    System.sale_dict['detail'][5] = id_adult
                kol_adult += 1
                System.sale_dict['kol_adult'] = kol_adult
                System.sale_dict['price_adult'] = price
            # считаем детские билеты
            else:
                if time == 1:
                    # проверяем текущий день является выходным
                    if System.what_a_day == 0:
                        price = System.ticket_child_1
                    else:
                        price = System.ticket_child_week_1
                elif time == 2:
                    if many_child == 0:
                        if System.what_a_day == 0:
                            price = System.ticket_child_2
                        else:
                            price = System.ticket_child_week_2
                    # день многодетных
                    else:
                        price = System.ticket_many_child
                        kol_child_many_child += 1
                else:
                    if System.what_a_day == 0:
                        price = System.ticket_child_3
                    else:
                        price = System.ticket_child_week_3
                kol_child += 1
                System.sale_dict['kol_child'] = kol_child
                System.sale_dict['price_child'] = price
            # устанавливаем цену в таблицу и пересчитываем
            self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{price}"))
            """применяем скидку"""
            # в день многодетных
            if many_child == 1:
                # 100%
                self.ui.checkBox_2.setEnabled(True)
                self.ui.comboBox_2.setCurrentIndex(15)
                new_price = 0
                self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{new_price}"))
            # скидка 50% в будни
            elif many_child == 2:
                # 50%
                self.ui.checkBox_2.setEnabled(True)
                self.ui.comboBox_2.setCurrentIndex(10)
                new_price = price * 0.5
                self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{new_price}"))
            # скидка инвалидам
            elif invalid == 1:
                self.ui.checkBox_2.setEnabled(True)
                # 100%
                self.ui.comboBox_2.setCurrentIndex(15)
                new_price = 0
                self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{new_price}"))
            # иначе проверяем активен ли checkbox со скидкой и размер скидки больше 0
            else:
                if self.ui.checkBox_2.isChecked():
                    if int(self.ui.comboBox_2.currentText()) > 0:
                        System.sale_discount = int(self.ui.comboBox_2.currentText())
                        System.sale_dict['detail'][4] = System.sale_discount
                        if System.sale_discount > 0:
                            new_price = int(price - (price * System.sale_discount / 100))
                            # если checkbox в tableWidget_2 активирован, то применяем к этой строке скидку
                            if self.ui.tableWidget_2.cellWidget(row, 7).findChild(QCheckBox).isChecked():
                                if type == 'взрослый':
                                    kol_sale_adult += 1
                                    System.sale_dict['detail'][0] = kol_sale_adult
                                    System.sale_dict['detail'][1] = new_price
                                else:
                                    kol_sale_child += 1
                                    System.sale_dict['detail'][2] = kol_sale_child
                                    System.sale_dict['detail'][3] = new_price
                                self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{new_price}"))
                    # если сначала применили скидку, а потом отменили ее
                    else:
                        System.sale_discount = int(self.ui.comboBox_2.currentText())
                        System.sale_dict['detail'][4] = System.sale_discount
                        if type == 'взрослый':
                            System.sale_dict['detail'][1] = System.sale_dict['price_adult']
                        else:
                            System.sale_dict['detail'][3] = System.sale_dict['price_child']
            # была ли применена скидка в день многодетных?
            if new_price == 0 and many_child == 1:
                sale = new_price
            # была ли применена скидка инвалидам?
            elif new_price == 0 and invalid == 1:
                sale = new_price
            # скидки не было, оставляем прежнюю цену
            elif new_price == 0:
                sale = sale + price
            else:
                sale = sale + price
        itog = ((System.sale_dict['kol_adult'] - System.sale_dict['detail'][0]) * System.sale_dict['price_adult']) + \
               ((System.sale_dict['kol_child'] - System.sale_dict['detail'][2]) * System.sale_dict['price_child']) + \
               (System.sale_dict['detail'][0] * System.sale_dict['detail'][1]) + \
               (System.sale_dict['detail'][2] * System.sale_dict['detail'][3])
        self.ui.label_8.setText(str(itog))
        System.sale_dict['detail'][7] = itog
        self.ui.label_5.setText(str(kol_adult))
        self.ui.label_7.setText(str(kol_child))
        self.ui.label_17.setText(str(kol_adult_many_child))
        self.ui.label_19.setText(str(kol_child_many_child))
        """Сохраняем данные продажи"""
        logger.warning('sale_dict')
        logger.warning(System.sale_dict)
        """Генерируем список с билетами"""
        for row in range(rows):
            tickets.append((self.ui.tableWidget_2.item(row, 0).text(),
                            self.ui.tableWidget_2.item(row, 1).text(),
                            self.ui.tableWidget_2.item(row, 2).text(),
                            self.ui.tableWidget_2.item(row, 3).text(),
                            self.ui.tableWidget_2.item(row, 4).text(),
                            self.ui.tableWidget_2.item(row, 5).text(),
                            self.ui.tableWidget_2.item(row, 6).text(),
                            time_ticket, talent, date_time))
        System.sale_tickets = tickets
        logger.info('System.sale_tickets')
        logger.info(System.sale_tickets)
        """Проверяем есть ли в продаже взрослый"""
        if System.sale_dict['kol_adult'] >= 1:
            self.ui.pushButton_5.setEnabled(True)
        else:
            self.ui.pushButton_5.setEnabled(False)

    def extension_many_child(self):
        """Обновляем таблицу заказа для продления билетов многодетным"""
        logger.info("Inside the function def extension_many_child")
        kol_adult = 0
        kol_child = 0
        id_adult = 0
        time = 0
        time_ticket = self.ui.comboBox.currentText()
        sale = 0
        tickets = []
        talent = 0
        if (int(time_ticket)) == 1:
            time = 1
            talent = System.talent_1
        elif (int(time_ticket)) == 2:
            time = 2
            talent = System.talent_2
        elif (int(time_ticket)) == 3:
            time = 3
            talent = System.talent_3
        System.sale_dict['detail'][6] = time
        date_time = self.ui.dateEdit.date().toString("yyyy-MM-dd")
        """считаем общую сумму"""
        rows = self.ui.tableWidget_2.rowCount()
        for row in range(rows):
            # проверяем категорию посетителя
            # если многодетный
            if self.ui.tableWidget_2.item(row, 4).text() == 'м':
                """Считаем общее количество позиций и берем цену"""
                type = self.ui.tableWidget_2.item(row, 2).text()
                # считаем взрослые билеты
                if type == 'взрослый':
                    if time == 1:
                        price = System.ticket_adult_1
                    elif time == 2:
                        price = System.ticket_adult_2
                    else:
                        # если продолжительность 3 часа
                        price = System.ticket_adult_3
                    """Привязываем продажу ко взрослому"""
                    if id_adult == 0:
                        id_adult = self.ui.tableWidget_2.item(row, 5).text()
                        System.sale_dict['detail'][5] = id_adult
                    kol_adult += 1
                    System.sale_dict['kol_adult'] = kol_adult
                    System.sale_dict['price_adult'] = price
                # считаем детские билеты
                else:
                    if time == 1:
                        price = System.ticket_child_week_1
                    elif time == 2:
                        price = System.ticket_child_week_2
                    else:
                        price = System.ticket_child_week_3
                    kol_child += 1
                    System.sale_dict['kol_child'] = kol_child
                    System.sale_dict['price_child'] = price
                # устанавливаем цену в таблицу и пересчитываем
                self.ui.tableWidget_2.setItem(row, 3,
                                              QTableWidgetItem(f"{price}"))
                sale = sale + price
                self.ui.label_8.setText(str(sale))
        self.ui.label_5.setText(str(kol_adult))
        self.ui.label_7.setText(str(kol_child))
        System.sale_discount = sale / 100 * int(self.ui.comboBox_2.currentText())
        if sale >= 0:
            # new_price = sale - (sale/100 * System.sale_discount)
            new_price = sale - System.sale_discount
            new_price = int(new_price)
            self.ui.label_8.setText(str(new_price))
        itog = ((System.sale_dict['kol_adult'] - System.sale_dict['detail'][0]) * System.sale_dict['price_adult']) + \
               ((System.sale_dict['kol_child'] - System.sale_dict['detail'][2]) * System.sale_dict['price_child']) + \
               (System.sale_dict['detail'][0] * System.sale_dict['detail'][1]) + \
               (System.sale_dict['detail'][2] * System.sale_dict['detail'][3])
        self.ui.label_8.setText(str(itog))
        System.sale_dict['detail'][7] = itog
        self.ui.label_5.setText(str(kol_adult))
        self.ui.label_7.setText(str(kol_child))
        """Генерируем список с билетами"""
        for row in range(rows):
            tickets.append((self.ui.tableWidget_2.item(row, 0).text(),
                            self.ui.tableWidget_2.item(row, 1).text(),
                            self.ui.tableWidget_2.item(row, 2).text(),
                            self.ui.tableWidget_2.item(row, 3).text(),
                            self.ui.tableWidget_2.item(row, 4).text(),
                            self.ui.tableWidget_2.item(row, 5).text(),
                            self.ui.tableWidget_2.item(row, 6).text(),
                            '1',
                            # проверить состояние checkbox`a
                            # self.ui.tableWidget_2.item(row, 8).text(),
                            time_ticket, talent, date_time))
        logger.info('System.sale_dict')
        logger.info(System.sale_dict)
        System.sale_tickets = tickets
        logger.info('System.sale_tickets')
        logger.info(System.sale_tickets)
        """Проверяем есть ли в продаже взрослый"""
        if System.sale_tuple[0] >= 1:
            self.ui.pushButton_5.setEnabled(True)
        else:
            self.ui.pushButton_5.setEnabled(False)

    def sale_save(self):
        """Сохраняем данные заказа"""
        logger.info("Inside the function def sale_save")
        if System.sale_status == 0:
            self.ui.pushButton_5.setEnabled(True)
            add_sale = Sale(price=System.sale_dict['detail'][7],
                            id_user=System.user[3],
                            id_client=System.sale_dict['detail'][5],
                            status=0,
                            discount=System.sale_dict['detail'][4],
                            pc_name=System.pc_name,
                            datetime=dt.datetime.now())
            logger.debug('add_sale %s' % (add_sale))
            """Сохраняем продажу"""
            logger.info("Сохраняем продажу")
            session = Session()
            session.add(add_sale)
            session.commit()
            System.sale_id = session.query(Sale).count()
            session.close()
            """Генерируем билеты"""
            logger.info("Генерируем билеты")
            logger.debug(System.sale_tickets)
            type = None
            session = Session()
            for i in range(len(System.sale_tickets)):
                """Считаем количество начисленных талантов"""
                if System.sale_tickets[i][2] == 'взрослый':
                    type = 0
                elif System.sale_tickets[i][2] == 'детский':
                    type = 1
                logger.info('тип билета %s' % (type))
                add_ticket = Ticket(id_client=System.sale_tickets[i][5],
                                    id_sale=int(System.sale_id),
                                    arrival_time=System.sale_tickets[i][7],
                                    talent=System.sale_tickets[i][8],
                                    price=System.sale_tickets[i][3],
                                    description=System.sale_tickets[i][4],
                                    ticket_type=type,
                                    client_age=System.sale_tickets[i][6])
                logger.info("Сохраняем билет")
                logger.info(add_ticket)
                session.add(add_ticket)
                session.commit()
            session.close()
            self.close()

    @logger.catch()
    def sale_transaction(self, payment_type):
        """Проводим операцию продажи"""
        logger.info("Inside the function def sale_transaction")
        # если сумма продажи 0 - генерируем билеты
        if System.sale_dict['detail'][7] == 0:
            self.sale_save()
            self.generate_saved_tickets()
        else:
            state_check, payment = kkt.check_open(System.sale_dict,
                                                  payment_type, System.user, 1)
            check = None
            """Если прошла оплата"""
            if state_check == 1:
                if payment == 1:  # если оплата банковской картой
                    logger.info("Читаем слип-чек из файла")
                    pinpad_file = r"C:\sc552\p"
                    with open(pinpad_file, 'r', encoding='IBM866') as file:
                        while (line := file.readline().rstrip()):
                            logger.debug(line)
                    check = kkt.read_slip_check()
                if System.sale_status == 0:
                    """Сохраняем данные о новой продаже"""
                    self.sale_save()
                # обновляем информацию о продаже в БД
                session = Session()
                session.execute(update(Sale).where(
                    Sale.id == System.sale_id).values(
                    status=1, id_user=System.user[3],
                    pc_name=System.pc_name,
                    payment_type=payment,
                    bank_pay=check,
                    datetime=dt.datetime.now()))
                session.commit()
                session.close()
                self.generate_saved_tickets()

                System.sale_status = 0
                # предлагаем очистить окно для проведения новой продажи
                res = windows.info_dialog_window('Внимание',
                                                 'Открыть окно с новой продажей?')
                logger.debug('res %s' % (res))
                if res == 1:
                    self.ui.dateEdit.setEnabled(True)
                    self.ui.dateEdit.setDate(date.today())
                    self.ui.label_5.setText(str(0))
                    self.ui.label_8.setText(str(7))
                    self.ui.label_8.setText(str(0))
                    self.ui.dateEdit.setDate(date.today())
                    self.ui.comboBox.setEnabled(True)
                    self.ui.checkBox.setEnabled(True)
                    self.ui.pushButton_3.setEnabled(True)
                    self.ui.pushButton_6.setEnabled(True)
                    while (self.ui.tableWidget_2.rowCount() > 0):
                        self.ui.tableWidget_2.removeRow(0)
                else:
                    self.close()
            else:
                logger.info('Оплата не прошла')
                windows.info_window(
                    "Внимание",
                    'Закройте это окно, откройте сохраненную продажу и проведите'
                    'операцию возврата еще раз.', '')
        MainWindow.button_all_sales()

    @logger.catch()
    def sale_return(self):
        """Проводим операцию возврата"""
        logger.info("Inside the function def sale_return")
        logger.info('Обновляем данные продажи')
        self.edit_sale()
        logger.info('Запрашиваем метод оплаты в БД')
        session = Session()
        payment_type_sale = session.query(Sale.payment_type).filter(
            Sale.id == System.sale_id).one()._asdict()
        session.close
        logger.info(payment_type_sale)
        # 1 - безнал, 2 - наличные
        if payment_type_sale.get('payment_type') == 1:
            payment_type = 101
        else:
            payment_type = 102
        logger.info(payment_type)
        state_check, payment = kkt.check_open(System.sale_dict,
                                              payment_type, System.user, 2)
        check = None
        """Если возврат прошел"""
        if state_check == 1:
            if payment == 1:  # если оплата банковской картой
                logger.info("Читаем слип-чек из файла")
                pinpad_file = r"C:\sc552\p"
                with open(pinpad_file, 'r', encoding='IBM866') as file:
                    while (line := file.readline().rstrip()):
                        logger.debug(line)
                check = kkt.read_slip_check()
            # записываем информацию о возврате в БД
            session = Session()
            session.execute(update(Sale).where(
                Sale.id == System.sale_id).values(
                status=2, user_return=System.user[3],
                pc_name=System.pc_name,
                payment_type=payment,
                bank_return=check,
                datetime_return=dt.datetime.now()))
            session.commit()
            session.close()
            self.close()
        else:
            logger.info('Операция возврата завершилась с ошибкой')
            windows.info_window(
                "Внимание",
                'Закройте это окно, откройте сохраненную продажу и проведите'
                'операцию возврата еще раз.', '')

    @logger.catch()
    def generate_saved_tickets(self):
        """Генерируем список с ранее сохраненными билетами"""
        logger.info('Генерируем список с ранее сохраненными билетами')
        logger.info('sate_tickets')
        logger.info(System.sale_tickets)
        client_in_sale = System.sale_tickets
        """Удаляем предыдущий файл с билетами"""
        os.system("TASKKILL /F /IM SumatraPDF.exe")
        if os.path.exists('./ticket.pdf'):  # os.path.isfile ()?
            os.remove('./ticket.pdf')
        # формируем билеты
        otchet.generate_saved_tickets(client_in_sale)
        # печатаем билеты
        subprocess.Popen([r'print.cmd'])
        System.sale_tickets = []

    def open_pay(self, txt):
        """Открываем форму оплаты"""
        logger.info("Inside the function def open_pay")
        pay = PayForm()
        # Передаем текст в форму PayForm
        pay.setText(txt)

        res = pay.exec_()
        # если пользователь нажал крестик или кнопку Escape,
        # то по-умолчанию возвращается QDialog.Rejected
        if res == QDialog.Rejected:
            # наверное, надо ничего не делать в этом случае и
            # просто завершить работу функции
            return
            # или закрыть SaleForm при помощи вызова reject()

        # иначе, если оплата выбрана
        if res == Payment.Card:
            # Оплачено картой
            logger.info('CARD')
            payment_type = Payment.Card
            # запустить оплату по терминалу
            self.sale_transaction(payment_type)
        elif res == Payment.Cash:
            logger.info('CASH')
            payment_type = Payment.Cash
            self.sale_transaction(payment_type)
        # Генерируем чек

        # Закрываем окно продажи и возвращаем QDialog.Accepted
        self.accept()


class Payment:
    """Тип платежа (перечисление)"""
    Card = 101
    Cash = 102


class System:
    """Системная информация"""
    user = None
    # флаг для обновления клиента
    client_id = None
    client_update = None
    all_clients = None
    # статус продажи: 0 - создана, 1 - оплачена, 2 - возвращена
    sale_status = None
    sale_id = None
    sale_discount = None
    sale_tickets = []
    sale_tuple = []
    # какой сегодня день: 0 - будний, 1 - выходной
    what_a_day = None
    # первое воскресенье месяца: 0 - нет, 1 - да
    sunday = None
    today = date.today()
    num_of_week = 0
    pc_name = socket.gethostname()
    # стоимость билетов
    ticket_child_1 = 200
    ticket_child_2 = 400
    ticket_child_3 = 600
    ticket_child_week_1 = 250
    ticket_child_week_2 = 500
    ticket_child_week_3 = 750
    ticket_adult_1 = 100
    ticket_adult_2 = 150
    ticket_adult_3 = 200
    ticket_many_child = 0
    # количество начисляемых талантов
    talent_1 = 25
    talent_2 = 35
    talent_3 = 50
    # информация о РМ
    kol_pc = 0
    pc_1 = ''
    pc_2 = ''
    sale_dict = {'kol_adult': 0, 'price_adult': 0,
                'kol_child': 0, 'price_child': 0,
                'detail': [0, 0, 0, 0, 0, 0, 0, 0]}

    # 'detail': [kol_adult, price_adult, kol_child, price_child, discount, id_adult, time, sum]
    # храним id нового клиента
    id_new_client_in_sale = 0

    def check_login(self, login, password):
        """Авторизация кассира"""
        session = Session()
        kassir = session.query(User.last_name,
                               User.first_name,
                               User.inn,
                               User.id).filter(and_(User.login ==
                                                    login,
                                                    User.password ==
                                                    password)).first()
        session.close
        if kassir:
            # сохраняем данные авторизовавшегося кассира
            System.user = kassir
            return 1

    def check_day(self, day=dt.datetime.now().strftime('%Y-%m-%d')):
        """Проверка статуса дня: выходной ли это"""
        session = Session()
        # текущая дата есть в списке дополнительных рабочих дней?
        check_day = session.query(Workday.date).filter(
            Workday.date == day).first()  # all?
        session.close
        if check_day:
            status = 0
        else:
            # преобразуем текущую дату в список
            day = day.split('-')
            # вычисляем день недели
            num_day = calendar.weekday(int(day[0]), int(day[1]), int(day[2]))
            # день недели 5 или 6
            if num_day >= 5:
                status = 1
                System.what_a_day = 1
            else:
                day = '-'.join(day)
                session = Session()
                # текущая дата есть в списке праздничных дней?
                check_day = session.query(Holiday.date).filter(
                    Holiday.date == day).all()  # all?
                session.close
                if check_day:
                    status = 1
                    System.what_a_day = 1
                else:
                    status = 0
        return status

    def check_one_sunday(self):
        """Проверка 1го воскресного дня месяца"""
        day = 0
        num_of_week = None
        if System.what_a_day == 1:
            # проверяем если номер дня недели равен 7 и дата <= 7
            num_of_week = dt.datetime.today().isoweekday()
            date_num = date.today().day
            if num_of_week == 7 and date_num <= 7:
                logger.info('день многодетных')
                day = 1
                System.sunday = day
        return day, num_of_week


class PayForm(QDialog):
    """Форма оплаты"""
    startGenerate = Signal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_Pay()
        self.ui.setupUi(self)
        # Посылаем сигнал генерации чека
        # self.ui.pushButton.clicked.connect(self.startGenerate.emit)
        # при вызове done() окно должно закрыться и exec_
        # вернет переданный аргумент из done()
        self.ui.pushButton.clicked.connect(lambda: self.done(Payment.Cash))
        self.ui.pushButton_2.clicked.connect(lambda: self.done(Payment.Card))

    def setText(self, txt):
        # Устанавливаем текстовое значение в метку
        self.ui.label_2.setText(txt)


if __name__ == "__main__":
    db = QtSql.QSqlDatabase.addDatabase("QPSQL")
    db.setHostName(f"{host}")
    db.setPort(int(port))
    db.setDatabaseName(f"{database}")
    db.setUserName(f"{user}")
    db.setPassword(f"{pswrd}")

    app = QApplication(sys.argv)
    auth = AuthForm()
    auth.show()

    sys.exit(app.exec_())
