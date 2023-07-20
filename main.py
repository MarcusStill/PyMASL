import calendar
import datetime as dt
import os
import socket
import subprocess
import sys
from configparser import ConfigParser
from datetime import date, timedelta
from design.main_form import Ui_MainWindow

from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QCheckBox, QDialog
from PySide6.QtCore import Qt, Signal
from typing import Type
from design.pay import Ui_Dialog_Pay

from design.sale import Ui_Dialog_Sale
from files import windows
from files.logger import *
import design.pay as pay
from design.authorization import Ui_Dialog
from loguru import logger
from db.models import Client
from db.models import Holiday
from db.models import Sale
from db.models import Ticket
from db.models import Workday
from db.models.user import User
from db.models.sale_service import SaleService
from sqlalchemy import engine, and_, select, func, update, desc
from PySide6.QtGui import QPixmap
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, exc
from design.client import Ui_Dialog_Client
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QCheckBox, QDialog, QHBoxLayout
from PySide6.QtWidgets import QMainWindow, QTableWidgetItem, QWidget
from PySide6 import QtCore  #, QtSql


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


engine = create_engine("postgresql+psycopg2://postgres:" + pswrd + "@" + host + ":" + port + "/" + database, echo=True)

logger.add(log_file, rotation="1 MB")

class AuthForm(QDialog):
    """Форма авторизации"""

    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        # Добавляем логотип на форму
        pixmap = QPixmap('pylogo.png')
        self.ui.label_4.setPixmap(pixmap)
        self.ui.label_7.setText(software_version)
        self.ui.pushButton.clicked.connect(self.starting_the_main_form)
        self.ui.pushButton_2.clicked.connect(self.close)

    def starting_the_main_form(self) -> None:
        """
        Функция выполняет следующее:
        - проверяет правильность ввода пользователем данных на форме авторизации;
        - проверяет статус текущего дня (обычный день, праздничный, день многодетных);
        - устанавливает параметров главной формы (размер окна, отображение списка продаж, загрузка доп. параметров).
        """
        logger.info("Запуск функции starting_the_main_form")
        login:str = self.ui.lineEdit.text()
        password:str = self.ui.lineEdit_2.text()
        kassir:int = System.user_authorization(login, password)
        if kassir == 1:
            # После закрытия окна авторизации открываем главную форму
            auth.close()
            # Устанавливаем размер окна
            window = MainWindow()
            window.showMaximized()
            # Добавляем в заголовок дополнительную информацию
            window.setWindowTitle('PyMASL ver. ' + software_version + '. Пользователь: ' +
                                  str(System.user.first_name) + ' ' + str(System.user.last_name) + '. БД: ' + database)
            # отображаем записи на форме продаж
            window.main_button_all_sales()
            # проверяем статус текущего дня
            day_today:int = System.check_day(self)
            logger.info('Статус текущего дня %s' % day_today)
            if day_today == 0:
                System.what_a_day = 0
                logger.info("Сегодня будний день. System.what_a_day = %s" % System.what_a_day)
            elif day_today == 1:
                System.what_a_day = 1
                logger.info("Сегодня выходной день. System.what_a_day = %s" % System.what_a_day)
            # проверяем номер дня в неделе
            number_day_of_the_week:int = dt.datetime.today().isoweekday()
            logger.debug('Номер дня в неделе: %s' % number_day_of_the_week)
            System.num_of_week = number_day_of_the_week
            # проверяем номер дня в месяце
            number_day_of_the_month:int = date.today().day
            logger.info("Номер дня в месяце:  %s" % number_day_of_the_month)
            if number_day_of_the_week == 7 and number_day_of_the_month <= 7:
                logger.info("Сегодня день многодетных")
                System.sunday = 1
            # считываем количество РМ и имена
            System.kol_pc = kol_pc
            System.pc_1 = pc_1
            System.pc_2 = pc_2
            window.show()
            window.exec_()
        else:
            logger.warning("Неудачная авторизация пользователя %s" % login)
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
        """
        Функция запоминает фамилию нового клиента для последующей вставки.
        Полезна при внесении в БД сведений об однофамильцах.
        """
        logger.info("Запуск функции client_data_copy")
        System.last_name = str(self.ui.lineEdit.text()).title()

    def client_data_paste(self):
        """
        Функция вставляет в соответствующее поле заранее сохраненную фамилию клиента,
        внесенного в БД в предыдущий раз
        """
        logger.info("Запуск функции client_data_paste")
        self.ui.lineEdit.setText(System.last_name)

    def client_data_save(self):
        """Функция сохраняет в БД сведения о новом клиенте"""
        logger.info("Запуск функции client_data_save")
        # сбрасываем id последнего добавленного клиента
        System.add_new_client_in_sale = 0
        # делаем заглавными первые буквы фамилии и имени
        System.last_name = str(self.ui.lineEdit.text()).title()
        first_name = str(self.ui.lineEdit_2.text()).title()
        # проверяем заполнены ли поля имени и фамилии
        if len(System.last_name) >= 2 and len(first_name) >= 2:
            if System.client_update != 1:
                logger.info('Добавляем нового клиента')
                with Session(engine) as session:
                    # # получаем максимальный id в таблице клиентов
                    query = func.max(Client.id)
                    client_index: int = session.execute(query).scalars().first()
                    logger.debug('Количество клиентов в бд: %s' % client_index)
                    new_client = Client(
                        id=client_index + 1,
                        last_name=System.last_name,
                        first_name=str(self.ui.lineEdit_2.text()),
                        middle_name=str(self.ui.lineEdit_3.text()),
                        birth_date=(self.ui.dateEdit.date().toString("yyyy-MM-dd")),
                        gender=str(self.ui.comboBox.currentText()),
                        phone=self.ui.lineEdit_4.text(),
                        email=self.ui.lineEdit_5.text(),
                        privilege=str(self.ui.comboBox_2.currentText())
                    )
                    session.add(new_client)
                    session.commit()
                # сохраняем id нового клиента
                System.id_new_client_in_sale = client_index + 1
            elif System.client_update == 1:
                # обновляем информацию о клиенте
                logger.info('Обновляем информацию о клиенте')
                with Session(engine) as session:
                    session.execute(
                        update(Client).where(Client.id == System.client_id).values(
                            id=System.client_id,
                            last_name=str(self.ui.lineEdit.text()),
                            first_name=str(self.ui.lineEdit_2.text()),
                            middle_name=str(self.ui.lineEdit_3.text()),
                            birth_date=self.ui.dateEdit.date().toString("yyyy-MM-dd"),
                            gender=str(self.ui.comboBox.currentText()),
                            phone=self.ui.lineEdit_4.text(),
                            email=self.ui.lineEdit_5.text(),
                            privilege=str((self.ui.comboBox_2.currentText()))
                        )
                    )
                    session.commit()
            self.close()
            System.client_update = None
            System.client_id = None
        else:
            windows.info_window('Внимание!',
                                'Необходимо заполнить обязательные поля: имя и фамилия',
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
            query = '%' + self.ui.lineEdit.text() + '%'
            with Session(engine) as session:
                search: list[Type[Client]] = session.query(Client).filter(Client.phone.like(query)).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(f"{client.first_name}"))
                # Вычисляем возраст клиента
                age = (today.year - client.birth_date.year - (
                        (today.month, today.day) < (client.birth_date.month, client.birth_date.day)
                ))
                self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(f"{age}"))
                self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(5, True)
        elif index == 1:
            # Поиск по фамилии
            query = '%' + self.ui.lineEdit.text() + '%'
            self.ui.tableWidget.setRowCount(0)
            with Session(engine) as session:
                search: list[Type[Client]] = session.query(Client).filter(Client.last_name.ilike(query)).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(f"{client.first_name}"))
                # Вычисляем возраст клиента
                age = (today.year - client.birth_date.year - (
                        (today.month, today.day) < (client.birth_date.month, client.birth_date.day)
                ))
                self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(f"{age}"))
                self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(5, True)
        elif index == 0:
            # Поиск по фамилии и имени
            self.ui.tableWidget.setRowCount(0)
            search = self.ui.lineEdit.text().title()
            # разбиваем поисковую фразу на две
            lst = search.split()
            if len(lst) == 2:
                with Session(engine) as session:
                    search: list[Type[Client]] = session.query(Client).filter(and_(Client.first_name.ilike(
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
                age = (today.year - client.birth_date.year - (
                        (today.month, today.day) < (client.birth_date.month, client.birth_date.day)
                ))
                self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(f"{age}"))
                self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(5, True)
        elif index == 3:
            # Поиск инвалидов
            self.ui.tableWidget.setRowCount(0)
            with Session(engine) as session:
                search: list[Type[Client]] = session.query(Client).filter(Client.privilege.ilike('%' + 'и')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(f"{client.first_name}"))
                # Вычисляем возраст клиента
                age = (today.year - client.birth_date.year - (
                        (today.month, today.day) < (client.birth_date.month, client.birth_date.day)
                ))
                self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(f"{age}"))
                self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(5, True)
        elif index == 4:
            # Поиск многодетных
            self.ui.tableWidget.setRowCount(0)
            with Session(engine) as session:
                search: list[Type[Client]] = session.query(Client).filter(Client.privilege.ilike('%' + 'м')).all()
            for client in search:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row)
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(f"{client.last_name}"))
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(f"{client.first_name}"))
                # Вычисляем возраст клиента
                age = (today.year - client.birth_date.year - (
                        (today.month, today.day) < (client.birth_date.month, client.birth_date.day)
                ))
                self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(f"{age}"))
                self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(f"{client.privilege}"))
                self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(f"{client.phone}"))
                self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(f"{client.id}"))
                self.ui.tableWidget.setColumnHidden(5, True)

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
                # активируем поле со скидкой
                self.ui.tableWidget_2.cellWidget(row, 7).findChild(QCheckBox).setCheckState(Qt.Checked)
                # проверяем если номер дня недели равен 7 и дата <= 7
                # установлена галочка "продление многодетным"
                if System.sunday == 1 and self.ui.checkBox_3.isChecked():
                    logger.info('Продление билетов многодетным')
                    # отменяем скидку 100%
                    many_child = 0
                    self.ui.checkBox_2.setEnabled(True)
                    self.ui.checkBox_2.setChecked(True)
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
                    # отключаем кнопку возврата
                    self.ui.pushButton_6.setEnabled(False)
                # используем "флаг" many_child, для скидки 50%
                elif System.num_of_week <= 5:
                    logger.info('Многодетным скидка 50%')
                    many_child = 2
                    # устанавливаем скидку
                    self.ui.checkBox_2.setChecked(True)
                    self.ui.checkBox_2.setEnabled(True)
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
                # отключаем кнопки сохранения и возврата
                self.ui.pushButton_3.setEnabled(False)
                self.ui.pushButton_6.setEnabled(False)
            # если стоит флаг 'н' - исключаем из продажи
            elif self.ui.tableWidget_2.item(row, 4).text() == 'н':
                self.ui.tableWidget_2.cellWidget(row, 8).findChild(QCheckBox).setCheckState(Qt.Checked)
            # учитываем тип билета
            type_ticket = self.ui.tableWidget_2.item(row, 2).text()
            # считаем взрослые билеты
            if type_ticket == 'взрослый':
                # если продолжительность посещения 1 час
                if System.sale_dict['detail'][6] == 1:
                    # сохраняем цену билета
                    price = System.ticket_adult_1
                elif System.sale_dict['detail'][6] == 2:
                    # если день многодетных
                    if many_child == 1:
                        price = System.ticket_free
                        kol_adult_many_child += 1
                        # изменяем цену и записываем размер скидки
                        logger.debug('Добавляем взрослого мног-го в sale_dict[detail]')
                        System.sale_dict['detail'][0] = kol_adult_many_child
                        System.sale_dict['detail'][1] = price
                    # если обычный день
                    else:
                        price = System.ticket_adult_2
                else:
                    # если продолжительность 3 часа
                    # если в продаже инвалид
                    if invalid == 1:
                        price = System.ticket_free
                        kol_adult_invalid += 1
                        # изменяем цену и записываем размер скидки
                        System.sale_dict['detail'][0] = kol_adult_invalid
                        System.sale_dict['detail'][1] = price
                        # меняем категорию билета на 'c' - сопровождающий
                        self.ui.tableWidget_2.setItem(
                            row, 4, QTableWidgetItem('с'))
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
                        # ставим метку "не идет"
                        self.ui.tableWidget_2.setItem(
                            row, 4, QTableWidgetItem('н'))
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
                        self.ui.tableWidget_2.setItem(
                            row, 4, QTableWidgetItem('-'))
                        self.ui.tableWidget_2.setItem(
                            row, 4, QTableWidgetItem(price))
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
                    # если день многодетных
                    if many_child == 1:
                        price = System.ticket_free
                        kol_child_many_child += 1
                        # применяем сидку
                        System.sale_dict['detail'][2] = kol_child_many_child
                        System.sale_dict['detail'][3] = price
                    # если обычный день
                    else:
                        # проверяем текущий день является выходным
                        if System.what_a_day == 0:
                            price = System.ticket_child_2
                        else:
                            price = System.ticket_child_week_2
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
                logger.debug("В продаже многодетные")
                # помечаем продажу как "особенную"
                System.sale_special = 1
                logger.debug('Продажа особенная %s' % System.sale_special)
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
                logger.debug("В продаже инвалид")
                # помечаем продажу как "особенную"
                System.sale_special = 1
                logger.debug('Продажа особенная %s' % System.sale_special)
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
            # если установлена метка "не идет"
            if self.ui.tableWidget_2.item(row, 4).text() == 'н':
                # изменяем цену
                logger.debug('Изменяем цену в билете посетителя!')
                self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f'{System.ticket_free}'))
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
            self.ui.pushButton_5.setEnabled(True)
        else:
            self.ui.pushButton_5.setEnabled(False)

    def sale_save_selling(self):
        """Сохраняем данные продажи"""
        logger.info("Запуск функции sale_save_selling")
        logger.debug('Статус сохраняемой продажи %s' % System.sale_status)
        # если продажа особенная - сохраним ее статус оплаченной
        if System.sale_special == 1:
            System.sale_status = 1
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
        logger.debug('System.sale_status: %s' % System.sale_status)
        logger.debug('System.sale_id: %s' % System.sale_id)
        # если продажа новая
        if System.sale_id is None:
            self.sale_save_selling()
        # если продажа особенная - генерируем билеты без оплаты
        if System.sale_special == 1:
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
        state_check, payment = kkt.check_open(System.sale_dict,
                                              payment_type, System.user, 2, 1)
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
        """Функция генерирует список с ранее сохраненными билетами"""
        logger.info('Запуск функции sale_generate_saved_tickets')
        logger.info('Список билетов %s' % System.sale_tickets)
        client_in_sale: tuple = System.sale_tickets
        # Удаляем существующий файл с билетами
        os.system("TASKKILL /F /IM SumatraPDF.exe")
        if os.path.exists('./ticket.pdf'):
            os.remove('./ticket.pdf')
        # Формируем новый файл с билетами
        otchet.generate_saved_tickets(client_in_sale)
        # Печатаем билеты
        subprocess.Popen([r'print.cmd'])
        System.sale_tickets = []

    def sale_open_pay(self, txt):
        """Функция открывает окно оплаты"""
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
            # Оплата банковской картой
            logger.info('Оплата банковской картой')
            payment_type = Payment.Card
            # запускаем оплату по терминалу
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

class PayForm(QDialog):
    """Форма оплаты"""
    startGenerate = Signal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_Pay()
        self.ui.setupUi(self)
        # self.ui.checkBox.setChecked(True)
        # self.ui.checkBox.stateChanged.connect(self.check_print)
        # # Посылаем сигнал генерации чека
        # # self.ui.pushButton.clicked.connect(self.startGenerate.emit)
        # # при вызове done() окно должно закрыться и exec_
        # # вернет переданный аргумент из done()
        # self.ui.pushButton.clicked.connect(lambda: self.done(Payment.Cash))
        # self.ui.pushButton_2.clicked.connect(lambda: self.done(Payment.Card))
        # self.ui.pushButton_3.clicked.connect(lambda: self.done(Payment.Offline))

    def setText(self, txt):
        """Устанавливаем текстовое значение в метку"""
        logger.info("Запуск функции setText")
        self.ui.label_2.setText(txt)
        # по умолчанию печатаем чек
        System.print_check = 1

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """Главная форма"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Открыть окно добавления нового клиента
        self.ui.pushButton_2.clicked.connect(self.main_open_client)
        self.ui.pushButton_23.clicked.connect(self.main_open_sale)

    def main_search_clients(self):
        """
        Выводим в tableWidget (вкладка "посетители")
        отфильтрованный список клиентов
        """
        pass

    def main_edit_client(self):
        """
        Поиск выделенной строки в таблице клиентов
        и открытие формы для редактирования
        """
        pass

    def main_filter_clear(self):
        """
        Передаем значение пользовательского
        фильтра в модель QSqlTableModel
        """
        pass

    def main_search_selected_sale(self):
        """
        Поиск выделенной строки в таблице продаж
        и открытие формы с полученными данными
        """
        pass

    def main_button_all_sales(self):
        """Фильтр продаж в tableWidget за 1, 3 и 7 дней"""
        pass

    def main_open_client(self):
        """Открываем форму с данными клиента"""
        client = ClientForm()
        client.show()
        client.exec()

    def main_open_sale(self):
        """Открываем форму с продажей"""
        sale = SaleForm()
        sale.show()
        sale.exec()

    def main_get_statistic(self):
        """Генерация сводной информации о продажах и билетах"""
        pass

    def main_otchet_administratora(self):
        """Формирование отчета администратора"""
        pass

    def main_otchet_kassira(self):
        """Формирование отчета кассира"""
        pass


class Payment:
    """Тип платежа (перечисление)"""
    Card = 101
    Cash = 102
    Offline = 100


class System:
    """Системная информация"""
    # данные успешно авторизованного пользователя
    user = None
    # флаг для обновления клиента
    client_id = None
    client_update = None
    all_clients = None
    # сохраняем фамилию нового клиента
    last_name = ''
    # статус продажи: 0 - создана, 1 - оплачена, 2 - возвращена
    sale_status = None
    sale_id = None
    sale_discount = None
    sale_tickets = ()
    sale_tuple = ()
    sale_special = None
    # номер строки с активным CheckBox для исключения взрослого из продажи
    sale_checkbox_row = None
    # состояние CheckBox для искл. взрослого из продажи: 0 - есть, 1 - нет
    exclude_from_sale = 0
    # какой сегодня день: 0 - будний, 1 - выходной
    what_a_day = None
    # первое воскресенье месяца: 0 - нет, 1 - да
    sunday = None
    today = date.today()
    # номер дня недели
    mumber_day_of_the_week = 0
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
    def user_authorization(login, password) -> int:
        """Функция проверяет есть ли пользователь, данные которого указаны на форме авторизации, в БД"""
        logger.info('Запуск функции user_authorization')
        with Session(engine) as session:
            query = select(User).where(User.login == login, User.password == password)
            kassir: User | None = session.execute(query).scalars().first()
        if kassir:
            # если авторизация прошла успешно - сохраняем данные пользователя
            System.user = kassir
            return 1

    def check_day(self, day=dt.datetime.now().strftime('%Y-%m-%d')) -> int:
        """Проверяем статус дня: выходной ли это"""
        logger.info('Запуск функции check_day')
        # проверяем есть ли текущая дата в списке дополнительных рабочих дней
        with Session(engine) as session:
            query = select(Workday).where(Workday.date == day)
            check_day: Workday | None = session.execute(query).scalars().first()
        if check_day:
            logger.info('Сегодня дополнительный рабочий день')
            status_day: int = 0
        else:
            # преобразуем текущую дату в список
            day:list[str] = day.split('-')
            # вычисляем день недели
            number_day:int = calendar.weekday(int(day[0]), int(day[1]), int(day[2]))
            # проверяем день недели равен 5 или 6
            if number_day >= 5:
                status_day: int = 1
                # System.what_a_day = 1 TODO: нужно ли
                logger.info('Сегодня выходной день')
            else:
                day:str = '-'.join(day)
                # проверяем есть ли текущая дата в списке дополнительных праздничных дней
                with Session(engine) as session:
                    query = select(Holiday).where(Holiday.date == day)
                    check_day: Holiday | None = session.execute(query).scalars().first()
                if check_day:
                    status_day: int = 1
                    # System.what_a_day = 1 TODO: нужно ли
                    logger.info('Сегодня дополнительный выходной')
                else:
                    status_day: int = 0
        return status_day


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    auth = AuthForm()
    auth.show()
    #auth.ui.label_9.setText(database)
    sys.exit(app.exec())

    # window = MainWindow()
    # window.show()
    # sys.exit(app.exec())