import calendar
import os
import socket
import subprocess
import sys
import time
from configparser import ConfigParser
from datetime import date, timedelta
from time import sleep

import datetime as dt
import psycopg2
from PySide6 import QtCore, QtGui, QtWidgets, QtSql
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QCheckBox, QDialog, QHBoxLayout, QMainWindow, QTableWidgetItem, QWidget
from PySide6.QtGui import QPixmap
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from sqlalchemy import create_engine, and_, desc, update
from sqlalchemy.orm import sessionmaker

from db.models import Client
from db.models import Holiday
from db.models import Sale
from db.models import Ticket
from db.models import Workday
from db.models.user import User
from files.logger import *
from files import kkt
from files import windows
from forms.authorization import Ui_Dialog
from forms.client import Ui_Dialog_Client
from forms.main_form import Ui_MainWindow
from forms.pay import Ui_Dialog_Pay
from forms.sale import Ui_Dialog_Sale
# from forms.sale_saved import Ui_Dialog_Sale


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
        self.ui.pushButton_6.clicked.connect(kkt.smena_close(System.user))
        self.ui.pushButton_7.clicked.connect(kkt.get_status_obmena)
        self.ui.pushButton_15.clicked.connect(kkt.continue_print)
        self.ui.pushButton_10.clicked.connect(kkt.smena_info)
        self.ui.pushButton_16.clicked.connect(kkt.terminal_check_itog_window)
        self.ui.pushButton_12.clicked.connect(self.open_sale)
        self.ui.pushButton_13.clicked.connect(self.button_all_sales)
        self.ui.tableWidget_2.doubleClicked.connect(self.search_selected_sale)
        self.ui.pushButton_17.clicked.connect(self.statistic_ticket)
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
        self.ui.comboBox_2.clear()
        for i in range(self.model.columnCount()):
            self.ui.comboBox_2.addItem(self.model.headerData(i, type_col))
        self.ui.lineEdit_2.textChanged.connect(self.filter_table_client)
        headers_view = ["N", "Фамилия", "Имя", "Отчество", "Дата рожд.", "Пол", "Телефон", "Email", "Категория"]
        for i in range(len(headers_view)):
            self.model.setHeaderData(i, Qt.Horizontal, headers_view[i])

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
            # ! bug отображение сохраненной продажи + добавить новую форму для них
            # запрашиваем статус продажи
            sale_status = (session.query(Sale.status).filter(
                Sale.id == sale_number).one())._asdict()
            """Передаем в форму данные клиента"""
            sale = SaleForm()
            # для уже созданных продаж отключаем модель к таблице клиентов
            self.model_clear = QtSql.QSqlTableModel()
            # self.ui.tableView.setModel(self.model_clear)
            sale.ui.tableView_2.setModel(self.model_clear)
            sale.ui.tableWidget_2.setRowCount(0)
            sale.ui.dateEdit.setDate(client_in_sale[0][11])
            sale.ui.dateEdit.setEnabled(False)
            sale.ui.comboBox.setCurrentText(str(client_in_sale[0][9]))
            sale.ui.comboBox.setEnabled(False)
            sale.ui.checkBox.setEnabled(False)
            if sale_status.get('status') == 1:
                sale.ui.pushButton_3.setEnabled(False)
                sale.ui.pushButton_5.setEnabled(False)
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
            # res.append(client_in_sale)
            sale.ui.label_5.setText(str(kol_adult))
            sale.ui.label_7.setText(str(kol_child))
            sale.ui.label_8.setText(str(sum))
            # SaleForm.edit_sale(self)
            sale.show()
            # передаем сведения о сохраненной продаже
            System.sale_status = 1
            logger.warning("System.sale_status %s" % (System.sale_status))
            System.sale_id = sale_number
            # System.sale_tickets = res[0]
            System.sale_tickets = client_in_sale
            # logger.info(res[0][0])
            # logger.warning("System.sale_id %s" % (System.sale_id))
            logger.warning('selected sale')
            logger.debug(System.sale_tickets)
            sale.exec_()

    @logger_wraps()
    def button_all_sales(self):
        """Показ всех продаж в tableWidget"""
        logger.info("Inside the function def button_all_sales")
        type = None
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
        session = Session()
        sales = session.query(Sale).filter(Sale.datetime >=
                                           filter_day).order_by(Sale.id)
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
                type = 'создана'
            if sale.status == 1:
                type = 'оплачена'
            self.ui.tableWidget_2.setItem(
                row, 4, QTableWidgetItem(f"{type}"))
            self.ui.tableWidget_2.setItem(
                row, 5, QTableWidgetItem(f"{sale.discount}"))
            self.ui.tableWidget_2.setItem(
                row, 6, QTableWidgetItem(f"{sale.pc_name}"))
            if sale.payment_type == 1:
                type = 'карта'
            if sale.payment_type == 2:
                type = 'наличные'
            else:
                type = '-'
            self.ui.tableWidget_2.setItem(
                row, 7, QTableWidgetItem(f"{type}"))
            # self.ui.tableWidget_2.setItem(
            #     row, 8, QTableWidgetItem(f"{sale.datetime}"))
            # self.ui.tableWidget_2.setItem(
            #     row, 3, QTableWidgetItem(f"{sale.datetime_save}"))
        session.close()

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
        # sale.button_all_clients_to_sale()  # показываем список всех клиентов
        sale.show()
        sale.exec_()

    def statistic_ticket(self):
        logger.info("Inside the function def statistic_ticket")
        # считаем выручку
        start_time = ' 00:00:00'
        end_time = ' 23:59:59'
        dt1 = self.ui.dateEdit_2.date().toString("yyyy-MM-dd") + start_time
        dt2 = self.ui.dateEdit.date().toString("yyyy-MM-dd") + end_time
        session = Session()
        sales = session.query(Sale.pc_name, Sale.payment_type, Sale.price).filter(Sale.datetime.between(dt1, dt2)).all()
        session.close()
        logger.info('sales')
        logger.info(sales)
        pc_1 = {'Name PC': 'prog20-note', 'sum_card': 0, 'sum_cashe': 0}
        pc_2 = {'Name PC': 'prog20-note1', 'sum_card': 0, 'sum_cashe': 0}
        type = [1, 2]
        for i in range(len(sales)):
            if sales[i][0] in pc_1.values():
                if sales[i][1] == type[1]:
                    pc_1['sum_card'] += sales[i][2]
                else:
                    pc_1['sum_cashe'] += sales[i][2]
            else:
                if sales[i][1] == type[1]:
                    pc_2['sum_card'] += sales[i][2]
                else:
                    pc_2['sum_cashe'] += sales[i][2]
        logger.info('pc_1')
        logger.debug(pc_1)
        logger.info('pc_2')
        logger.debug(pc_2)
        card = int(pc_1['sum_card']) + int(pc_2['sum_card'])
        cashe = int(pc_1['sum_cashe']) + int(pc_2['sum_cashe'])
        sum = card + cashe
        self.ui.tableWidget_4.setRowCount(0)
        self.ui.tableWidget_4.insertRow(0)
        self.ui.tableWidget_4.setItem(0, 0, QTableWidgetItem(f"{pc_1['Name PC']}"))
        self.ui.tableWidget_4.setItem(0, 1, QTableWidgetItem(f"{pc_1['sum_card']}"))
        self.ui.tableWidget_4.setItem(0, 2, QTableWidgetItem(f"{pc_1['sum_cashe']}"))
        self.ui.tableWidget_4.insertRow(1)
        self.ui.tableWidget_4.setItem(1, 0, QTableWidgetItem(pc_2['Name PC']))
        self.ui.tableWidget_4.setItem(1, 1, QTableWidgetItem(f"{pc_2['sum_card']}"))
        self.ui.tableWidget_4.setItem(1, 2, QTableWidgetItem(f"{pc_2['sum_cashe']}"))
        self.ui.tableWidget_4.insertRow(2)
        self.ui.tableWidget_4.setItem(2, 0, QTableWidgetItem(f"Итого"))
        self.ui.tableWidget_4.setItem(2, 1, QTableWidgetItem(f"{card}"))
        self.ui.tableWidget_4.setItem(2, 2, QTableWidgetItem(f"{cashe}"))
        self.ui.tableWidget_4.setItem(2, 3, QTableWidgetItem(f"{sum}"))

        # считаем билеты
        session = Session()
        tickets = session.query(Ticket.ticket_type, Ticket.arrival_time, Ticket.description).filter(
            Ticket.datetime.between(dt1, dt2)).all()
        session.close()
        logger.info('tickets')
        logger.info(tickets)
        logger.debug((len(tickets)))
        type_tickets = [0, 1]
        time_arrival = [1, 2, 3]
        child = {'sum': 0, 't_1': 0, 't_2': 0, 't_3': 0}
        adult = {'sum': 0, 't_1': 0, 't_2': 0, 't_3': 0}
        for i in range(len(tickets)):
            if tickets[i][0] == type_tickets[0]:
                adult['sum'] += 1
                if tickets[i][1] == time_arrival[0]:
                    adult['t_1'] += 1
                elif tickets[i][1] == time_arrival[1]:
                    adult['t_2'] += 1
                elif tickets[i][1] == time_arrival[2]:
                    adult['t_3'] += 1
            elif tickets[i][0] == type_tickets[1]:
                child['sum'] += 1
                if tickets[i][1] == time_arrival[0]:
                    child['t_1'] += 1
                elif tickets[i][1] == time_arrival[1]:
                    child['t_2'] += 1
                elif tickets[i][1] == time_arrival[2]:
                    child['t_3'] += 1
        self.ui.tableWidget_3.setRowCount(0)
        self.ui.tableWidget_3.insertRow(0)
        self.ui.tableWidget_3.setItem(0, 0, QTableWidgetItem('взрослый'))
        self.ui.tableWidget_3.setItem(0, 1, QTableWidgetItem(f"{adult['sum']}"))
        self.ui.tableWidget_3.setItem(0, 2, QTableWidgetItem(f"{adult['t_1']}"))
        self.ui.tableWidget_3.setItem(0, 3, QTableWidgetItem(f"{adult['t_2']}"))
        self.ui.tableWidget_3.setItem(0, 4, QTableWidgetItem(f"{adult['t_3']}"))
        self.ui.tableWidget_3.insertRow(1)
        self.ui.tableWidget_3.setItem(1, 0, QTableWidgetItem('детский'))
        self.ui.tableWidget_3.setItem(1, 1, QTableWidgetItem(f"{child['sum']}"))
        self.ui.tableWidget_3.setItem(1, 2, QTableWidgetItem(f"{child['t_1']}"))
        self.ui.tableWidget_3.setItem(1, 3, QTableWidgetItem(f"{child['t_2']}"))
        self.ui.tableWidget_3.setItem(1, 4, QTableWidgetItem(f"{child['t_3']}"))

    def otchet_kassira(self):
        """Формирование отчета кассира"""
        pass
        # """Удаляем предыдущий файл"""
        # os.system("TASKKILL /F /IM SumatraPDF.exe")
        # if os.path.exists('./otchet.pdf'):  # os.path.isfile ()?
        #     os.remove('./otchet.pdf')

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
            # отображаем всех клиентов при запуске
            window.button_all_sales()
            # window.buttonAllClient()
            # проверяем статус текущего дня
            day_today = System.check_day(self)
            logger.info('day_today %s' % (day_today))
            if day_today == 0:
                System.what_a_day = 0
            elif day_today == 1:
                System.what_a_day = 1
                sun = System.check_one_sunday(self)
                System.sunday = sun
            else:
                System.what_a_day = 0  # надо ли??
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
        self.ui.pushButton_2.clicked.connect(lambda: MainWindow.open_client(self))
        self.ui.pushButton_3.clicked.connect(self.sale_save)
        self.ui.pushButton_4.clicked.connect(self.close)
        self.ui.pushButton_5.clicked.connect(lambda: self.open_pay(self.ui.label_8.text()))
        self.ui.pushButton_6.clicked.connect(self.sale_return)
        self.ui.pushButton_7.clicked.connect(self.generate_saved_tickets)
        self.ui.tableView_2.clicked.connect(self.add_client_to_sale)
        cur_today = date.today()
        self.ui.dateEdit.setDate(cur_today)
        self.ui.dateEdit.dateChanged.connect(self.calendar_color_change)
        self.ui.comboBox.currentTextChanged.connect(self.edit_sale)
        self.ui.checkBox_2.stateChanged.connect(self.check_sale_enabled)
        self.ui.comboBox_2.currentTextChanged.connect(self.edit_sale)
        self.ui.tableWidget_2.clicked.connect(self.edit_sale)
        # tableView с клиентами
        self.model_3 = QtSql.QSqlTableModel()
        self.ui.tableView_2.setModel(self.model_3)
        self.model_3.setTable("client")
        self.model_3.select()
        # фильтр для tableView
        type_col = QtCore.Qt.Horizontal
        self.ui.comboBox_3.clear()
        for i in range(self.model_3.columnCount()):
            self.ui.comboBox_3.addItem(self.model_3.headerData(i, type_col))
        self.ui.lineEdit.textChanged.connect(self.filter_sale_client)
        # устанавливаем заголовки столбцов для tableView
        headers_view = ["N", "Фамилия", "Имя", "Отчество", "Дата рожд.", "Пол", "Телефон", "Email", "Категория"]
        for i in range(len(headers_view)):
            self.model_3.setHeaderData(i, Qt.Horizontal, headers_view[i])
        # при открытии проверяем день недели
        self.calendar_color_change()
        self.ui.checkBox_3.setEnabled(False)

    def filter_sale_client(self, text):
        filter = (" {} LIKE '%{}%'".format(self.ui.comboBox_3.currentText(),
                                           text) if text else text)
        self.model_3.setFilter(filter)

    def calendar_color_change(self):
        logger.info("Inside the function def calendar_color_change")
        logger.warning(self.ui.dateEdit.date())
        date = str(self.ui.dateEdit.date())
        date_slice = date[21:(len(date)-1)]
        logger.debug(date_slice)
        date = date_slice.replace(', ', '-')
        logger.debug(date)
        if System.check_day(self, date) == 1:
            self.ui.dateEdit.setStyleSheet('background-color: red;')
            System.what_a_day = 1
            logger.debug(self.ui.dateEdit.date)
        else:
            self.ui.dateEdit.setStyleSheet('background-color: white;')
            System.what_a_day = 0
            logger.debug(self.ui.dateEdit.date)
        self.edit_sale()
        System.check_day(self)

    def check_sale_enabled(self):
        logger.info("Inside the function def check_sale_enabled")
        if self.ui.checkBox_2.isChecked():
            self.ui.comboBox_2.setEnabled(True)
        else:
            self.ui.comboBox_2.setEnabled(False)

    @logger_wraps()
    def add_client_to_sale(self, *args, **kwargs):
        """Поиск выделенной строки в таблице клиентов
        и передача ее в таблицу заказа
        """
        logger.info("Inside the function def add_client_to_sale")
        # если продажа новая - обновляем статус
        System.sale_status = 0
        logger.warning("status_sale %s" % (System.sale_status))
        """Поиск строки и ячейки"""
        index = (self.ui.tableView_2.selectionModel().currentIndex())
        # ! исправить передавать в index всегда первый столбец
        value = index.sibling(index.row(), index.column()).data()
        if type(value) == int:
            session = Session()
            search_client = session.query(Client).filter_by(id=(value)).first()
            session.close()
            """Вычисляем возраст клиента"""
            today = date.today()
            age = today.year - (search_client.birth_date.year -
                                ((today.month, today.day) < (search_client.birth_date.month,
                                                             search_client.birth_date.day)))
            """Определяем тип билета и цену"""
            if 5 <= age < 14:
                type_ticket = 'детский'
            elif age >= 14:
                type_ticket = 'взрослый'
            """Определяем тип билета и цену"""
            time_ticket = self.ui.comboBox.currentText()
            if (int(time_ticket)) == 1:
                if type_ticket == 'детский':
                    price = System.ticket_child_1
                else:
                    price = System.ticket_adult_1
            elif (int(time_ticket)) == 2:
                if type_ticket == 'детский':
                    price = System.ticket_child_2
                else:
                    price = System.ticket_adult_2
            else:
                if type_ticket == 'детский':
                    price = System.ticket_child_3
                else:
                    price = System.ticket_adult_3
            """Создаем виджет checkbox"""
            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Checked)
            layoutH = QHBoxLayout(widget)
            layoutH.addWidget(checkbox)
            layoutH.setAlignment(Qt.AlignCenter)
            layoutH.setContentsMargins(0, 0, 0, 0)
            row = self.ui.tableWidget_2.rowCount()
            self.ui.tableWidget_2.insertRow(row)
            """Передаем в таблицу заказа данные клиента"""
            self.ui.tableWidget_2.setItem(row, 0, QTableWidgetItem(f"{search_client.last_name}"))
            self.ui.tableWidget_2.setItem(row, 1, QTableWidgetItem(f"{search_client.first_name}"))
            self.ui.tableWidget_2.setItem(row, 2, QTableWidgetItem(f"{search_client.middle_name}"))
            self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{type_ticket}"))
            self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(f"{price}"))
            self.ui.tableWidget_2.setItem(row, 5, QTableWidgetItem(f"{search_client.privilege}"))
            self.ui.tableWidget_2.setItem(row, 6, QTableWidgetItem(f"{search_client.id}"))
            # self.ui.tableWidget_2.setColumnHidden(6, True)
            """добавляем checkbox"""
            self.ui.tableWidget_2.setCellWidget(row, 7, widget)
            self.ui.tableWidget_2.setItem(row, 8, QTableWidgetItem(f"{age}"))
            # self.ui.tableWidget_2.setColumnHidden(8, True)
            """Заполняем таблицу с итоговой информацией"""
            self.edit_sale()

    @logger_wraps()
    def keyPressEvent(self, event):  # don`t fix this
        """Отслеживаем нажатие кнопок "delete", "backspace" """
        logger.info("Inside the function def keyPressEvent")
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            self.del_selected_item()
        QDialog.keyPressEvent(self, event)

    @logger_wraps()
    def del_selected_item(self):
        """Удаляем запись из таблицы при нажатии кнопки в key_press_event"""
        logger.info("Inside the function def del_selected_item")
        logger.warning('press key')
        if self.ui.tableWidget_2.rowCount() > 0:
            currentrow = self.ui.tableWidget_2.currentRow()
            self.ui.tableWidget_2.removeRow(currentrow)
            self.edit_sale()

    def edit_sale(self):
        """Обновляем таблицу заказа и генерируем информацию
        о продаже и список билетов
        """
        logger.info("Inside the function def edit_sale")
        kol_adult = 0
        kol_child = 0
        price_adult = 0
        price_child = 0
        kol_adult_many_child = 0
        kol_child_many_child = 0
        id_adult = 0
        time = 0
        time_ticket = self.ui.comboBox.currentText()
        sale = 0
        tickets = []
        many_child = 0
        if (int(time_ticket)) == 1:
            time = 1
            talent = System.talent_1
        elif (int(time_ticket)) == 2:
            time = 2
            talent = System.talent_2
        elif (int(time_ticket)) == 3:
            time = 3
            talent = System.talent_3
        date_time = self.ui.dateEdit.date().toString("yyyy-MM-dd")
        """считаем общую сумму"""
        rows = self.ui.tableWidget_2.rowCount()
        for row in range(rows):
            print('flag', self.ui.tableWidget_2.item(row, 5).text())
            # if self.ui.tableWidget_2.item(row, 5).text() == 'м':
            #     print('yes')
            """Акция день многодетных?"""
            print('system day', System.sunday)
            if self.ui.tableWidget_2.item(row, 5).text() == 'м':
                if System.sunday == 1:
                    many_child = 1
                    # устанавливаем продолжительность посещения
                    self.ui.comboBox.setCurrentIndex(1)
                    self.ui.comboBox.setEnabled(False)
                    # отмена скидки многодетным
                    self.ui.checkBox_3.setEnabled(True)  # ! добавить логику
                    self.ui.checkBox_2.setEnabled(False)
                    logger.info('многодетный')
            """Считаем общее количество позиций и берем цену"""
            type = self.ui.tableWidget_2.item(row, 3).text()
            if type == 'взрослый':
                """Привязываем продажу ко взрослому"""
                if time == 1:
                    price = System.ticket_adult_1
                elif time == 2:
                    if many_child == 0:
                        if System.what_a_day == 0:
                            price = System.ticket_adult_2
                    else:
                        price = System.ticket_many_child
                        kol_adult_many_child += 1
                else:
                    price = System.ticket_adult_3
                if id_adult == 0:
                    id_adult = self.ui.tableWidget_2.item(row, 6).text()
                    logger.warning('id_adult %s' % (id_adult))
                kol_adult += 1
                price_adult = self.ui.tableWidget_2.item(row, 4).text()
            else:
                if time == 1:
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
                    else:
                        price = System.ticket_many_child
                        kol_child_many_child += 1
                else:
                    if System.what_a_day == 0:
                        price = System.ticket_child_3
                    else:
                        price = System.ticket_child_week_3
                kol_child += 1
                price_child = self.ui.tableWidget_2.item(row, 4).text()
            self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(f"{price}"))
            sale = sale + price
            self.ui.label_8.setText(str(sale))
        self.ui.label_5.setText(str(kol_adult))
        self.ui.label_7.setText(str(kol_child))
        self.ui.label_17.setText(str(kol_adult_many_child))
        self.ui.label_19.setText(str(kol_child_many_child))
        """проверить есть ли взрослый"""
        # !
        """применяем скидку"""
        System.sale_discount = sale/100 * int(self.ui.comboBox_2.currentText())
        if sale >= 0:
            # new_price = sale - (sale/100 * System.sale_discount)
            new_price = sale - System.sale_discount
            new_price = int(new_price)
            self.ui.label_8.setText(str(new_price))
        """Сохраняем данные продажи"""
        sale_tuple = (kol_adult, int(price_adult), kol_child,
                      int(price_child), int(new_price), id_adult,
                      System.sale_discount)
        logger.warning('sale_tuple')
        logger.warning(sale_tuple)
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
                            self.ui.tableWidget_2.item(row, 8).text(),
                            time_ticket, talent, date_time))
        System.sale_tuple = sale_tuple
        logger.info('System.sale_tuple')
        logger.info(System.sale_tuple)
        System.sale_tickets = tickets
        logger.info('System.sale_tickets')
        logger.info(System.sale_tickets)
        # return sale_tuple, tickets

    def sale_save(self):
        """Сохраняем данные заказа"""
        logger.info("Inside the function def sale_save")
        # sale_tuple, tickets = self.edit_sale()
        logger.info('sale_tuple')
        logger.info(System.sale_tuple)
        if System.sale_status == 0:
            if System.sale_tuple[0] == 1:
                add_sale = Sale(price=int(self.ui.label_8.text()),
                                id_user=System.user[3],
                                id_client=System.sale_tuple[5],
                                status=0,
                                discount=int(self.ui.comboBox_2.currentText()),
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

                # self.close()
            else:
                windows.info_window(
                    'Внимание! В продаже отсутствует взрослый',
                    'Для оформления новой продажи добавьте,'
                    'пожалуйста, в нее взрослого.', '')
        """Генерируем билеты"""
        logger.info("Генерируем билеты")
        logger.debug(System.sale_tickets)
        session = Session()
        for i in range(len(System.sale_tickets)):
            type = 0
            """Считаем количество начисленных талантов"""
            if System.sale_tickets[i][3] == 'взрослый':
                type = 0
            elif System.sale_tickets[i][3] == 'детский':
                type = '1'
            logger.info('тип билета %s' % (type))
            add_ticket = Ticket(id_client=System.sale_tickets[i][6],
                                id_sale=int(System.sale_id),
                                arrival_time=System.sale_tickets[i][9],
                                talent=System.sale_tickets[i][10],
                                price=System.sale_tickets[i][4],
                                description=System.sale_tickets[i][5],
                                ticket_type=type,
                                # print=System.sale_tickets[i][7],
                                # если печатаем билет
                                # исправить на checkbox
                                client_age=System.sale_tickets[i][8])
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
        state_check = 1
        payment = 2
        # state_check, payment = kkt.check_open(System.sale_tuple,
        #                                       payment_type, System.user, 1)
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

    @logger.catch()
    def sale_return(self):
        """Проводим операцию возврата"""
        logger.info("Inside the function def sale_return")
        payment_type = None
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
        state_check, payment = kkt.check_open(System.sale_tuple,
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
        """Устанавливаем параметры макета билета"""
        pdfmetrics.registerFont(TTFont('DejaVuSerif', 'files/DejaVuSerif.ttf'))
        c = canvas.Canvas("ticket.pdf", pagesize=(21 * cm, 8 * cm))
        c.setFont('DejaVuSerif', 12)
        """Сохраняем билеты"""
        logger.info(len(client_in_sale))
        for i in range(len(client_in_sale)):
            logger.info(client_in_sale[i])
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
        if res == Payment.ByCard:
            # Оплачено картой
            logger.info('CARD')
            payment_type = Payment.ByCard
            # запустить оплату по терминалу
            self.sale_transaction(payment_type)
        elif res == Payment.ByCash:
            logger.info('CASH')
            payment_type = Payment.ByCash
            self.sale_transaction(payment_type)
        # Генерируем чек

        # Закрываем окно продажи и возвращаем QDialog.Accepted
        self.accept()


class Payment:
    """Тип платежа (перечисление)"""
    ByCard = 101
    ByCash = 102


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
    pc_name = socket.gethostname()
    # цена билетов
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
    # количество талантов
    talent_1 = 25
    talent_2 = 35
    talent_3 = 50

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
        status = None
        num_day = None
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
        if System.what_a_day == 1:
            # проверяем если номер дня недели равен 7 и дата <= 7
            if dt.datetime.today().isoweekday() == 7 and date.today().day <= 7:
                print('mnogodet!')
                System.sunday = 1
                return 1


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
        self.ui.pushButton.clicked.connect(lambda: self.done(Payment.ByCash))
        self.ui.pushButton_2.clicked.connect(lambda: self.done(Payment.ByCard))

        # Устанавливаем текстовое значение в метку
    def setText(self, txt):
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
