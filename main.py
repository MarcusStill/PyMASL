import calendar
import datetime as dt
import os
import socket
import subprocess
import sys
from configparser import ConfigParser
from datetime import date, timedelta

from PySide6 import QtCore, QtSql
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QCheckBox, QDialog, QHBoxLayout
from PySide6.QtWidgets import QMainWindow, QTableWidgetItem, QWidget
from sqlalchemy import and_, create_engine, func, update, desc
from sqlalchemy.orm import sessionmaker, exc

from db.models import Client
from db.models import Holiday
from db.models import Sale
from db.models import Ticket
from db.models import Workday
from db.models.user import User
from files import kkt
from files import otchet
from files import windows
from files.logger import *
from forms.authorization import Ui_Dialog
from forms.client import Ui_Dialog_Client
from forms.main_form import Ui_MainWindow
from forms.pay import Ui_Dialog_Pay
from forms.sale import Ui_Dialog_Sale

# Чтение параметров из файла конфигурации
config = ConfigParser()
config.read("config.ini")
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
        self.ui.pushButton.clicked.connect(self.main_search_clients)
        # Открыть окно добавления нового клиента
        self.ui.pushButton_2.clicked.connect(self.main_open_client)
        self.ui.pushButton_2.clicked.connect(self.main_edit_client)
        self.ui.tableWidget.doubleClicked.connect(self.main_edit_client)
        # Отображение всех клиентов
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
        self.ui.pushButton_23.clicked.connect(self.main_open_sale)
        self.ui.pushButton_13.clicked.connect(self.main_button_all_sales)
        self.ui.pushButton_18.clicked.connect(self.main_otchet_kassira)
        self.ui.pushButton_19.clicked.connect(self.main_otchet_administratora)
        self.ui.tableWidget_2.doubleClicked.connect(self.main_search_selected_sale)
        self.ui.pushButton_17.clicked.connect(self.main_get_statistic)
        self.ui.dateEdit.setDate(date.today())
        self.ui.dateEdit_2.setDate(date.today())
        self.ui.lineEdit_2.returnPressed.connect(self.main_search_clients)
        self.ui.comboBox_3.currentTextChanged.connect(self.main_filter_clear)
        # изменяем ширину столбца
        self.ui.tableWidget_2.setColumnWidth(3, 250)

    @logger_wraps()
    def main_search_clients(self):
        """
        Выводим в tableWidget (вкладка "посетители")
        отфильтрованный список клиентов
        """
        logger.info("Запуск функции main_search_clients")
        # вычисляем индекс значения
        index = self.ui.comboBox_3.currentIndex()
        if index == 2:
            # Поиск по номеру телефона
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.phone.like(
                "%" + self.ui.lineEdit_2.text() + "%")).all()
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
                    row, 4, QTableWidgetItem(f"{client.gender}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 6, QTableWidgetItem(f"{client.email}"))
                self.ui.tableWidget.setItem(
                    row, 7, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 8, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(8, True)
            session.close()
        elif index == 1:
            # Поиск по фамилии
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.last_name.ilike(
                "%" + self.ui.lineEdit_2.text() + "%")).all()
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
                    row, 4, QTableWidgetItem(f"{client.gender}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 6, QTableWidgetItem(f"{client.email}"))
                self.ui.tableWidget.setItem(
                    row, 7, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 8, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(8, True)
            session.close()
        elif index == 0:
            # Поиск по фамилии и имени
            self.ui.tableWidget.setRowCount(0)
            search = self.ui.lineEdit_2.text().title()
            # разбиваем поисковую фразу на две
            lst = search.split()
            if len(lst) == 2:
                session = Session()
                search = session.query(Client).filter(and_(Client.first_name.ilike(
                    lst[1] + "%"), Client.last_name.ilike(
                    lst[0] + "%"))).all()
            else:
                windows.info_window("Неправильно задано условие для поиска",
                                    "Введите начальные буквы фамилии"
                                    "и имени через пробел", "")
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
                    row, 4, QTableWidgetItem(f"{client.gender}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 6, QTableWidgetItem(f"{client.email}"))
                self.ui.tableWidget.setItem(
                    row, 7, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 8, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(8, True)
            session.close()
        elif index == 3:
            # Поиск инвалидов
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.privilege.ilike(
                "%" + "и")).all()
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
                    row, 4, QTableWidgetItem(f"{client.gender}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 6, QTableWidgetItem(f"{client.email}"))
                self.ui.tableWidget.setItem(
                    row, 7, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 8, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(8, True)
            session.close()
        elif index == 4:
            # Поиск многодетных
            self.ui.tableWidget.setRowCount(0)
            session = Session()
            search = session.query(Client).filter(Client.privilege.ilike(
                "%" + "м")).all()
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
                    row, 4, QTableWidgetItem(f"{client.gender}"))
                self.ui.tableWidget.setItem(
                    row, 5, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(
                    row, 6, QTableWidgetItem(f"{client.email}"))
                self.ui.tableWidget.setItem(
                    row, 7, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(
                    row, 8, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(8, True)
            session.close()

    def main_edit_client(self):
        """
        Поиск выделенной строки в таблице клиентов
        и открытие формы для редактирования
        """
        logger.info("Запуск функции main_edit_client")
        # ищем индекс и значение ячейки
        for idx in self.ui.tableWidget.selectionModel().selectedIndexes():
            # Номер строки найден
            row_number = idx.row()
            # Получаем содержимое ячейки
            client_id = self.ui.tableWidget.item(row_number, 8).text()
            session = Session()
            search_client = session.query(Client).filter_by(id=client_id).first()
            session.close()
            # сохраняем id клиента
            System.client_id = search_client.id
            # Передаем в форму данные клиента
            client = ClientForm()
            client.ui.lineEdit.setText(search_client.last_name)
            client.ui.lineEdit_2.setText(search_client.first_name)
            client.ui.lineEdit_3.setText(search_client.middle_name)
            client.ui.dateEdit.setDate(search_client.birth_date)
            # Поиск значения для установки в ComboBox gender
            index_gender = client.ui.comboBox.findText(
                search_client.gender, Qt.MatchFixedString)
            if index_gender >= 0:
                client.ui.comboBox.setCurrentIndex(index_gender)
            client.ui.lineEdit_4.setText(search_client.phone)
            client.ui.lineEdit_5.setText(search_client.email)
            # Поиск значения для установки в ComboBox privilege
            index_privilege = client.ui.comboBox.findText(
                search_client.privilege, Qt.MatchFixedString)
            if index_privilege >= 0:
                client.ui.comboBox_2.setCurrentIndex(index_privilege)
            client.show()
            # сохраняем параметры данных об уже существующем клиенте
            System.client_update = 1
            logger.info("Обновляем инф. клиента %s" % System.client_update)
            logger.debug("id клиента %s" % System.client_id)
            client.exec_()

    def main_filter_clear(self):
        """
        Передаем значение пользовательского
        фильтра в модель QSqlTableModel
        """
        logger.info("Запуск функции main_filter_clear")
        self.ui.lineEdit_2.clear()

    def main_search_selected_sale(self):
        """
        Поиск выделенной строки в таблице продаж
        и открытие формы с полученными данными
        """
        logger.info("Запуск функции mail_search_selected_sale")
        kol_adult = 0
        kol_child = 0
        summ = 0
        for idx in self.ui.tableWidget_2.selectionModel().selectedIndexes():
            # Номер строки найден
            row_number = idx.row()
            # Получаем содержимое ячейки
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
                                           Ticket.datetime).join(Ticket).filter(
                and_(
                    Client.id == Ticket.id_client,
                    Ticket.id_sale == sale_number
                )
            ).all()
            # запрашиваем статус продажи
            sale_status = (session.query(Sale.status).filter(Sale.id == sale_number).one())._asdict().get("status")
            logger.info("Статус продажи %s" % sale_status)
            # Передаем в форму данные клиента
            sale = SaleForm()
            sale.ui.tableWidget_2.setRowCount(0)
            sale.ui.dateEdit.setDate(client_in_sale[0][11])
            sale.ui.comboBox.setCurrentText(str(client_in_sale[0][9]))
            # если продажа оплачена
            if sale_status == 1 or sale_status == 2:
                # кнопка сохранить
                sale.ui.pushButton_3.setEnabled(False)
                # кнопка оплатить
                sale.ui.pushButton_5.setEnabled(False)
                # кнопка обновить
                sale.ui.pushButton_10.setEnabled(False)
                # кнопка возврат
                sale.ui.pushButton_6.setEnabled(True)
                # кнопка печать билетов
                sale.ui.pushButton_7.setEnabled(True)
                # кнопка просмотр билетов
                sale.ui.pushButton_8.setEnabled(True)
                # дата посещения
                sale.ui.dateEdit.setEnabled(False)
                # время посещения
                sale.ui.comboBox.setEnabled(False)
                # клиенты в заказе
                sale.ui.tableWidget_2.setEnabled(False)
                # поле скидка
                sale.ui.checkBox_2.setEnabled(False)
            # если продажа многодетным/инвалидам
            if sale_status == 3 or sale_status == 4:
                sale.ui.pushButton_3.setEnabled(False)
                sale.ui.pushButton_5.setEnabled(False)
                sale.ui.pushButton_10.setEnabled(False)
                sale.ui.pushButton_6.setEnabled(True)
                sale.ui.pushButton_7.setEnabled(True)
                sale.ui.pushButton_8.setEnabled(True)
                sale.ui.dateEdit.setEnabled(False)
                sale.ui.comboBox.setEnabled(False)
                sale.ui.tableWidget_2.setEnabled(False)
                sale.ui.checkBox_2.setEnabled(False)
            # если продажа не оплачена
            elif sale_status == 0:
                sale.ui.pushButton_3.setEnabled(False)
                sale.ui.pushButton_5.setEnabled(True)
                sale.ui.pushButton_10.setEnabled(True)
                sale.ui.pushButton_6.setEnabled(False)
                sale.ui.pushButton_7.setEnabled(False)
                sale.ui.pushButton_8.setEnabled(False)
                sale.ui.dateEdit.setEnabled(True)
                sale.ui.comboBox.setEnabled(True)
                sale.ui.tableWidget_2.setEnabled(True)
                sale.ui.checkBox_2.setEnabled(True)
            for search_client in client_in_sale:
                logger.debug(search_client)
                if search_client[8] >= System.age_max:
                    type_ticket = 'взрослый'
                    kol_adult += 1
                else:
                    type_ticket = 'детский'
                    kol_child += 1
                # Изменяем ширину столбцов
                sale.ui.tableWidget_2.setColumnWidth(3, 5)
                sale.ui.tableWidget_2.setColumnWidth(4, 5)
                sale.ui.tableWidget_2.setColumnWidth(7, 40)
                sale.ui.tableWidget_2.setColumnWidth(8, 5)
                # Создаем виджет checkbox для скидки
                widget = QWidget()
                checkbox = QCheckBox()
                checkbox.setCheckState(Qt.Unchecked)
                layoutH = QHBoxLayout(widget)
                layoutH.addWidget(checkbox)
                layoutH.setAlignment(Qt.AlignCenter)
                layoutH.setContentsMargins(0, 0, 0, 0)
                # Создаем виджет checkbox для исключения из продажи
                widget_1 = QWidget()
                checkbox_1 = QCheckBox()
                checkbox.setCheckState(Qt.Unchecked)
                layoutH = QHBoxLayout(widget_1)
                layoutH.addWidget(checkbox_1)
                layoutH.setAlignment(Qt.AlignCenter)
                layoutH.setContentsMargins(0, 0, 0, 0)
                row = sale.ui.tableWidget_2.rowCount()
                sale.ui.tableWidget_2.insertRow(row)
                # добавляем checkbox скидки
                sale.ui.tableWidget_2.setCellWidget(row, 7, widget)
                # Добавляем checkbox "присутствия" в продаже
                sale.ui.tableWidget_2.setCellWidget(row, 8, widget_1)
                # имя
                sale.ui.tableWidget_2.setItem(
                    row, 0, QTableWidgetItem(f"{search_client[1]}"))
                # фамилия
                sale.ui.tableWidget_2.setItem(
                    row, 1, QTableWidgetItem(f"{search_client[0]}"))
                # тип билета
                sale.ui.tableWidget_2.setItem(
                    row, 2, QTableWidgetItem(type_ticket))
                # цена
                sale.ui.tableWidget_2.setItem(
                    row, 3, QTableWidgetItem(f"{search_client[4]}"))
                # примечание
                sale.ui.tableWidget_2.setItem(
                    row, 4, QTableWidgetItem(f"{search_client[5]}"))
                # id клиента
                sale.ui.tableWidget_2.setItem(
                    row, 5, QTableWidgetItem(f"{search_client[6]}"))
                sale.ui.tableWidget_2.setColumnHidden(5, True)
                # возраст
                sale.ui.tableWidget_2.setItem(
                    row, 6, QTableWidgetItem(f"{search_client[8]}"))
                summ += int(search_client[4])
            session.close()
            sale.ui.label_5.setText(str(kol_adult))
            sale.ui.label_7.setText(str(kol_child))
            sale.ui.label_8.setText(str(summ))
            sale.show()
            windows.info_window("Внимание",
                                'Перед проведением оплаты нажмите на кнопку обновить',
                                "")
            # передаем сведения о сохраненной продаже
            System.sale_status = sale_status
            System.sale_id = sale_number
            System.sale_tickets = client_in_sale
            logger.debug("Билеты сохр-й продажи %s" % System.sale_tickets)
            sale.exec_()

    def main_button_all_sales(self):
        """Фильтр продаж в tableWidget за 1, 3 и 7 дней"""
        logger.info("Запуск функции main_button_all_sales")
        filter_day = 0
        self.ui.tableWidget_2.setRowCount(0)
        # Фильтр продаж за 1, 3 и 7 дней
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
                                               filter_day).order_by(desc(Sale.id))
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
                    elif sale.status == 2:
                        status_type = 'возврат'
                    elif sale.status == 3:
                        status_type = 'многодетные'
                    elif sale.status == 4:
                        status_type = 'инвалид'
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
                    elif sale.payment_type == 3:
                        payment_type = 'карта offline'
                    else:
                        payment_type = '-'
                    self.ui.tableWidget_2.setItem(
                        row, 7, QTableWidgetItem(f"{payment_type}"))
            session.close()
        except Exception as e:
            logger.info(e)
            logger.info("Продаж за выбранный период не было")

    @logger_wraps()
    def main_open_client(self):
        """Открываем форму с данными клиента"""
        logger.info("Запуск функции main_open_client")
        client = ClientForm()
        client.show()
        client.exec_()

    @logger_wraps()
    def main_open_sale(self):
        """Открываем форму с продажей"""
        logger.info("Запуск функции main_open_sale")
        sale = SaleForm()
        sale.show()
        # кнопка сохранить
        sale.ui.pushButton_3.setEnabled(True)
        # кнопка оплатить
        sale.ui.pushButton_5.setEnabled(True)
        # кнопка обновить
        sale.ui.pushButton_10.setEnabled(True)
        # кнопка возврат
        sale.ui.pushButton_6.setEnabled(False)
        # кнопка печать билетов
        sale.ui.pushButton_7.setEnabled(False)
        # кнопка просмотр билетов
        sale.ui.pushButton_8.setEnabled(False)
        # дата посещения
        sale.ui.dateEdit.setEnabled(True)
        # время посещения
        sale.ui.comboBox.setEnabled(True)
        # клиенты в заказе
        sale.ui.tableWidget_2.setEnabled(True)
        # поле скидка
        sale.ui.checkBox_2.setEnabled(True)
        System.sale_discount = 0
        # сбрасываем номер строки QCheckBox для исключения из продажи
        System.sale_checkbox_row = None
        # флаг состояния QCheckBox для исключения из продажи 0 - не активен
        System.exclude_from_sale = 0
        # Обновляем System.sale_dict
        System.sale_dict['kol_adult'] = 0
        System.sale_dict['price_adult'] = 0
        System.sale_dict['kol_child'] = 0
        System.sale_dict['price_child'] = 0
        System.sale_dict['detail'][0] = 0
        System.sale_dict['detail'][1] = 0
        System.sale_dict['detail'][2] = 0
        System.sale_dict['detail'][3] = 0
        System.sale_dict['detail'][4] = 0
        System.sale_dict['detail'][5] = 0
        System.sale_dict['detail'][6] = 0
        System.sale_dict['detail'][7] = 0
        sale.exec_()

    @logger_wraps()
    def main_get_statistic(self):
        """Генерация сводной информации о продажах и билетах"""
        logger.info("Запуск функции main_get_statistic")
        # устанавливаем временной период
        start_time = ' 00:00:00'
        end_time = ' 23:59:59'
        dt1 = self.ui.dateEdit_2.date().toString("yyyy-MM-dd") + start_time
        dt2 = self.ui.dateEdit.date().toString("yyyy-MM-dd") + end_time
        session = Session()
        sales = session.query(Sale.pc_name,
                              Sale.payment_type,
                              Sale.price, Sale.status
                              ).filter(and_(Sale.status == '1',
                                            Sale.datetime.between(dt1,
                                                                  dt2))).all()
        session.close()
        logger.debug("Продажи за выбранный период %s" % sales)
        # анализируем полученные данные
        # предполагаем что кассовых РМ два
        pc_1 = {'Name PC': f'{System.pc_1}', 'card': 0, 'cash': 0}
        pc_2 = {'Name PC': f'{System.pc_2}', 'card': 0, 'cash': 0}
        # тип оплаты: 1 - карта, 2 - наличные
        type_rm = [1, 2]
        for i in range(len(sales)):
            if sales[i][0] in pc_1.values():
                # если карта
                if sales[i][1] == type_rm[0]:
                    pc_1['card'] += sales[i][2]
                # если наличные
                else:
                    pc_1['cash'] += sales[i][2]
            else:
                if sales[i][1] == type_rm[0]:
                    pc_2['card'] += sales[i][2]
                else:
                    pc_2['cash'] += sales[i][2]
        logger.debug("Данные с pc_1 %s" % pc_1)
        logger.debug("Данные с pc_2 %s" % pc_2)
        card = int(pc_1['card']) + int(pc_2['card'])
        cash = int(pc_1['cash']) + int(pc_2['cash'])
        summa = card + cash
        self.ui.tableWidget_4.setRowCount(0)
        self.ui.tableWidget_4.insertRow(0)
        self.ui.tableWidget_4.setItem(0, 0,
                                      QTableWidgetItem(f"{pc_1['Name PC']}"))
        self.ui.tableWidget_4.setItem(0, 1,
                                      QTableWidgetItem(f"{pc_1['card']}"))
        self.ui.tableWidget_4.setItem(0, 2,
                                      QTableWidgetItem(f"{pc_1['cash']}"))
        self.ui.tableWidget_4.insertRow(1)
        self.ui.tableWidget_4.setItem(1, 0,
                                      QTableWidgetItem(f"{pc_2['Name PC']}"))
        self.ui.tableWidget_4.setItem(1, 1,
                                      QTableWidgetItem(f"{pc_2['card']}"))
        self.ui.tableWidget_4.setItem(1, 2,
                                      QTableWidgetItem(f"{pc_2['cash']}"))
        self.ui.tableWidget_4.insertRow(2)
        self.ui.tableWidget_4.setItem(2, 0,
                                      QTableWidgetItem(f"{'Итого'}"))
        self.ui.tableWidget_4.setItem(2, 1,
                                      QTableWidgetItem(f"{card}"))
        self.ui.tableWidget_4.setItem(2, 2,
                                      QTableWidgetItem(f"{cash}"))
        self.ui.tableWidget_4.setItem(2, 3,
                                      QTableWidgetItem(f"{summa}"))
        # считаем билеты
        session = Session()
        tickets = session.query(Ticket.ticket_type,
                                Ticket.arrival_time,
                                Ticket.description,
                                Sale.status,
                                Sale.id,
                                ).filter(and_(
                                                Sale.id == Ticket.id_sale,
                                                Sale.status == '1',
                                                Ticket.datetime.between(
                                                    dt1, dt2
                                                ))).all()
        session.close()
        logger.debug("Билеты %s" % tickets)
        type_tickets = [0, 1, 'м', 'и', '-']
        # 0-взрослый, 1-детский, 2-многодетный, 3-инвалид
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
        # выводим обобщенную информацию в таблицу
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
    def main_otchet_administratora(self):
        """Формирование отчета администратора"""
        logger.info("Запуск функции main_otchet_administratora")
        path = "./otchet.pdf"
        path = os.path.realpath(path)
        row = self.ui.tableWidget_3.rowCount()
        if row >= 1:
            type_ticket = ['Взрослый, 1 ч.', 'Взрослый, 2 ч.', 'Взрослый, 3 ч.',
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
                    ['1', type_ticket[0], System.ticket_adult_1, table[0],
                     int(System.ticket_adult_1) * int(table[0])],
                    ['2', type_ticket[1], System.ticket_adult_2, table[1],
                     int(System.ticket_adult_2) * int(table[1])],
                    ['3', type_ticket[2], System.ticket_adult_3, table[2],
                     int(System.ticket_adult_3) * int(table[2])],
                    ['4', type_ticket[3], System.ticket_child_1, table[3],
                     int(System.ticket_child_1) * int(table[3])],
                    ['5', type_ticket[4], System.ticket_child_2, table[4],
                     int(System.ticket_child_2) * int(table[4])],
                    ['6', type_ticket[5], System.ticket_child_3, table[5],
                     int(System.ticket_child_3) * int(table[5])],
                    ['7', type_ticket[6], '-', table[6], '-'],
                    ['8', type_ticket[7], '-', table[7], '-']]
            logger.debug("Сведения для отчета администратора %s" % data)
            otchet.otchet_administratora(dt1, dt2, data)
            os.startfile(path)

    @logger_wraps()
    def main_otchet_kassira(self):
        """Формирование отчета кассира"""
        logger.info("Запуск функции main_otchet_kassira")
        path = "./otchet.pdf"
        path = os.path.realpath(path)
        # Удаляем предыдущий файл
        row_tab_1 = self.ui.tableWidget_3.rowCount()
        row_tab_2 = self.ui.tableWidget_4.rowCount()
        if row_tab_1 >= 1 and row_tab_2 >= 1:
            os.system("TASKKILL /F /IM SumatraPDF.exe")
            if os.path.exists(path):
                os.remove(path)
            dt1 = self.ui.dateEdit_2.date().toString("dd-MM-yyyy")
            dt2 = self.ui.dateEdit.date().toString("dd-MM-yyyy")
            # формируем данные
            logger.info("Формируем сведения для отчета %s"
                        % self.ui.tableWidget_3.item(0, 0).text())
            logger.info("Имя ПК %s" % System.pc_name)
            if System.pc_name == self.ui.tableWidget_4.item(0, 0).text():
                values = [self.ui.tableWidget_4.item(0, 1).text(),
                          self.ui.tableWidget_4.item(0, 2).text()]
            else:
                values = [self.ui.tableWidget_4.item(1, 1).text(),
                          self.ui.tableWidget_4.item(1, 2).text()]
            logger.debug("Сведения для отчета кассира %s" % values)
            otchet.otchet_kassira(values, dt1, dt2, System.user)
            os.startfile(path)


class AuthForm(QDialog):
    """Форма авторизации"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        # Добавляем логотип на форму
        pixmap = QPixmap('pylogo.png')
        self.ui.label_4.setPixmap(pixmap)
        self.ui.label_7.setText(software_version)
        self.ui.pushButton.clicked.connect(self.auth_login_check)
        self.ui.pushButton_2.clicked.connect(self.close)

    def auth_login_check(self):
        """Проверяем есть ли в таблице user запись с указанными полями"""
        logger.info("Запуск функции auth_login_check")
        login = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()
        kassir = System.user_authorization(login, password)
        if kassir == 1:
            # После закрытия окна авторизации открываем главную форму
            auth.close()
            # Устанавливаем размер окна
            window = MainWindow()
            window.showMaximized()
            # Добавляем в заголовок доп. инф-ю
            window.setWindowTitle('PyMasl ver. ' + software_version +
                                  '. Пользователь: ' +
                                  System.user[0] + ' ' +
                                  System.user[1] + '. БД: ' + database)
            # отображаем все продажи при запуске
            window.main_button_all_sales()
            # проверяем статус текущего дня
            day_today = System.check_day(self)
            if day_today == 0:
                System.what_a_day = 0
                logger.info("Сегодня будний день %s" % System.what_a_day)
            elif day_today == 1:
                System.what_a_day = 1
                sun, num_of_week = System.check_one_sunday(self)
                # проверяем если номер дня недели равен 7 и дата <= 7
                System.sunday = sun
                System.num_of_week = num_of_week
            # считываем количество РМ и имена
            System.kol_pc = kol_pc
            System.pc_1 = pc_1
            System.pc_2 = pc_2
            window.show()
            window.exec_()
        else:
            logger.warning("Неудачная авторизация %s" % login, password)
            windows.info_window(
                'Пользователь не найден',
                'Проверьте правильность ввода логина и пароля.', '')


class ClientForm(QDialog):
    """Форма с данными клиента"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_Client()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.client_data_save)
        self.ui.pushButton_2.clicked.connect(self.close)
        self.ui.pushButton_3.clicked.connect(self.client_data_copy)
        self.ui.pushButton_4.clicked.connect(self.client_data_paste)

    def client_data_copy(self):
        """Запоминаем фамилию нового клиента"""
        logger.info("Запуск функции client_data_copy")
        System.last_name = str(self.ui.lineEdit.text()).title()

    def client_data_paste(self):
        """Возвращаем фамилию нового клиента"""
        logger.info("Запуск функции client_data_paste")
        self.ui.lineEdit.setText(System.last_name)

    def client_data_save(self):
        """Сохраняем информацию о новом клиенте"""
        logger.info("Запуск функции client_data_save")
        # сбрасываем id последнего добавленного клиента
        System.add_new_client_in_sale = 0
        # первые буквы делаем заглавными
        System.last_name = str(self.ui.lineEdit.text()).title()
        first_name = str(self.ui.lineEdit_2.text()).title()
        # проверяем заполнены ли поля имени и фамилии
        if len(System.last_name) >= 2 and len(first_name) >= 2:
            if System.client_update != 1:
                logger.info('Добавляем нового клиента')
                session = Session()
                # получаем максимальный id в таблице клиентов
                client_index = session.query(func.max(Client.id)).scalar()
                logger.debug('Количество клиентов в бд: %s' % client_index)
                add_client = Client(id=client_index + 1,
                                    last_name=System.last_name,
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
                try:
                    session.commit()
                except exc.sa_exc.SQLAlchemyError as e:
                    error = str(e.__dict__['orig'])
                    session.rollback()
                    logger.error('Ошибка при сохранении в БД: %s' % error)
                    windows.info_window('Ошибка при сохранении в БД!', '', error)
                finally:
                    session.close()
                self.close()
            elif System.client_update == 1:
                # обновляем информацию о клиенте
                logger.info('Обновляем информацию о клиенте')
                session = Session()
                try:
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
                    session.commit()
                except exc.sa_exc.SQLAlchemyError as e:
                    error = str(e.__dict__['orig'])
                    session.rollback()
                    logger.error('Ошибка при сохранении в БД: %s' % error)
                    windows.info_window('Ошибка при сохранении в БД!', '', error)
                finally:
                    session.close()
                self.close()
                System.client_update = None
                System.client_id = None

        else:
            windows.info_window('Внимание!',
                                'Необходимо заполнить поля имени и фамилии',
                                '')


class SaleForm(QDialog):
    """Форма продажи"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_Sale()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.sale_search_clients)
        self.ui.pushButton_2.clicked.connect(lambda: MainWindow.main_open_client(self))
        self.ui.pushButton_11.clicked.connect(self.sale_edit_client)
        self.ui.pushButton_3.clicked.connect(self.sale_save_selling)
        self.ui.pushButton_4.clicked.connect(self.close)
        self.ui.pushButton_5.clicked.connect(
            lambda: self.sale_open_pay(self.ui.label_8.text()))
        self.ui.pushButton_6.clicked.connect(self.sale_return_selling)
        self.ui.pushButton_7.clicked.connect(self.sale_generate_saved_tickets)
        self.ui.tableWidget.doubleClicked.connect(self.sale_add_client_to_selling)
        cur_today = date.today()
        self.ui.dateEdit.setDate(cur_today)
        self.ui.dateEdit.dateChanged.connect(self.sale_calendar_color_change)
        self.ui.comboBox.currentTextChanged.connect(self.sale_edit_selling)
        self.ui.checkBox_2.stateChanged.connect(self.sale_check_discount_enabled)
        self.ui.comboBox_2.currentTextChanged.connect(self.sale_edit_selling)
        # адаптированный для пользователя фильтр
        self.ui.comboBox_4.currentTextChanged.connect(self.sale_check_filter_update)
        # KeyPressEvent
        self.ui.tableWidget_2.keyPressEvent = self.sale_key_pressed
        self.ui.pushButton_9.clicked.connect(self.sale_add_new_client)
        self.ui.pushButton_10.clicked.connect(self.sale_edit_selling)
        self.ui.tableWidget_3.doubleClicked.connect(self.sale_add_client_to_selling_2)

    def sale_edit_client(self):
        """
        Поиск выделенной строки в таблице клиентов
        и открытие формы для редактирования данных клиента
        """
        logger.info("Запуск функции sale_edit_client")
        # ищем индекс и значение ячейки
        for idx in self.ui.tableWidget.selectionModel().selectedIndexes():
            # Номер строки найден
            row_number = idx.row()
            # Получаем содержимое ячейки
            client_id = self.ui.tableWidget.item(row_number, 5).text()
            session = Session()
            search_client = session.query(Client).filter_by(id=client_id).first()
            session.close()
            # сохраняем id клиента
            System.client_id = search_client.id
            # Передаем в форму данные клиента
            client = ClientForm()
            client.ui.lineEdit.setText(search_client.last_name)
            client.ui.lineEdit_2.setText(search_client.first_name)
            client.ui.lineEdit_3.setText(search_client.middle_name)
            client.ui.dateEdit.setDate(search_client.birth_date)
            # Поиск значения для установки в ComboBox gender
            index_gender = client.ui.comboBox.findText(
                search_client.gender, Qt.MatchFixedString)
            if index_gender >= 0:
                client.ui.comboBox.setCurrentIndex(index_gender)
            client.ui.lineEdit_4.setText(search_client.phone)
            client.ui.lineEdit_5.setText(search_client.email)
            # Поиск значения для установки в ComboBox privilege
            index_privilege = client.ui.comboBox.findText(
                search_client.privilege, Qt.MatchFixedString)
            if index_privilege >= 0:
                client.ui.comboBox_2.setCurrentIndex(index_privilege)
            client.show()
            # сохраняем параметры данных об уже существующем клиенте
            System.client_update = 1
            logger.info('Обновляем инф. клиента %s' % System.client_update)
            logger.debug('id клиента %s' % System.client_id)
            client.exec_()

    def sale_add_new_client(self):
        """Добавляем в окно продажи только что созданного клиента"""
        logger.info("Запуск функции sale_add_new_client")
        type_ticket = ''
        # Запрашиваем данные нового клиента
        session = Session()
        search_client = session.query(Client).filter_by(
            id=System.id_new_client_in_sale).first()
        session.close()
        logger.debug("Найденный клиент %s" % search_client)
        # Вычисляем возраст клиента
        today = date.today()
        age = (today.year - search_client.birth_date.year -
               ((today.month, today.day) < (search_client.birth_date.month,
                                            search_client.birth_date.day)))
        # Определяем тип билета и цену
        if age < System.age_min:
            type_ticket = 'бесплатный'
        if System.age_min <= age < System.age_max:
            type_ticket = 'детский'
        elif age >= System.age_max:
            type_ticket = 'взрослый'
        # Определяем тип билета и цену
        time = int(self.ui.comboBox.currentText())
        if type_ticket == 'бесплатный':
            price = System.ticket_free
        elif type_ticket == 'взрослый':
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
        # Создаем виджет checkbox
        widget = QWidget()
        checkbox = QCheckBox()
        checkbox.setCheckState(Qt.Unchecked)
        layoutH = QHBoxLayout(widget)
        layoutH.addWidget(checkbox)
        layoutH.setAlignment(Qt.AlignCenter)
        layoutH.setContentsMargins(0, 0, 0, 0)
        # Создаем виджет checkbox для исключения из продажи
        widget_1 = QWidget()
        checkbox_1 = QCheckBox()
        checkbox.setCheckState(Qt.Unchecked)
        layoutH = QHBoxLayout(widget_1)
        layoutH.addWidget(checkbox_1)
        layoutH.setAlignment(Qt.AlignCenter)
        layoutH.setContentsMargins(0, 0, 0, 0)
        row = self.ui.tableWidget_2.rowCount()
        self.ui.tableWidget_2.insertRow(row)
        # добавляем checkbox скидки
        self.ui.tableWidget_2.setCellWidget(row, 7, widget)
        # Добавляем checkbox "присутствия" в продаже
        self.ui.tableWidget_2.setCellWidget(row, 8, widget_1)
        # Передаем в таблицу заказа данные клиента
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

    def sale_key_pressed(self, event):
        """Отслеживание нажатий клавиш на клавиатуре"""
        logger.info("Запуск функции sale_key_pressed")
        if event.key() == QtCore.Qt.Key_Delete:
            self.sale_del_selected_item()
        elif event.key() == QtCore.Qt.Key_Backspace:
            self.sale_del_selected_item()

    def sale_del_selected_item(self):
        """Удаляем запись из таблицы при нажатии кнопки в sale_key_press_event"""
        logger.info("Запуск функции sale_del_selected_item")
        if self.ui.tableWidget_2.rowCount() > 0:
            current_row = self.ui.tableWidget_2.currentRow()
            # Перед удалением записи обновляем sale_dict
            type_ticket = self.ui.tableWidget_2.item(current_row, 2).text()
            # если checkbox в tableWidget_2 активирован, то обновляем details
            if type_ticket == 'взрослый':
                if self.ui.tableWidget_2.cellWidget(current_row,
                                                    7).findChild(QCheckBox).isChecked():
                    System.sale_dict['detail'][0] -= 1
                else:
                    System.sale_dict['kol_adult'] -= 1
                # если активирована скидка
                if self.ui.checkBox_2.isChecked():
                    index = self.ui.comboBox_2.currentIndex()
                    if index > 0:
                        System.sale_dict['detail'][0] -= 1
            elif type_ticket == 'детский':
                if self.ui.tableWidget_2.cellWidget(current_row,
                                                    7).findChild(QCheckBox).isChecked():
                    System.sale_dict['detail'][2] -= 1
                else:
                    System.sale_dict['kol_child'] -= 1
                # если активирована скидка
                if self.ui.checkBox_2.isChecked():
                    index = self.ui.comboBox_2.currentIndex()
                    if index > 0:
                        System.sale_dict['detail'][2] -= 1
            self.ui.tableWidget_2.removeRow(current_row)
            self.sale_edit_selling()
        row = self.ui.tableWidget_2.rowCount()
        # если таблица заказа пустая
        if row == 0:
            # отменяем скидку 100%
            self.ui.comboBox_2.setEnabled(True)
            self.ui.comboBox_2.setCurrentIndex(0)
            self.ui.checkBox_2.setEnabled(True)
            self.ui.checkBox_2.setChecked(False)
            # активируем кнопки оплаты и возврата
            self.ui.pushButton_5.setEnabled(True)
            self.ui.pushButton_6.setEnabled(True)
            # Обновляем System.sale_dict
            System.sale_dict['kol_adult'] = 0
            System.sale_dict['price_adult'] = 0
            System.sale_dict['kol_child'] = 0
            System.sale_dict['price_child'] = 0
            System.sale_dict['detail'][0] = 0
            System.sale_dict['detail'][1] = 0
            System.sale_dict['detail'][2] = 0
            System.sale_dict['detail'][3] = 0
            System.sale_dict['detail'][4] = 0
            System.sale_dict['detail'][5] = 0
            System.sale_dict['detail'][6] = 0
            System.sale_dict['detail'][7] = 0
            System.sale_discount = 0
            self.sale_edit_selling()

    def sale_check_filter_update(self):
        """Функция очистки lineEdit"""
        logger.info("Запуск функции sale_check_filter_update ")
        self.ui.lineEdit.clear()

    def sale_calendar_color_change(self):
        """Изменение цвета поля dateEdit"""
        logger.info("Запуск функции sale_calendar_color_change")
        get_date = str(self.ui.dateEdit.date())
        date_slice = get_date[21:(len(get_date) - 1)]
        logger.debug(date_slice)
        get_date = date_slice.replace(', ', '-')
        if System.check_day(get_date) == 1:
            self.ui.dateEdit.setStyleSheet('background-color: red;')
        else:
            self.ui.dateEdit.setStyleSheet('background-color: white;')

    def sale_check_discount_enabled(self):
        """Проверка активности поля со скидкой"""
        logger.info("Запуск функции sale_check_discount_enabled")
        if self.ui.checkBox_2.isChecked():
            self.ui.comboBox_2.setEnabled(True)
        else:
            self.ui.comboBox_2.setEnabled(False)
            self.ui.comboBox_2.setCurrentIndex(0)
            # отменяем скидку
            System.sale_discount = 0
            System.sale_dict['detail'][4] = 0
            # Обновляем в System.sale_dict информацию о скидках
            System.sale_dict['detail'][0] = 0
            System.sale_dict['detail'][1] = 0
            System.sale_dict['detail'][2] = 0
            System.sale_dict['detail'][3] = 0
            self.sale_edit_selling()

    @logger_wraps()
    def sale_search_clients(self):
        """Выводим в tableWidget список найденных клиентов"""
        logger.info("Запуск функции sale_search_clients")
        today = date.today()
        if System.what_a_day == 1:
            self.ui.dateEdit.setStyleSheet('background-color: red;')
        # вычисляем индекс значения
        index = self.ui.comboBox_4.currentIndex()
        if index == 2:
            # Поиск по номеру телефона
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
                # Вычисляем возраст клиента
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
            # Поиск по фамилии
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
                # Вычисляем возраст клиента
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
            # Поиск по фамилии и имени
            self.ui.tableWidget.setRowCount(0)
            search = self.ui.lineEdit.text().title()
            # разбиваем поисковую фразу на две
            lst = search.split()
            if len(lst) == 2:
                session = Session()
                search = session.query(Client).filter(and_(Client.first_name.ilike(
                    lst[1] + '%'), Client.last_name.ilike(
                    lst[0] + '%'))).all()
            else:
                windows.info_window('Неправильно задано условие для поиска',
                                    'Введите начальные буквы фамилии'
                                    'и имени через пробел', '')
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(
                    row, 0, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(
                    row, 1, QTableWidgetItem(f"{client.first_name}"))
                # Вычисляем возраст клиента
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
            # Поиск инвалидов
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
                # Вычисляем возраст клиента
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
            # Поиск многодетных
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
                # Вычисляем возраст клиента
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
    def sale_add_client_to_selling(self, *args, **kwargs):
        """
        Поиск выделенной строки в таблице клиентов
        и передача ее в таблицу заказа
        """
        logger.info("Запуск функции sale_add_client_to_selling")
        # Изменяем ширину столбцов
        self.ui.tableWidget_2.setColumnWidth(3, 5)
        self.ui.tableWidget_2.setColumnWidth(4, 5)
        self.ui.tableWidget_2.setColumnWidth(7, 40)
        self.ui.tableWidget_2.setColumnWidth(8, 5)
        self.ui.tableWidget_3.setColumnWidth(3, 7)
        type_ticket = ''
        today = date.today()
        # если продажа новая - обновляем статус
        System.sale_status = 0
        logger.warning("Статус продажи - новая %s" % System.sale_status)
        for idx in self.ui.tableWidget.selectionModel().selectedIndexes():
            # Номер строки найден
            row_number = idx.row()
            # Получаем содержимое ячейки
            res = self.ui.tableWidget.item(row_number, 5).text()
            session = Session()
            # Находим выделенного в таблице клиента
            search_client = session.query(Client).filter_by(id=res).first()
            session.close()
            # Вычисляем возраст клиента
            age = int(self.ui.tableWidget.item(row_number, 2).text())
            # Определяем тип билета и цену"""
            if age < System.age_min:
                type_ticket = 'бесплатный'
            if System.age_min <= age < System.age_max:
                type_ticket = 'детский'
            elif age >= System.age_max:
                type_ticket = 'взрослый'
            # Создаем виджет checkbox для скидки
            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            layoutH = QHBoxLayout(widget)
            layoutH.addWidget(checkbox)
            layoutH.setAlignment(Qt.AlignCenter)
            layoutH.setContentsMargins(0, 0, 0, 0)
            # Создаем виджет checkbox для исключения из продажи
            widget_1 = QWidget()
            checkbox_1 = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            layoutH = QHBoxLayout(widget_1)
            layoutH.addWidget(checkbox_1)
            layoutH.setAlignment(Qt.AlignCenter)
            layoutH.setContentsMargins(0, 0, 0, 0)
            row = self.ui.tableWidget_2.rowCount()
            self.ui.tableWidget_2.insertRow(row)
            # Добавляем checkbox скидки
            self.ui.tableWidget_2.setCellWidget(row, 7, widget)
            # Добавляем checkbox "присутствия" в продаже
            self.ui.tableWidget_2.setCellWidget(row, 8, widget_1)
            # Передаем в таблицу заказа данные клиента
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
            self.sale_edit_selling()
            # Очищаем tableWidget_3
            while self.ui.tableWidget_3.rowCount() > 0:
                self.ui.tableWidget_3.removeRow(0)
            # Ищем продажи, в которых клиент был ранее
            client_list = set()
            session = Session()
            sales = session.query(Client.id,
                                  Ticket.id,
                                  Ticket.id_sale).filter(and_(Client.id == search_client.id,
                                                              Ticket.id_client == search_client.id))
            for client_in_sales in sales:
                if client_in_sales:
                    logger.debug('Продажи, в которых клиент был ранее %s'
                                 % (client_in_sales))
                    # Находим других посетителей, которые были в этих продажах
                    search_sale = session.query(Ticket.id_sale,
                                                Ticket.id_client).filter(Ticket.id_sale == client_in_sales[2])
                    for search_cl in search_sale:
                        # Запрашиваем информацию об этих клиентах
                        client_list.add(search_cl[1])
            logger.debug('Другие посетители из найденных продаж %s' % client_list)
            # изменяем ширину столбов
            self.ui.tableWidget_3.setColumnWidth(2, 15)
            # выводим в tableWidget_3 список найденных клиентов
            for client in client_list:
                search_cl_in_sale = session.query(Client).filter_by(id=client).first()
                row = self.ui.tableWidget_3.rowCount()
                self.ui.tableWidget_3.insertRow(row)
                self.ui.tableWidget_3.setItem(
                    row, 0, QTableWidgetItem(f"{search_cl_in_sale.last_name}"))
                self.ui.tableWidget_3.setItem(
                    row, 1, QTableWidgetItem(f"{search_cl_in_sale.first_name}"))
                # Вычисляем возраст клиента
                age = (today.year - search_cl_in_sale.birth_date.year -
                       ((today.month, today.day) < (search_cl_in_sale.birth_date.month,
                                                    search_cl_in_sale.birth_date.day)))
                self.ui.tableWidget_3.setItem(
                    row, 2, QTableWidgetItem(f"{age}"))
                self.ui.tableWidget_3.setItem(
                    row, 3, QTableWidgetItem(f"{search_cl_in_sale.privilege}"))
                self.ui.tableWidget_3.setItem(
                    row, 4, QTableWidgetItem(f"{search_cl_in_sale.id}"))
                self.ui.tableWidget_3.setColumnHidden(4, True)
            session.close()

    @logger_wraps()
    def sale_add_client_to_selling_2(self, *args, **kwargs):
        """
        Поиск выделенной строки в таблице клиентов, которые были вместе
        в одной продаже, и передача ее в таблицу заказа
        """
        logger.info("Запуск функции sale_add_client_to_selling_2")
        type_ticket = ''
        for idx in self.ui.tableWidget_3.selectionModel().selectedIndexes():
            # "Номер строки найден
            row_number = idx.row()
            # Получаем содержимое ячейки
            res = self.ui.tableWidget_3.item(row_number, 4).text()
            age = int(self.ui.tableWidget_3.item(row_number, 2).text())
            session = Session()
            # Находим выделенного в таблице клиента
            search_client = session.query(Client).filter_by(id=res).first()
            session.close()
            # Определяем тип билета и цену
            if age < System.age_min:
                type_ticket = 'бесплатный'
            if System.age_min <= age < System.age_max:
                type_ticket = 'детский'
            elif age >= System.age_max:
                type_ticket = 'взрослый'
            # Создаём виджет checkbox для скидки
            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            layoutH = QHBoxLayout(widget)
            layoutH.addWidget(checkbox)
            layoutH.setAlignment(Qt.AlignCenter)
            layoutH.setContentsMargins(0, 0, 0, 0)
            # Создаем виджет checkbox для исключения из продажи
            widget_1 = QWidget()
            checkbox_1 = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            layoutH = QHBoxLayout(widget_1)
            layoutH.addWidget(checkbox_1)
            layoutH.setAlignment(Qt.AlignCenter)
            layoutH.setContentsMargins(0, 0, 0, 0)
            row = self.ui.tableWidget_2.rowCount()
            self.ui.tableWidget_2.insertRow(row)
            # добавляем checkbox
            self.ui.tableWidget_2.setCellWidget(row, 7, widget)
            # Добавляем checkbox "присутствия" в продаже
            self.ui.tableWidget_2.setCellWidget(row, 8, widget_1)
            # Передаем в таблицу заказа данные клиента
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
            self.sale_edit_selling()

    def sale_edit_selling(self):
        """
        Обновляем таблицу заказа, генерируем информацию
        о продаже и список билетов
        """
        logger.info("Запуск функцию sale_edit_selling")
        # считаем количество посетителей
        kol_adult = 0
        kol_child = 0
        # считаем количество посетителей со скидкой
        kol_sale_adult = 0
        kol_sale_child = 0
        # считаем количество посетителей с категорией
        kol_adult_many_child = 0
        kol_child_many_child = 0
        kol_adult_invalid = 0
        kol_child_invalid = 0
        # запоминаем id для "привязки" продажи ко взрослому
        id_adult = 0
        # учитываем продолжительность посещения
        time_ticket = self.ui.comboBox.currentText()
        # сохраняем билеты
        tickets = []
        # флаг "многодетные": 1 - 2 часа бесплатно, 2 - скидка 50%
        many_child = 0
        invalid = 0
        # считаем количество золотых талантов
        talent = 0
        # устанавливаем время и количество талантов
        if (int(time_ticket)) == 1:
            System.sale_dict['detail'][6] = 1
            talent = System.talent_1
        elif (int(time_ticket)) == 2:
            System.sale_dict['detail'][6] = 2
            talent = System.talent_2
        elif (int(time_ticket)) == 3:
            System.sale_dict['detail'][6] = 3
            talent = System.talent_3
        # записываем в sale_dict время посещения
        date_time = self.ui.dateEdit.date().toString("yyyy-MM-dd")
        # анализируем таблицу с заказом
        rows = self.ui.tableWidget_2.rowCount()
        for row in range(rows):
            # сегодня день многодетных?
            # проверяем категорию посетителя - если многодетный
            if self.ui.tableWidget_2.item(row, 4).text() == 'м':
                # проверяем если номер дня недели равен 7 и дата <= 7
                # установлена галочка "продление многодетным"
                if System.sunday == 1 and self.ui.checkBox_3.isChecked():
                    logger.info('Продление билетов многодетным')
                    # отменяем скидку 100%
                    many_child = 0
                    self.ui.checkBox_2.setEnabled(True)
                    self.ui.comboBox_2.setCurrentIndex(0)
                    self.ui.comboBox.setEnabled(True)
                elif System.sunday == 1:
                    # используем "флаг" many_child
                    many_child = 1
                    logger.info('Сегодня день многодетных')
                    # устанавливаем продолжительность посещения 2 часа
                    self.ui.comboBox.setCurrentIndex(1)
                    self.ui.comboBox.setEnabled(False)
                    # устанавливаем скидку
                    self.ui.checkBox_2.setEnabled(False)
                    self.ui.comboBox_2.setCurrentIndex(15)
                    self.ui.comboBox_2.setEnabled(False)
                    System.sale_dict['detail'][4] = 100
                    # отключаем кнопки оплаты и возврата
                    self.ui.pushButton_5.setEnabled(False)
                    self.ui.pushButton_6.setEnabled(False)
                # используем "флаг" many_child, для скидки 50%
                elif System.num_of_week <= 5:
                    many_child = 2
                    # устанавливаем скидку
                    self.ui.checkBox_2.setChecked(True)
                    self.ui.checkBox_2.setEnabled(False)
                    self.ui.comboBox_2.setCurrentIndex(10)
                    self.ui.comboBox_2.setEnabled(False)
                    System.sale_dict['detail'][4] = 50
            # проверяем категорию посетителя - если инвалид
            elif self.ui.tableWidget_2.item(row, 4).text() == 'и':
                invalid = 1
                System.sale_dict['detail'][4] = 100
                # изменяем продолжительность времени посещения
                self.ui.comboBox.setCurrentIndex(2)
                self.ui.comboBox.setEnabled(False)
                # устанавливаем скидку
                self.ui.checkBox_2.setEnabled(False)
                self.ui.comboBox_2.setCurrentIndex(15)
                self.ui.comboBox_2.setEnabled(False)
                # отключаем кнопки оплаты и возврата
                self.ui.pushButton_5.setEnabled(False)
                self.ui.pushButton_6.setEnabled(False)
            # учитываем тип билета
            type_ticket = self.ui.tableWidget_2.item(row, 2).text()
            # считаем взрослые билеты
            if type_ticket == 'взрослый':
                # если продолжительность посещения 1 час
                if System.sale_dict['detail'][6] == 1:
                    # сохраняем цену билета
                    price = System.ticket_adult_1
                elif System.sale_dict['detail'][6] == 2:
                    # если обычный день
                    if many_child == 0:
                        price = System.ticket_adult_2
                    else:
                        # если день многодетных
                        price = System.ticket_free
                        kol_adult_many_child += 1
                        # изменяем цену и записываем размер скидки
                        logger.debug('Добавляем взрослого мног-го в sale_dict[detail]')
                        System.sale_dict['detail'][0] = kol_adult_many_child
                        System.sale_dict['detail'][1] = price
                else:
                    # если продолжительность 3 часа
                    # если в продаже инвалид
                    if invalid == 1:
                        price = System.ticket_free
                        kol_adult_invalid += 1
                        # изменяем цену и записываем размер скидки
                        System.sale_dict['detail'][0] = kol_adult_invalid
                        System.sale_dict['detail'][1] = price
                    else:
                        price = System.ticket_adult_3
                # Привязываем продажу ко взрослому
                if id_adult == 0:
                    System.sale_dict['detail'][5] = self.ui.tableWidget_2.item(row, 5).text()
                # если checkbox активен - взрослый в оплату не добавляется
                # если QCheckBox активен
                if self.ui.tableWidget_2.cellWidget(row, 8).findChild(QCheckBox).isChecked():
                    # и номер строки не запоминали
                    logger.info(System.sale_checkbox_row)
                    if System.sale_checkbox_row is None:
                        logger.info('Исключаем взрослого из продажи')
                        System.sale_dict['detail'][0] = 1
                        System.sale_dict['detail'][4] = 100
                        # запоминаем номер строки с активным QCheckBox
                        System.sale_checkbox_row = row
                        # изменяем флаг активности QCheckBox
                        System.exclude_from_sale = 1
                # если QCheckBox не активен
                else:
                    # флаг состояния QCheckBox активирован
                    if System.exclude_from_sale == 1:
                        self.ui.tableWidget_2.cellWidget(
                            row, 8
                        ).findChild(QCheckBox).setEnabled(False)
                    # флаг состояния QCheckBox не активирован (вернули в продажу)
                    else:
                        logger.info('активируем QCheckBox строке')
                        self.ui.tableWidget_2.cellWidget(
                            row, 8
                        ).findChild(QCheckBox).setEnabled(True)
                # флаг состояния QCheckBox активирован
                if System.exclude_from_sale == 1:
                    # если отмеченный ранее QCheckBox не активен
                    if not self.ui.tableWidget_2.cellWidget(
                            System.sale_checkbox_row, 8
                    ).findChild(QCheckBox).isChecked():
                        logger.info('возвращаем в продажу')
                        System.sale_dict['detail'][0] = 0
                        System.sale_dict['detail'][1] = 0
                        System.sale_dict['detail'][4] = 0
                        System.sale_checkbox_row = None
                        System.exclude_from_sale = 0
                kol_adult += 1
                System.sale_dict['kol_adult'] = kol_adult
                System.sale_dict['price_adult'] = price
            # считаем детские билеты
            elif type_ticket == 'детский':
                # отключаем исключающий из продажи QCheckBox
                self.ui.tableWidget_2.cellWidget(
                    row, 8
                ).findChild(QCheckBox).setEnabled(False)
                # если продолжительность посещения 1 час
                if System.sale_dict['detail'][6] == 1:
                    # проверяем текущий день является выходным
                    if System.what_a_day == 0:
                        price = System.ticket_child_1
                    else:
                        price = System.ticket_child_week_1
                elif System.sale_dict['detail'][6] == 2:
                    # если продолжительность посещения 2 часа
                    # если не день многодетных
                    if many_child == 0:
                        # проверяем текущий день является выходным
                        if System.what_a_day == 0:
                            price = System.ticket_child_2
                        else:
                            price = System.ticket_child_week_2
                    # если день многодетных
                    else:
                        price = System.ticket_free
                        kol_child_many_child += 1
                        # применяем сидку
                        System.sale_dict['detail'][2] = kol_child_many_child
                        System.sale_dict['detail'][3] = price
                else:
                    # если продолжительность посещения 3 часа
                    # если в продаже инвалид
                    if invalid == 1:
                        price = System.ticket_free
                        kol_child_invalid += 1
                        # изменяем цену и записываем размер скидки
                        System.sale_dict['detail'][2] = kol_child_invalid
                        System.sale_dict['detail'][3] = price
                    elif System.what_a_day == 0:
                        price = System.ticket_child_3
                    else:
                        price = System.ticket_child_week_3
                kol_child += 1
                System.sale_dict['kol_child'] = kol_child
                System.sale_dict['price_child'] = price
            # считаем бесплатные билеты
            else:
                price = System.ticket_free
            # устанавливаем цену в таблицу и пересчитываем
            self.ui.tableWidget_2.setItem(
                row,
                3,
                QTableWidgetItem(f"{price}")
            )
            # применяем скидку
            logger.info('Применяем скидку')
            # в день многодетных
            if many_child == 1:
                logger.info('скидка 100% в день многодетных')
                self.ui.tableWidget_2.setItem(
                    row,
                    3,
                    QTableWidgetItem(f"{System.ticket_free}")
                )
                System.sale_status = 3
                logger.warning("Статус продажи - многодетные %s" % System.sale_status)
            # скидка 50% в будни
            elif many_child == 2:
                logger.info('скидка 50% многодетным в будни')
                self.ui.comboBox_2.setCurrentIndex(10)
                new_price = round(price * 0.5)
                self.ui.tableWidget_2.setItem(
                    row,
                    3,
                    QTableWidgetItem(f"{new_price}")
                )
            # скидка инвалидам
            elif invalid == 1:
                logger.info('скидка 100% инвалидам')
                self.ui.tableWidget_2.setItem(
                    row, 3, QTableWidgetItem(f"{System.ticket_free}"))
                System.sale_status = 4
                logger.warning("Статус продажи-инвалид %s" % System.sale_status)
            # иначе проверяем активен ли checkbox со скидкой и размер > 0
            if self.ui.checkBox_2.isChecked():
                logger.info('Checkbox со скидкой активен - обычный гость')
                if int(self.ui.comboBox_2.currentText()) > 0:
                    System.sale_discount = int(self.ui.comboBox_2.currentText())
                    logger.debug('Sale_discount %s' % System.sale_discount)
                    System.sale_dict['detail'][4] = System.sale_discount
                    if System.sale_discount > 0:
                        new_price = int(price -
                                        (price * System.sale_discount / 100))
                        # если checkbox в акт - применяем к этой строке скидку
                        if self.ui.tableWidget_2.cellWidget(
                                row,
                                7).findChild(QCheckBox).isChecked():
                            if type_ticket == 'взрослый':
                                kol_sale_adult += 1
                                logger.debug('kol_sale_adult %s' % kol_sale_adult)
                                System.sale_dict['detail'][0] = kol_sale_adult
                                System.sale_dict['detail'][1] = new_price
                            elif type_ticket == 'детский':
                                kol_sale_child += 1
                                logger.debug('kol_sale_child %s' % kol_sale_child)
                                System.sale_dict['detail'][2] = kol_sale_child
                                System.sale_dict['detail'][3] = new_price
                            self.ui.tableWidget_2.setItem(
                                row, 3, QTableWidgetItem(f"{new_price}")
                            )
        logger.debug('System.sale_dict %s' % System.sale_dict)
        itog = ((System.sale_dict['kol_adult'] -
                 System.sale_dict['detail'][0]) *
                System.sale_dict['price_adult']) + (
                       (System.sale_dict['kol_child'] -
                        System.sale_dict['detail'][2]) *
                       System.sale_dict['price_child']) + (
                       System.sale_dict['detail'][0] *
                       System.sale_dict['detail'][1]) + (
                       System.sale_dict['detail'][2] *
                       System.sale_dict['detail'][3])
        logger.debug('Итого %s' % itog)
        self.ui.label_8.setText(str(itog))
        System.sale_dict['detail'][7] = itog
        self.ui.label_5.setText(str(kol_adult))
        self.ui.label_7.setText(str(kol_child))
        self.ui.label_17.setText(str(kol_adult_many_child))
        self.ui.label_19.setText(str(kol_child_many_child))
        # Сохраняем данные продажи
        logger.debug('Sale_dict %s' % System.sale_dict)
        # Генерируем список с билетами
        for row in range(rows):
            tickets.append((self.ui.tableWidget_2.item(row, 0).text(),
                            # фамилия
                            self.ui.tableWidget_2.item(row, 1).text(),
                            # имя
                            self.ui.tableWidget_2.item(row, 2).text(),
                            # тип билета
                            self.ui.tableWidget_2.item(row, 3).text(),
                            # цена
                            self.ui.tableWidget_2.item(row, 4).text(),
                            # категория
                            self.ui.tableWidget_2.item(row, 5).text(),
                            # id взрослого
                            self.ui.tableWidget_2.item(row, 6).text(),
                            # возраст
                            time_ticket, talent, date_time))
        System.sale_tickets = tickets
        logger.info('System.sale_tickets %s' % System.sale_tickets)
        # Проверяем есть ли в продаже взрослый
        if System.sale_dict['kol_adult'] >= 1:
            # если в продаже не многодетные и не инвалиды
            if invalid != 1 and many_child != 1:
                # активируем кнопку оплаты
                self.ui.pushButton_5.setEnabled(True)
        else:
            self.ui.pushButton_5.setEnabled(False)

    def sale_save_selling(self):
        """Сохраняем данные продажи"""
        logger.info("Запуск функции sale_save_selling")
        logger.debug('Статус сохраняемой продажи %s' % System.sale_status)
        if System.sale_dict['kol_adult'] >= 1:
            add_sale = Sale(price=System.sale_dict['detail'][7],
                            id_user=System.user[3],
                            id_client=System.sale_dict['detail'][5],
                            status=System.sale_status,
                            discount=System.sale_dict['detail'][4],
                            pc_name=System.pc_name,
                            datetime=dt.datetime.now())
            logger.debug('Получена продажа %s' % add_sale)
            # Сохраняем продажу
            logger.debug("Сохраняем продажу в БД")
            session = Session()
            session.add(add_sale)
            try:
                session.commit()
            except exc.sa_exc.SQLAlchemyError as e:
                error = str(e.__dict__['orig'])
                session.rollback()
                logger.error('Ошибка при сохранении в БД: %s' % error)
                windows.info_window('Ошибка при сохранении в БД!', '', error)
            finally:
                session.close()
            # Получаем номер сохраненной продажи
            session = Session()
            System.sale_id = session.query(func.max(Sale.id)).scalar()
            session.close()
            # Сохраняем билеты
            type_ticket = None
            logger.debug("Сохраняем билеты в БД")
            session = Session()
            for i in range(len(System.sale_tickets)):
                # Считаем количество начисленных талантов
                if System.sale_tickets[i][2] == 'взрослый':
                    type_ticket = 0
                elif System.sale_tickets[i][2] == 'детский':
                    type_ticket = 1
                elif System.sale_tickets[i][2] == 'бесплатный':
                    type_ticket = 2
                add_ticket = Ticket(id_client=System.sale_tickets[i][5],
                                    id_sale=int(System.sale_id),
                                    arrival_time=System.sale_tickets[i][7],
                                    talent=System.sale_tickets[i][8],
                                    price=System.sale_tickets[i][3],
                                    description=System.sale_tickets[i][4],
                                    ticket_type=type_ticket,
                                    client_age=System.sale_tickets[i][6])
                session.add(add_ticket)
                logger.info('Сохраненный билет %s' % add_ticket)
            try:
                session.commit()
            except exc.sa_exc.SQLAlchemyError as e:
                error = str(e.__dict__['orig'])
                session.rollback()
                logger.error('Ошибка при сохранении в БД: %s' % error)
                windows.info_window('Ошибка при сохранении в БД!', '', error)
            finally:
                session.close()
            self.close()
        else:
            windows.info_window(
                'Ошибка при сохранении продажи',
                'Необходимо добавить в нее взрослого',
                ''
            )

    @logger.catch()
    def sale_transaction_selling(self, payment_type, print_check):
        """Проводим операцию продажи"""
        logger.info("Запуск функции sale_transaction_selling")
        # сохраняем продажу
        self.sale_save_selling()
        # если сумма продажи 0 - генерируем билеты
        if System.sale_dict['kol_adult'] == 0:
            self.sale_generate_saved_tickets()
        else:
            state_check, payment = kkt.check_open(System.sale_dict,
                                                  payment_type,
                                                  System.user,
                                                  1,
                                                  print_check)
            check = None
            # Если прошла оплата
            if state_check == 1:
                logger.info("Оплата прошла успешно")
                if print_check == 0:
                    windows.info_window('Оплата прошла успешно.', 'Чек не печатаем.', '')
                if payment == 1:  # если оплата банковской картой
                    logger.info("Читаем слип-чек из файла")
                    pinpad_file = r"C:\sc552\p"
                    with open(pinpad_file, 'r', encoding='IBM866') as file:
                        while line := file.readline().rstrip():
                            logger.debug(line)
                    check = kkt.read_slip_check()
                    # печать банковского чека: 1 - да, 0 - нет
                    if print_check == 1:
                        kkt.print_slip_check()
                if payment == 3:  # если оплата offline банковской картой
                    check = 'offline'
                # обновляем информацию о продаже в БД
                logger.info('Обновляем информацию о продаже в БД')
                session = Session()
                session.execute(update(Sale).where(
                    Sale.id == System.sale_id).values(
                    status=1,
                    id_user=System.user[3],
                    pc_name=System.pc_name,
                    payment_type=payment,
                    bank_pay=check,
                    datetime=dt.datetime.now()))
                try:
                    session.commit()
                except exc.sa_exc.SQLAlchemyError as e:
                    error = str(e.__dict__['orig'])
                    session.rollback()
                    logger.error('Ошибка при сохранении в БД: %s' % error)
                    windows.info_window('Ошибка при сохранении в БД!', '', error)
                finally:
                    session.close()
                # генерируем билеты
                self.sale_generate_saved_tickets()
                # сбрасываем статус продажи
                System.sale_status = 0
                self.close()
            else:
                logger.warning('Оплата не прошла')
                windows.info_window(
                    "Внимание",
                    'Закройте это окно, откройте сохраненную продажу и проведите'
                    'операцию оплаты еще раз.', '')

    @logger.catch()
    def sale_return_selling(self):
        """Проводим операцию возврата"""
        logger.info("Запуск функции sale_return_selling")
        # Обновляем данные о продаже
        self.sale_edit_selling()
        logger.info('Запрашиваем метод оплаты в БД')
        session = Session()
        payment_type_sale = session.query(Sale.payment_type).filter(
            Sale.id == System.sale_id).one()._asdict()
        session.close()
        logger.info(payment_type_sale)
        # 1 - карта, 2 - наличные
        if payment_type_sale.get('payment_type') == 1:
            payment_type = 101
        else:
            payment_type = 102
        logger.info(payment_type)
        state_check, payment = kkt.check_open(System.sale_dict,
                                              payment_type, System.user, 2)
        check = None
        # Если возврат прошел
        if state_check == 1:
            logger.info("Операция возврата прошла успешно")
            if payment == 1:  # если оплата банковской картой
                logger.info("Читаем слип-чек из файла")
                pinpad_file = r"C:\sc552\p"
                with open(pinpad_file, 'r', encoding='IBM866') as file:
                    while line := file.readline().rstrip():
                        logger.debug(line)
                check = kkt.read_slip_check()
            # записываем информацию о возврате в БД
            session = Session()
            session.execute(update(Sale).where(
                Sale.id == System.sale_id).values(
                status=2,
                user_return=System.user[3],
                pc_name=System.pc_name,
                payment_type=payment,
                bank_return=check,
                datetime_return=dt.datetime.now()))
            try:
                session.commit()
            except exc.sa_exc.SQLAlchemyError as e:
                error = str(e.__dict__['orig'])
                session.rollback()
                logger.error('Ошибка при сохранении в БД: %s' % error)
                windows.info_window('Ошибка при сохранении в БД!', '', error)
            finally:
                session.close()
            self.close()
        else:
            logger.warning('Операция возврата завершилась с ошибкой')
            windows.info_window(
                "Внимание",
                'Закройте это окно, откройте сохраненную продажу и проведите'
                'операцию возврата еще раз.', '')

    @logger.catch()
    def sale_generate_saved_tickets(self):
        """Генерируем список с ранее сохраненными билетами"""
        logger.info('Запуск функции sale_generate_saved_tickets')
        logger.info('Список билетов %s' % System.sale_tickets)
        client_in_sale = System.sale_tickets
        # Удаляем предыдущий файл с билетами
        os.system("TASKKILL /F /IM SumatraPDF.exe")
        if os.path.exists('./ticket.pdf'):
            os.remove('./ticket.pdf')
        # формируем билеты
        otchet.generate_saved_tickets(client_in_sale)
        # печатаем билеты
        subprocess.Popen([r'print.cmd'])
        System.sale_tickets = []

    def sale_open_pay(self, txt):
        """Открываем форму оплаты"""
        logger.info("Запуск функции sale_open_pay")
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
            logger.info('Оплата банковской картой')
            payment_type = Payment.Card
            # запустить оплату по терминалу
            self.sale_transaction_selling(payment_type, System.print_check)
        elif res == Payment.Cash:
            logger.info('Оплата наличными')
            payment_type = Payment.Cash
            self.sale_transaction_selling(payment_type, System.print_check)
        elif res == Payment.Offline:
            logger.info('Оплата банковской картой offline')
            payment_type = Payment.Offline
            self.sale_transaction_selling(payment_type, System.print_check)
        # Закрываем окно продажи и возвращаем QDialog.Accepted
        self.accept()


class Payment:
    """Тип платежа (перечисление)"""
    Card = 101
    Cash = 102
    Offline = 100


class System:
    """Системная информация"""
    user = None
    # флаг для обновления клиента
    client_id = None
    client_update = None
    all_clients = None
    # сохраняем фамилию нового клиента
    last_name = ''
    # статус продажи: 0 - создана, 1 - оплачена,
    #                 2 - возвращена, 3 - многодетный,
    #                 4 - инвалид
    sale_status = None
    sale_id = None
    sale_discount = None
    sale_tickets = []
    sale_tuple = []
    # номер строки с активным CheckBox для исключения взрослого из продажи
    sale_checkbox_row = None
    # состояние CheckBox для искл. взрослого из продажи: 0 - есть, 1 - нет
    exclude_from_sale = 0
    # какой сегодня день: 0 - будний, 1 - выходной
    what_a_day = None
    # первое воскресенье месяца: 0 - нет, 1 - да
    sunday = None
    today = date.today()
    num_of_week = 0
    pc_name = socket.gethostname()
    # стоимость билетов
    ticket_child_1 = 300
    ticket_child_2 = 600
    ticket_child_3 = 900
    ticket_child_week_1 = 300
    ticket_child_week_2 = 600
    ticket_child_week_3 = 900
    ticket_adult_1 = 150
    ticket_adult_2 = 200
    ticket_adult_3 = 250
    ticket_free = 0
    # количество начисляемых талантов
    talent_1 = 25
    talent_2 = 35
    talent_3 = 50
    # возраст посетителей
    age_min = 5
    age_max = 15
    # информация о РМ
    kol_pc = 0
    pc_1 = ''
    pc_2 = ''
    sale_dict = {'kol_adult': 0, 'price_adult': 0,
                 'kol_child': 0, 'price_child': 0,
                 'detail': [0, 0, 0, 0, 0, 0, 0, 0]}

    # 'detail': [kol_adult, price_adult, kol_child, price_child,
    #            discount, id_adult, time, sum]

    # храним id нового клиента
    id_new_client_in_sale = 0
    # флаг печати кассовых и банковских чеков
    print_check = 1

    @staticmethod
    def user_authorization(login, password):
        """Авторизация кассира"""
        logger.info('Запуск функции user_authorization')
        session = Session()
        kassir = session.query(User.last_name,
                               User.first_name,
                               User.inn,
                               User.id).filter(and_(User.login ==
                                                    login,
                                                    User.password ==
                                                    password)).first()
        session.close()
        if kassir:
            # сохраняем данные авторизовавшегося кассира
            System.user = kassir
            return 1

    def check_day(self, day=dt.datetime.now().strftime('%Y-%m-%d')):
        """Проверяем статус дня: выходной ли это"""
        logger.info('Запуск функции check_day')
        session = Session()
        # текущая дата есть в списке дополнительных рабочих дней?
        check_day = session.query(Workday.date).filter(
            Workday.date == day).first()
        session.close()
        if check_day:
            logger.info('Сегодня дополнительный рабочий день')
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
                logger.info('Сегодня выходной день')
            else:
                day = '-'.join(day)
                session = Session()
                # текущая дата есть в списке праздничных дней?
                check_day = session.query(Holiday.date).filter(
                    Holiday.date == day).all()  # all?
                session.close()
                if check_day:
                    status = 1
                    System.what_a_day = 1
                    logger.info('Сегодня дополнительный выходной')
                else:
                    status = 0
        return status

    def check_one_sunday(self):
        """Проверяем день многодетных"""
        logger.info("Запуск функции check_one_sunday")
        day = 0
        num_of_week = None
        # если сегодня выходной
        if System.what_a_day == 1:
            # проверяем если номер дня недели равен 7 и дата <= 7
            num_of_week = dt.datetime.today().isoweekday()
            date_num = date.today().day
            if num_of_week == 7 and date_num <= 7:
                logger.info("Сегодня день многодетных")
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
        self.ui.checkBox.setChecked(True)
        self.ui.checkBox.stateChanged.connect(self.check_print)
        # Посылаем сигнал генерации чека
        # self.ui.pushButton.clicked.connect(self.startGenerate.emit)
        # при вызове done() окно должно закрыться и exec_
        # вернет переданный аргумент из done()
        self.ui.pushButton.clicked.connect(lambda: self.done(Payment.Cash))
        self.ui.pushButton_2.clicked.connect(lambda: self.done(Payment.Card))
        self.ui.pushButton_3.clicked.connect(lambda: self.done(Payment.Offline))

    def setText(self, txt):
        """Устанавливаем текстовое значение в метку"""
        logger.info("Запуск функции setText")
        self.ui.label_2.setText(txt)
        # по умолчанию печатаем чек
        System.print_check = 1

    def check_print(self):
        logger.info("Запуск функции check_print")
        if self.ui.checkBox.isChecked():
            System.print_check = 1
        else:
            System.print_check = 0


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
