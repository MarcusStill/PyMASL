import calendar
import datetime as dt
import os
import socket
import subprocess
import sys
from configparser import ConfigParser
from datetime import date, timedelta
from design.main_form import Ui_MainWindow

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QApplication, QCheckBox, QDialog
from PySide6.QtCore import Qt, Signal
from typing import Any, Type
from design.pay import Ui_Dialog_Pay

from design.sale import Ui_Dialog_Sale
from files import windows
from files.logger import *
import design.pay as pay
from files import kkt
from files import otchet
from design.authorization import Ui_Dialog
from loguru import logger
from db.models import Client
from db.models import Holiday
from db.models import Sale
from db.models import Ticket
from db.models import Workday
from db.models.user import User
from db.models.price import Price
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
        Функция запускает предпродажные проверки и устанавливает системные параметры.
        Она выполняет следующее:
        - проверяет правильность ввода пользователем данных на форме авторизации;
        - проверяет статус текущего дня (обычный день, праздничный, день многодетных);
        - устанавливает параметров главной формы (размер окна, отображение списка продаж, загрузка доп. параметров).

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции starting_the_main_form")
        login: str = self.ui.lineEdit.text()
        password: str = self.ui.lineEdit_2.text()
        kassir: int = System.user_authorization(self, login, password)
        if kassir == 1:
            # После закрытия окна авторизации открываем главную форму
            auth.close()
            # Устанавливаем размер окна
            window = MainWindow()
            window.showMaximized()
            System.get_price(self)
            # Добавляем в заголовок дополнительную информацию
            window.setWindowTitle('PyMASL ver. ' + software_version + '. Пользователь: ' +
                                  str(System.user.first_name) + ' ' + str(System.user.last_name) + '. БД: ' + database)
            # отображаем записи на форме продаж
            window.main_button_all_sales()
            # проверяем статус текущего дня
            day_today: int = System.check_day(self)
            logger.info('Статус текущего дня %s' % day_today)
            if day_today == 0:
                System.what_a_day = 0
                logger.info("Сегодня будний день. System.what_a_day = %s" % System.what_a_day)
            elif day_today == 1:
                System.what_a_day = 1
                logger.info("Сегодня выходной день. System.what_a_day = %s" % System.what_a_day)
            # проверяем номер дня в неделе
            number_day_of_the_week: int = dt.datetime.today().isoweekday()
            logger.debug('Номер дня в неделе: %s' % number_day_of_the_week)
            System.num_of_week = number_day_of_the_week
            # проверяем номер дня в месяце
            number_day_of_the_month: int = date.today().day
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
        Функция вставляет в соответствующее поле фамилию клиента,
        внесенного в БД в последний раз.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции client_data_paste")
        self.ui.lineEdit.setText(System.last_name)

    def client_data_save(self):
        """
        Функция сохраняет в БД сведения о новом клиенте.

        Параметры:

        Возвращаемое значение:
        """
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
        self.ui.pushButton_11.clicked.connect(self.edit_client_in_sale)
        self.ui.pushButton_3.clicked.connect(self.save_sale)
        self.ui.pushButton_4.clicked.connect(self.close)
        self.ui.pushButton_5.clicked.connect(
            lambda: self.open_pay_form(self.ui.label_8.text()))
        self.ui.pushButton_6.clicked.connect(self.sale_return)
        self.ui.pushButton_7.clicked.connect(self.sale_generate_saved_tickets)
        self.ui.tableWidget.doubleClicked.connect(self.adding_client_to_sale)
        cur_today = date.today()
        self.ui.dateEdit.setDate(cur_today)
        self.ui.dateEdit.dateChanged.connect(self.changing_color_of_calendar)
        self.ui.comboBox.currentTextChanged.connect(self.sale_update)
        self.ui.checkBox_2.stateChanged.connect(self.checking_status_discounted_field)
        self.ui.comboBox_2.currentTextChanged.connect(self.sale_update)
        # Адаптированный для пользователя фильтр
        self.ui.comboBox_4.currentTextChanged.connect(self.check_filter_update)
        # KeyPressEvent
        self.ui.tableWidget_2.keyPressEvent = self.tracking_button_pressing
        self.ui.pushButton_9.clicked.connect(self.adding_new_client_to_sale)
        self.ui.pushButton_10.clicked.connect(self.sale_update)
        self.ui.tableWidget_3.doubleClicked.connect(self.adding_related_client_to_sale)
        self.ui.pushButton_12.clicked.connect(self.clearing_client_list)

    def edit_client_in_sale(self) -> None:
        """
        Функция ищет выделенную строку в таблице клиентов и открывает форму для редактирования данных.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции edit_client_in_sale")
        # Ищем индекс и значение ячейки
        row_number: int = self.ui.tableWidget.currentRow()
        # Получаем содержимое ячейки
        client_id: str = self.ui.tableWidget.item(row_number, 5).text()
        with Session(engine) as session:
            search_client: Type[Client] = session.query(Client).filter_by(id=client_id).first()
        # Сохраняем id клиента
        System.client_id = search_client.id
        # Передаем в форму данные клиента
        client = ClientForm()
        client.ui.lineEdit.setText(search_client.last_name)
        client.ui.lineEdit_2.setText(search_client.first_name)
        client.ui.lineEdit_3.setText(search_client.middle_name)
        client.ui.dateEdit.setDate(search_client.birth_date)
        # Поиск значения для установки в ComboBox gender
        index_gender: int = client.ui.comboBox.findText(
            search_client.gender, Qt.MatchFixedString)
        if index_gender >= 0:
            client.ui.comboBox.setCurrentIndex(index_gender)
        client.ui.lineEdit_4.setText(search_client.phone)
        client.ui.lineEdit_5.setText(search_client.email)
        # Ищем значение для установки в ComboBox privilege
        index_privilege: int | None = client.ui.comboBox.findText(search_client.privilege, Qt.MatchFixedString)
        if index_privilege >= 0:
            client.ui.comboBox_2.setCurrentIndex(index_privilege)
        client.show()
        # Сохраняем параметры данных об уже существующем клиенте
        System.client_update = 1
        logger.info('Обновляем инф. клиента %s' % System.client_update)
        logger.debug('id клиента %s' % System.client_id)
        client.exec_()

    def adding_new_client_to_sale(self) -> None:
        """
        Функция добавляет в окно продажи только что созданного клиента.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции adding_new_client_to_sale")
        # Запрашиваем данные нового клиента
        with Session(engine) as session:
            search_client = session.query(Client).filter_by(id=System.id_new_client_in_sale).one_or_none()
        logger.debug("Найденный клиент %s" % search_client)
        # Вычисляем возраст клиента
        age: int = System.calculate_age(search_client.birth_date)
        # Определяем тип билета и цену
        type_ticket: str = System.calculate_ticket_type(age)
        # Определяем тип билета и цену
        time: int = int(self.ui.comboBox.currentText())
        if type_ticket == 'бесплатный':
            price = System.price['ticket_free']
        elif type_ticket == 'взрослый':
            if time == 1:
                price = System.price['ticket_adult_1']
            elif time == 2:
                price = System.price['ticket_adult_2']
            else:
                price = System.price['ticket_adult_3']
        else:
            if time == 1:
                price = System.price['ticket_child_1']
            elif time == 2:
                price = System.price['ticket_child_2']
            else:
                price = System.price['ticket_child_3']
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
        self.filling_client_table_widget_2(row, search_client.last_name, search_client.first_name, type_ticket, price,
                                           search_client.privilege, search_client.id, age)

    def tracking_button_pressing(self, event) -> None:
        """
        Функция отслеживает нажатия клавиш Delete и Backspace.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции tracking_button_pressing")
        if event.key() == QtCore.Qt.Key_Delete:
            self.deleting_selected_record()
        elif event.key() == QtCore.Qt.Key_Backspace:
            self.deleting_selected_record()

    def deleting_selected_record(self) -> None:
        """
        Функция Удаляет запись из таблицы при нажатии кнопки в tracking_button_pressing.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции deleting_selected_record")
        if self.ui.tableWidget_2.rowCount() > 0:
            current_row: int = self.ui.tableWidget_2.currentRow()
            # Перед удалением записи обновляем sale_dict
            type_ticket: str = self.ui.tableWidget_2.item(current_row, 2).text()
            # Если checkbox в tableWidget_2 активирован, то обновляем details
            if type_ticket == 'взрослый':
                if self.ui.tableWidget_2.cellWidget(current_row, 7).findChild(QCheckBox).isChecked():
                    System.sale_dict['detail'][0] -= 1
                else:
                    System.sale_dict['kol_adult'] -= 1
                # Если активирована скидка
                if self.ui.checkBox_2.isChecked():
                    index: int = self.ui.comboBox_2.currentIndex()
                    if index > 0:
                        System.sale_dict['detail'][0] -= 1
            elif type_ticket == 'детский':
                if self.ui.tableWidget_2.cellWidget(current_row, 7).findChild(QCheckBox).isChecked():
                    System.sale_dict['detail'][2] -= 1
                else:
                    System.sale_dict['kol_child'] -= 1
                # Если активирована скидка
                if self.ui.checkBox_2.isChecked():
                    index: int = self.ui.comboBox_2.currentIndex()
                    if index > 0:
                        System.sale_dict['detail'][2] -= 1
            self.ui.tableWidget_2.removeRow(current_row)
            self.sale_update()
        row: int = self.ui.tableWidget_2.rowCount()
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
            self.sale_update()

    def check_filter_update(self) -> None:
        """
        Функция очищает строку поиска (lineEdit).

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции check_filter_update")
        self.ui.lineEdit.clear()

    def changing_color_of_calendar(self) -> None:
        """
        Функция изменяет цвет календаря.
        Если текущий день праздничный или выходной - dateEdit становится красным.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции changing_color_of_calendar")
        get_date: str = str(self.ui.dateEdit.date())
        date_slice: str = get_date[21:(len(get_date) - 1)]
        logger.debug(date_slice)
        get_date: str = date_slice.replace(', ', '-')
        if System.check_day(get_date) == 1:
            self.ui.dateEdit.setStyleSheet('background-color: red;')
        else:
            self.ui.dateEdit.setStyleSheet('background-color: white;')

    def checking_status_discounted_field(self) -> None:
        """
        Функция проверяет активность поля со скидкой.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции checking_status_discounted_field")
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
            self.sale_update()

    def filling_client_table_widget(self, last_name: str, first_name: str, age: int, privilege: str, phone: str,
                                    id: int) -> None:
        """
        Функция заполняет полученными данными tableWidget (список посетителей).

        Параметры:

        Возвращаемое значение:
        """
        row = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row)
        self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(last_name))
        self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(first_name))
        self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(str(age)))
        self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(privilege))
        self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(phone))
        self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(str(id)))
        self.ui.tableWidget.setColumnHidden(5, True)

    def filling_client_table_widget_2(self, row: int, last_name: str, first_name: str, type_ticket: str, price: int,
                                      privilege: str, id: int, age: int) -> None:
        """
        Функция заполняет полученными данными tableWidget_2 (перечень клиентов в продаже).

        Параметры:

        Возвращаемое значение:
        """
        self.ui.tableWidget_2.setItem(row, 0, QTableWidgetItem(last_name))
        self.ui.tableWidget_2.setItem(row, 1, QTableWidgetItem(first_name))
        self.ui.tableWidget_2.setItem(row, 2, QTableWidgetItem(type_ticket))
        self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(price))
        self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(privilege))
        self.ui.tableWidget_2.setItem(row, 5, QTableWidgetItem(str(id)))
        self.ui.tableWidget_2.setColumnHidden(5, True)
        self.ui.tableWidget_2.setItem(row, 6, QTableWidgetItem(age))

    def filling_client_table_widget_3(self, row: int, last_name: str, first_name: str, age: int,
                                      privilege: str, id: int) -> None:
        """
        Функция заполняет полученными данными tableWidget_3 (список связанных с выбранным клиентом посетителей).

        Параметры:

        Возвращаемое значение:
        """
        self.ui.tableWidget_3.insertRow(row)
        self.ui.tableWidget_3.setItem(row, 0, QTableWidgetItem(last_name))
        self.ui.tableWidget_3.setItem(row, 1, QTableWidgetItem(first_name))
        self.ui.tableWidget_3.setItem(row, 2, QTableWidgetItem(str(age)))
        self.ui.tableWidget_3.setItem(row, 3, QTableWidgetItem(privilege))
        self.ui.tableWidget_3.setItem(row, 4, QTableWidgetItem(str(id)))
        self.ui.tableWidget_3.setColumnHidden(4, True)

    @logger_wraps()
    def sale_search_clients(self) -> None:
        """
        Функция Выводит в tableWidget список найденных клиентов.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции sale_search_clients")
        if System.what_a_day == 1:
            self.ui.dateEdit.setStyleSheet('background-color: red;')
        # Вычисляем индекс значения
        index: int = self.ui.comboBox_4.currentIndex()
        if index == 2:
            # Поиск по номеру телефона
            user_filter: str = '%' + self.ui.lineEdit.text() + '%'
            with Session(engine) as session:
                search = session.query(Client).filter(Client.phone.ilike(user_filter)).all()
            logger.debug(search)
            for client in search:
                age = System.calculate_age(client.birth_date)
                self.filling_client_table_widget(
                    client.last_name, client.first_name, age, client.privilege, client.phone, client.id
                )
        elif index == 1:
            # Поиск по фамилии
            query: str = '%' + self.ui.lineEdit.text() + '%'
            self.ui.tableWidget.setRowCount(0)
            with Session(engine) as session:
                search: list[Type[Client]] = session.query(Client).filter(Client.last_name.ilike(query)).all()
            for client in search:
                age = System.calculate_age(client.birth_date)
                self.filling_client_table_widget(
                    client.last_name, client.first_name, age, client.privilege, client.phone, client.id
                )
        elif index == 0:
            # Поиск по фамилии и имени
            self.ui.tableWidget.setRowCount(0)
            search: list[Type[Client]] = self.ui.lineEdit.text().title()
            # Разбиваем поисковую фразу на две
            lst: Any = search.split()
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
                age = System.calculate_age(client.birth_date)
                self.filling_client_table_widget(
                    client.last_name, client.first_name, age, client.privilege, client.phone, client.id
                )
        elif index == 3:
            # Поиск инвалидов
            self.ui.tableWidget.setRowCount(0)
            with Session(engine) as session:
                search: list[Type[Client]] = session.query(Client).filter(Client.privilege.ilike('%' + 'и')).all()
            for client in search:
                age = System.calculate_age(client.birth_date)
                self.filling_client_table_widget(
                    client.last_name, client.first_name, age, client.privilege, client.phone, client.id
                )
        elif index == 4:
            # Поиск многодетных
            self.ui.tableWidget.setRowCount(0)
            with Session(engine) as session:
                search: list[Type[Client]] = session.query(Client).filter(Client.privilege.ilike('%' + 'м')).all()
            for client in search:
                age = System.calculate_age(client.birth_date)
                self.filling_client_table_widget(
                    client.last_name, client.first_name, age, client.privilege, client.phone, client.id
                )

    def clearing_client_list(self) -> None:
        """
        Функция очищает список клиентов (tableWidget).

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции check_filter_update")
        self.ui.tableWidget.clearContents()
        self.ui.tableWidget.setRowCount(0)

    @logger_wraps()
    def adding_client_to_sale(self, *args, **kwargs) -> None:
        """
        Функция ищет выделенную строку в таблице клиентов и передает ее в таблицу заказа.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции adding_client_to_sale")
        # Изменяем ширину столбцов
        self.ui.tableWidget_2.setColumnWidth(3, 5)
        self.ui.tableWidget_2.setColumnWidth(4, 5)
        self.ui.tableWidget_2.setColumnWidth(7, 40)
        self.ui.tableWidget_2.setColumnWidth(8, 5)
        self.ui.tableWidget_3.setColumnWidth(3, 7)
        # Если продажа новая - обновляем статус
        System.sale_status = 0
        logger.warning("Статус продажи - новая %s" % System.sale_status)
        row_number: int = self.ui.tableWidget.currentRow()
        res: str = self.ui.tableWidget.item(row_number, 5).text()
        with Session(engine) as session:
            search_client: Type[Client] = session.query(Client).filter_by(id=res).first()
        # Вычисляем возраст клиента
        age: int = int(self.ui.tableWidget.item(row_number, 2).text())
        # Определяем тип билета и цену
        type_ticket: str = System.calculate_ticket_type(age)
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
        row: int = self.ui.tableWidget_2.rowCount()
        self.ui.tableWidget_2.insertRow(row)
        # Добавляем checkbox скидки
        self.ui.tableWidget_2.setCellWidget(row, 7, widget)
        # Добавляем checkbox "присутствия" в продаже
        self.ui.tableWidget_2.setCellWidget(row, 8, widget_1)
        # Передаем в таблицу заказа данные клиента
        self.filling_client_table_widget_2(row, search_client.last_name, search_client.first_name, type_ticket, 0,
                                           search_client.privilege, search_client.id, age)
        self.sale_update()
        # Очищаем tableWidget_3
        while self.ui.tableWidget_3.rowCount() > 0:
            self.ui.tableWidget_3.removeRow(0)
        # Ищем продажи, в которых клиент был ранее
        client_list: set = set()
        with Session(engine) as session:
            sales = session.query(Client.id, Ticket.id_sale, Ticket.id_sale).filter(and_(Client.id == search_client.id,
                                                                                         Ticket.id_client == search_client.id))
            for client_in_sales in sales:
                if client_in_sales:
                    # Находим других посетителей, которые были в этих продажах
                    search_sale = session.query(Ticket.id_sale,
                                                Ticket.id_client).filter(Ticket.id_sale == client_in_sales[2])
                    for search_cl in search_sale:
                        # Запрашиваем информацию об этих клиентах
                        client_list.add(search_cl[1])
        # изменяем ширину столбов
        self.ui.tableWidget_3.setColumnWidth(2, 15)
        # выводим в tableWidget_3 список найденных клиентов
        for client in client_list:
            search_cl_in_sale = session.query(Client).filter_by(id=client).one()
            row: int = self.ui.tableWidget_3.rowCount()
            age: int = System.calculate_age(search_cl_in_sale.birth_date)
            self.filling_client_table_widget_3(row, search_cl_in_sale.last_name, search_cl_in_sale.first_name, age,
                                               search_cl_in_sale.privilege, search_cl_in_sale.id)

    @logger_wraps()
    def adding_related_client_to_sale(self, *args, **kwargs) -> None:
        """
        Функция ищет выделенную строку в таблице клиентов, которые были ранее в одной продаже,
        и передает данные об этом посетителе в таблицу заказа.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции adding_related_client_to_sale")
        row_number: int = self.ui.tableWidget_3.currentRow()
        # Получаем содержимое ячейки
        res: str = self.ui.tableWidget_3.item(row_number, 4).text()
        age: int = int(self.ui.tableWidget_3.item(row_number, 2).text())
        # Находим выделенного в таблице клиента
        with Session(engine) as session:
            search_client = session.query(Client).filter_by(id=res).first()
        # Определяем тип билета и цену
        type_ticket: str = System.calculate_ticket_type(age)
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
        row: int = self.ui.tableWidget_2.rowCount()
        self.ui.tableWidget_2.insertRow(row)
        # Добавляем checkbox
        self.ui.tableWidget_2.setCellWidget(row, 7, widget)
        # Добавляем checkbox "присутствия" в продаже
        self.ui.tableWidget_2.setCellWidget(row, 8, widget_1)
        # Передаем в таблицу заказа данные клиента
        self.filling_client_table_widget_2(
            row, search_client.last_name, search_client.first_name, type_ticket, 0, search_client.privilege,
            search_client.id, age
        )
        self.sale_update()

    def sale_update(self) -> None:
        """
        Функция обновляет позиции в заказе, генерирует информацию о продаже и список билетов.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функцию sale_update")
        # Используем для подсчета количества посетителей
        kol_adult: int = 0
        kol_child: int = 0
        # Используем для подсчета количества посетителей со скидкой
        kol_sale_adult: int = 0
        kol_sale_child: int = 0
        # Используем для подсчета количества посетителей с категорией
        kol_adult_many_child: int = 0
        kol_child_many_child: int = 0
        kol_adult_invalid: int = 0
        kol_child_invalid: int = 0
        # Запоминаем id для "привязки" продажи ко взрослому
        id_adult: int = 0
        # Учитываем продолжительность посещения
        time_ticket: int = int(self.ui.comboBox.currentText())
        # Сохраняем билеты
        tickets: list[tuple[str, str, str, str, str, str, str, str, int, str]] = []
        # Флаг "многодетные": 1 - 2 часа бесплатно, 2 - скидка 50%
        many_child: int = 0
        invalid: int = 0
        # Считаем количество золотых талантов
        talent: int = 0
        # Устанавливаем время и количество талантов
        if time_ticket == 1:
            System.sale_dict['detail'][6] = 1
            talent: int = System.talent['1_hour']
        elif time_ticket == 2:
            System.sale_dict['detail'][6] = 2
            talent: int = System.talent['2_hour']
        elif time_ticket == 3:
            System.sale_dict['detail'][6] = 3
            talent: int = System.talent['3_hour']
        # Записываем в sale_dict время посещения
        date_time: str = self.ui.dateEdit.date().toString("yyyy-MM-dd")
        # Анализируем таблицу с заказом
        rows: int = self.ui.tableWidget_2.rowCount()
        for row in range(rows):
            # Сегодня день многодетных?
            # Проверяем категорию посетителя - если многодетный
            if self.ui.tableWidget_2.item(row, 4).text() == 'м':
                # Активируем поле со скидкой
                self.ui.tableWidget_2.cellWidget(row, 7).findChild(QCheckBox).setCheckState(Qt.Checked)
                # Проверяем если номер дня недели равен 7 и дата <= 7
                # Установлена галочка "продление многодетным"
                if System.sunday == 1 and self.ui.checkBox_3.isChecked():
                    logger.info('Продление билетов многодетным')
                    # Отменяем скидку 100%
                    many_child: int = 0
                    self.ui.checkBox_2.setEnabled(True)
                    self.ui.checkBox_2.setChecked(True)
                    self.ui.comboBox_2.setCurrentIndex(0)
                    self.ui.comboBox.setEnabled(True)
                elif System.sunday == 1:
                    # Используем "флаг" many_child
                    many_child: int = 1
                    logger.info('Сегодня день многодетных')
                    # Устанавливаем продолжительность посещения 2 часа
                    self.ui.comboBox.setCurrentIndex(1)
                    self.ui.comboBox.setEnabled(False)
                    # Устанавливаем скидку
                    self.ui.checkBox_2.setEnabled(False)
                    self.ui.comboBox_2.setCurrentIndex(15)
                    self.ui.comboBox_2.setEnabled(False)
                    System.sale_dict['detail'][4] = 100
                    # Отключаем кнопку возврата
                    self.ui.pushButton_6.setEnabled(False)
                # используем "флаг" many_child, для скидки 50%
                elif System.num_of_week <= 5:
                    logger.info('Многодетным скидка 50%')
                    many_child: int = 2
                    # Устанавливаем скидку
                    self.ui.checkBox_2.setChecked(True)
                    self.ui.checkBox_2.setEnabled(True)
                    self.ui.comboBox_2.setCurrentIndex(10)
                    self.ui.comboBox_2.setEnabled(False)
                    System.sale_dict['detail'][4] = 50
            # Проверяем категорию посетителя - если инвалид
            elif self.ui.tableWidget_2.item(row, 4).text() == 'и':
                invalid: int = 1
                System.sale_dict['detail'][4] = 100
                # Изменяем продолжительность времени посещения
                self.ui.comboBox.setCurrentIndex(2)
                self.ui.comboBox.setEnabled(False)
                # Устанавливаем скидку
                self.ui.checkBox_2.setEnabled(False)
                self.ui.comboBox_2.setCurrentIndex(15)
                self.ui.comboBox_2.setEnabled(False)
                # Отключаем кнопки сохранения и возврата
                self.ui.pushButton_3.setEnabled(False)
                self.ui.pushButton_6.setEnabled(False)
            # Если стоит флаг 'н' - исключаем из продажи
            elif self.ui.tableWidget_2.item(row, 4).text() == 'н':
                self.ui.tableWidget_2.cellWidget(row, 8).findChild(QCheckBox).setCheckState(Qt.Checked)
            # Учитываем тип билета
            type_ticket: str = self.ui.tableWidget_2.item(row, 2).text()
            # Считаем взрослые билеты
            if type_ticket == 'взрослый':
                # Если продолжительность посещения 1 час
                if System.sale_dict['detail'][6] == 1:
                    # Сохраняем цену билета
                    price: int = System.price['ticket_adult_1']
                elif System.sale_dict['detail'][6] == 2:
                    # Если день многодетных
                    if many_child == 1:
                        price: int = System.price['ticket_free']
                        kol_adult_many_child += 1
                        # Изменяем цену и записываем размер скидки
                        logger.debug('Добавляем взрослого мног-го в sale_dict[detail]')
                        System.sale_dict['detail'][0] = kol_adult_many_child
                        System.sale_dict['detail'][1] = price
                    # Если обычный день
                    else:
                        price: int = System.price['ticket_adult_2']
                else:
                    # Если продолжительность 3 часа
                    # Если в продаже инвалид
                    if invalid == 1:
                        price: int = System.price['ticket_free']
                        kol_adult_invalid += 1
                        # Изменяем цену и записываем размер скидки
                        System.sale_dict['detail'][0] = kol_adult_invalid
                        System.sale_dict['detail'][1] = price
                        # Меняем категорию билета на 'c' - сопровождающий
                        self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem('с'))
                    else:
                        price: int = System.price['ticket_adult_3']
                # Привязываем продажу ко взрослому
                if id_adult == 0:
                    System.sale_dict['detail'][5] = self.ui.tableWidget_2.item(row, 5).text()
                # Если checkbox активен - взрослый в оплату не добавляется
                if self.ui.tableWidget_2.cellWidget(row, 8).findChild(QCheckBox).isChecked():
                    # И номер строки не запоминали
                    if System.sale_checkbox_row is None:
                        logger.info('Исключаем взрослого из продажи')
                        System.sale_dict['detail'][0] = 1
                        System.sale_dict['detail'][4] = 100
                        # Запоминаем номер строки с активным QCheckBox
                        System.sale_checkbox_row = row
                        # Изменяем флаг активности QCheckBox
                        System.exclude_from_sale = 1
                        # Ставим метку "не идет"
                        self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem('н'))
                # Если QCheckBox не активен
                else:
                    # Флаг состояния QCheckBox активирован
                    if System.exclude_from_sale == 1:
                        self.ui.tableWidget_2.cellWidget(row, 8).findChild(QCheckBox).setEnabled(False)
                    # Флаг состояния QCheckBox не активирован (вернули в продажу)
                    else:
                        logger.info('Активируем QCheckBox строке')
                        self.ui.tableWidget_2.cellWidget(row, 8).findChild(QCheckBox).setEnabled(True)
                # Флаг состояния QCheckBox активирован
                if System.exclude_from_sale == 1:
                    # Если отмеченный ранее QCheckBox не активен
                    if not self.ui.tableWidget_2.cellWidget(System.sale_checkbox_row, 8).findChild(
                            QCheckBox).isChecked():
                        logger.info('Возвращаем в продажу')
                        self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem('-'))
                        self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(price))
                        System.sale_dict['detail'][0] = 0
                        System.sale_dict['detail'][1] = 0
                        System.sale_dict['detail'][4] = 0
                        System.sale_checkbox_row = None
                        System.exclude_from_sale = 0
                kol_adult += 1
                System.sale_dict['kol_adult'] = kol_adult
                System.sale_dict['price_adult'] = price
            # Считаем детские билеты
            elif type_ticket == 'детский':
                # Отключаем исключающий из продажи QCheckBox
                self.ui.tableWidget_2.cellWidget(row, 8).findChild(QCheckBox).setEnabled(False)
                # Если продолжительность посещения 1 час
                if System.sale_dict['detail'][6] == 1:
                    # Проверяем текущий день является выходным
                    if System.what_a_day == 0:
                        price: int = System.price['ticket_child_1']
                    else:
                        price: int = System.price['ticket_child_week_1']
                elif System.sale_dict['detail'][6] == 2:
                    # если день многодетных
                    if many_child == 1:
                        price: int = System.price['ticket_free']
                        kol_child_many_child += 1
                        # Применяем сидку
                        System.sale_dict['detail'][2] = kol_child_many_child
                        System.sale_dict['detail'][3] = price
                    # Если обычный день
                    else:
                        # Проверяем текущий день является выходным
                        if System.what_a_day == 0:
                            price: int = System.price['ticket_child_2']
                        else:
                            price: int = System.price['ticket_child_week_2']
                else:
                    # Если продолжительность посещения 3 часа
                    # Если в продаже инвалид
                    if invalid == 1:
                        price: int = System.price['ticket_free']
                        kol_child_invalid += 1
                        # Изменяем цену и записываем размер скидки
                        System.sale_dict['detail'][2] = kol_child_invalid
                        System.sale_dict['detail'][3] = price
                    elif System.what_a_day == 0:
                        price: int = System.price['ticket_child_3']
                    else:
                        price: int = System.price['ticket_child_week_3']
                kol_child += 1
                System.sale_dict['kol_child'] = kol_child
                System.sale_dict['price_child'] = price
            # Считаем бесплатные билеты
            else:
                price: int = System.price['ticket_free']
            # Устанавливаем цену в таблицу и пересчитываем
            self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{price}"))
            # Применяем скидку
            logger.info('Применяем скидку')
            # В день многодетных
            if many_child == 1:
                logger.info('Скидка 100% в день многодетных')
                self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{System.price['ticket_free']}"))
                logger.debug("В продаже многодетные")
                # Помечаем продажу как "особенную"
                System.sale_special = 1
                logger.debug('Продажа особенная %s' % System.sale_special)
            # Скидка 50% в будни
            elif many_child == 2:
                logger.info('Скидка 50% многодетным в будни')
                self.ui.comboBox_2.setCurrentIndex(10)
                new_price: int = round(price * 0.5)
                self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{new_price}"))
            # Скидка инвалидам
            elif invalid == 1:
                logger.info('Скидка 100% инвалидам')
                self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{System.price['ticket_free']}"))
                logger.debug("В продаже инвалид")
                # Помечаем продажу как "особенную"
                System.sale_special = 1
                logger.debug('Продажа особенная %s' % System.sale_special)
            # Иначе проверяем активен ли checkbox со скидкой и размер > 0
            if self.ui.checkBox_2.isChecked():
                logger.info('Checkbox со скидкой активен - обычный гость')
                if int(self.ui.comboBox_2.currentText()) > 0:
                    System.sale_discount = int(self.ui.comboBox_2.currentText())
                    logger.debug('Sale_discount %s' % System.sale_discount)
                    System.sale_dict['detail'][4] = System.sale_discount
                    if System.sale_discount > 0:
                        new_price: int = int(price - (price * System.sale_discount / 100))
                        # Если checkbox в акт - применяем к этой строке скидку
                        if self.ui.tableWidget_2.cellWidget(row, 7).findChild(QCheckBox).isChecked():
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
                            self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{new_price}"))
        logger.debug('System.sale_dict %s' % System.sale_dict)
        itog = (
                ((System.sale_dict['kol_adult'] - System.sale_dict['detail'][0]) * System.sale_dict['price_adult']) +
                ((System.sale_dict['kol_child'] - System.sale_dict['detail'][2]) * System.sale_dict['price_child']) +
                (System.sale_dict['detail'][0] * System.sale_dict['detail'][1]) +
                (System.sale_dict['detail'][2] * System.sale_dict['detail'][3])
        )
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
            # Если установлена метка "не идет"
            if self.ui.tableWidget_2.item(row, 4).text() == 'н':
                # Изменяем цену
                logger.debug('Изменяем цену в билете посетителя!')
                self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{System.price['ticket_free']}"))
            tickets.append(
                (
                    # Фамилия
                    self.ui.tableWidget_2.item(row, 0).text(),
                    # Имя
                    self.ui.tableWidget_2.item(row, 1).text(),
                    # Тип билета
                    self.ui.tableWidget_2.item(row, 2).text(),
                    # Цена
                    self.ui.tableWidget_2.item(row, 3).text(),
                    # Категория
                    self.ui.tableWidget_2.item(row, 4).text(),
                    # Id взрослого
                    self.ui.tableWidget_2.item(row, 5).text(),
                    # Возраст
                    self.ui.tableWidget_2.item(row, 6).text(),
                    time_ticket,
                    talent,
                    date_time
                )
            )
        System.sale_tickets = tickets
        logger.info('System.sale_tickets %s' % System.sale_tickets)
        # Проверяем есть ли в продаже взрослый
        if System.sale_dict['kol_adult'] >= 1:
            self.ui.pushButton_5.setEnabled(True)
        else:
            self.ui.pushButton_5.setEnabled(False)

    def save_sale(self) -> None:
        """
        Функция сохраняет в БД информацию о продаже, а так же билеты посетителей.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции save_sale")
        logger.debug('Статус сохраняемой продажи %s' % System.sale_status)
        # Если продажа особенная - сохраним ее статус оплаченной
        if System.sale_special == 1:
            System.sale_status = 1
        if System.sale_dict['kol_adult'] >= 1:
            add_sale: Sale = Sale(price=System.sale_dict['detail'][7],
                                  id_user=System.user[3],
                                  id_client=System.sale_dict['detail'][5],
                                  status=System.sale_status,
                                  discount=System.sale_dict['detail'][4],
                                  pc_name=System.pc_name,
                                  datetime=dt.datetime.now())
            logger.debug('Получена продажа %s' % add_sale)
            # Сохраняем продажу
            logger.debug("Сохраняем продажу в БД")
            with Session(engine) as session:
                session.add(add_sale)
                session.commit()
            # Получаем номер сохраненной продажи
            with Session(engine) as session:
                query = func.max(Sale.id)
                System.sale_id = session.execute(query).scalars().first()
            # Сохраняем билеты
            type_ticket: int | None = None
            logger.debug("Сохраняем билеты в БД")
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
                with Session(engine) as session:
                    session.add(add_ticket)
                    session.commit()
                logger.info('Сохраненный билет %s' % add_ticket)
            self.close()
        else:
            windows.info_window(
                'Ошибка при сохранении продажи',
                'Необходимо добавить в нее взрослого',
                ''
            )

    @logger.catch()
    def sale_transaction(self, payment_type, print_check) -> None:
        """
        Функция осуществляет оплату ранее сохраненной продажи.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции sale_transaction")
        logger.debug('System.sale_status: %s' % System.sale_status)
        logger.debug('System.sale_id: %s' % System.sale_id)
        # Если продажа новая
        if System.sale_id is None:
            self.save_sale()
        # Если продажа особенная - генерируем билеты без оплаты
        if System.sale_special == 1:
            self.sale_generate_saved_tickets()
        else:
            state_check, payment = kkt.check_open(System.sale_dict, payment_type, System.user, 1, print_check)
            check = None
            # Если прошла оплата
            if state_check == 1:
                logger.info("Оплата прошла успешно")
                if print_check == 0:
                    windows.info_window('Оплата прошла успешно.', 'Чек не печатаем.', '')
                if payment == 1:  # Если оплата банковской картой
                    logger.info("Читаем слип-чек из файла")
                    pinpad_file = r"C:\sc552\p"
                    with open(pinpad_file, 'r', encoding='IBM866') as file:
                        while line := file.readline().rstrip():
                            logger.debug(line)
                    check = kkt.read_slip_check()
                    # Печать банковский чек: 1 - да, 0 - нет
                    if print_check == 1:
                        kkt.print_slip_check()
                if payment == 3:  # Если оплата offline банковской картой
                    check = 'offline'
                # Обновляем информацию о продаже в БД
                logger.info('Обновляем информацию о продаже в БД')
                with Session(engine) as session:
                    query = update(Sale).where(Sale.id == System.sale_id).values(
                        status=1, id_user=System.user[3], pc_name=System.pc_name,
                        payment_type=payment, bank_pay=check, datetime=dt.datetime.now()
                    )
                    session.execute(query)
                # генерируем билеты
                self.sale_generate_saved_tickets()
                # Сбрасываем статус продажи
                System.sale_status = 0
                self.close()
            else:
                logger.warning('Оплата не прошла')
                windows.info_window(
                    "Внимание",
                    'Закройте это окно, откройте сохраненную продажу и проведите'
                    'операцию оплаты еще раз.', '')

    @logger.catch()
    def sale_return(self):
        """
        Функция осуществляет операцию возврата продажи.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции sale_return")
        # Обновляем данные о продаже
        self.sale_update()
        logger.info('Запрашиваем метод оплаты в БД')
        with Session(engine) as session:
            query = select(Sale.payment_type).filter(Sale.id == System.sale_id)
            payment_type_sale = session.execute(query).scalars().one()
            # payment_type_sale = session.execute(query).scalars().one()._asdict()
        logger.info('payment_type_sale %s' % payment_type_sale)
        # 1 - карта, 2 - наличные
        if payment_type_sale.get('payment_type') == 1:
            payment_type: int = 101
        else:
            payment_type: int = 102
        state_check, payment = kkt.check_open(System.sale_dict, payment_type, System.user, 2, 1)
        check = None
        # Если возврат прошел
        if state_check == 1:
            logger.info("Операция возврата прошла успешно")
            if payment == 1:  # Если оплата банковской картой
                logger.info("Читаем слип-чек из файла")
                pinpad_file = r"C:\sc552\p"
                with open(pinpad_file, 'r', encoding='IBM866') as file:
                    while line := file.readline().rstrip():
                        logger.debug(line)
                check = kkt.read_slip_check()
            # Записываем информацию о возврате в БД
            with Session(engine) as session:
                query = update(Sale).where(Sale.id == System.sale_id).values(
                    status=2, id_user=System.user[3], pc_name=System.pc_name,
                    payment_type=payment, bank_pay=check, datetime=dt.datetime.now()
                )
                session.execute(query)
            self.close()
        else:
            logger.warning('Операция возврата завершилась с ошибкой')
            windows.info_window(
                "Внимание",
                'Закройте это окно, откройте сохраненную продажу и проведите'
                'операцию возврата еще раз.', '')

    @logger.catch()
    def sale_generate_saved_tickets(self):
        """
        Функция генерирует список с ранее сохраненными билетами.

        Параметры:

        Возвращаемое значение:
        """
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

    def open_pay_form(self, txt):
        """
        Функция открывает форму оплаты.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции open_pay_form")
        pay = PayForm()
        # Передаем текст в форму PayForm
        pay.setText(txt)

        res: int = pay.exec_()
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
            payment_type: int = Payment.Card
            # запускаем оплату по терминалу
            self.sale_transaction(payment_type, System.print_check)
        elif res == Payment.Cash:
            logger.info('Оплата наличными')
            payment_type: int = Payment.Cash
            self.sale_transaction(payment_type, System.print_check)
        elif res == Payment.Offline:
            logger.info('Оплата банковской картой offline')
            payment_type: int = Payment.Offline
            self.sale_transaction(payment_type, System.print_check)
        # Закрываем окно продажи и возвращаем QDialog.Accepted
        self.accept()


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

    def setText(self, txt) -> None:
        """
        Функция устанавливает текстовое значение в метку.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции setText")
        self.ui.label_2.setText(txt)
        # По умолчанию печатаем чек
        System.print_check = 1

    def check_print(self) -> None:
        """
        Функция печатает кассовый чек, если checkBox на форме оплаты был активен.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции check_print")
        if self.ui.checkBox.isChecked():
            System.print_check = 1
        else:
            System.print_check = 0


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """Главная форма"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.main_search_clients)
        # Открыть окно добавления нового клиента
        self.ui.pushButton_2.clicked.connect(self.main_open_client)
        self.ui.pushButton_3.clicked.connect(self.main_edit_client)
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

    def filling_client_table_widget_main_form(self, last_name: str, first_name: str, middle_name: str, birth_date: date,
                                    gender: str, phone: str, email: str,privilege: str, id: int) -> None:
        """
        Функция заполняет полученными данными tableWidget (список посетителей).

        Параметры:

        Возвращаемое значение:
        """
        row = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row)
        self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(last_name))
        self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(first_name))
        self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(middle_name))
        self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(birth_date))
        self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(gender))
        self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(phone))
        self.ui.tableWidget.setItem(row, 6, QTableWidgetItem(email))
        self.ui.tableWidget.setItem(row, 7, QTableWidgetItem(privilege))
        self.ui.tableWidget.setItem(row, 8, QTableWidgetItem(id))
        self.ui.tableWidget.setColumnHidden(8, True)

    @logger_wraps()
    def main_search_clients(self) -> None:
        """
        Функция выводит в tableWidget (вкладка "посетители") отфильтрованный список клиентов.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции main_search_clients")
        user_filter: str = '%' + self.ui.lineEdit_2.text() + '%'
        # Вычисляем индекс значения
        index: int = self.ui.comboBox_3.currentIndex()
        # Изменяем ширину столбов
        self.ui.tableWidget.setColumnWidth(0, 200)
        self.ui.tableWidget.setColumnWidth(1, 150)
        self.ui.tableWidget.setColumnWidth(2, 150)
        self.ui.tableWidget.setColumnWidth(6, 200)
        self.ui.tableWidget.setColumnWidth(7, 200)
        if index == 2:
            # Поиск по номеру телефона
            self.ui.tableWidget.setRowCount(0)
            with Session(engine) as session:
                search: list[Type[Client]] = session.query(Client).filter(Client.phone.ilike(user_filter)).all()
            for client in search:
                self.filling_client_table_widget_main_form(
                    client.last_name, client.first_name, client.middle_name, str(client.birth_date), client.gender,
                    client.phone, client.email, client.privilege, str(client.id)
                )
        elif index == 1:
            # Поиск по фамилии
            self.ui.tableWidget.setRowCount(0)
            with Session(engine) as session:
                search: list[Type[Client]] = session.query(Client).filter(Client.last_name.ilike(user_filter)).all()
            for client in search:
                self.filling_client_table_widget_main_form(
                    client.last_name, client.first_name, client.middle_name, str(client.birth_date), client.gender,
                    client.phone, client.email, client.privilege, str(client.id)
                )
        elif index == 0:
            # Поиск по фамилии и имени
            self.ui.tableWidget.setRowCount(0)
            user_filter: str = self.ui.lineEdit_2.text().title()
            # Разбиваем поисковую фразу на две
            lst: Any = user_filter.split()
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
                self.filling_client_table_widget_main_form(
                    client.last_name, client.first_name, client.middle_name, str(client.birth_date), client.gender,
                    client.phone, client.email, client.privilege, str(client.id)
                )
        elif index == 3:
            # Поиск инвалидов
            self.ui.tableWidget.setRowCount(0)
            with Session(engine) as session:
                search: list[Type[Client]] = session.query(Client).filter(Client.privilege.ilike('%' + 'и')).all()
            for client in search:
                self.filling_client_table_widget_main_form(
                    client.last_name, client.first_name, client.middle_name, str(client.birth_date), client.gender,
                    client.phone, client.email, client.privilege, str(client.id)
                )
        elif index == 4:
            # Поиск многодетных
            self.ui.tableWidget.setRowCount(0)
            with Session(engine) as session:
                search: list[Type[Client]] = session.query(Client).filter(Client.privilege.ilike('%' + 'м')).all()
            for client in search:
                self.filling_client_table_widget_main_form(
                    client.last_name, client.first_name, client.middle_name, str(client.birth_date), client.gender,
                    client.phone, client.email, client.privilege, str(client.id)
                )

    def main_edit_client(self) -> None:
        """
        Функция ищет выделенную строку в таблице клиентов и открывает форму для редактирования данных.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции edit_client_in_sale")
        # Ищем индекс и значение ячейки
        row_number: int = self.ui.tableWidget.currentRow()
        # Получаем содержимое ячейки
        client_id: str = self.ui.tableWidget.item(row_number, 8).text()

        with Session(engine) as session:
            search_client: Type[Client] = session.query(Client).filter_by(id=client_id).first()
        # Сохраняем id клиента
        System.client_id = search_client.id
        # Передаем в форму данные клиента
        client = ClientForm()
        client.ui.lineEdit.setText(search_client.last_name)
        client.ui.lineEdit_2.setText(search_client.first_name)
        client.ui.lineEdit_3.setText(search_client.middle_name)
        client.ui.dateEdit.setDate(search_client.birth_date)
        # Поиск значения для установки в ComboBox gender
        index_gender: int = client.ui.comboBox.findText(search_client.gender, Qt.MatchFixedString)
        if index_gender >= 0:
            client.ui.comboBox.setCurrentIndex(index_gender)
        client.ui.lineEdit_4.setText(search_client.phone)
        client.ui.lineEdit_5.setText(search_client.email)
        # Ищем значение для установки в ComboBox privilege
        index_privilege: int | None = client.ui.comboBox.findText(search_client.privilege, Qt.MatchFixedString)
        if index_privilege >= 0:
            client.ui.comboBox_2.setCurrentIndex(index_privilege)
        client.show()
        # Сохраняем параметры данных об уже существующем клиенте
        System.client_update = 1
        logger.info('Обновляем информацию о клиенте %s' % System.client_update)
        logger.debug('id клиента %s' % System.client_id)
        client.exec_()

    def main_filter_clear(self) -> None:
        """
        Функция очищает строку поиска (lineEdit).

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции check_filter_update")
        self.ui.lineEdit_2.clear()

    def main_search_selected_sale(self) -> None:
        """
        Поиск выделенной строки в таблице продаж и открытие формы с полученными данными.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции mail_search_selected_sale")
        kol_adult: int = 0
        kol_child: int = 0
        summ: int = 0
        for idx in self.ui.tableWidget_2.selectionModel().selectedIndexes():
            # Номер строки найден
            row_number: int = idx.row()
            # Получаем содержимое ячейки
            sale_number: str = self.ui.tableWidget_2.item(row_number, 0).text()
            with Session(engine) as session:
                query = select(Client.first_name, Client.last_name, Client.middle_name, Ticket.ticket_type,
                               Ticket.price, Ticket.description, Client.id, Ticket.print, Ticket.client_age,
                               Ticket.arrival_time, Ticket.talent, Ticket.datetime).join(Ticket).where(
                    and_(Client.id == Ticket.id_client, Ticket.id_sale == sale_number)
                )
                client_in_sale = session.execute(query).all()
                # Запрашиваем статус продажи
                sale_status: Any = (
                    session.query(Sale.status).where(Sale.id == sale_number).one_or_none()
                )._asdict().get("status")
            logger.info("client_in_sale %s" % client_in_sale)
            logger.info("sale_status %s" % sale_status)
            # Передаем в форму данные клиента
            sale: SaleForm = SaleForm()
            sale.ui.tableWidget_2.setRowCount(0)
            sale.ui.dateEdit.setDate(client_in_sale[0][11])
            sale.ui.comboBox.setCurrentText(str(client_in_sale[0][9]))
            # Если продажа оплачена
            if sale_status == 1 or sale_status == 2:
                # Кнопка сохранить
                sale.ui.pushButton_3.setEnabled(False)
                # Кнопка оплатить
                sale.ui.pushButton_5.setEnabled(False)
                # Кнопка обновить
                sale.ui.pushButton_10.setEnabled(False)
                # Кнопка возврат
                sale.ui.pushButton_6.setEnabled(True)
                # Кнопка печать билетов
                sale.ui.pushButton_7.setEnabled(True)
                # Кнопка просмотр билетов
                sale.ui.pushButton_8.setEnabled(True)
                # Дата посещения
                sale.ui.dateEdit.setEnabled(False)
                # Время посещения
                sale.ui.comboBox.setEnabled(False)
                # Клиенты в заказе
                sale.ui.tableWidget_2.setEnabled(False)
                # Поле скидка
                sale.ui.checkBox_2.setEnabled(False)
            # Если продажа не оплачена
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
                if search_client[8] >= System.age['max']:
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
                # Добавляем checkbox скидки
                sale.ui.tableWidget_2.setCellWidget(row, 7, widget)
                # Добавляем checkbox "присутствия" в продаже
                sale.ui.tableWidget_2.setCellWidget(row, 8, widget_1)
                # Имя
                sale.ui.tableWidget_2.setItem(row, 0, QTableWidgetItem(f"{search_client[1]}"))
                # Фамилия
                sale.ui.tableWidget_2.setItem(row, 1, QTableWidgetItem(f"{search_client[0]}"))
                # Тип билета
                sale.ui.tableWidget_2.setItem(row, 2, QTableWidgetItem(type_ticket))
                # Цена
                sale.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{search_client[4]}"))
                # Примечание
                sale.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(f"{search_client[5]}"))
                # id клиента
                sale.ui.tableWidget_2.setItem(row, 5, QTableWidgetItem(f"{search_client[6]}"))
                sale.ui.tableWidget_2.setColumnHidden(5, True)
                # Возраст
                sale.ui.tableWidget_2.setItem(row, 6, QTableWidgetItem(f"{search_client[8]}"))
                summ += int(search_client[4])
            logger.info("Статус продажи %s" % sale_status)
            sale.ui.label_5.setText(str(kol_adult))
            sale.ui.label_7.setText(str(kol_child))
            sale.ui.label_8.setText(str(summ))
            sale.show()
            windows.info_window("Внимание",
                                'Перед проведением оплаты нажмите на кнопку обновить',
                                "")
            # Передаем сведения о сохраненной продаже
            System.sale_status = sale_status
            System.sale_id = sale_number
            System.sale_tickets = client_in_sale
            logger.debug("Билеты сохраненной продажи %s" % System.sale_tickets)
            sale.exec_()

    def main_button_all_sales(self) -> None:
        """
        Функция выводит на форму продаж в соответствии с выбранным пользователем фильтром (за 1, 3 и 7 дней).

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции main_button_all_sales")
        filter_day = 0
        self.ui.tableWidget_2.setRowCount(0)
        # Фильтр продаж за 1, 3 и 7 дней
        if self.ui.radioButton.isChecked():
            filter_day = dt.datetime(dt.datetime.today().year, dt.datetime.today().month, dt.datetime.today().day)
        elif self.ui.radioButton_2.isChecked():
            filter_day = dt.datetime.today() - timedelta(days=3)
        elif self.ui.radioButton_3.isChecked():
            filter_day = dt.datetime.today() - timedelta(days=7)
        with Session(engine) as session:
            sales = session.query(Sale).filter(Sale.datetime >= filter_day).order_by(desc(Sale.id))
        if sales:
            for sale in sales:
                row = self.ui.tableWidget_2.rowCount()
                self.ui.tableWidget_2.insertRow(row)
                self.ui.tableWidget_2.setItem(row, 0, QTableWidgetItem(f"{sale.id}"))
                self.ui.tableWidget_2.setItem(row, 1, QTableWidgetItem(f"{sale.id_client}"))
                self.ui.tableWidget_2.setItem(row, 2, QTableWidgetItem(f"{sale.price}"))
                self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{sale.datetime}"))
                if sale.status == 0:
                    status_type = 'создана'
                elif sale.status == 1:
                    status_type = 'оплачена'
                elif sale.status == 2:
                    status_type = 'возврат'
                self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(f"{status_type}"))
                self.ui.tableWidget_2.setItem(row, 5, QTableWidgetItem(f"{sale.discount}"))
                self.ui.tableWidget_2.setItem(row, 6, QTableWidgetItem(f"{sale.pc_name}"))
                if sale.payment_type == 1:
                    payment_type = 'карта'
                elif sale.payment_type == 2:
                    payment_type = 'наличные'
                elif sale.payment_type == 3:
                    payment_type = 'карта offline'
                else:
                    payment_type = '-'
                self.ui.tableWidget_2.setItem(row, 7, QTableWidgetItem(f"{payment_type}"))

    def main_open_client(self) -> None:
        """
        Функция открывает форму с данными клиента.

        Параметры: None

        Возвращаемое значение: None
        """
        client = ClientForm()
        client.show()
        client.exec()

    def main_open_sale(self) -> None:
        """
        Функция открывает форму продажи.

        Параметры:

        Возвращаемое значение:
        """
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
        # флаг состояния особенной (бесплатной) продажи
        System.sale_special = None
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
        # сбрасываем id и статус продажи
        System.sale_id = None
        System.sale_status = None
        sale.exec_()

    def main_get_statistic(self) -> None:
        """
        Функция формирует сводную статистику о продажах и билетах.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции main_get_statistic")
        # Устанавливаем временной период
        start_time = ' 00:00:00'
        end_time = ' 23:59:59'
        dt1 = self.ui.dateEdit_2.date().toString("yyyy-MM-dd") + start_time
        dt2 = self.ui.dateEdit.date().toString("yyyy-MM-dd") + end_time
        with Session(engine) as session:
            query = select(Sale.pc_name, Sale.payment_type, Sale.price, Sale.status).where(
                and_(Sale.status == '1', Sale.datetime.between(dt1, dt2))
            )
            sales = session.execute(query).all()
        logger.debug("Продажи за выбранный период %s" % sales)
        # Предполагаем что кассовых РМ два
        pc_1 = {'Name PC': f'{System.pc_1}', 'card': 0, 'cash': 0}
        pc_2 = {'Name PC': f'{System.pc_2}', 'card': 0, 'cash': 0}
        # Тип оплаты: 1 - карта, 2 - наличные
        type_rm = [1, 2]
        for i in range(len(sales)):
            if sales[i][0] in pc_1.values():
                # Если карта
                if sales[i][1] == type_rm[0]:
                    pc_1['card'] += sales[i][2]
                # Если наличные
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
        self.ui.tableWidget_4.setItem(0, 0, QTableWidgetItem(f"{pc_1['Name PC']}"))
        self.ui.tableWidget_4.setItem(0, 1, QTableWidgetItem(f"{pc_1['card']}"))
        self.ui.tableWidget_4.setItem(0, 2, QTableWidgetItem(f"{pc_1['cash']}"))
        self.ui.tableWidget_4.insertRow(1)
        self.ui.tableWidget_4.setItem(1, 0, QTableWidgetItem(f"{pc_2['Name PC']}"))
        self.ui.tableWidget_4.setItem(1, 1, QTableWidgetItem(f"{pc_2['card']}"))
        self.ui.tableWidget_4.setItem(1, 2, QTableWidgetItem(f"{pc_2['cash']}"))
        self.ui.tableWidget_4.insertRow(2)
        self.ui.tableWidget_4.setItem(2, 0, QTableWidgetItem(f"{'Итого'}"))
        self.ui.tableWidget_4.setItem(2, 1, QTableWidgetItem(f"{card}"))
        self.ui.tableWidget_4.setItem(2, 2, QTableWidgetItem(f"{cash}"))
        self.ui.tableWidget_4.setItem(2, 3, QTableWidgetItem(f"{summa}"))
        # Считаем оплаченные билеты
        with Session(engine) as session:
            query = select(Ticket.ticket_type, Ticket.arrival_time, Ticket.description, Sale.status, Sale.id).where(
                and_(Sale.id == Ticket.id_sale, Sale.status == '1', Ticket.datetime.between(dt1, dt2))
            )
            tickets = session.execute(query).all()
        logger.debug("Билеты %s" % tickets)
        type_tickets = [0, 1, 'м', 'и', '-']
        # 0-взрослый, 1-детский, м-многодетный, и-инвалид, с-сопровождающий, н-не идет
        time_arrival = [1, 2, 3]
        # child
        c = {'sum': 0, 't_1': 0, 't_2': 0, 't_3': 0}
        # adult
        a = {'sum': 0, 't_1': 0, 't_2': 0, 't_3': 0}
        # many_child
        m_c = {'sum': 0, 't_1': 0, 't_2': 0, 't_3': 0}
        # many_adult
        m_a = {'sum': 0, 't_1': 0, 't_2': 0, 't_3': 0}
        # invalid
        i_ = {'sum': 0, 't_1': 0, 't_2': 0, 't_3': 0}
        # Считаем количество билетов
        for i in range(len(tickets)):
            # Обычный билет - '-'
            if tickets[i][2] == type_tickets[4]:
                # Взрослый?
                if tickets[i][0] == type_tickets[0]:
                    # Не многодетный
                    if tickets[i][2] != type_tickets[2]:
                        a['sum'] += 1
                        # Проверяем продолжительность времени
                        if tickets[i][1] == time_arrival[0]:
                            a['t_1'] += 1
                        elif tickets[i][1] == time_arrival[1]:
                            a['t_2'] += 1
                        elif tickets[i][1] == time_arrival[2]:
                            a['t_3'] += 1
                # Детский?
                elif tickets[i][0] == type_tickets[1]:
                    # Не многодетный
                    if tickets[i][2] != type_tickets[2]:
                        c['sum'] += 1
                        # Проверяем продолжительность времени
                        if tickets[i][1] == time_arrival[0]:
                            c['t_1'] += 1
                        elif tickets[i][1] == time_arrival[1]:
                            c['t_2'] += 1
                        elif tickets[i][1] == time_arrival[2]:
                            c['t_3'] += 1
            # Многодетный?
            elif tickets[i][2] == type_tickets[2]:
                # Взрослый?
                if tickets[i][0] == type_tickets[0]:
                    m_a['sum'] += 1
                    if tickets[i][1] == time_arrival[0]:
                        m_a['t_1'] += 1
                    elif tickets[i][1] == time_arrival[1]:
                        m_a['t_2'] += 1
                    elif tickets[i][1] == time_arrival[2]:
                        m_a['t_3'] += 1
                elif tickets[i][0] == type_tickets[1]:
                    m_c['sum'] += 1
                    if tickets[i][1] == time_arrival[0]:
                        m_c['t_1'] += 1
                    elif tickets[i][1] == time_arrival[1]:
                        m_c['t_2'] += 1
                    elif tickets[i][1] == time_arrival[2]:
                        m_c['t_3'] += 1
            # Инвалид?
            elif tickets[i][2] == type_tickets[3]:
                i_['sum'] += 1
                if tickets[i][1] == time_arrival[0]:
                    i_['t_1'] += 1
                elif tickets[i][1] == time_arrival[1]:
                    i_['t_2'] += 1
                elif tickets[i][1] == time_arrival[2]:
                    i_['t_3'] += 1
        # Выводим обобщенную информацию в таблицу
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
        self.ui.tableWidget_3.setItem(2, 0, QTableWidgetItem('мног-й взр.'))
        self.ui.tableWidget_3.setItem(2, 1, QTableWidgetItem(f"{m_a['sum']}"))
        self.ui.tableWidget_3.setItem(2, 2, QTableWidgetItem(f"{m_a['t_1']}"))
        self.ui.tableWidget_3.setItem(2, 3, QTableWidgetItem(f"{m_a['t_2']}"))
        self.ui.tableWidget_3.setItem(2, 4, QTableWidgetItem(f"{m_a['t_3']}"))
        self.ui.tableWidget_3.insertRow(3)
        self.ui.tableWidget_3.setItem(3, 0, QTableWidgetItem('мног-й дет.'))
        self.ui.tableWidget_3.setItem(3, 1, QTableWidgetItem(f"{m_c['sum']}"))
        self.ui.tableWidget_3.setItem(3, 2, QTableWidgetItem(f"{m_c['t_1']}"))
        self.ui.tableWidget_3.setItem(3, 3, QTableWidgetItem(f"{m_c['t_2']}"))
        self.ui.tableWidget_3.setItem(3, 4, QTableWidgetItem(f"{m_c['t_3']}"))
        self.ui.tableWidget_3.insertRow(4)
        self.ui.tableWidget_3.setItem(4, 0, QTableWidgetItem('инвалид'))
        self.ui.tableWidget_3.setItem(4, 1, QTableWidgetItem(f"{i_['sum']}"))
        self.ui.tableWidget_3.setItem(4, 2, QTableWidgetItem(f"{i_['t_1']}"))
        self.ui.tableWidget_3.setItem(4, 3, QTableWidgetItem(f"{i_['t_2']}"))
        self.ui.tableWidget_3.setItem(4, 4, QTableWidgetItem(f"{i_['t_3']}"))

    def main_otchet_administratora(self) -> None:
        """
        Функция формирует отчет администратора.

        Параметры:

        Возвращаемое значение:
        """
        logger.info("Запуск функции main_otchet_administratora")
        path = "./otchet.pdf"
        path = os.path.realpath(path)
        row = self.ui.tableWidget_3.rowCount()
        if row >= 1:
            type_ticket = ['Взрослый, 1 ч.', 'Взрослый, 2 ч.', 'Взрослый, 3 ч.',
                           'Детский, 1 ч.', 'Детский, 2 ч.', 'Детский, 3 ч.',
                           'Мног-й взр., 1 ч.', 'Мног-й взр., 2 ч.', 'Мног-й взр., 3 ч.',
                           'Мног-й дет., 1 ч.', 'Мног-й дет., 2 ч.', 'Мног-й дет., 3 ч.',
                           'Инвалид, 3 ч.']
            table = [self.ui.tableWidget_3.item(0, 2).text(),  # взр 1
                     self.ui.tableWidget_3.item(0, 3).text(),  # взр 2
                     self.ui.tableWidget_3.item(0, 4).text(),  # взр 3
                     self.ui.tableWidget_3.item(1, 2).text(),  # дет 1
                     self.ui.tableWidget_3.item(1, 3).text(),  # дет 2
                     self.ui.tableWidget_3.item(1, 4).text(),  # дет 3
                     self.ui.tableWidget_3.item(2, 2).text(),  # мн взр 1
                     self.ui.tableWidget_3.item(2, 3).text(),  # мн взр 2
                     self.ui.tableWidget_3.item(2, 4).text(),  # мн взр 3
                     self.ui.tableWidget_3.item(3, 2).text(),  # мн дет 1
                     self.ui.tableWidget_3.item(3, 3).text(),  # мн дет 2
                     self.ui.tableWidget_3.item(3, 4).text(),  # мн дет 3
                     self.ui.tableWidget_3.item(4, 1).text()]  # инв
            """Удаляем предыдущий файл"""
            os.system("TASKKILL /F /IM SumatraPDF.exe")
            if os.path.exists(path):
                os.remove(path)
            dt1 = self.ui.dateEdit_2.date().toString("dd-MM-yyyy")
            dt2 = self.ui.dateEdit.date().toString("dd-MM-yyyy")
            # Промежуточные расчеты
            adult_1 = System.price['ticket_adult_1'] * int(table[0])
            adult_2 = System.price['ticket_adult_2'] * int(table[1])
            adult_3 = System.price['ticket_adult_3'] * int(table[2])
            kol_adult = int(table[0]) + int(table[1]) + int(table[2])
            sum_adult = adult_1 + adult_2 + adult_3
            child_1 = System.price['ticket_child_1'] * int(table[3])
            child_2 = System.price['ticket_child_2'] * int(table[4])
            child_3 = System.price['ticket_child_3'] * int(table[5])
            kol_child = int(table[3]) + int(table[4]) + int(table[5])
            sum_child = child_1 + child_2 + child_3
            many_adult_1 = round(System.price['ticket_adult_1'] / 2 * int(table[6]))
            many_adult_2 = round(System.price['ticket_adult_2'] / 2 * int(table[7]))
            many_adult_3 = round(System.price['ticket_adult_3'] / 2 * int(table[8]))
            kol_many_adult = int(table[6]) + int(table[7]) + int(table[8])
            sum_many_adult = many_adult_1 + many_adult_2 + many_adult_3
            many_child_1 = round(System.price['ticket_child_1'] / 2 * int(table[9]))
            many_child_2 = round(System.price['ticket_child_2'] / 2 * int(table[10]))
            many_child_3 = round(System.price['ticket_child_3'] / 2 * int(table[11]))
            kol_many_child = int(table[9]) + int(table[10]) + int(table[11])
            sum_many_child = many_child_1 + many_child_2 + many_child_3
            # Формируем данные
            data = [['№ п/п', 'Тип\nбилета', 'Цена, руб.',
                     'Количество, шт.', 'Стоимость, руб.'],
                    # Взрослые
                    ['1', type_ticket[0], System.price['ticket_adult_1'], table[0], adult_1],
                    ['2', type_ticket[1], System.price['ticket_adult_2'], table[1], adult_2],
                    ['3', type_ticket[2], System.price['ticket_adult_3'], table[2], adult_3],
                    # Дети
                    ['4', 'Всего взрослых билетов', '', kol_adult, sum_adult],
                    ['5', type_ticket[3], System.price['ticket_child_1'], table[3], child_1],
                    ['6', type_ticket[4], System.price['ticket_child_2'], table[4], child_2],
                    ['7', type_ticket[5], System.price['ticket_child_3'], table[5], child_3],
                    ['8', 'Всего детских билетов', '', kol_child, sum_child],
                    # Многодетные взрослые
                    ['9', type_ticket[6], round(System.price['ticket_adult_1'] / 2), table[6], many_adult_1],
                    ['10', type_ticket[7], round(System.price['ticket_adult_2'] / 2), table[7], many_adult_2],
                    ['11', type_ticket[8], round(System.price['ticket_adult_3'] / 2), table[8], many_adult_3],
                    ['12', 'Всего многодетных взрослых билетов', '', kol_many_adult, sum_many_adult],
                    # Многодетные детские
                    ['13', type_ticket[9], round(System.price['ticket_child_1'] / 2), table[9], many_child_1],
                    ['14', type_ticket[10], round(System.price['ticket_child_2'] / 2), table[10], many_child_2],
                    ['15', type_ticket[11], round(System.price['ticket_child_3'] / 2), table[11], many_child_3],
                    ['16', 'Всего многодетных детских билетов', '', kol_many_child, sum_many_child],
                    ['17', type_ticket[12], '-', table[12], '-'],
                    ['', 'Итого билетов', '',
                     kol_adult + kol_child + kol_many_adult + kol_many_child,
                     sum_adult + sum_child + sum_many_adult + sum_many_child]]
            logger.debug("Сведения для отчета администратора %s" % data)
            otchet.otchet_administratora(dt1, dt2, data)
            os.startfile(path)

    def main_otchet_kassira(self) -> None:
        """
        Функция формирует отчет кассира.

        Параметры:

        Возвращаемое значение:
        """
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
            # Формируем данные
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


class Payment:
    """Класс типов платежа (перечисление)"""
    Card: int = 101
    Cash: int = 102
    Offline: int = 100


class System:
    """Класс для хранения системной информации и функций"""
    # Данные успешно авторизованного пользователя
    user: User | None = None
    # Флаг для обновления клиента
    client_id: int | None = None
    client_update: int | None = None
    #all_clients = None # TODO: необходимо?
    # Сохраняем фамилию нового клиента
    last_name: str = ''
    # Статус продажи: 0 - создана, 1 - оплачена, 2 - возвращена
    sale_status: int | None = None
    sale_id: int | None = None
    sale_discount: int | None = None
    sale_tickets: tuple = ()
    sale_tuple: tuple = ()
    sale_special: int | None = None
    # Номер строки с активным CheckBox для исключения взрослого из продажи
    sale_checkbox_row: int | None = None
    # Состояние CheckBox для искл. взрослого из продажи: 0 - есть, 1 - нет
    exclude_from_sale: int = 0
    # Какой сегодня день: 0 - будний, 1 - выходной
    what_a_day: int | None = None
    # Первое воскресенье месяца: 0 - нет, 1 - да
    sunday: int | None = None
    today: date = date.today()
    # Номер дня недели
    num_of_week: int = 0
    pc_name: str = socket.gethostname()
    # Прайс-лист основных услуг
    price: dict = {'ticket_child_1': 0, 'ticket_child_2': 0, 'ticket_child_3': 0, 'ticket_child_week_1': 0,
                   'ticket_child_week_2': 0, 'ticket_child_week_3': 0, 'ticket_adult_1': 0,
                   'ticket_adult_2': 0, 'ticket_adult_3': 0, 'ticket_free': 0}
    price_service: dict = {}
    # Количество начисляемых талантов
    talent: dict = {'1_hour': 25, '2_hour': 35, '3_hour': 50}
    # Возраст посетителей
    age: dict = {'min': 5, 'max': 15}
    # Информация о РМ
    kol_pc: int = 0
    pc_1: str = ''
    pc_2: str = ''
    sale_dict: dict = {'kol_adult': 0, 'price_adult': 0,
                       'kol_child': 0, 'price_child': 0,
                       'detail': [0, 0, 0, 0, 0, 0, 0, 0]}
    # Содержание detail: [kol_adult, price_adult, kol_child, price_child, discount, id_adult, time, sum]

    # Храним id нового клиента
    id_new_client_in_sale: int = 0
    # Флаг печати кассовых и банковских чеков
    print_check: int = 1

    def user_authorization(self, login, password) -> int:
        """
        Функция проверяет есть ли пользователь в БД с данными, указанными на форме авторизации.

        Параметры:

        Возвращаемое значение:
        """
        logger.info('Запуск функции user_authorization')
        with Session(engine) as session:
            query = select(User).where(User.login == login, User.password == password)
            kassir: User | None = session.execute(query).scalars().first()
        if kassir:
            # Если авторизация прошла успешно - сохраняем данные пользователя
            System.user = kassir
            logger.info('kassir: %s' % kassir)
            return 1
        else:
            return 0

    @staticmethod
    def get_price(self) -> None:
        """
        Функция загружает прайс-лист основных услуг из БД.

        Параметры:

        Возвращаемое значение:
        """
        logger.info('Запуск функции get_price')
        with Session(engine) as session:
            result = session.query(Price).all()
        if result is not None:
            # TODO: исправить преобразование типов
            System.price['ticket_child_1'] = int(str(result[0]))
            System.price['ticket_child_2'] = int(str(result[1]))
            System.price['ticket_child_3'] = int(str(result[2]))
            System.price['ticket_child_week_1'] = int(str(result[3]))
            System.price['ticket_child_week_2'] = int(str(result[4]))
            System.price['ticket_child_week_3'] = int(str(result[5]))
            System.price['ticket_adult_1'] = int(str(result[6]))
            System.price['ticket_adult_2'] = int(str(result[7]))
            System.price['ticket_adult_3'] = int(str(result[8]))
            logger.debug('System.price: %s' % System.price)

    def check_day(self) -> int:
        """
        Функция проверяет статус текущего дня.

        Параметры:

        Возвращаемое значение: 1 (выходной), 0 (будний день).
        """
        logger.info('Запуск функции check_day')
        day: list[str] = dt.datetime.now().strftime('%Y-%m-%d')
        # Проверяем есть ли текущая дата в списке дополнительных рабочих дней
        with Session(engine) as session:
            query = select(Workday).where(Workday.date == day)
            check_day: Workday | None = session.execute(query).scalars().first()
        if check_day:
            logger.info('Сегодня дополнительный рабочий день')
            status_day: int = 0
        else:
            # Преобразуем текущую дату в список
            day: list[str] = day.split('-')
            # Вычисляем день недели
            number_day: int = calendar.weekday(int(day[0]), int(day[1]), int(day[2]))
            # Проверяем день недели равен 5 или 6
            if number_day >= 5:
                status_day: int = 1
                # System.what_a_day = 1 TODO: нужно ли
                logger.info('Сегодня выходной день')
            else:
                day: str = '-'.join(day)
                # Проверяем есть ли текущая дата в списке дополнительных праздничных дней
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

    @staticmethod
    def calculate_age(born: date) -> int:
        """
        Функция вычисляет возраст посетителя.

        Параметры:

        Возвращаемое значение:
        """
        today: date = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    @staticmethod
    def calculate_ticket_type(age: int) -> str:
        """
        Функция определяет тип входного билета.

        Параметры:

        Возвращаемое значение:
        """
        if age < System.age['min']:
            return 'бесплатный'
        elif System.age['min'] <= age < System.age['max']:
            return 'детский'
        elif age >= System.age['max']:
            return 'взрослый'


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    auth = AuthForm()
    auth.show()
    # auth.ui.label_9.setText(database)
    sys.exit(app.exec())

    # window = MainWindow()
    # window.show()
    # sys.exit(app.exec())
