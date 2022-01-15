from datetime import date
import time as t
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QCheckBox, QWidget, QMessageBox
from PySide6.QtCore import Qt, Signal
from forms.authorization import Ui_Dialog
from forms.main_form import Ui_MainWindow
from forms.client import Ui_Dialog_Client
from forms.sale import Ui_Dialog_Sale
from forms.pay import Ui_Dialog_Pay
from models.client import Client
from models.user import User
from models.sale import Sale
from models.ticket import Ticket
from sqlalchemy import create_engine, and_, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import kkt
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from configparser import ConfigParser
from logger import *
import psycopg2
import windows


#Чтение параметров из файла конфигурации
config = ConfigParser()
config.read("config.ini")
host = config.get("DATABASE", "host")
port = config.get("DATABASE", "port")
database = config.get("DATABASE", "database")
user = config.get("DATABASE", "user")
password = config.get("DATABASE", "password")
software_version = config.get("OTHER", "version")
log_file = config.get("OTHER", "log_file")


engine = create_engine("postgresql://postgres:" + password + "@" + host + ":" + port + "/" + database, echo=True)


Base = declarative_base(bind=engine)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


logger.add(log_file)


class MainWindow(QMainWindow):
    """Главная форма"""
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(self)
        """Открыть окно добавления нового клиента"""
        self.ui.pushButton_2.clicked.connect(self.openClient)
        """Отображение всех клиентов"""
        self.ui.pushButton_4.clicked.connect(self.buttonAllClient)
        self.ui.tableWidget.doubleClicked.connect(self.search_selected_client)
        self.ui.pushButton_3.clicked.connect(self.search_selected_client)
        self.ui.pushButton.clicked.connect(self.search_client)
        self.ui.pushButton_8.clicked.connect(kkt.get_info)
        self.ui.pushButton_11.clicked.connect(kkt.last_document)
        self.ui.pushButton_9.clicked.connect(kkt.get_time)
        self.ui.pushButton_5.clicked.connect(kkt.report_x)
        self.ui.pushButton_6.clicked.connect(kkt.smena_close)
        self.ui.pushButton_7.clicked.connect(kkt.get_status_obmena)
        self.ui.pushButton_15.clicked.connect(kkt.continue_print)
        self.ui.pushButton_10.clicked.connect(kkt.smena_info)
        self.ui.pushButton_16.clicked.connect(kkt.terminal_check_itog_in_window)
        self.ui.pushButton_12.clicked.connect(self.openSale)
        self.ui.pushButton_13.clicked.connect(self.buttonAllSales)
        self.ui.pushButton_14.clicked.connect(self.buttonAllTickets)
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
            search = session.query(Client).filter(Client.phone.like('%'+self.ui.lineEdit.text()+'%')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(f"{client.first_name}"))
                self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(f"{client.middle_name}"))
                self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(f"{client.gender}"))
                self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(f"{client.birth_date}"))
                self.ui.tableWidget.setItem(row, 6, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(row, 7, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(row, 8, QTableWidgetItem(f"{client.email}"))
            session.close()
        elif combo_active_item == 'фамилия':
            """Очищаем tableWidget"""
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.last_name.ilike('%'+self.ui.lineEdit.text()+'%')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(f"{client.first_name}"))
                self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(f"{client.middle_name}"))
                self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(f"{client.gender}"))
                self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(f"{client.birth_date}"))
                self.ui.tableWidget.setItem(row, 6, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(row, 7, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(row, 8, QTableWidgetItem(f"{client.email}"))
            session.close()
        elif combo_active_item == 'имя':
            """Очищаем tableWidget"""
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.first_name.ilike('%'+self.ui.lineEdit.text()+'%')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(f"{client.first_name}"))
                self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(f"{client.middle_name}"))
                self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(f"{client.gender}"))
                self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(f"{client.birth_date}"))
                self.ui.tableWidget.setItem(row, 6, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(row, 7, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(row, 8, QTableWidgetItem(f"{client.email}"))
            session.close()


    @logger_wraps()
    def search_selected_client(self):
        """Поиск выделенной строки в таблице клиентов и открытие формы с найденными данными"""
        logger.info("Inside the function def search_selected_client")
        for idx in self.ui.tableWidget.selectionModel().selectedIndexes():
            """Номер строки найден"""
            row_number = idx.row()
            session = Session()
            search_client = session.query(Client).filter_by(id=(row_number+1)).first()
            """Передаем в форму данные клиента"""
            client = ClientForm()
            client.ui.lineEdit.setText(search_client.last_name)
            client.ui.lineEdit_2.setText(search_client.first_name)
            client.ui.lineEdit_3.setText(search_client.middle_name)
            client.ui.dateEdit.setDate(search_client.birth_date)
            """Поиск значения для установки в ComboBox gender"""
            index_gender = client.ui.comboBox.findText(search_client.gender, Qt.MatchFixedString)
            if index_gender >= 0:
                client.ui.comboBox.setCurrentIndex(index_gender)
            client.ui.lineEdit_4.setText(search_client.phone)
            client.ui.lineEdit_5.setText(search_client.email)
            """Поиск значения для установки в ComboBox privilege"""
            index_privilege = client.ui.comboBox.findText(search_client.privilege, Qt.MatchFixedString)
            if index_privilege >= 0:
                client.ui.comboBox_2.setCurrentIndex(index_privilege)
            """bug Запись сохраняется с новым id"""
            client.ui.pushButton.clicked.connect(client.buttonSave)
            session.close()
            client.show()
            client.exec_()


    @logger_wraps()
    def search_selected_sale(self):
        """Поиск выделенной строки в таблице продаж и открытие формы с найденными данными"""
        logger.info("Inside the function def search_client")
        for idx in self.ui.tableWidget_2.selectionModel().selectedIndexes():
            """Номер строки найден"""
            row_number = idx.row()
            session = Session()
            search_sale = session.query(Sale).filter_by(id=(row_number+1)).first()
            logger.info(search_sale)
            session.close()
        #search_sale = "WITH client_in_sale AS(SELECT * from client join ticket on client.id = ticket.id_client) SELECT * from client_in_sale WHERE id_sale = search_sale[0]"


    @logger_wraps()
    def openClient(self):
        """Открываем форму с данными клиента"""
        logger.info("Inside the function def openClient")
        client = ClientForm()
        client.show()
        client.exec_()


    @logger_wraps()
    def openSale(self):
        """Открываем форму с продажей"""
        logger.info("Inside the function def openSale")
        sale = SaleForm()
        sale.button_all_clients_to_sale()
        sale.show()
        sale.exec_()


    @logger_wraps()
    def buttonAllClient(self):
        """Очищаем tableWidget"""
        logger.info("Inside the function def buttonAllClient")
        self.ui.tableWidget.setRowCount(0)
        session = Session()
        clients = session.query(Client).order_by(Client.id)
        for client in clients:
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)
            # !убрать id из таблицы
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(f"{client.id}"))
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(f"{client.last_name}"))
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(f"{client.first_name}"))
            self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(f"{client.middle_name}"))
            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(f"{client.gender}"))
            self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(f"{client.birth_date}"))
            self.ui.tableWidget.setItem(row, 6, QTableWidgetItem(f"{client.privilege}"))
            self.ui.tableWidget.setItem(row, 7, QTableWidgetItem(f"{client.phone}"))
            self.ui.tableWidget.setItem(row, 8, QTableWidgetItem(f"{client.email}"))
        session.close()


    @logger_wraps()
    def buttonAllSales(self):
        """Очищаем tableWidget"""
        logger.info("Inside the function def buttonAllSales")
        self.ui.tableWidget_2.setRowCount(0)
        session = Session()
        sales = session.query(Sale).order_by(Sale.id)
        for sale in sales:
            row = self.ui.tableWidget_2.rowCount()
            self.ui.tableWidget_2.insertRow(row)
            self.ui.tableWidget_2.setItem(row, 0, QTableWidgetItem(f"{sale.id}"))
            self.ui.tableWidget_2.setItem(row, 1, QTableWidgetItem(f"{sale.id_client}"))
            self.ui.tableWidget_2.setItem(row, 2, QTableWidgetItem(f"{sale.price}"))
            self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{sale.datetime}"))
        session.close()


    # !нужно ли?
    @logger_wraps()
    def buttonAllTickets(self):
        """Очищаем tableWidget"""
        logger.info("Inside the function def buttonAllTickets")
        self.ui.tableWidget_3.setRowCount(0)
        session = Session()
        tickets = session.query(Ticket).order_by(Ticket.id)
        for ticket in tickets:
            row = self.ui.tableWidget_3.rowCount()
            self.ui.tableWidget_3.insertRow(row)
            self.ui.tableWidget_3.setItem(row, 0, QTableWidgetItem(f"{ticket.id}"))
            self.ui.tableWidget_3.setItem(row, 1, QTableWidgetItem(f"{ticket.id_client}"))
            self.ui.tableWidget_3.setItem(row, 2, QTableWidgetItem(f"{ticket.id_sale}"))
            self.ui.tableWidget_3.setItem(row, 3, QTableWidgetItem(f"{ticket.client_age}"))
            self.ui.tableWidget_3.setItem(row, 4, QTableWidgetItem(f"{ticket.datetime}"))
            self.ui.tableWidget_3.setItem(row, 5, QTableWidgetItem(f"{ticket.arrival_time}"))
            self.ui.tableWidget_3.setItem(row, 6, QTableWidgetItem(f"{ticket.talent}"))
            self.ui.tableWidget_3.setItem(row, 7, QTableWidgetItem(f"{ticket.price}"))
            self.ui.tableWidget_3.setItem(row, 8, QTableWidgetItem(f"{ticket.description}"))
        session.close()


class AuthForm(QDialog):
    """Форма авторизации"""


    #@logger_wraps()
    def logincheck(self):
        """Проверяем есть ли в таблице user запись с указанными полями"""
        logger.info("Inside the function def logincheck")
        session = Session()
        result = session.query(User).filter(and_(User.login == self.ui.lineEdit.text(), User.password == self.ui.lineEdit_2.text())).first()
        kassir = session.query(User.last_name, User.first_name, User.middle_name).filter(and_(User.login == self.ui.lineEdit.text(), User.password == self.ui.lineEdit_2.text())).first()
        session.close()
        if result:
            """После закрытия окна авторизации открываем главную форму"""
            auth.close()
            self.openMain(kassir)
        else:
            info = 'Пользователь не найден'
            windows.info_window(info, 'Проверьте правильность ввода логина и пароля.')


    @logger_wraps()
    def openMain(self, kassir):
        """После закрытия окна авторизации открываем главную форму"""
        logger.info("Inside the function def openMain")
        logger.debug(kassir)
        auth.close()
        window = MainWindow()
        window.buttonAllClient()
        window.show()
        window.exec_()

    def __init__(self):
        super().__init__()
        """Проверяем статус соединения с БД"""
        try:
            db = psycopg2.connect("dbname="+database+" user="+user+" host="+host+" password="+password)
            if db:
                result = 1
        except:
            logger.warning("Connection was invalidated")
            result = 0
        finally:
            self.ui = Ui_Dialog()
            self.ui.setupUi(self)
            if result == 1:
                self.ui.label_3.setText('установлено')
            else:
                self.ui.label_3.setText('ошибка соединения!')
            self.ui.label_7.setText(software_version)
            self.ui.pushButton.clicked.connect(self.logincheck)
            self.ui.pushButton_2.clicked.connect(self.close)


class ClientForm(QDialog):
    """Форма с данными клиента"""
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_Client()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.buttonSave)
        self.ui.pushButton_2.clicked.connect(self.close)


    # def word_check(word):
    #     """Введенные данные должны состоять только из букв русского алфавита."""
    #     if re.search(r'[^а-яА-ЯёЁ]', word):
    #         raise ValueError("Ошибка ввода! Буквы должны быть только русского алфавита.")


    # def number_check(number):
    #     """Номер телефона должен начинаться с префикса "+7" или цифры 8 и иметь длину 10 цифр."""
    #     if re.search(r'(\+7|8)(\d{10})', number) and len(number) == 10:
    #         raise ValueError("Ошибка ввода! Номер должен быть длиной 10 знаков и начинаться с 8 или 9.")


    # def date_check(date):
    #     """Проверка правильности ввода даты."""
    #     try:
    #         return datetime.strptime(date, '%Y-%m-%d')
    #     except ValueError:
    #         print("Ошибка ввода! Введите дату корректно.")


    @logger_wraps()
    def buttonSave(self):
        """Сохраняем информацию о новом клиенте"""
        logger.info("Inside the function def buttonSave")
        session = Session()
        add_client = Client(last_name=str(self.ui.lineEdit.text()),
                            first_name=str(self.ui.lineEdit_2.text()),
                            middle_name=str(self.ui.lineEdit_3.text()),
                            birth_date=self.ui.dateEdit.date().toString("yyyy-MM-dd"),
                            gender=str(self.ui.comboBox.currentText()),
                            phone=self.ui.lineEdit_4.text(),
                            email=self.ui.lineEdit_5.text(),
                            privilege=str(self.ui.comboBox_2.currentText()))
        session.add(add_client)
        session.commit()
        session.close()
        self.close()


class SaleForm(QDialog):
    """Форма с данными клиента"""
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_Sale()
        self.ui.setupUi(self)
        self.ui.pushButton_3.clicked.connect(self.close)
        self.ui.pushButton_4.clicked.connect(self.close)
        self.ui.pushButton_5.clicked.connect(lambda: self.openPay(self.ui.label_8.text()))
        self.ui.pushButton_5.clicked.connect(self.close)
        #self.ui.pushButton_5.clicked.connect(self.check_ticket_generate)
        self.ui.tableWidget.doubleClicked.connect(self.add_client_to_sale)
        cur_today = date.today()
        self.ui.dateEdit.setDate(cur_today)
        self.ui.comboBox.currentTextChanged.connect(self.edit_sale)
        self.ui.checkBox_2.stateChanged.connect(self.check_sale_enabled)
        self.ui.comboBox_2.currentTextChanged.connect(self.edit_sale)


    #@logger_wraps()
    def check_sale_enabled(self):
        logger.info("Inside the function def check_sale_enabled")
        if self.ui.checkBox_2.isChecked():
            self.ui.comboBox_2.setEnabled(True)
        else:
            self.ui.comboBox_2.setEnabled(False)


    @logger_wraps()
    def button_all_clients_to_sale(self):
        """Выводим в tableWidget новой продажи список всех клиентов"""
        logger.info("Inside the function def button_all_clients_to_sale")
        session = Session()
        clients = session.query(Client).order_by(Client.id)
        for client in clients:
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(f"{client.last_name}"))
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(f"{client.first_name}"))
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(f"{client.middle_name}"))
            self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(f"{client.birth_date}"))
            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(f"{client.privilege}"))
            self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(f"{client.phone}"))
        session.close()


    @logger_wraps()
    def add_client_to_sale(self, *args, **kwargs):
        """Поиск выделенной строки в таблице клиентов и передача ее в таблицу заказа"""
        logger.info("Inside the function def add_client_to_sale")
        for idx in self.ui.tableWidget.selectionModel().selectedIndexes():
            """Номер строки найден"""
            row_number = idx.row()
            session = Session()
            search_client = session.query(Client).filter_by(id=(row_number+1)).first()
            session.close()
            """Вычисляем возраст клиента"""
            today = date.today()
            age = today.year - search_client.birth_date.year - ((today.month, today.day) < (search_client.birth_date.month, search_client.birth_date.day))
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
            """Передаем в таблицу заказа данные клиента"""
            row = self.ui.tableWidget_2.rowCount()
            self.ui.tableWidget_2.insertRow(row)
            self.ui.tableWidget_2.setItem(row, 0, QTableWidgetItem(f"{search_client.last_name}"))
            self.ui.tableWidget_2.setItem(row, 1, QTableWidgetItem(f"{search_client.first_name}"))
            self.ui.tableWidget_2.setItem(row, 2, QTableWidgetItem(f"{search_client.middle_name}"))
            self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{type_ticket}"))
            self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(f"{price}"))
            self.ui.tableWidget_2.setItem(row, 5, QTableWidgetItem(f"{search_client.privilege}"))
            self.ui.tableWidget_2.setItem(row, 6, QTableWidgetItem(f"{search_client.id}"))
            self.ui.tableWidget_2.setColumnHidden(6, True)
            """Заполняем таблицу с итоговой информацией"""
            self.edit_sale()


    @logger_wraps()
    def keyPressEvent(self, event):
        """Отслеживаем нажатие кнопок "delete", "backspace" """
        logger.info("Inside the function def keyPressEvent")
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            self.del_selected_item()
        QDialog.keyPressEvent(self, event)


    @logger_wraps()
    def del_selected_item(self):
        """Удаляем запись из таблицы при нажатии кнопки в keyPressEvent"""
        logger.info("Inside the function def del_selected_item")
        if self.ui.tableWidget_2.rowCount() > 0:
            currentrow = self.ui.tableWidget_2.currentRow()
            self.ui.tableWidget_2.removeRow(currentrow)
            self.edit_sale()


    #@logger_wraps() ломает работу функции
    def edit_sale(self):
        """Обновляем таблицу заказа"""
        logger.debug("combobox changed!")
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
        elif (int(time_ticket)) == 2:
            price = 400
        else:
            price = 600
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
                kol_adult += 1
                price_adult = self.ui.tableWidget_2.item(row, 4).text()
            else:
                kol_child += 1
                price_child = self.ui.tableWidget_2.item(row, 4).text()
        self.ui.label_5.setText(str(kol_adult))
        self.ui.label_7.setText(str(kol_child))
        """проверить есть ли взрослый"""
        #!
        """применяем скидку"""
        discount = int(self.ui.comboBox_2.currentText())
        if sale >= 0:
            new_price = sale - (sale/100 * discount)
            new_price = int(new_price)
            self.ui.label_8.setText(str(new_price))
        """Сохраняем данные продажи"""
        sale_tuple = (kol_adult, int(price_adult), kol_child, int(price_child), int(new_price), id_adult)
        """Генерируем список с билетами"""
        for row in range(rows):
            tickets.append((self.ui.tableWidget_2.item(row, 0).text(), self.ui.tableWidget_2.item(row, 1).text(), self.ui.tableWidget_2.item(row, 2).text(), self.ui.tableWidget_2.item(row, 3).text(), self.ui.tableWidget_2.item(row, 4).text(), self.ui.tableWidget_2.item(row, 5).text(), self.ui.tableWidget_2.item(row, 6).text()))
        return sale_tuple, tickets


    @logger.catch()
    def check_ticket_generate(self, payment_type):
        """Сохраняем данные данные заказа"""
        logger.info("Inside the function def check_ticket_generate")
        sale_tuple, tickets = self.edit_sale()
        state_check = kkt.check_open(sale_tuple, payment_type)
        #state_check = 1
        price = 0
        """Если прошла оплата"""
        if state_check == 1:
            """Сохраняем данные о продаже"""
            session = Session()
            add_sale = Sale(price=int(self.ui.label_8.text()),
                            id_user='1', #id кассира
                            id_client=sale_tuple[5])
            session.add(add_sale)
            session.commit()
            session.close()
            self.close()
            #проверка сохранения данных  в БД
            """Удаляем предыдущий файл с билетами"""
            if os.path.exists('./ticket.pdf'):
                os.remove('./ticket.pdf')
            """Устанавливаем параметры макета билета"""
            pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))
            c = canvas.Canvas("ticket.pdf", pagesize=(21 * cm, 8 * cm))
            c.setFont('DejaVuSerif', 12)
            """Сохраняем билеты"""
            session = Session()
            sale_index = session.query(Sale).count()
            for l in tickets:
                for l in tickets:
                    """Сохраняем макет билета"""
                    c.setFont('DejaVuSerif', 12)
                    c.drawString(20 * mm, 53 * mm, str([l[0]]).replace("'", "").replace("[", "").replace("]", ""))
                    c.drawString(20 * mm, 47 * mm, str([l[1]]).replace("'", "").replace("[", "").replace("]", ""))
                    c.drawString(95 * mm, 53 * mm, "Возраст")
                    c.drawString(20 * mm, 41 * mm, str([l[6]]).replace("'", "").replace("[", "").replace("]", ""))
                    c.drawString(95 * mm, 41 * mm, str(date.today()))
                    c.drawString(70 * mm, 30 * mm, "МАСТЕРСЛАВЛЬ")
                    c.drawString(70 * mm, 23 * mm, "БЕЛГОРОД")
                    c.drawString(121 * mm, 30 * mm, str([l[4]]).replace("'", "").replace("[", "").replace("]", ""))
                    c.drawString(31 * mm, 13 * mm, str([l[5]]).replace("'", "").replace("[", "").replace("]", ""))
                    c.drawString(90 * mm, 13 * mm, "Примечание 2")
                    c.drawString(153 * mm, 40 * mm, "Таланты")
                    c.showPage()
                    #price = str([l[4]]).replace("'", "")
                    if [l[5]] == 'взрослый':
                        price = sale_tuple[1]
                    elif [l[5]] == 'детский':
                        price = sale_tuple[3]
                    add_ticket = Ticket(id_client=int(l[6]),
                                        id_sale=int(sale_index),
                                        client_age='1',
                                        arrival_time=self.ui.comboBox.currentText(),
                                        talent='1',
                                        price=price,
                                        description=[l[5]])
                session.add(add_ticket)
                session.commit()
            session.close()
            self.close()
            c.save()
            """Печатаем билеты"""
            t.sleep(5)
            os.startfile("ticket.pdf", "print")
            t.sleep(5)
            os.system("TASKKILL /F /IM AcroRD32.exe")
            os.system("TASKKILL /F /IM Acrobat.exe")
        else:
            logger.info('Оплата не прошла')
            windows.info_window("Оплата не прошла", '')


    #@logger_wraps()
    def openPay(self, txt):
        """Открываем форму оплаты"""
        logger.info("Inside the function def openPay")
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
        if res == PaymentType.ByCard:
        # Оплачено картой
            logger.info('CARD')
            payment_type = PaymentType.ByCard
            #запустить оплату по терминалу
            self.check_ticket_generate(payment_type)
        elif res == PaymentType.ByCash:
            logger.info('CASH')
            payment_type = PaymentType.ByCash
            self.check_ticket_generate(payment_type)
        # Генерируем чек

        # Закрываем окно продажи и возвращаем QDialog.Accepted
        self.accept()


# Тип платежа (перечисление)
class PaymentType:
    ByCard = 101
    ByCash = 102


class PayForm(QDialog):
    """Форма оплаты"""
    startGenerate = Signal()
    def __init__(self):
            super().__init__()
            self.ui = Ui_Dialog_Pay()
            self.ui.setupUi(self)
            # Посылаем сигнал генерации чека
            # self.ui.pushButton.clicked.connect(self.startGenerate.emit)
            # при вызове done() окно должно закрыться и exec_ вернет переданный аргумент из done()
            self.ui.pushButton.clicked.connect(lambda: self.done(PaymentType.ByCash))
            self.ui.pushButton_2.clicked.connect(lambda: self.done(PaymentType.ByCard))

        # Устанавливаем текстовое значение в метку
    def setText(self, txt):
        self.ui.label_2.setText(txt)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    auth = AuthForm()
    auth.show()

    sys.exit(app.exec_())
