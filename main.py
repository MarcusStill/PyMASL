import calendar
import os
import socket
import subprocess
import sys
from configparser import ConfigParser
from datetime import date, timedelta

import datetime as dt
import psycopg2

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QCheckBox, QDialog, QHBoxLayout, QMainWindow, QTableWidgetItem, QWidget
from PySide6.QtGui import QPixmap
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
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


# Чтение параметров из файла конфигурации
config = ConfigParser()
config.read('config.ini')
host = config.get("DATABASE", "host")
port = config.get("DATABASE", "port")
db = config.get("DATABASE", "database")
user = config.get("DATABASE", "user")
pswrd = config.get("DATABASE", "password")
software_version = config.get("OTHER", "version")
log_file = config.get("OTHER", "log_file")


engine = create_engine("postgresql://postgres:"
                       + pswrd + "@" + host + ":"
                       + port + "/" + db, echo=True)
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
        self.ui.pushButton_4.clicked.connect(self.button_all_client)
        self.ui.tableWidget.doubleClicked.connect(self.search_selected_client)
        self.ui.pushButton_3.clicked.connect(self.search_selected_client)
        self.ui.pushButton.clicked.connect(self.search_client)
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
        # self.ui.pushButton_14.clicked.connect(self.buttonAllTickets)
        self.ui.tableWidget_2.doubleClicked.connect(self.search_selected_sale)

    @logger_wraps()
    def search_client(self):
        """Поиск клиента"""
        logger.info("Inside the function def search_client")
        combo_active_item = self.ui.comboBox.currentText()
        logger.info(combo_active_item)
        if combo_active_item == 'телефон':
            """Очищаем tableWidget"""
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(
                Client.phone.like('%'+self.ui.lineEdit.text()+'%')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(
                    row, 0, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setItem(
                    row, 1, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(
                    row, 2, QTableWidgetItem(f"{client.first_name}"))
                self.ui.tableWidget.setItem(
                    row, 3, QTableWidgetItem(f"{client.middle_name}"))
                self.ui.tableWidget.setItem(
                    row, 4, QTableWidgetItem(f"{client.gender}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.birth_date}"))
                self.ui.tableWidget.setItem(
                    row, 6, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 7, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 8, QTableWidgetItem(f"{client.email}"))
            session.close()
        elif combo_active_item == 'фамилия':
            """Очищаем tableWidget"""
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.last_name.ilike(
                '%'+self.ui.lineEdit.text()+'%')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(
                    row, 0, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setItem(
                    row, 1, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(
                    row, 2, QTableWidgetItem(f"{client.first_name}"))
                self.ui.tableWidget.setItem(
                    row, 3, QTableWidgetItem(f"{client.middle_name}"))
                self.ui.tableWidget.setItem(
                    row, 4, QTableWidgetItem(f"{client.gender}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.birth_date}"))
                self.ui.tableWidget.setItem(
                    row, 6, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 7, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 8, QTableWidgetItem(f"{client.email}"))
            session.close()
        elif combo_active_item == 'имя':
            """Очищаем tableWidget"""
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.first_name.ilike(
                '%'+self.ui.lineEdit.text()+'%')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(
                    row, 0, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setItem(
                    row, 1, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(
                    row, 2, QTableWidgetItem(f"{client.first_name}"))
                self.ui.tableWidget.setItem(
                    row, 3, QTableWidgetItem(f"{client.middle_name}"))
                self.ui.tableWidget.setItem(
                    row, 4, QTableWidgetItem(f"{client.gender}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.birth_date}"))
                self.ui.tableWidget.setItem(
                    row, 6, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 7, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 8, QTableWidgetItem(f"{client.email}"))
            session.close()

    def search_selected_client(self):
        """Поиск выделенной строки в таблице клиентов
         и открытие формы с найденными данными
        """
        logger.info("Inside the function def search_selected_client")
        for idx in self.ui.tableWidget.selectionModel().selectedIndexes():
            """Номер строки найден"""
            row_number = idx.row()
            """Получаем содержимое ячейки"""
            res = self.ui.tableWidget.item(row_number, 0).text()
            session = Session()
            search_client = session.query(Client).filter_by(id=(res)).first()
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
            row_count = self.ui.tableWidget_2.rowCount()
            sale_number = row_count - row_number
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

    @logger_wraps()
    def button_all_client(self):
        """Очищаем tableWidget"""
        logger.info("Inside the function def button_all_client")
        self.ui.tableWidget.setRowCount(0)
        session = Session()
        System.all_clients = session.query(Client).order_by(Client.id)
        for client in System.all_clients:
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)
            self.ui.tableWidget.setItem(
                row, 0, QTableWidgetItem(f"{client.id}"))
            self.ui.tableWidget.setItem(
                row, 1, QTableWidgetItem(f"{client.last_name}"))
            self.ui.tableWidget.setItem(
                row, 2, QTableWidgetItem(f"{client.first_name}"))
            self.ui.tableWidget.setItem(
                row, 3, QTableWidgetItem(f"{client.middle_name}"))
            self.ui.tableWidget.setItem(
                row, 4, QTableWidgetItem(f"{client.gender}"))
            self.ui.tableWidget.setItem(
                row, 5, QTableWidgetItem(f"{client.birth_date}"))
            self.ui.tableWidget.setItem(
                row, 6, QTableWidgetItem(f"{client.privilege}"))
            self.ui.tableWidget.setItem(
                row, 7, QTableWidgetItem(f"{client.phone}"))
            self.ui.tableWidget.setItem(
                row, 8, QTableWidgetItem(f"{client.email}"))
        session.close()

    @logger_wraps()
    def button_all_sales(self):
        """Очищаем tableWidget"""
        logger.info("Inside the function def button_all_sales")
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
                                           filter_day).order_by(desc(Sale.id))
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
                row, 3, QTableWidgetItem(f"{sale.status}"))
            self.ui.tableWidget_2.setItem(
                row, 3, QTableWidgetItem(f"{sale.discount}"))
            self.ui.tableWidget_2.setItem(
                row, 3, QTableWidgetItem(f"{sale.payment_type}"))
            self.ui.tableWidget_2.setItem(
                row, 3, QTableWidgetItem(f"{sale.id_user}"))
            self.ui.tableWidget_2.setItem(
                row, 3, QTableWidgetItem(f"{sale.pc_name}"))
            self.ui.tableWidget_2.setItem(
                row, 3, QTableWidgetItem(f"{sale.datetime}"))
            # self.ui.tableWidget_2.setItem(
            #     row, 3, QTableWidgetItem(f"{sale.datetime_save}"))
        session.close()


class AuthForm(QDialog):
    """Форма авторизации"""
    def __init__(self):
        super().__init__()
        """Проверяем статус соединения с БД"""
        address = "dbname="+db+" user="+user+" host="+host+" password="+pswrd
        try:
            conn = psycopg2.connect(address)
            if conn:
                result = 1
        except:
            logger.warning("Connection was invalidated")
            result = 0
        finally:
            self.ui = Ui_Dialog()
            self.ui.setupUi(self)
            """Добавляем логотип на форму"""
            pixmap = QPixmap('pylogo.png')
            self.ui.label_4.setPixmap(pixmap)
            """Проверяем соединение с БД"""
            if result == 1:
                self.ui.label_3.setText('установлено')
            else:
                self.ui.label_3.setText('ошибка соединения!')
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
            else:
                System.what_a_day = 0
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
        """Выводим в tableWidget новой продажи список всех клиентов"""
        logger.info("Inside the function def button_all_clients_to_sale")
        if System.what_a_day == 1:
            self.ui.dateEdit.setStyleSheet('background-color: red;')
        if self.ui.radioButton_3.isChecked():
            """Очищаем tableWidget"""
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.phone.like(
                '%'+self.ui.lineEdit.text()+'%')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(
                    row, 0, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(
                    row, 1, QTableWidgetItem(f"{client.first_name}"))
                self.ui.tableWidget.setItem(
                    row, 2, QTableWidgetItem(f"{client.middle_name}"))
                self.ui.tableWidget.setItem(
                    row, 3, QTableWidgetItem(f"{client.birth_date}"))
                self.ui.tableWidget.setItem(
                    row, 4, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 6, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(6, True)
            session.close()
        elif self.ui.radioButton.isChecked():
            """Очищаем tableWidget"""
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.last_name.ilike(
                '%' + self.ui.lineEdit.text()+'%')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(
                    row, 0, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(
                    row, 1, QTableWidgetItem(f"{client.first_name}"))
                self.ui.tableWidget.setItem(
                    row, 2, QTableWidgetItem(f"{client.middle_name}"))
                self.ui.tableWidget.setItem(
                    row, 3, QTableWidgetItem(f"{client.birth_date}"))
                self.ui.tableWidget.setItem(
                    row, 4, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 6, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(6, True)
            session.close()
        elif self.ui.radioButton_2.isChecked():
            """Очищаем tableWidget"""
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.first_name.ilike(
                '%' + self.ui.lineEdit.text()+'%')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(
                    row, 0, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(
                    row, 1, QTableWidgetItem(f"{client.first_name}"))
                self.ui.tableWidget.setItem(
                    row, 2, QTableWidgetItem(f"{client.middle_name}"))
                self.ui.tableWidget.setItem(
                    row, 3, QTableWidgetItem(f"{client.birth_date}"))
                self.ui.tableWidget.setItem(
                    row, 4, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 6, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(6, True)
            session.close()

    @logger_wraps()
    def add_client_to_sale(self, *args, **kwargs):
        """Поиск выделенной строки в таблице клиентов
        и передача ее в таблицу заказа
        """
        logger.info("Inside the function def add_client_to_sale")
        # если продажа новая - обновляем статус
        System.sale_status = 0
        logger.warning("status_sale %s" % (System.sale_status))

        for idx in self.ui.tableWidget.selectionModel().selectedIndexes():
            """Номер строки найден"""
            row_number = idx.row()
            """Получаем содержимое ячейки"""
            res = self.ui.tableWidget.item(row_number, 6).text()
            session = Session()
            search_client = session.query(Client).filter_by(id=(res)).first()
            session.close()
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
            time_ticket = self.ui.comboBox.currentText()
            if (int(time_ticket)) == 1:
                price = 200
            elif (int(time_ticket)) == 2:
                price = 400
            else:
                price = 600
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
            """добавляем checkbox"""
            self.ui.tableWidget_2.setCellWidget(row, 7, widget)
            """Передаем в таблицу заказа данные клиента"""
            self.ui.tableWidget_2.setItem(
                row, 0, QTableWidgetItem(f"{search_client.last_name}"))
            self.ui.tableWidget_2.setItem(
                row, 1, QTableWidgetItem(f"{search_client.first_name}"))
            self.ui.tableWidget_2.setItem(
                row, 2, QTableWidgetItem(f"{search_client.middle_name}"))
            self.ui.tableWidget_2.setItem(
                row, 3, QTableWidgetItem(f"{type_ticket}"))
            self.ui.tableWidget_2.setItem(
                row, 4, QTableWidgetItem(f"{price}"))
            self.ui.tableWidget_2.setItem(
                row, 5, QTableWidgetItem(f"{search_client.privilege}"))
            self.ui.tableWidget_2.setItem(
                row, 6, QTableWidgetItem(f"{search_client.id}"))
            self.ui.tableWidget_2.setColumnHidden(6, True)
            self.ui.tableWidget_2.setItem(row, 8, QTableWidgetItem(f"{age}"))
            self.ui.tableWidget_2.setColumnHidden(8, True)
            """Заполняем таблицу с итоговой информацией"""
            self.edit_sale()

    @logger_wraps()
    def key_press_event(self, event):
        """Отслеживаем нажатие кнопок "delete", "backspace" """
        logger.info("Inside the function def key_press_event")
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            self.del_selected_item()
        QDialog.key_press_event(self, event)

    @logger_wraps()
    def del_selected_item(self):
        """Удаляем запись из таблицы при нажатии кнопки в key_press_event"""
        logger.info("Inside the function def del_selected_item")
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
        id_adult = 0
        time_ticket = self.ui.comboBox.currentText()
        sale = 0
        tickets = []
        if (int(time_ticket)) == 1:
            price = 200
            talent = 25
        elif (int(time_ticket)) == 2:
            price = 400
            talent = 35
        elif (int(time_ticket)) == 3:
            price = 600
            talent = 50
        date_time = self.ui.dateEdit.date().toString("yyyy-MM-dd")
        """считаем общую сумму"""
        rows = self.ui.tableWidget_2.rowCount()
        for row in range(rows):
            self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(f"{price}"))
            sale = sale + price
            self.ui.label_8.setText(str(sale))
            """Считаем общее количество позиций и берем цену"""
            type = self.ui.tableWidget_2.item(row, 3).text()
            if type == 'взрослый':
                """Привязываем продажу ко взрослому"""
                if id_adult == 0:
                    id_adult = self.ui.tableWidget_2.item(row, 6).text()
                    logger.warning('id_adult %s' % (id_adult))
                kol_adult += 1
                price_adult = self.ui.tableWidget_2.item(row, 4).text()
            else:
                kol_child += 1
                price_child = self.ui.tableWidget_2.item(row, 4).text()
        self.ui.label_5.setText(str(kol_adult))
        self.ui.label_7.setText(str(kol_child))
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
                            # self.ui.tableWidget_2.item(row, 7).text(),
                            self.ui.tableWidget_2.item(row, 8).text(),
                            time_ticket, talent, date_time))
        System.sale_tuple = sale_tuple
        System.sale_tickets = tickets
        return sale_tuple, tickets

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
                        type = 1
                    logger.info('тип билета %s' % (type))
                    add_ticket = Ticket(id_client=System.sale_tickets[i][6],
                                        id_sale=int(System.sale_id),
                                        arrival_time=System.sale_tickets[i][9],
                                        talent=System.sale_tickets[i][10],
                                        price=System.sale_tickets[i][4],
                                        description=System.sale_tickets[i][5],
                                        ticket_type=type,
                                        print=System.sale_tickets[i][7],
                                        # если печатаем билет
                                        # исправить на checkbox
                                        client_age=System.sale_tickets[i][8])
                    logger.info("Сохраняем билет")
                    logger.info(add_ticket)
                    session.add(add_ticket)
                    session.commit()
                session.close()
                self.close()
            else:
                windows.info_window(
                    'Внимание! В продаже отсутствует взрослый',
                    'Для оформления новой продажи добавьте,'
                    'пожалуйста, в нее взрослого.', '')

    @logger.catch()
    def sale_transaction(self, payment_type):
        """Проводим операцию продажи"""
        logger.info("Inside the function def sale_transaction")
        # state_check = 1
        # payment = 2
        state_check, payment = kkt.check_open(System.sale_tuple,
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
        pay.set_text(txt)

        res = pay.exec_()
        # если пользователь нажал крестик или кнопку Escape,
        # то по-умолчанию возвращается QDialog.Rejected
        if res == QDialog.Rejected:\
        # наверное, надо ничего не делать в этом случае и
        # просто завершить работу функции
            return
            # или закрыть SaleForm при помощи вызова reject()

        # иначе, если оплата выбрана
        if res == PaymentType.ByCard:
            # Оплачено картой
            logger.info('CARD')
            payment_type = PaymentType.ByCard
            # запустить оплату по терминалу
            self.sale_transaction(payment_type)
        elif res == PaymentType.ByCash:
            logger.info('CASH')
            payment_type = PaymentType.ByCash
            self.sale_transaction(payment_type)
        # Генерируем чек

        # Закрываем окно продажи и возвращаем QDialog.Accepted
        self.accept()


# Тип платежа (перечисление)
class PaymentType:
    ByCard = 101
    ByCash = 102


class System:
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
    pc_name = socket.gethostname()

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
        """Проверка статуса дня"""
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


class PayForm(QDialog):
    """Форма оплаты"""
    start_generate = Signal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_Pay()
        self.ui.setupUi(self)
        """Посылаем сигнал генерации чека
        self.ui.pushButton.clicked.connect(self.start_generate.emit)
        при вызове done() окно должно закрыться и exec_
        вернет переданный аргумент из done()
        """
        self.ui.pushButton.clicked.connect(lambda:
                                           self.done(PaymentType.ByCash))
        self.ui.pushButton_2.clicked.connect(lambda:
                                             self.done(PaymentType.ByCard))
        # Устанавливаем текстовое значение в метку

    def set_text(self, txt):
        self.ui.label_2.setText(txt)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    auth = AuthForm()
    auth.show()

    sys.exit(app.exec_())
