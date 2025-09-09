import datetime as dt
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Optional, Type

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal, QThread
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QTableWidgetItem,
)
from PySide6.QtWidgets import QDialog, QWidget
from PySide6.QtWidgets import QMessageBox
from sqlalchemy import and_, select, update, desc
from sqlalchemy.orm import Session

from db.models import Client
from db.models import Sale
from db.models import Ticket
from design.logic.authorization import Ui_Dialog
from design.logic.client import Ui_Dialog_Client
from design.logic.main_form import Ui_MainWindow
from design.logic.pay import Ui_Dialog_Pay
from design.logic.sale import Ui_Dialog_Sale
from design.logic.slip import Ui_Dialog_Slip
from modules import otchet
from modules import payment_equipment as pq
from modules import windows
from modules.auth_logic import perform_pre_sale_checks
from modules.logger import logger, logger_wraps
from modules.progress_window import ProgressWindow
from modules.sale_logic import (
    calculate_age,
    calculate_ticket_type,
    calculated_ticket_price,
    calculate_adult_price,
    calculate_child_price,
    calculate_discounted_price,
    calculate_discount,
    calculate_itog,
    convert_sale_dict_values,
    generating_parts_for_partial_returns,
    get_talent_based_on_time,
    update_adult_count,
    update_child_count,
)
from modules.system import System
from modules.worker import TransactionWorker

system = System()
config_data = system.config
logger.add(system.log_file, rotation="1 MB")


class AuthForm(QDialog):
    """Форма авторизации"""

    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        # Добавляем логотип на форму
        pixmap = QPixmap("pylogo.png")
        self.ui.label_4.setPixmap(pixmap)
        self.ui.label_7.setText(system.software_version)
        self.ui.pushButton.clicked.connect(self.starting_the_main_form)
        self.ui.pushButton_2.clicked.connect(self.close)

    def starting_the_main_form(self) -> None:
        """
        Функция запускает предпродажные проверки и устанавливает системные параметры.
        Выполняет проверку авторизации пользователя, подключение к ККТ, а затем отображает главное окно приложения.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, а выполняет ряд операций, включая проверку входных данных и отображение главного окна.
        """
        logger.info("Запуск функции starting_the_main_form")
        if not system.check_db_connection():
            windows.info_window(
                "База данных недоступна",
                "Не удалось подключиться к серверу базы данных.\n Приложение будет закрыто.",
                ""
            )
            sys.exit(1)
        login: str = self.ui.lineEdit.text()
        password: str = self.ui.lineEdit_2.text()

        if not self.perform_login_checks(login, password):
            return
        # Проверка состояния ККТ
        self.check_kkt_connection()
        self.show_main_window()

    @staticmethod
    def perform_login_checks(login: str, password: str) -> bool:
        """
        Проверка авторизации пользователя.
        Проверяет введенные логин и пароль, и если они корректны, закрывает окно авторизации.
        В случае ошибки показывает окно с информацией о неверных данных.

        Параметры:
            login: str
                Логин пользователя, введенный в поле входа.

            password: str
                Пароль пользователя, введенный в поле входа.

        Возвращаемое значение:
            bool: Возвращает `True`, если авторизация прошла успешно, и `False`, если произошла ошибка.
        """
        if perform_pre_sale_checks(login, password) == 1:
            auth.close()
            return True
        else:
            windows.info_window("Пользователь не найден", "Проверьте правильность ввода логина и пароля.",
                                "Убедитесь, что используете правильный логин и пароль для входа в систему.")
            return False

    def check_kkt_connection(self):
        """
        Проверка подключения и состояния ККТ.
        Проверяет физическое подключение кассового аппарата и его работоспособность. Если ККТ не подключен,
        выводит предупреждающее сообщение и продолжает работу без фискальных операций.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, а лишь выполняет проверку подключения и выводит сообщения при необходимости.
        """
        try:
            if pq.is_kkt_connected():
                self.perform_kkt_checks()
            elif pq.kkt_available:
                try:
                    if pq.get_info(hide=True) is not None:
                        # Если получили информацию, значит ККТ подключен
                        self.perform_kkt_checks()
                        return
                except (ConnectionError, TimeoutError) as e:
                    logger.error(f"Ошибка при получении информации о ККТ: {e}")
                except Exception as e:  # Общий блок для других исключений
                    logger.error(f"Неизвестная ошибка при получении информации о ККТ: {e}")

                # Показать предупреждение, если ККТ не подключен
                windows.info_window(
                    "Внимание",
                    "Кассовый аппарат не подключен",
                    "Программа продолжит работу без фискальных операций."
                )
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Ошибка при проверке подключения к ККТ: {e}")
        except Exception as e:  # Общий блок для других исключений
            logger.error(f"Неизвестная ошибка при проверке ККТ: {e}")

    @staticmethod
    def perform_kkt_checks():
        """
        Проверка информации с ККТ и последнего чека.
        Запрашивает информацию о текущем состоянии ККТ и проверяет дату последнего чека.
        Если дата последнего чека превышает максимально допустимый период, выводится предупреждающее сообщение.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, а только выполняет проверку состояния ККТ.
        """
        if pq.get_info(hide=True) is not None:
            last_check = pq.get_last_document_datetime()
            pq.check_stale_document(last_check, max_days=7)

    @staticmethod
    def show_main_window():
        """
        Отображение главного окна приложения.
        Создает и отображает главное окно приложения, устанавливая заголовок окна и показывая основные элементы интерфейса.
        Также выводится информация о пользователе, версии программы и базе данных.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, а лишь выполняет отображение главного окна.
        """
        window = MainWindow()
        window.showMaximized()
        user_full_name = f"{system.user.last_name} {system.user.first_name}"
        window.setWindowTitle(
            f"PyMASL ver. {system.software_version}. Пользователь: {user_full_name}. БД: {system.database}"
        )
        window.main_button_all_sales()
        window.exec_()



class ClientForm(QDialog):
    """Форма с данными клиента"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_Client()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.client_save)
        self.ui.pushButton_2.clicked.connect(self.close)
        self.ui.pushButton_3.clicked.connect(self.client_data_copy)
        self.ui.pushButton_4.clicked.connect(self.client_data_paste)

    def client_data_copy(self):
        """
        Функция запоминает фамилию нового клиента для последующей вставки.
        Полезна при внесении в БД сведений об однофамильцах.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, просто сохраняет фамилию клиента в системную переменную.
        """
        logger.info("Запуск функции client_data_copy")
        system.last_name = str(self.ui.lineEdit.text()).title()

    def client_data_paste(self):
        """
        Функция вставляет в соответствующее поле фамилию клиента,
        внесенного в БД в последний раз.

        Параметры:
        self: object
            Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
        None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции client_data_paste")
        self.ui.lineEdit.setText(system.last_name)

    def client_save(self):
        """
        Функция сохраняет в БД сведения о новом клиенте.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
        """
        logger.info("Запуск функции client_save")
        # сбрасываем id последнего добавленного клиента
        system.add_new_client_in_sale = 0
        # делаем заглавными первые буквы фамилии и имени
        system.last_name = str(self.ui.lineEdit.text()).title()
        first_name = str(self.ui.lineEdit_2.text()).title()
        # проверяем заполнены ли поля имени и фамилии
        if len(system.last_name) >= 2 and len(first_name) >= 2:
            if system.client_update != 1:
                logger.info("Добавляем нового клиента")
                with Session(system.engine) as session:
                    new_client = Client(
                        last_name=system.last_name,
                        first_name=str(self.ui.lineEdit_2.text()),
                        middle_name=str(self.ui.lineEdit_3.text()),
                        birth_date=(self.ui.dateEdit.date().toString("yyyy-MM-dd")),
                        gender=str(self.ui.comboBox.currentText()),
                        phone=self.ui.lineEdit_4.text(),
                        email=self.ui.lineEdit_5.text(),
                        privilege=str(self.ui.comboBox_2.currentText()),
                    )
                    session.add(new_client)
                    session.commit()
                    # сохраняем id нового клиента
                    system.id_new_client_in_sale = new_client.id
            elif system.client_update == 1:
                # обновляем информацию о клиенте
                logger.info("Обновляем информацию о клиенте")
                with Session(system.engine) as session:
                    session.execute(
                        update(Client)
                        .where(Client.id == system.client_id)
                        .values(
                            id=system.client_id,
                            last_name=str(self.ui.lineEdit.text()),
                            first_name=str(self.ui.lineEdit_2.text()),
                            middle_name=str(self.ui.lineEdit_3.text()),
                            birth_date=self.ui.dateEdit.date().toString("yyyy-MM-dd"),
                            gender=str(self.ui.comboBox.currentText()),
                            phone=self.ui.lineEdit_4.text(),
                            email=self.ui.lineEdit_5.text(),
                            privilege=str((self.ui.comboBox_2.currentText())),
                        )
                    )
                    session.commit()
            self.close()
            system.client_update = None
            system.client_id = None
        else:
            windows.info_window(
                "Внимание!", "Необходимо заполнить обязательные поля: имя и фамилия", ""
            )


class SaleForm(QDialog):
    """Форма продажи"""

    def __init__(self, main_window=None):
        super().__init__()
        self.ui = Ui_Dialog_Sale()
        self.ui.setupUi(self)

        # Инициализация worker
        self.worker = None
        self.thread = None
        self._transaction_finished = False
        self.progress_window = None  # Создаем атрибут, но не инициализируем окно сразу
        self.main_window = main_window  # Сохраняем ссылку на MainWindow

        self.ui.pushButton.clicked.connect(self.sale_search_clients)
        self.ui.pushButton_2.clicked.connect(lambda: MainWindow.main_open_client(self))
        self.ui.pushButton_11.clicked.connect(self.edit_client_in_sale)
        self.ui.pushButton_3.clicked.connect(self.save_sale)
        self.ui.pushButton_4.clicked.connect(self.close)
        self.ui.pushButton_5.clicked.connect(
            lambda: self.open_pay_form(self.ui.label_8.text())
        )
        self.ui.pushButton_6.clicked.connect(self.sale_return)
        self.ui.pushButton_7.clicked.connect(self.print_saved_tickets)
        self.ui.pushButton_8.clicked.connect(self.open_saved_tickets)
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
        self.ui.pushButton_13.clicked.connect(SlipForm.get_slip)
        # функция отмены платежа
        self.ui.pushButton_14.clicked.connect(self.sale_canceling)

    def edit_client_in_sale(self) -> None:
        """
        Функция ищет выделенную строку в таблице клиентов и открывает форму для редактирования данных.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
        """
        logger.info("Запуск функции edit_client_in_sale")
        # Ищем индекс и значение ячейки
        row_number: int = self.ui.tableWidget.currentRow()
        # Получаем содержимое ячейки
        client_id: str = self.ui.tableWidget.item(row_number, 5).text()
        # При типизации указываем, что search_client может быть либо экземпляром Client, либо None
        with Session(system.engine) as session:
            search_client: Optional[Client] = (
                session.query(Client).filter_by(id=client_id).first()
            )
        # Проверяем, найден ли клиент
        if search_client:
            # Сохраняем id клиента
            system.client_id = search_client.id  # Присваиваем id клиента
        else:
            logger.error(f"Клиент с id {client_id} не найден.")
        # Передаем в форму данные клиента
        client = ClientForm()
        client.ui.lineEdit.setText(search_client.last_name)
        client.ui.lineEdit_2.setText(search_client.first_name)
        client.ui.lineEdit_3.setText(search_client.middle_name)
        client.ui.dateEdit.setDate(search_client.birth_date)
        # Поиск значения для установки в ComboBox gender
        index_gender: int = client.ui.comboBox.findText(
            search_client.gender, Qt.MatchFixedString
        )
        if index_gender >= 0:
            client.ui.comboBox.setCurrentIndex(index_gender)
        client.ui.lineEdit_4.setText(search_client.phone)
        client.ui.lineEdit_5.setText(search_client.email)
        # Ищем значение для установки в ComboBox privilege
        index_privilege: int | None = client.ui.comboBox.findText(
            search_client.privilege, Qt.MatchFixedString
        )
        if index_privilege >= 0:
            client.ui.comboBox_2.setCurrentIndex(index_privilege)
        client.show()
        # Сохраняем параметры данных об уже существующем клиенте
        system.client_update = 1
        logger.info(f"Обновляем инф. клиента {system.client_id}")
        client.exec_()

    def adding_new_client_to_sale(self) -> None:
        """
        Функция добавляет в окно продажи только что созданного клиента.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
        """
        logger.info("Запуск функции adding_new_client_to_sale")
        # Запрашиваем данные нового клиента
        with Session(system.engine) as session:
            search_client = (
                session.query(Client)
                .filter_by(id=system.id_new_client_in_sale)
                .one_or_none()
            )
        # Проверяем, найден ли клиент
        if search_client is None:
            logger.error(f"Клиент с ID {system.id_new_client_in_sale} не найден.")
            return
        logger.debug(f"Найденный клиент: {search_client.id}")
        # Вычисляем возраст клиента
        age: int = calculate_age(
            search_client.birth_date
        )  # system.calculate_age(search_client.birth_date)
        # Определяем тип билета и цену
        type_ticket: str = calculate_ticket_type(age)
        # Определяем тип билета и цену
        time: int = int(self.ui.comboBox.currentText())
        price = calculated_ticket_price(type_ticket, time)
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
        self.filling_client_table_widget_2(
            row,
            search_client.last_name,
            search_client.first_name,
            type_ticket,
            price,
            search_client.privilege,
            search_client.id,
            age,
        )

    def tracking_button_pressing(self, event) -> None:
        """
        Функция отслеживает нажатия клавиш Delete и Backspace.

        Параметры:
            event: QKeyEvent - Событие клавиатуры, которое содержит информацию о нажатой клавише.

        Возвращаемое значение:
            None
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
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
        """
        logger.info("Запуск функции deleting_selected_record")
        if self.ui.tableWidget_2.rowCount() > 0:
            current_row: int = self.ui.tableWidget_2.currentRow()
            # Перед удалением записи обновляем sale_dict
            type_ticket: str = self.ui.tableWidget_2.item(current_row, 2).text()
            # Если checkbox в tableWidget_2 активирован, то обновляем details
            if type_ticket == "взрослый":
                if (
                    self.ui.tableWidget_2.cellWidget(current_row, 7)
                    .findChild(QCheckBox)
                    .isChecked()
                ):
                    system.sale_dict["detail"][0] -= 1
                else:
                    system.sale_dict["kol_adult"] -= 1
                # Если активирована скидка
                if self.ui.checkBox_2.isChecked():
                    index: int = self.ui.comboBox_2.currentIndex()
                    if index > 0:
                        system.sale_dict["detail"][0] -= 1
            elif type_ticket == "детский":
                if (
                    self.ui.tableWidget_2.cellWidget(current_row, 7)
                    .findChild(QCheckBox)
                    .isChecked()
                ):
                    system.sale_dict["detail"][2] -= 1
                else:
                    system.sale_dict["kol_child"] -= 1
                # Если активирована скидка
                if self.ui.checkBox_2.isChecked():
                    index: int = self.ui.comboBox_2.currentIndex()
                    if index > 0:
                        system.sale_dict["detail"][2] -= 1
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
            # Обновляем system.sale_dict
            sale_initial_values = {
                "kol_adult": 0,
                "price_adult": 0,
                "kol_child": 0,
                "price_child": 0,
                "detail": [0, 0, 0, 0, 0, 0, 0, 0],
            }
            system.sale_dict.update(sale_initial_values)
            system.sale_discount = 0
            self.sale_update()

    def check_filter_update(self) -> None:
        """
        Функция очищает строку поиска (lineEdit).

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
        """
        logger.info("Запуск функции check_filter_update")
        self.ui.lineEdit.clear()

    def changing_color_of_calendar(self) -> None:
        """
        Функция изменяет цвет календаря.
        Если текущий день праздничный или выходной - dateEdit становится красным.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
        """
        logger.info("Запуск функции changing_color_of_calendar")
        if system.check_day() == 1:
            self.ui.dateEdit.setStyleSheet("background-color: red;")
        else:
            self.ui.dateEdit.setStyleSheet("background-color: white;")

    def checking_status_discounted_field(self) -> None:
        """
        Функция проверяет активность поля со скидкой.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
        """
        logger.info("Запуск функции checking_status_discounted_field")
        if self.ui.checkBox_2.isChecked():
            self.ui.comboBox_2.setEnabled(True)
        else:
            self.ui.comboBox_2.setEnabled(False)
            self.ui.comboBox_2.setCurrentIndex(0)
            # отменяем скидку
            system.sale_discount = 0
            system.sale_dict["detail"][4] = 0
            # Обновляем в system.sale_dict информацию о скидках
            system.sale_dict["detail"][0] = 0
            system.sale_dict["detail"][1] = 0
            system.sale_dict["detail"][2] = 0
            system.sale_dict["detail"][3] = 0
            self.sale_update()

    def filling_client_table_widget(
        self,
        last_name: str,
        first_name: str,
        age: int,
        privilege: str,
        phone: str,
        id: int,
    ) -> None:
        """
        Функция заполняет полученными данными tableWidget (список посетителей).

        Параметры:
            last_name (str): Фамилия клиента.
            first_name (str): Имя клиента.
            age (int): Возраст клиента.
            privilege (str): Привилегия клиента.
            phone (str): Телефон клиента.
            id (int): Идентификатор клиента.

        Возвращаемое значение:
            None
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

    def filling_client_table_widget_2(
        self,
        row: int,
        last_name: str,
        first_name: str,
        type_ticket: str,
        price: int,
        privilege: str,
        id: int,
        age: int,
    ) -> None:
        """
        Функция заполняет полученными данными tableWidget_2 (перечень клиентов в продаже).

        Параметры:
            row (int): Номер строки в таблице.
            last_name (str): Фамилия клиента.
            first_name (str): Имя клиента.
            type_ticket (str): Тип билета (например, взрослый или детский).
            price (int): Цена билета.
            privilege (str): Привилегия клиента.
            id (int): Идентификатор клиента.
            age (int): Возраст клиента.

        Возвращаемое значение:
            None
        """
        self.ui.tableWidget_2.setItem(row, 0, QTableWidgetItem(last_name))
        self.ui.tableWidget_2.setItem(row, 1, QTableWidgetItem(first_name))
        self.ui.tableWidget_2.setItem(row, 2, QTableWidgetItem(type_ticket))
        self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(price))
        self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(privilege))
        self.ui.tableWidget_2.setItem(row, 5, QTableWidgetItem(str(id)))
        self.ui.tableWidget_2.setColumnHidden(5, True)
        self.ui.tableWidget_2.setItem(row, 6, QTableWidgetItem(str(age)))

    def filling_client_table_widget_3(
        self,
        row: int,
        last_name: str,
        first_name: str,
        age: int,
        privilege: str,
        id: int,
    ) -> None:
        """
        Функция заполняет полученными данными tableWidget_3 (список связанных с выбранным клиентом посетителей).

        Параметры:
            row (int): Номер строки в таблице.
            last_name (str): Фамилия клиента.
            first_name (str): Имя клиента.
            age (int): Возраст клиента.
            privilege (str): Привилегия клиента.
            id (int): Идентификатор клиента.

        Возвращаемое значение:
            None
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
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
        """
        logger.info("Запуск функции sale_search_clients")
        if system.what_a_day == 1:
            self.ui.dateEdit.setStyleSheet("background-color: red;")
        # Вычисляем индекс значения
        index: int = self.ui.comboBox_4.currentIndex()
        if index == 2:
            # Поиск по номеру телефона
            user_filter: str = "%" + self.ui.lineEdit.text() + "%"
            with Session(system.engine) as session:
                search = (
                    session.query(Client).filter(Client.phone.ilike(user_filter)).all()
                )
            # logger.debug(search)
            for client in search:
                age = calculate_age(client.birth_date)
                self.filling_client_table_widget(
                    client.last_name,
                    client.first_name,
                    age,
                    client.privilege,
                    client.phone,
                    client.id,
                )
        elif index == 1:
            # Поиск по фамилии
            query: str = "%" + self.ui.lineEdit.text() + "%"
            self.ui.tableWidget.setRowCount(0)
            with Session(system.engine) as session:
                search: list[Type[Client]] = (
                    session.query(Client).filter(Client.last_name.ilike(query)).all()
                )
            for client in search:
                age = calculate_age(client.birth_date)
                self.filling_client_table_widget(
                    client.last_name,
                    client.first_name,
                    age,
                    client.privilege,
                    client.phone,
                    client.id,
                )
        elif index == 0:
            # Поиск по фамилии и имени
            self.ui.tableWidget.setRowCount(0)
            search: list[Type[Client]] = self.ui.lineEdit.text().title()
            # Разбиваем поисковую фразу на две
            lst: Any = search.split()
            if len(lst) == 2:
                with Session(system.engine) as session:
                    search: list[Type[Client]] = (
                        session.query(Client)
                        .filter(
                            and_(
                                Client.first_name.ilike(lst[1] + "%"),
                                Client.last_name.ilike(lst[0] + "%"),
                            )
                        )
                        .all()
                    )
            else:
                windows.info_window(
                    "Неправильно задано условие для поиска",
                    "Введите начальные буквы фамилии" "и имени через пробел",
                    "",
                )
            for client in search:
                age = calculate_age(client.birth_date)
                self.filling_client_table_widget(
                    client.last_name,
                    client.first_name,
                    age,
                    client.privilege,
                    client.phone,
                    client.id,
                )
        elif index == 3:
            # Поиск инвалидов
            self.ui.tableWidget.setRowCount(0)
            with Session(system.engine) as session:
                search: list[Type[Client]] = (
                    session.query(Client)
                    .filter(Client.privilege.ilike("%" + "и"))
                    .all()
                )
            for client in search:
                age = calculate_age(client.birth_date)
                self.filling_client_table_widget(
                    client.last_name,
                    client.first_name,
                    age,
                    client.privilege,
                    client.phone,
                    client.id,
                )
        elif index == 4:
            # Поиск многодетных
            self.ui.tableWidget.setRowCount(0)
            with Session(system.engine) as session:
                search: list[Type[Client]] = (
                    session.query(Client)
                    .filter(Client.privilege.ilike("%" + "м"))
                    .all()
                )
            for client in search:
                age = calculate_age(client.birth_date)
                self.filling_client_table_widget(
                    client.last_name,
                    client.first_name,
                    age,
                    client.privilege,
                    client.phone,
                    client.id,
                )

    def clearing_client_list(self) -> None:
        """
        Функция очищает список клиентов (tableWidget).

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
        """
        logger.info("Запуск функции clearing_client_list")
        self.ui.tableWidget.clearContents()
        self.ui.tableWidget.setRowCount(0)

    @logger_wraps()
    def adding_client_to_sale(self, *args, **kwargs) -> None:
        """
        Функция ищет выделенную строку в таблице клиентов и передает ее в таблицу заказа.

        Параметры:
            args: Дополнительные позиционные аргументы.
            kwargs: Дополнительные именованные аргументы.

        Возвращаемое значение:
            None
        """
        logger.info("Запуск функции adding_client_to_sale")
        # Изменяем ширину столбцов
        self.ui.tableWidget_2.setColumnWidth(3, 5)
        self.ui.tableWidget_2.setColumnWidth(4, 5)
        self.ui.tableWidget_2.setColumnWidth(7, 40)
        self.ui.tableWidget_2.setColumnWidth(8, 5)
        self.ui.tableWidget_3.setColumnWidth(3, 7)
        # Если продажа новая - обновляем статус
        system.sale_status = 0
        logger.warning(f"Статус продажи - новая")
        row_number: int = self.ui.tableWidget.currentRow()
        res: str = self.ui.tableWidget.item(row_number, 5).text()
        with Session(system.engine) as session:
            search_client: Type[Client] = (
                session.query(Client).filter_by(id=res).first()
            )
        # Вычисляем возраст клиента
        age: int = int(self.ui.tableWidget.item(row_number, 2).text())
        # Определяем тип билета и цену
        type_ticket: str = calculate_ticket_type(age)
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
        self.filling_client_table_widget_2(
            row,
            search_client.last_name,
            search_client.first_name,
            type_ticket,
            0,
            search_client.privilege,
            search_client.id,
            age,
        )
        self.sale_update()
        # Очищаем tableWidget_3
        while self.ui.tableWidget_3.rowCount() > 0:
            self.ui.tableWidget_3.removeRow(0)
        # Ищем продажи, в которых клиент был ранее
        client_list: set = set()
        with Session(system.engine) as session:
            sales = (
                session.query(Client.id, Ticket.id_sale, Ticket.id_sale)
                .filter(
                    and_(
                        Client.id == search_client.id,
                        Ticket.id_client == search_client.id,
                    )
                )
                .join(Ticket, Client.id == Ticket.id_client)
            )
            for client_in_sales in sales:
                if client_in_sales:
                    # Находим других посетителей, которые были в этих продажах
                    search_sale = session.query(
                        Ticket.id_sale, Ticket.id_client
                    ).filter(Ticket.id_sale == client_in_sales[2])
                    for search_cl in search_sale:
                        # Запрашиваем информацию об этих клиентах
                        client_list.add(search_cl[1])
        # изменяем ширину столбов
        self.ui.tableWidget_3.setColumnWidth(2, 15)
        # выводим в tableWidget_3 список найденных клиентов
        for client in client_list:
            search_cl_in_sale = session.query(Client).filter_by(id=client).one()
            row: int = self.ui.tableWidget_3.rowCount()
            age: int = calculate_age(search_cl_in_sale.birth_date)
            self.filling_client_table_widget_3(
                row,
                search_cl_in_sale.last_name,
                search_cl_in_sale.first_name,
                age,
                search_cl_in_sale.privilege,
                search_cl_in_sale.id,
            )

    @logger_wraps()
    def adding_related_client_to_sale(self, *args, **kwargs) -> None:
        """
        Функция ищет выделенную строку в таблице клиентов, которые были ранее в одной продаже,
        и передает данные об этом посетителе в таблицу заказа.

        Параметры:
            *args:
                Дополнительные позиционные аргументы, которые могут быть переданы функции.
            **kwargs:
                Дополнительные именованные аргументы, которые могут быть переданы функции.

        Возвращаемое значение:
            None:
                Функция не возвращает значений.
        """
        logger.info("Запуск функции adding_related_client_to_sale")
        row_number: int = self.ui.tableWidget_3.currentRow()
        # Получаем содержимое ячейки
        res: str = self.ui.tableWidget_3.item(row_number, 4).text()
        age: int = int(self.ui.tableWidget_3.item(row_number, 2).text())
        # Находим выделенного в таблице клиента
        with Session(system.engine) as session:
            search_client = session.query(Client).filter_by(id=res).first()
        # Определяем тип билета и цену
        type_ticket: str = calculate_ticket_type(age)
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
            row,
            search_client.last_name,
            search_client.first_name,
            type_ticket,
            0,
            search_client.privilege,
            search_client.id,
            age,
        )
        self.sale_update()

    def sale_update(self) -> None:
        """
        Функция обновляет позиции в заказе, генерирует информацию о продаже и список билетов.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, сохраняет или обновляет запись о клиенте в базе данных.
        """
        logger.info("Запуск функции sale_update")
        # Используем для подсчета количества посетителей
        # В id_adult запоминаем идентификатор для "привязки" продажи ко взрослому
        # Флаг "многодетные": 1 - 2 часа бесплатно, 2 - скидка 50%
        count_initial_values = {
            "kol_adult": 0,
            "kol_child": 0,
            "kol_sale_adult": 0,
            "kol_sale_child": 0,
            "kol_adult_many_child": 0,
            "kol_child_many_child": 0,
            "kol_adult_invalid": 0,
            "kol_child_invalid": 0,
            "id_adult": 0,
            "many_child": 0,
            "invalid": 0,
            "talent": 0,
        }
        if system.count_number_of_visitors is None:
            system.count_number_of_visitors = {}
        system.count_number_of_visitors.update(count_initial_values)
        # Учитываем продолжительность посещения
        time_ticket: int = int(self.ui.comboBox.currentText())
        # Сохраняем билеты
        tickets: list[tuple[str, str, str, str, str, str, str, str, int, str]] = []
        # Обнуляем system.sale_dict
        sale_initial_values = {
            "kol_adult": 0,
            "price_adult": 0,
            "kol_child": 0,
            "price_child": 0,
            "detail": [0, 0, 0, 0, 0, 0, 0, 0],
        }
        if system.sale_dict is None:
            system.sale_dict = {}
        system.sale_dict.update(sale_initial_values)
        # Устанавливаем время и количество талантов
        system.sale_dict["detail"][6], system.count_number_of_visitors["talent"] = (
            get_talent_based_on_time(time_ticket)
        )
        # Записываем в sale_dict время посещения
        date_time: str = self.ui.dateEdit.date().toString("yyyy-MM-dd")
        # Анализируем таблицу с заказом
        rows: int = self.ui.tableWidget_2.rowCount()
        for row in range(rows):
            # Сегодня день многодетных?
            self.analyzing_visitor_category(row)
            # Учитываем тип билета
            type_ticket: str = self.ui.tableWidget_2.item(row, 2).text()
            price = self.ticket_counting(row, type_ticket)
            self.apply_discounts(row, price, type_ticket)
        itog: int = calculate_itog()
        self.ui.label_8.setText(str(itog))
        system.sale_dict["detail"][7] = itog
        self.ui.label_5.setText(str(system.count_number_of_visitors["kol_adult"]))
        self.ui.label_7.setText(str(system.count_number_of_visitors["kol_child"]))
        self.ui.label_17.setText(
            str(system.count_number_of_visitors["kol_adult_many_child"])
        )
        self.ui.label_19.setText(
            str(system.count_number_of_visitors["kol_child_many_child"])
        )
        # Преобразуем значения в system.sale_dict к нужным типам данных
        system.sale_dict = convert_sale_dict_values(system.sale_dict)
        logger.debug(f"Обновленный system.sale_dict: {system.sale_dict}")
        # Генерируем список с билетами
        for row in range(rows):
            # Если установлена метка "не идет"
            if self.ui.tableWidget_2.item(row, 4).text() == "н":
                self.ui.tableWidget_2.setItem(
                    row, 3, QTableWidgetItem(f"{system.price['ticket_free']}")
                )
            self.generate_ticket_list(row, tickets, date_time)
        system.sale_tickets = tickets
        # Проверяем есть ли в продаже взрослый
        if system.sale_dict["kol_adult"] >= 1:
            self.ui.pushButton_5.setEnabled(True)
        else:
            self.ui.pushButton_5.setEnabled(False)
        # Отключаем checkbox исключения из продажи для других позиций
        if system.exclude_from_sale == 1:
            for row in range(rows):
                if row != system.sale_checkbox_row:
                    self.ui.tableWidget_2.cellWidget(row, 8).findChild(
                        QCheckBox
                    ).setEnabled(False)
                # Флаг состояния QCheckBox не активирован (вернули в продажу)
                else:
                    logger.debug(
                        "Активируем QCheckBox строке - возвращаем клиента в продажу"
                    )
                    self.ui.tableWidget_2.cellWidget(row, 8).findChild(
                        QCheckBox
                    ).setEnabled(True)

    def apply_discounts(self, row: int, price: int, type_ticket: str) -> None:
        """
        Применяет скидки к билетам посетителей.

        Параметры:
            row (int): Номер строки.
            price (int): Цена до применения скидок.
            type_ticket (str): Тип билета (взрослый, детский).

        Возвращаемое значение:
            None
        """
        logger.info("Запуск функции apply_discounts")
        # Устанавливаем цену в таблицу и пересчитываем
        self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{price}"))
        system.sale_discount = int(self.ui.comboBox_2.currentText())
        logger.debug(system.sale_discount)
        new_price, category, discount_status = calculate_discounted_price(
            price, type_ticket
        )
        # Применяем скидку
        self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(f"{new_price}"))
        # Если категория изменена, устанавливаем ее в таблицу
        if category:
            self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(category))
        # Иначе проверяем активен ли checkbox со скидкой и размер > 0
        if self.ui.checkBox_2.isChecked():
            if system.sale_discount > 0:
                system.sale_dict["detail"][4] = system.sale_discount
                if system.sale_discount > 0:
                    new_price = calculate_discount(price, system.sale_discount)
                    # Если checkbox в акт - применяем к этой строке скидку
                    if (
                        self.ui.tableWidget_2.cellWidget(row, 7)
                        .findChild(QCheckBox)
                        .isChecked()
                    ):
                        if type_ticket == "взрослый":
                            system.count_number_of_visitors["kol_sale_adult"] += 1
                            system.sale_dict["detail"][0] = (
                                system.count_number_of_visitors["kol_sale_adult"]
                            )
                            system.sale_dict["detail"][1] = new_price
                        elif type_ticket == "детский":
                            system.count_number_of_visitors["kol_sale_child"] += 1
                            system.sale_dict["detail"][2] = (
                                system.count_number_of_visitors["kol_sale_child"]
                            )
                            system.sale_dict["detail"][3] = new_price
                        self.ui.tableWidget_2.setItem(
                            row, 3, QTableWidgetItem(f"{new_price}")
                        )

    def ticket_counting(self, row: int, type_ticket: str) -> int:
        """
        Функция считает количество билетов.

        Параметры:
            row (int): Номер строки.
            type_ticket (str): Тип билета (взрослый или детский).

        Возвращаемое значение:
            int: Цена билета.
        """
        logger.info("Запуск функции ticket_counting")

        if type_ticket == "взрослый":
            return self.calculate_adult(row)
        elif type_ticket == "детский":
            return self.calculate_child(row)
        else:
            return system.price["ticket_free"]

    def calculate_adult(self, row: int) -> int:
        """
        Считает цену взрослого билета в зависимости от продолжительности и категорий.

        Параметры:
            row (int): Номер строки.

        Возвращаемое значение:
            int: Цена взрослого билета.
        """
        logger.info("Запуск функции calculate_adult")
        price = calculate_adult_price()
        self.bind_adult_to_sale(row)
        # Если checkbox активен - взрослый в оплату не добавляется
        self.adult_exclusion(row)
        update_adult_count()
        system.sale_dict["price_adult"] = price

        return price

    def calculate_child(self, row: int) -> int:
        """
        Считает цену детского билета в зависимости от продолжительности и категорий.

        Параметры:
            row (int): Номер строки.

        Возвращаемое значение:
            int: Цена детского билета.
        """
        logger.info("Запуск функции calculate_child")
        self.ui.tableWidget_2.cellWidget(row, 8).findChild(QCheckBox).setEnabled(False)
        price = calculate_child_price()
        update_child_count()
        system.sale_dict["price_child"] = price

        return price

    def bind_adult_to_sale(self, row: int) -> None:
        """
        Привязывает взрослого посетителя к продаже, если его еще нет в списке.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.
            row (int): Номер строки в таблице.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции bind_adult_to_sale")
        if system.count_number_of_visitors["id_adult"] == 0:
            system.count_number_of_visitors["id_adult"] += 1
            system.sale_dict["detail"][5] = self.ui.tableWidget_2.item(row, 5).text()

    def analyzing_visitor_category(self, row: int) -> None:
        """
        Функция анализирует типы категорий посетителей.

        Параметры:
            row (int): Номер строки в таблице.

        Возвращаемое значение: None
        """
        logger.info("Запуск функции analyzing_visitor_category")
        visitor_category = self.ui.tableWidget_2.item(row, 4).text()
        if visitor_category == "м":
            self.handle_many_children_discount(row)
        elif visitor_category == "и":
            self.handle_invalid_discount()

    def handle_many_children_discount(self, row: int) -> None:
        """
        Обрабатывает скидки для многодетных.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.
            row (int): Номер строки в таблице.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции handle_many_children_discount")
        self.ui.tableWidget_2.cellWidget(row, 7).findChild(QCheckBox).setCheckState(
            Qt.Checked
        )
        if system.sunday == 1 and self.ui.checkBox_3.isChecked():
            self.apply_extended_many_children_discount()
        elif system.sunday == 1:
            self.apply_full_many_children_discount()
        elif system.num_of_week <= 5:
            self.apply_half_many_children_discount()

    def handle_invalid_discount(self) -> None:
        """
        Обрабатывает скидки для инвалидов.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции handle_invalid_discount")
        system.count_number_of_visitors["invalid"] = 1
        system.sale_dict["detail"][4] = 100
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

    def apply_extended_many_children_discount(self) -> None:
        """
        Применение скидки на продление для многодетных.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции apply_extended_many_children_discount")
        system.count_number_of_visitors["many_child"] = 0
        self.ui.checkBox_2.setEnabled(False)
        self.ui.checkBox_2.setChecked(True)
        self.ui.comboBox_2.setCurrentIndex(10)
        self.ui.comboBox.setEnabled(True)

    def apply_full_many_children_discount(self) -> None:
        """
        Применение полной скидки для многодетных.

        Параметры:
        self: object
            Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции apply_full_many_children_discount")
        logger.info("Сегодня день многодетных")
        system.count_number_of_visitors["many_child"] = 1
        # Устанавливаем продолжительность посещения 2 часа
        self.ui.comboBox.setCurrentIndex(1)
        self.ui.comboBox.setEnabled(False)
        # Устанавливаем скидку
        self.ui.checkBox_2.setEnabled(False)
        self.ui.comboBox_2.setCurrentIndex(15)
        self.ui.comboBox_2.setEnabled(False)
        self.ui.checkBox_2.setChecked(True)
        system.sale_dict["detail"][4] = 100
        # Отключаем кнопку возврата
        self.ui.pushButton_6.setEnabled(False)

    def apply_half_many_children_discount(self) -> None:
        """
        Применение 50% скидки для многодетных.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции apply_half_many_children_discount")
        logger.info("Многодетным скидка 50%")
        system.count_number_of_visitors["many_child"] = 2
        # Устанавливаем скидку
        self.ui.checkBox_2.setChecked(True)
        self.ui.checkBox_2.setEnabled(False)
        self.ui.comboBox_2.setCurrentIndex(10)
        self.ui.comboBox_2.setEnabled(False)
        system.sale_dict["detail"][4] = 50
        self.ui.comboBox.setEnabled(True)

    def adult_exclusion(self, row: int) -> None:
        """
        Функция исключает взрослого из продажи.

        Параметры:
            row (int): Номер строки в таблице.

        Возвращаемое значение:
            None
        """
        logger.info("Запуск функции adult_exclusion")
        if self.ui.tableWidget_2.cellWidget(row, 8).findChild(QCheckBox).isChecked():
            # Исключаем взрослого из продажи номер строки не запоминали
            if system.sale_checkbox_row is None:
                logger.info("Исключаем взрослого из продажи")
                system.sale_dict["detail"][0] = 1
                system.sale_dict["detail"][4] = 100
                # Запоминаем номер строки с активным QCheckBox
                system.sale_checkbox_row = row
                # Изменяем флаг активности QCheckBox
                system.exclude_from_sale = 1
                # Ставим метку "не идет"
                self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem("н"))
            else:
                # Если взрослый исключен из продажи, корректируем цену билета и наличие скидки
                self.ui.tableWidget_2.setItem(
                    row, 3, QTableWidgetItem(f"{system.price['ticket_free']}")
                )
                system.sale_dict["detail"][0] = 1
                system.sale_dict["detail"][4] = 100
        else:
            if system.exclude_from_sale == 1:
                logger.info("Возвращаем взрослого в продажу")
                if (
                    not self.ui.tableWidget_2.cellWidget(system.sale_checkbox_row, 8)
                    .findChild(QCheckBox)
                    .isChecked()
                ):
                    self.ui.tableWidget_2.setItem(
                        system.sale_checkbox_row, 4, QTableWidgetItem("-")
                    )
                    system.sale_dict["detail"][0] = 0
                    system.sale_dict["detail"][1] = 0
                    system.sale_dict["detail"][4] = 0
                    system.sale_checkbox_row = None
                    system.exclude_from_sale = 0

    def generate_ticket_list(
        self,
        row: int,
        ticket_list: list[tuple[str, str, str, str, str, str, str, str, int, str]],
        date_time: str,
    ):
        """Генерация списка билетов.

        Параметры:
            row (int): Номер строки.
            ticket_list (list[tuple]): Список билетов для заполнения.
            date_time (str): Дата и время билета.

        Возвращаемое значение:
            None
        """
        ticket_list.append(
            (
                *map(lambda col: self.ui.tableWidget_2.item(row, col).text(), range(7)),
                system.sale_dict["detail"][6],
                system.count_number_of_visitors["talent"],
                date_time,
            )
        )

    def save_sale(self) -> None:
        """
        Функция сохраняет в БД информацию о продаже, а так же билеты посетителей.

        Параметры:
        self: object
            Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции save_sale")
        logger.debug(f"Статус сохраняемой продажи: {system.sale_status}")
        # Если продажа особенная - сохраним ее статус оплаченной
        if system.sale_special == 1:
            system.sale_status = 1
        if system.sale_dict["kol_adult"] >= 1:
            add_sale: Sale = Sale(
                price=system.sale_dict["detail"][7],
                id_user=system.user.id,
                id_client=system.sale_dict["detail"][5],
                status=system.sale_status,
                discount=system.sale_dict["detail"][4],
                pc_name=system.pc_name,
                datetime=dt.datetime.now(),
            )
            logger.debug(f"Получена продажа: {add_sale}")
            # Сохраняем продажу
            with Session(system.engine) as session:
                session.add(add_sale)
                session.commit()
                # Запоминаем номер сохраненной продажи
                system.sale_id = add_sale.id
            # Сохраняем билеты
            type_ticket: int | None = None
            for i in range(len(system.sale_tickets)):
                # Считаем количество начисленных талантов
                if system.sale_tickets[i][2] == "взрослый":
                    type_ticket = 0
                elif system.sale_tickets[i][2] == "детский":
                    type_ticket = 1
                elif system.sale_tickets[i][2] == "бесплатный":
                    type_ticket = 2
                add_ticket = Ticket(
                    id_client=system.sale_tickets[i][5],
                    id_sale=int(system.sale_id),
                    arrival_time=system.sale_tickets[i][7],
                    talent=system.sale_tickets[i][8],
                    price=system.sale_tickets[i][3],
                    description=system.sale_tickets[i][4],
                    ticket_type=type_ticket,
                    client_age=system.sale_tickets[i][6],
                )
                with Session(system.engine) as session:
                    session.add(add_ticket)
                    session.commit()
            self.close()
        else:
            windows.info_window(
                "Ошибка при сохранении продажи",
                "Необходимо добавить в нее взрослого",
                "",
            )

    @logger.catch()
    def sale_transaction(self, payment_type, print_check) -> None:
        """
        Выполняет транзакцию продажи с учетом типа оплаты и необходимости печати чека.

        Параметры:
           payment_type (int): Тип оплаты (например, 1 — карта, 3 — оффлайн).
           print_check (bool): Флаг, указывающий, нужно ли печатать чек.

        Возвращаемое значение:
           None: Эта функция не возвращает значения, но выполняет транзакцию и обновляет статус.
        """
        logger.info("Запуск функции sale_transaction")
        logger.debug(
            f"system.sale_status: {system.sale_status}, system.sale_id: {system.sale_id}"
        )
        self.progress_window = ProgressWindow()
        self.progress_window.show()

        # Создание воркера
        self.worker = TransactionWorker(
            payment_type,
            print_check,
            system,
            pq,
            Session,
            self  # передаем self, чтобы вызвать print_saved_tickets
        )

        # Подключение сигналов
        self.worker.progress_updated.connect(self.progress_window.update_status)
        self.worker.finished.connect(self.on_transaction_finished)
        self.worker.save_sale_signal.connect(self.save_sale)
        self.worker.error_signal.connect(self.handle_error)  # Обработка ошибок
        self.worker.info_signal.connect(self.handle_info)
        self.worker.print_ticket_signal.connect(self.print_saved_tickets)
        #self.worker.close_window_signal.connect(self.close)
        self.worker.close_window_signal.connect(self.progress_window.close)

        # Поток
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()


    def handle_error(self, title: str, text: str, details: str):
        """
        Обрабатывает ошибку, закрывая окно прогресса и отображая сообщение с ошибкой.

        Параметры:
            title (str): Заголовок окна с ошибкой.
            text (str): Основное сообщение об ошибке.
            details (str): Дополнительные подробности об ошибке (если имеются).

        Возвращаемое значение:
            None: Функция ничего не возвращает, но закрывает окно прогресса и отображает сообщение об ошибке.
        """
        # Закрытие окна прогресса перед отображением ошибки
        if hasattr(self, 'progress_window') and self.progress_window:
            self.progress_window.close()

        # Создание окна с ошибкой
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(text)
        if details:
            msg_box.setDetailedText(details)
        msg_box.exec()

    def handle_info(self, message: str):
        """
        Обрабатывает информационные сообщения, выводя их в окно прогресса.

        Параметры:
            message (str): Сообщение для вывода в окно прогресса.

        Возвращаемое значение:
            None: Функция ничего не возвращает, но добавляет сообщение в окно прогресса.
        """

        self.progress_window.ui.textEdit.append(message)
        # Закрытие окна прогресса только в конце
        # self.progress_window.close() можно оставить в конце, если завершение работы всех шагов произошло

    def on_transaction_finished(self):
        """
        Обрабатывает завершение транзакции, закрывая окно прогресса и логируя завершение.

        Возвращаемое значение:
            None: Эта функция ничего не возвращает, но закрывает окно прогресса и логирует завершение транзакции.
        """
        logger.info("Запуск функции on_transaction_finished")
        if hasattr(self, '_transaction_finished') and self._transaction_finished:
            return
        self._transaction_finished = True
        logger.info("Завершение транзакции")
        # Закрываем окно прогресса
        if hasattr(self, 'progress_window') and self.progress_window:
            self.progress_window.close()
            self.progress_window = None

        if self.main_window:
            self.main_window.main_button_all_sales()


    @logger.catch()
    def sale_return(self):
        """
        Функция осуществляет операцию возврата продажи.

        Параметры:
        self: object
            Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции sale_return")
        # Счетчик для отслеживания корректности проведения возврата за наличный способ расчета
        balance_error: int = 0
        partial_return: int = 0
        bank: int = 0
        new_tickets = {}
        state_check: int = 0
        tickets = self.generating_items_for_the_return_check()
        logger.info("Запрашиваем информацию о продаже в БД")
        with Session(system.engine) as session:
            query = select(Sale).filter(Sale.id == system.sale_id)
            sale = session.execute(query).scalars().one()
        logger.debug(f"Итоговая сумма: {sale.price}, тип оплаты: {sale.payment_type}")
        logger.debug(f"Сохраняем id продажи: {sale.id}")
        system.sale_id = sale.id
        price: int = sale.price
        if sale.status == 5:
            logger.debug("Требуется частичный возврат.")
            partial_return: int = int(sale.partial_return)
            new_tickets: dict | dict = generating_parts_for_partial_returns(tickets, partial_return)
            logger.debug(f"Список билетов: {new_tickets}")
        # 1 - карта, 2 - наличные
        if sale.payment_type == 1:
            payment_type: int = 101
        else:
            payment_type: int = 102
            system.amount_of_money_at_the_cash_desk = pq.balance_check()
            if sale.price > system.amount_of_money_at_the_cash_desk:
                balance_error: int = 1
                windows.info_window(
                    "Внимание",
                    "В кассе недостаточно наличных денег!\nОперация возврата будет прервана.\n"
                    "Необходимо выполнить операцию внесения денежных средств в кассу\n"
                    "и после этого повторить возврат снова.",
                    "",
                )
        # Продолжаем если возврат по банковской карте или если баланс наличных денег в кассе больше суммы возврата
        if sale.payment_type == 1 or balance_error == 0:
            # Если нужен обычный возврат или частичный возврат
            if sale.status in (1, 5):
                logger.debug("Продажа оплачена. Запускаем возврат")
                if payment_type == 102:
                    # TODO: убрать price
                    state_check = pq.check_open(
                        tickets, payment_type, system.user, 2, 1, price, None
                    )
                elif payment_type == 101:
                    logger.debug(
                        f"Проверяем был ли уже проведен возврат по банковскому терминалу. Sale.bank_return = {sale.bank_return}"
                    )
                    if sale.bank_return is None:
                        logger.debug("Запускаем возврат по банковскому терминалу")
                        # В зависимости от типа возврата отправляем на банковский терминал нужную сумму
                        if sale.status == 1:
                            bank, payment = pq.universal_terminal_operation(
                                payment_type=payment_type,
                                amount=price,
                                progress_signal=None,
                                operation_type=2,  # возврат
                                error_callback=lambda title, msg, code: windows.info_window(title, msg, str(code))
                            )
                        elif sale.status == 5:
                            bank, payment = pq.universal_terminal_operation(
                                payment_type=payment_type,
                                amount=partial_return,
                                progress_signal=None,
                                operation_type=2,  # возврат
                                error_callback=lambda title, msg, code: windows.info_window(title, msg, str(code))
                            )
                        if bank == 1:
                            check = pq.read_pinpad_file(remove_newline=False)
                            logger.debug(f"Чек возврата: {check}")
                            with Session(system.engine) as session:
                                session.execute(
                                    update(Sale)
                                    .where(Sale.id == system.sale_id)
                                    .values(
                                        bank_return=check,
                                    )
                                )
                                session.commit()
                            pq.print_pinpad_check()
                        else:
                            logger.warning(
                                "Возврат по банковскому терминалу прошел не успешно"
                            )
                            windows.info_window(
                                "Внимание",
                                "Возврат по банковскому терминалу прошел не успешно.\n"
                                "Закройте это окно, откройте продажу и проведите"
                                "операцию возврата еще раз.",
                                "",
                            )
                    else:
                        logger.debug(
                            "Возврат по банковскому терминалу был произведен ранее, но статус продажи не изменен"
                        )
                        bank = 1
                    if bank == 1:
                        # Если возврат по банковскому терминалу прошел успешно, то запускаем формирование кассового чека
                        if sale.status == 1:
                            # TODO: убрать price
                            state_check = pq.check_open(
                                tickets, payment_type, system.user, 2, 1, price, bank
                            )
                        elif sale.status == 5:
                            state_check = pq.check_open(
                                new_tickets,
                                payment_type,
                                system.user,
                                2,
                                1,
                                partial_return,
                                bank,
                            )
                # Если возврат прошел
                if state_check == 1:
                    # Для обычного возврата устанавливаем статус 2, для частичного возврата статус 6
                    if sale.status == 5:
                        status_info: int = 6
                    else:
                        status_info: int = 2
                    logger.info("Обновляем информацию о возврате в БД")
                    with Session(system.engine) as session:
                        session.execute(
                            update(Sale)
                            .where(Sale.id == system.sale_id)
                            .values(
                                status=status_info,
                                id_user=system.user.id,
                                user_return=system.user.id,
                                datetime_return=dt.datetime.now(),
                            )
                        )
                        session.commit()
                    self.close()
                else:
                    logger.warning("Операция возврата завершилась с ошибкой")
                    windows.info_window(
                        "Внимание",
                        "Закройте это окно, откройте продажу и проведите"
                        "операцию возврата еще раз.",
                        "",
                    )
            elif sale.status == 3:
                logger.debug("Требуется повторный возврат по банковскому терминалу")
                bank, payment = pq.universal_terminal_operation(
                    payment_type=payment_type,
                    amount=price,
                    progress_signal=None,
                    operation_type=2,  # возврат
                    error_callback=lambda title, msg, code: windows.info_window(title, msg, str(code))
                )

                if bank == 1:
                    logger.info("Операция повторного возврата прошла успешно")
                    check = pq.read_pinpad_file(remove_newline=False)
                    logger.debug(f"Чек возврата: {check}")
                    with Session(system.engine) as session:
                        session.execute(
                            update(Sale)
                            .where(Sale.id == system.sale_id)
                            .values(
                                bank_return=check,
                                status=4,
                                datetime_return=dt.datetime.now(),
                            )
                        )
                        session.commit()
                    pq.print_pinpad_check()
                    windows.info_window(
                        "Внимание", "Операция повторного возврата прошла успешно.", ""
                    )
                    self.close()
                else:
                    logger.warning("Возврат по банковскому терминалу прошел не успешно")
                    windows.info_window(
                        "Внимание",
                        "Возврат по банковскому терминалу прошел не успешно.\n"
                        "Закройте это окно, откройте продажу и проведите"
                        "операцию возврата еще раз.",
                        "",
                    )

    @logger.catch()
    def sale_canceling(self):
        """
        Функция осуществляет операцию отмены продажи.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции sale_canceling")
        # Счетчик для отслеживания корректности проведения возврата за наличный способ расчета
        tickets = self.generating_items_for_the_return_check()
        with Session(system.engine) as session:
            query = select(Sale).filter(Sale.id == system.sale_id)
            sale = session.execute(query).scalars().one()
        logger.debug(f"Итоговая сумма: {sale.price}, тип оплаты: {sale.payment_type}")
        system.sale_id = sale.id
        price: int = sale.price
        payment_type: int = 0
        state_check: int = 0
        # 1 - карта, 2 - наличные
        if sale.payment_type == 1:
            payment_type: int = 101
        # Продолжаем если возврат по банковской карте
        if sale.payment_type == 1:
            if sale.status == 1:
                logger.debug("Продажа оплачена. Запускаем отмену")
                if payment_type == 101:
                    logger.debug(
                        f"Проверяем был ли уже проведен возврат по банковскому терминалу. Sale.bank_return = {sale.bank_return}"
                    )
                    if sale.bank_return is None:
                        logger.debug("Запускаем отмену по банковскому терминалу")
                        bank, payment = pq.universal_terminal_operation(
                            payment_type=payment_type,
                            amount=price,
                            progress_signal=None,
                            operation_type=3,  # отмена
                            error_callback=lambda title, msg, code: windows.info_window(title, msg, str(code))
                        )
                        if bank == 1:
                            check = pq.read_pinpad_file(remove_newline=False)
                            logger.debug(f"Чек возврата: {check}")
                            with Session(system.engine) as session:
                                session.execute(
                                    update(Sale)
                                    .where(Sale.id == system.sale_id)
                                    .values(
                                        bank_return=check,
                                    )
                                )
                                session.commit()
                            pq.print_pinpad_check()
                        else:
                            logger.warning(
                                "Отмена по банковскому терминалу прошла не успешно"
                            )
                            windows.info_window(
                                "Внимание",
                                "Возврат по банковскому терминалу прошел не успешно.\n"
                                "Закройте это окно, откройте продажу и проведите"
                                "операцию возврата еще раз.",
                                "",
                            )
                    else:
                        logger.debug(
                            "Возврат по банковскому терминалу был произведен ранее, но статус продажи не изменен"
                        )
                        bank = 1
                    if bank == 1:
                        # Если отмена по банковскому терминалу прошла успешно, то запускаем формирование кассового чека
                        if sale.status == 1:
                            # TODO: убрать price
                            state_check = pq.check_open(
                                tickets, payment_type, system.user, 2, 1, price, bank
                            )
                # Если отмена прошла
                if state_check == 1:
                    # Изменяем статус для отмененного платежа
                    status_info: int = 8
                    logger.info("Обновляем информацию об отмене в БД")
                    with Session(system.engine) as session:
                        session.execute(
                            update(Sale)
                            .where(Sale.id == system.sale_id)
                            .values(
                                status=status_info,
                                id_user=system.user.id,
                                user_return=system.user.id,
                                datetime_return=dt.datetime.now(),
                            )
                        )
                        session.commit()
                    self.close()
                else:
                    logger.warning("Операция отмены завершилась с ошибкой")
                    windows.info_window(
                        "Внимание",
                        "Закройте это окно, откройте продажу и проведите"
                        "операцию отмены еще раз.",
                        "",
                    )

    @logger.catch()
    def generating_items_for_the_return_check(self):
        """
        Функция формирует список позиций для чека возврата прихода.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции generating_items_for_the_return_check")
        logger.debug(f"Билеты сохраненной продажи: {system.sale_tickets}")
        dct: dict = dict(list())
        adult = 0
        adult_promotion = 0
        child = 0
        child_promotion = 0
        # Определение типов билетов
        adult_ticket_types = {
            1: ("Билет взрослый 1 ч.", "Билет взрослый акция 1 ч.", "ticket_adult_1"),
            2: ("Билет взрослый 2 ч.", "Билет взрослый акция 2 ч.", "ticket_adult_2"),
            3: ("Билет взрослый 3 ч.", "Билет взрослый акция 3 ч.", "ticket_adult_3"),
        }
        child_ticket_types = {
            1: (
                "Билет детский 1 ч.",
                "Билет детский акция 1 ч.",
                ["ticket_child_1", "ticket_child_week_1"],
            ),
            2: (
                "Билет детский 2 ч.",
                "Билет детский акция 2 ч.",
                ["ticket_child_2", "ticket_child_week_2"],
            ),
            3: (
                "Билет детский 3 ч.",
                "Билет детский акция 3 ч.",
                ["ticket_child_3", "ticket_child_week_3"],
            ),
        }
        for ticket_in_sale in system.sale_tickets:
            ticket_price = ticket_in_sale[3]  # цена билета
            client_age = ticket_in_sale[6]  # возраст
            duration = ticket_in_sale[7]  # продолжительность
            if ticket_price == 0:
                continue  # Пропускаем нулевые билеты
            ticket_types = (
                adult_ticket_types
                if client_age >= system.age["max"]
                else child_ticket_types
            )
            if duration not in ticket_types:
                logger.error(f"Неизвестная продолжительность билета: {duration}")
                continue  # Пропускаем некорректные данные
            type_ticket, promo_ticket, price_keys = ticket_types[duration]
            if isinstance(price_keys, list):  # Для детских билетов
                if ticket_price in (system.price[key] for key in price_keys):
                    ticket_category = "child"
                    type_ticket = type_ticket
                else:
                    ticket_category = "child_promotion"
                    type_ticket = promo_ticket
            else:  # Для взрослых билетов
                if ticket_price == system.price[price_keys]:
                    ticket_category = "adult"
                    type_ticket = type_ticket
                else:
                    ticket_category = "adult_promotion"
                    type_ticket = promo_ticket
            # Увеличение счетчика соответствующего типа билетов
            if ticket_category == "adult":
                adult += 1
                ticket = [ticket_price, adult]
            elif ticket_category == "adult_promotion":
                adult_promotion += 1
                ticket = [ticket_price, adult_promotion]
            elif ticket_category == "child":
                child += 1
                ticket = [ticket_price, child]
            else:  # "child_promotion"
                child_promotion += 1
                ticket = [ticket_price, child_promotion]
            dct[type_ticket] = ticket
        return dct

    @logger.catch()
    def sale_generate_saved_tickets(self):
        """
        Функция генерирует список с ранее сохраненными билетами.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции sale_generate_saved_tickets")
        logger.info(f"Список билетов: {system.sale_tickets}")
        client_in_sale: tuple = system.sale_tickets
        try:
            # Удаляем существующий файл с билетами
            if os.path.exists("./ticket.pdf"):
                os.remove("./ticket.pdf")
        except Exception as e:
            logger.error(f"Произошла ошибка при удалении файла с билетами: {e}")
        # Формируем новый файл с билетами
        otchet.generate_saved_tickets(client_in_sale)

    def is_printing_enabled(self) -> bool:
        """Функция проверяет, разрешена ли печать билетов.

        Возвращает:
            bool: True только если:
                  - параметр 'ticket' существует
                  - и равен 'on' (регистронезависимо)
                  Во всех остальных случаях возвращает False.
        """
        # Проверяем наличие атрибута и что он не None
        if not hasattr(system, 'ticket_print') or system.ticket_print is None:
            return False

        # Приводим к строке и сравниваем с 'on'
        return str(system.ticket_print).strip().lower() == "on"

    def print_saved_tickets(self):
        """
        Функция для печати сохраненных билетов.
        Печатает только если в конфигурации [PRINT] ticket = on.
        """
        logger.info("Запуск функции print_saved_tickets")
        if not self.is_printing_enabled():
            logger.info("Печать билетов отключена (параметр 'ticket' не равен 'on' или отсутствует)")
            return
        try:
            self.sale_generate_saved_tickets()
            logger.info("Завершение процесса SumatraPDF, если он открыт.")
            os.system("TASKKILL /F /IM SumatraPDF.exe")
            print_cmd_path = Path(__file__).parent / "scripts" / "print.cmd"
            subprocess.Popen([str(print_cmd_path)])
        except FileNotFoundError:
            logger.error("Файл print.cmd не найден.")
        except Exception as e:
            logger.error(f"Произошла ошибка при запуске файла print.cmd: {e}")

    def open_saved_tickets(self):
        """
        Функция для открытия созданного PDF файла с билетами.
        """
        logger.info("Запуск функции open_saved_tickets")
        # Исправленный вызов метода
        self.sale_generate_saved_tickets()
        try:
            os.system("TASKKILL /F /IM SumatraPDF.exe")
            open_cmd_path = Path(__file__).parent / "scripts" / "open.cmd"
            subprocess.Popen([str(open_cmd_path)])
        except FileNotFoundError:
            logger.error("Файл open.cmd не найден.")
        except Exception as e:
            logger.error(f"Произошла ошибка при запуске файла open.cmd: {e}")

    def open_pay_form(self, txt):
        """
        Функция открывает форму оплаты.

        Параметры:
            txt (str): Текст, который передается в форму оплаты.

        Возвращаемое значение:
            None
        """
        logger.info("Запуск функции open_pay_form")
        pay: PayForm = PayForm()
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

        # Получаем флаг отладки из MainWindow
        dev_mode = self.main_window.dev_mode if self.main_window else False

        if res == Payment.Card:
            if dev_mode:
                logger.info("РЕЖИМ ОТЛАДКИ: Имитация оплаты картой")
                # Создаем тестовый слип-чек
                slip = "DEBUG_SLIP\nДата: {}\nСумма: {}\nОдобрено".format(
                    dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                    txt
                )
                # Сохраняем тестовые данные
                self.save_debug_payment(Payment.Card, slip)
                self.accept()
                return

            # Оплата банковской картой
            logger.info("Оплата банковской картой")
            payment_type: int = Payment.Card
            # запускаем оплату по терминалу
            self.sale_transaction(payment_type, system.print_check)
        elif res == Payment.Cash:
            logger.info("Оплата наличными")
            payment_type: int = Payment.Cash
            self.sale_transaction(payment_type, system.print_check)
        elif res == Payment.Offline:
            if dev_mode:
                logger.info("РЕЖИМ ОТЛАДКИ: Имитация offline оплаты")
                slip = "DEBUG_SLIP_OFFLINE\nДата: {}\nСумма: {}\nОффлайн".format(
                    dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                    txt
                )
                self.save_debug_payment(Payment.Offline, slip)
                self.accept()
                return

            user_choice = windows.info_dialog_window(
                "Внимание",
                f"Вы точно хотите провести оплату методом offline?\n\n"
                f"Это надо делать ТОЛЬКО после успешной проверки проведения операции по банковскому терминалу!\n"
                f"Для этого выполните команду: Касса -> Операции с банковским терминалом -> Печать ранее подготовленного документа.\n\n"
                f"Операция считается успешной, если в распечатанном банковском слип-чеке:\n"
                f" - сумма, дата и время проведения операции операции совпадают с данными из заказа;\n"
                f" - указано слово 'ОДОБРЕНО'.",
            )
            if user_choice == 1:
                logger.info("Оплата банковской картой offline")
                payment_type: int = Payment.Offline
                self.sale_transaction(payment_type, system.print_check)
        # Закрываем окно продажи и возвращаем QDialog.Accepted
        self.accept()

    @staticmethod
    def save_debug_payment(payment_type, slip_text):
        """Сохранение тестового платежа в режиме отладки"""
        try:
            logger.debug(f"Сохранение тестового платежа: payment_type = {payment_type}, slip = {slip_text}")
            # ... код для сохранения в БД ...
        except Exception as e:
            logger.error(f"Ошибка сохранения тестового платежа: {str(e)}")


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
            txt (str):
                Текстовое значение, которое будет установлено в метку.

        Возвращаемое значение:
            None:
                Функция не возвращает значений.
        """
        logger.info("Запуск функции setText")
        self.ui.label_2.setText(txt)
        # По умолчанию печатаем чек
        system.print_check = 1

    def check_print(self) -> None:
        """
        Функция печатает кассовый чек, если checkBox на форме оплаты был активен.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции check_print")
        if self.ui.checkBox.isChecked():
            system.print_check = 1
        else:
            system.print_check = 0


class SlipForm(QDialog):
    """Форма просмотра банковского слип-чека"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_Slip()
        self.ui.setupUi(self)

    def get_slip(self) -> None:
        """
        Функция запрашивает банковский слип-чек в БД и отображает его во всплывающем окне.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, отображает данные слип-чека в форме.
        """
        logger.info("Запуск функции get_slip")
        card_tail, merchant_id, rrn_value, load_slip = system.get_slip_data(system.sale_id)

        slip: SlipForm = SlipForm()
        slip.ui.label_5.setText(card_tail)
        slip.ui.label_6.setText(merchant_id)
        slip.ui.lineEdit.setText(rrn_value)
        slip.ui.textEdit.setText(load_slip)
        slip.show()
        slip.exec_()


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
        self.ui.pushButton_8.clicked.connect(pq.get_info)
        self.ui.pushButton_11.clicked.connect(pq.last_document)
        self.ui.pushButton_9.clicked.connect(pq.get_time)
        self.ui.pushButton_5.clicked.connect(pq.report_x)
        self.ui.pushButton_6.clicked.connect(lambda: pq.smena_close(system.user))
        self.ui.pushButton_7.clicked.connect(pq.get_status_obmena)
        self.ui.pushButton_15.clicked.connect(pq.continue_print)
        self.ui.pushButton_10.clicked.connect(pq.smena_info)
        self.ui.pushButton_16.clicked.connect(pq.terminal_check_itog)
        self.ui.pushButton_21.clicked.connect(pq.terminal_svod_check)
        self.ui.pushButton_22.clicked.connect(pq.terminal_control_lenta)
        self.ui.pushButton_12.clicked.connect(pq.terminal_copy_last_check)
        self.ui.pushButton_23.clicked.connect(self.main_open_sale)
        self.ui.pushButton_13.clicked.connect(self.main_button_all_sales)
        self.ui.pushButton_18.clicked.connect(self.main_otchet_kassira)
        self.ui.pushButton_19.clicked.connect(self.main_otchet_administratora)
        self.ui.tableWidget_2.doubleClicked.connect(self.main_search_selected_sale)
        self.ui.pushButton_17.clicked.connect(self.main_get_statistic)
        self.ui.pushButton_24.clicked.connect(
            lambda: pq.deposit_of_money(system.amount_to_pay_or_deposit)
        )
        self.ui.pushButton_25.clicked.connect(
            lambda: pq.payment(system.amount_to_pay_or_deposit)
        )
        self.ui.pushButton_26.clicked.connect(pq.balance_check)
        self.ui.pushButton_27.clicked.connect(pq.terminal_menu)
        self.ui.pushButton_28.clicked.connect(pq.terminal_print_file)
        # self.ui.pushButton_29.clicked.connect(pq.terminal_file_in_window)
        self.ui.dateEdit.setDate(date.today())
        self.ui.dateEdit_2.setDate(date.today())
        self.ui.dateEdit_3.setDate(date.today())
        self.ui.lineEdit_2.returnPressed.connect(self.main_search_clients)
        self.ui.comboBox_3.currentTextChanged.connect(self.main_filter_clear)
        # при вводе в поле lineEdit сохраняем значение в system.amount_to_pay_or_deposit
        self.ui.lineEdit.textEdited.connect(
            self.main_transfer_of_deposit_or_payment_amount
        )
        # изменяем ширину столбца
        self.ui.tableWidget_2.setColumnWidth(3, 250)
        # Флаг режима отладки
        self.dev_mode = False

    def main_transfer_of_deposit_or_payment_amount(self) -> None:
        """
        Функция сохраняет значение строки lineEdit для передачи в функции внесения/выплаты денег.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции main_transfer_of_deposit_or_payment_amount")
        system.amount_to_pay_or_deposit = int(self.ui.lineEdit.text())

    def filling_client_table_widget_main_form(
        self,
        last_name: str,
        first_name: str,
        middle_name: str,
        birth_date: date,
        gender: str,
        phone: str,
        email: str,
        privilege: str,
        id: int,
    ) -> None:
        """
        Функция заполняет полученными данными tableWidget (список посетителей).

        Параметры:
            last_name (str): Фамилия клиента.
            first_name (str): Имя клиента.
            middle_name (str): Отчество клиента.
            birth_date (date): Дата рождения.
            gender (str): Пол.
            phone (str): Номер телефона.
            email (str): Адрес электронной почты.
            privilege (str): Привилегия клиента.
            id (int): Идентификатор клиента.

        Возвращаемое значение:
            None
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
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции main_search_clients")
        user_filter: str = "%" + self.ui.lineEdit_2.text() + "%"
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
            with Session(system.engine) as session:
                search: list[Type[Client]] = (
                    session.query(Client).filter(Client.phone.ilike(user_filter)).all()
                )
            for client in search:
                self.filling_client_table_widget_main_form(
                    client.last_name,
                    client.first_name,
                    client.middle_name,
                    str(client.birth_date),
                    client.gender,
                    client.phone,
                    client.email,
                    client.privilege,
                    str(client.id),
                )
        elif index == 1:
            # Поиск по фамилии
            self.ui.tableWidget.setRowCount(0)
            with Session(system.engine) as session:
                search: list[Type[Client]] = (
                    session.query(Client)
                    .filter(Client.last_name.ilike(user_filter))
                    .all()
                )
            for client in search:
                self.filling_client_table_widget_main_form(
                    client.last_name,
                    client.first_name,
                    client.middle_name,
                    str(client.birth_date),
                    client.gender,
                    client.phone,
                    client.email,
                    client.privilege,
                    str(client.id),
                )
        elif index == 0:
            # Поиск по фамилии и имени
            self.ui.tableWidget.setRowCount(0)
            user_filter: str = self.ui.lineEdit_2.text().title()
            # Разбиваем поисковую фразу на две
            lst: Any = user_filter.split()
            # Инициализация переменной search пустым списком, чтобы избежать ошибки
            search: list[Type[Client]] = []
            if len(lst) == 2:
                with Session(system.engine) as session:
                    search: list[Type[Client]] = (
                        session.query(Client)
                        .filter(
                            and_(
                                Client.first_name.ilike(lst[1] + "%"),
                                Client.last_name.ilike(lst[0] + "%"),
                            )
                        )
                        .all()
                    )
            else:
                windows.info_window(
                    "Неправильно задано условие для поиска",
                    "Введите начальные буквы фамилии" "и имени через пробел",
                    "",
                )
            for client in search:
                self.filling_client_table_widget_main_form(
                    client.last_name,
                    client.first_name,
                    client.middle_name,
                    str(client.birth_date),
                    client.gender,
                    client.phone,
                    client.email,
                    client.privilege,
                    str(client.id),
                )
        elif index == 3:
            # Поиск инвалидов
            self.ui.tableWidget.setRowCount(0)
            with Session(system.engine) as session:
                search: list[Type[Client]] = (
                    session.query(Client)
                    .filter(Client.privilege.ilike("%" + "и"))
                    .all()
                )
            for client in search:
                self.filling_client_table_widget_main_form(
                    client.last_name,
                    client.first_name,
                    client.middle_name,
                    str(client.birth_date),
                    client.gender,
                    client.phone,
                    client.email,
                    client.privilege,
                    str(client.id),
                )
        elif index == 4:
            # Поиск многодетных
            self.ui.tableWidget.setRowCount(0)
            with Session(system.engine) as session:
                search: list[Type[Client]] = (
                    session.query(Client)
                    .filter(Client.privilege.ilike("%" + "м"))
                    .all()
                )
            for client in search:
                self.filling_client_table_widget_main_form(
                    client.last_name,
                    client.first_name,
                    client.middle_name,
                    str(client.birth_date),
                    client.gender,
                    client.phone,
                    client.email,
                    client.privilege,
                    str(client.id),
                )

    def main_edit_client(self) -> None:
        """
        Функция ищет выделенную строку в таблице клиентов и открывает форму для редактирования данных.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции main_edit_client")
        # Ищем индекс и значение ячейки
        row_number: int = self.ui.tableWidget.currentRow()
        # Проверяем, что строка выбрана
        if row_number == -1:
            logger.error("Строка не выбрана в таблице.")
            return
        # Получаем содержимое ячейки
        client_id: str = self.ui.tableWidget.item(row_number, 8).text()
        if client_id is None:
            logger.error("Ячейка пуста или не существует.")
            return
        with Session(system.engine) as session:
            search_client: Type[Client] = (
                session.query(Client).filter_by(id=client_id).first()
            )
            if search_client is None:
                logger.error(f"Клиент с ID {client_id} не найден.")
        # Сохраняем id клиента
        system.client_id = search_client.id
        # Передаем в форму данные клиента
        client = ClientForm()
        client.ui.lineEdit.setText(search_client.last_name)
        client.ui.lineEdit_2.setText(search_client.first_name)
        client.ui.lineEdit_3.setText(search_client.middle_name)
        client.ui.dateEdit.setDate(search_client.birth_date)
        # Поиск значения для установки в ComboBox gender
        index_gender: int = client.ui.comboBox.findText(
            search_client.gender, Qt.MatchFixedString
        )
        if index_gender >= 0:
            client.ui.comboBox.setCurrentIndex(index_gender)
        client.ui.lineEdit_4.setText(search_client.phone)
        client.ui.lineEdit_5.setText(search_client.email)
        # Ищем значение для установки в ComboBox privilege
        index_privilege: int | None = client.ui.comboBox.findText(
            search_client.privilege, Qt.MatchFixedString
        )
        if index_privilege >= 0:
            client.ui.comboBox_2.setCurrentIndex(index_privilege)
        client.show()
        # Сохраняем параметры данных об уже существующем клиенте
        system.client_update = 1
        logger.info(f"Обновляем информацию о клиенте")
        client.exec_()

    def main_filter_clear(self) -> None:
        """
        Функция очищает строку поиска (lineEdit).

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции main_filter_clear")
        self.ui.lineEdit_2.clear()

    def main_search_selected_sale(self) -> None:
        """
        Поиск выделенной строки в таблице продаж и открытие формы с полученными данными.

        Параметры:
        self: object
            Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
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
            with Session(system.engine) as session:
                query = (
                    select(
                        Client.last_name,
                        Client.first_name,
                        Ticket.ticket_type,
                        Ticket.price,
                        Ticket.description,
                        Client.id,
                        Ticket.client_age,
                        Ticket.arrival_time,
                        Ticket.talent,
                        Ticket.datetime,
                    )
                    .join(Ticket)
                    .where(
                        and_(
                            Client.id == Ticket.id_client, Ticket.id_sale == sale_number
                        )
                    )
                )
                client_in_sale = session.execute(query).all()
                # Запрашиваем статус продажи
                sale_status: Any = (
                    (
                        session.query(Sale.status)
                        .where(Sale.id == sale_number)
                        .one_or_none()
                    )
                    ._asdict()
                    .get("status")
                )
            logger.info(f"client_in_sale: {client_in_sale}, sale_status: {sale_status}")
            # Передаем в форму данные клиента
            sale: SaleForm = SaleForm()
            sale.ui.tableWidget_2.setRowCount(0)
            sale.ui.dateEdit.setDate(client_in_sale[0][9])
            sale.ui.comboBox.setCurrentText(str(client_in_sale[0][7]))
            # Если продажа оплачена
            if sale_status == 1:
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
                # sale.ui.tableWidget_2.setEnabled(False)
                # Поле скидка
                sale.ui.checkBox_2.setEnabled(False)
                # Кнопки просмотра слип-чека и отмены платежа по банковской карте
                if self.ui.tableWidget_2.item(row_number, 7).text() != "карта":
                    sale.ui.pushButton_13.setEnabled(False)
                    # sale.ui.pushButton_14.setEnabled(False)
            # Если продажа не оплачена
            elif sale_status == 0:
                # обновляем данные о продаже
                system.sale_tickets = None
                system.sale_dict = {}  # Инициализация перед использованием
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
            # Если продажа возвращена
            elif sale_status == 2:
                # Кнопка сохранить
                sale.ui.pushButton_3.setEnabled(False)
                # Кнопка оплатить
                sale.ui.pushButton_5.setEnabled(False)
                # Кнопка обновить
                sale.ui.pushButton_10.setEnabled(False)
                # Кнопка возврат
                sale.ui.pushButton_6.setEnabled(False)
                # Кнопка отмены платежа по банковской карте
                sale.ui.pushButton_14.setEnabled(False)
                sale.ui.pushButton_7.setEnabled(False)
                sale.ui.pushButton_8.setEnabled(False)
            # Если продажа требует повторный возврат по банковскому терминалу
            elif sale_status == 3:
                # Кнопка сохранить
                sale.ui.pushButton_3.setEnabled(False)
                # Кнопка оплатить
                sale.ui.pushButton_5.setEnabled(False)
                # Кнопка обновить
                sale.ui.pushButton_10.setEnabled(False)
                # Кнопка возврат
                sale.ui.pushButton_6.setEnabled(True)
                # Кнопка отмены платежа по банковской карте
                sale.ui.pushButton_14.setEnabled(False)
                sale.ui.pushButton_7.setEnabled(False)
                sale.ui.pushButton_8.setEnabled(False)
            # Если продажа требует частичный возврат
            elif sale_status == 5:
                # Кнопка сохранить
                sale.ui.pushButton_3.setEnabled(False)
                # Кнопка оплатить
                sale.ui.pushButton_5.setEnabled(False)
                # Кнопка обновить
                sale.ui.pushButton_10.setEnabled(False)
                # Кнопка возврат
                sale.ui.pushButton_6.setEnabled(True)
                # Кнопка отмены платежа по банковской карте
                sale.ui.pushButton_14.setEnabled(False)
                sale.ui.pushButton_7.setEnabled(False)
                sale.ui.pushButton_8.setEnabled(False)
            # Если продажа требует частичный возврат
            elif sale_status == 7:
                # Кнопка сохранить
                sale.ui.pushButton_3.setEnabled(False)
                # Кнопка оплатить
                sale.ui.pushButton_5.setEnabled(False)
                # Кнопка обновить
                sale.ui.pushButton_10.setEnabled(False)
                # Кнопка возврат
                sale.ui.pushButton_6.setEnabled(False)
                # Кнопка отмены платежа по банковской карте
                sale.ui.pushButton_14.setEnabled(False)
                sale.ui.pushButton_7.setEnabled(False)
                sale.ui.pushButton_8.setEnabled(False)
            elif sale_status == 8:
                # Кнопка сохранить
                sale.ui.pushButton_3.setEnabled(False)
                # Кнопка оплатить
                sale.ui.pushButton_5.setEnabled(False)
                # Кнопка обновить
                sale.ui.pushButton_10.setEnabled(False)
                # Кнопка возврат
                sale.ui.pushButton_6.setEnabled(False)
                # Кнопка отмены платежа по банковской карте
                sale.ui.pushButton_14.setEnabled(False)
                sale.ui.pushButton_7.setEnabled(False)
                sale.ui.pushButton_8.setEnabled(False)
            else:
                # Кнопка сохранить
                sale.ui.pushButton_3.setEnabled(False)
                # Кнопка оплатить
                sale.ui.pushButton_5.setEnabled(False)
                # Кнопка обновить
                sale.ui.pushButton_10.setEnabled(False)
                # Кнопка возврат
                sale.ui.pushButton_6.setEnabled(False)
                # Кнопка отмены платежа по банковской карте
                sale.ui.pushButton_14.setEnabled(False)
            for search_client in client_in_sale:
                if search_client[6] >= system.age["max"]:
                    type_ticket = "взрослый"
                    kol_adult += 1
                else:
                    type_ticket = "детский"
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
                sale.ui.tableWidget_2.setItem(
                    row, 0, QTableWidgetItem(f"{search_client[1]}")
                )
                # Фамилия
                sale.ui.tableWidget_2.setItem(
                    row, 1, QTableWidgetItem(f"{search_client[0]}")
                )
                # Тип билета
                sale.ui.tableWidget_2.setItem(row, 2, QTableWidgetItem(type_ticket))
                # Цена
                sale.ui.tableWidget_2.setItem(
                    row, 3, QTableWidgetItem(f"{search_client[3]}")
                )
                # Примечание
                sale.ui.tableWidget_2.setItem(
                    row, 4, QTableWidgetItem(f"{search_client[4]}")
                )
                # id клиента
                sale.ui.tableWidget_2.setItem(
                    row, 5, QTableWidgetItem(f"{search_client[5]}")
                )
                sale.ui.tableWidget_2.setColumnHidden(5, True)
                # Возраст
                sale.ui.tableWidget_2.setItem(
                    row, 6, QTableWidgetItem(f"{search_client[6]}")
                )
                summ += int(search_client[3])
            sale.ui.label_5.setText(str(kol_adult))
            sale.ui.label_7.setText(str(kol_child))
            sale.ui.label_8.setText(str(summ))
            sale.show()
            windows.info_window(
                "Внимание", "Перед проведением оплаты нажмите на кнопку обновить", ""
            )
            # Передаем сведения о сохраненной продаже
            system.sale_status = sale_status
            system.sale_id = int(sale_number)
            system.sale_tickets = client_in_sale
            logger.debug(f"Билеты сохраненной продажи: {system.sale_tickets}")
            sale.exec_()

    @logger_wraps(entry=True, exit=True, level="DEBUG")
    def main_button_all_sales(self) -> None:
        """
        Функция выводит на форму продаж в соответствии с выбранным пользователем фильтром (за 1, 3 и 7 дней).

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции main_button_all_sales")
        # Устанавливаем временной период
        start_time = " 00:00:00"
        end_time = " 23:59:59"
        self.ui.tableWidget_2.setRowCount(0)
        # Инициализация переменных по умолчанию
        filter_start = None
        filter_end = None
        # Определяем диапазон дат в зависимости от выбора
        if self.ui.radioButton_7.isChecked():
            filter_start = self.ui.dateEdit_3.date().toString("yyyy-MM-dd") + start_time
            filter_end = self.ui.dateEdit_3.date().toString("yyyy-MM-dd") + end_time
        else:
            # Определение периода для 1, 3 и 7 дней без учета времени
            if self.ui.radioButton.isChecked():
                filter_start = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
                filter_end = dt.datetime.today().replace(hour=23, minute=59, second=59, microsecond=999999)
            elif self.ui.radioButton_2.isChecked():
                filter_start = (dt.datetime.today() - timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
                filter_end = dt.datetime.today().replace(hour=23, minute=59, second=59, microsecond=999999)
            elif self.ui.radioButton_3.isChecked():
                filter_start = (dt.datetime.today() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
                filter_end = dt.datetime.today().replace(hour=23, minute=59, second=59, microsecond=999999)
        # Определяем, какие статусы фильтровать
        sale_status_filter = [2, 3, 4, 5, 6, 8] if self.ui.checkBox.isChecked() else []

        # Генерация запроса
        with Session(system.engine) as session:
            query = session.query(
                Sale.id,
                Sale.id_client,
                Sale.price,
                Sale.datetime,
                Sale.status,
                Sale.discount,
                Sale.pc_name,
                Sale.payment_type,
                Client.last_name,
            ).filter(Sale.id_client == Client.id)
            # Фильтруем по диапазону дат, игнорируя время
            if filter_end:
                query = query.filter(Sale.datetime.between(filter_start, filter_end))
            else:  # Фильтруем по дням (например, последние 1, 3 или 7 дней)
                query = query.filter(Sale.datetime >= filter_start)

            if sale_status_filter:  # Если есть фильтрация по статусу
                query = query.filter(Sale.status.in_(sale_status_filter))

            query = query.order_by(desc(Sale.id))
            sales = query.all()

        # Заполнение таблицы
        if sales:
            for sale in sales:
                row = self.ui.tableWidget_2.rowCount()
                self.ui.tableWidget_2.insertRow(row)
                self.ui.tableWidget_2.setItem(row, 0, QTableWidgetItem(str(sale[0])))

                # Устанавливаем данные для колонок
                self.ui.tableWidget_2.setColumnWidth(1, 150)
                self.ui.tableWidget_2.setItem(row, 1, QTableWidgetItem(str(sale[8])))
                self.ui.tableWidget_2.setItem(row, 2, QTableWidgetItem(str(sale[2])))
                self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(str(sale[3])))

                # Обрабатываем статус
                status_dict = {
                    0: "создана",
                    1: "оплачена",
                    2: "возврат",
                    3: "требуется повторный возврат по банковскому терминалу",
                    4: "повторный возврат по банковскому терминалу",
                    5: "требуется частичный возврат",
                    6: "частичный возврат",
                    7: "возврат по банковским реквизитам",
                    8: "отмена",
                }
                status_type = status_dict.get(sale[4], "неизвестно")
                self.ui.tableWidget_2.setColumnWidth(4, 350)
                self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(status_type))
                self.ui.tableWidget_2.setItem(row, 5, QTableWidgetItem(str(sale[5])))
                self.ui.tableWidget_2.setItem(row, 6, QTableWidgetItem(str(sale[6])))

                # Обрабатываем тип оплаты
                payment_dict = {1: "карта", 2: "наличные", 3: "карта offline"}
                if sale[7] is not None and isinstance(sale[7], int):
                    payment_type = payment_dict.get(sale[7], "-")
                else:
                    payment_type = "-"  # Если sale[7] равно None, сразу устанавливаем дефолтное значение
                self.ui.tableWidget_2.setItem(row, 7, QTableWidgetItem(payment_type))

    def main_open_client(self) -> None:
        """
        Функция открывает форму с данными клиента.

        Параметры:
        self: object
            Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции main_open_client")
        client: ClientForm = ClientForm()
        client.show()
        client.exec()

    def main_open_sale(self) -> None:
        """
        Функция открывает форму продажи.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции main_open_sale")
        sale: SaleForm = SaleForm(main_window=self)
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
        system.sale_discount = 0
        # сбрасываем номер строки QCheckBox для исключения из продажи
        system.sale_checkbox_row = None
        # флаг состояния QCheckBox для исключения из продажи 0 - не активен
        system.exclude_from_sale = 0
        # флаг состояния особенной (бесплатной) продажи
        system.sale_special = None
        # Обновляем system.sale_dict
        # Обнуляем system.sale_dict
        sale_initial_values = {
            "kol_adult": 0,
            "price_adult": 0,
            "kol_child": 0,
            "price_child": 0,
            "detail": [0, 0, 0, 0, 0, 0, 0, 0],
        }
        system.sale_dict.update(sale_initial_values)
        # сбрасываем id и статус продажи
        system.sale_id = None
        system.sale_status = None
        sale.exec_()

    def main_get_statistic(self) -> None:
        """
        Основная функция для получения статистики продаж, возвратов и билетов за заданный период.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI и взаимодействия с базой данных.

        Возвращаемое значение:
            None: Функция не возвращает значений, но обновляет таблицы с данными о продажах и билетах.
        """
        logger.info("Запуск функции main_get_statistic")
        # Получение дат
        dt1, dt2 = self.get_date_range_from_ui()
        # Получение данных из БД
        sales, sales_return, tickets = self.fetch_stat_data(dt1, dt2)
        # Преобразовываем Row к обычному tuple
        sales = [tuple(row) for row in sales]
        sales_return = [tuple(row) for row in sales_return]
        sales_data = otchet.process_sales_and_returns(sales, sales_return)
        # Обработка и отображение продаж и возвратов
        self.fill_sales_table(sales_data)
        # Обработка и отображение билетов
        tickets = [tuple(row) for row in tickets]
        tickets_data = otchet.process_ticket_stats(tickets)
        self.fill_ticket_table(tickets_data)
        logger.info(f"Обработано {len(sales)} продаж и {len(sales_return)} возвратов")

    def get_date_range_from_ui(self) -> tuple[str, str]:
        """
        Получение диапазона дат из пользовательского интерфейса.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            tuple[str, str]: Кортеж, содержащий начальную и конечную дату в формате "yyyy-MM-dd HH:mm:ss".

        Исключения:
            ValueError: Выбрасывается, если начальная дата больше конечной.
        """
        logger.info("Запуск функции get_date_range_from_ui")
        start_time = " 00:00:00"
        end_time = " 23:59:59"
        dt1 = self.ui.dateEdit_2.date().toString("yyyy-MM-dd") + start_time
        dt2 = self.ui.dateEdit.date().toString("yyyy-MM-dd") + end_time
        if dt1 > dt2:
            raise ValueError("Начальная дата не может быть больше конечной")
        return dt1, dt2

    def fetch_stat_data(self, dt1: str, dt2: str):
        """
        Получение статистических данных о продажах и билетах из базы данных.

        Параметры:
            dt1 (str): Начальная дата в формате "yyyy-MM-dd HH:mm:ss", которая используется для фильтрации данных.
            dt2 (str): Конечная дата в формате "yyyy-MM-dd HH:mm:ss", которая используется для фильтрации данных.

        Возвращаемое значение:
            tuple: Кортеж, содержащий три элемента:
                - Список продаж (sales): Каждое из которых включает имя ПК, тип оплаты, цену и статус.
                - Список возвратов (sales_return): Каждое из которых включает имя ПК, тип оплаты, цену и статус возврата.
                - Список билетов (tickets): Каждое из которых включает тип билета, время прибытия, описание, статус и цену.

        Описание:
            Функция выполняет запросы к базе данных с использованием SQLAlchemy для получения данных о продажах, возвратах и билетах за указанный диапазон дат.
        """
        logger.info("Запуск функции fetch_stat_data")
        with Session(system.engine) as session:
            sales = session.execute(
                select(Sale.pc_name, Sale.payment_type, Sale.price, Sale.status)
                .where(and_(Sale.status == "1", Sale.datetime.between(dt1, dt2)))
            ).all()
            sales_return = session.execute(
                select(Sale.pc_name, Sale.payment_type, Sale.price, Sale.status)
                .where(and_(
                    Sale.datetime_return.between(dt1, dt2),
                    Sale.status.in_([2, 3, 4, 5, 6])
                ))
            ).all()
            tickets = session.execute(
                select(
                    Ticket.ticket_type, Ticket.arrival_time, Ticket.description, Sale.status, Sale.id, Ticket.price
                ).where(
                    and_(
                        Sale.id == Ticket.id_sale,
                        Sale.status == "1",
                        Ticket.datetime.between(dt1, dt2),
                        )
                )
            ).all()
        return sales, sales_return, tickets


    def fill_sales_table(self, data):
        """
        Заполнение таблицы продаж данными.

        Параметры:
            data (list): Список данных для отображения в таблице, где каждая строка представляется как список значений.

        Возвращаемое значение:
            None: Функция не возвращает значений, а только заполняет таблицу в интерфейсе.

        Описание:
            Функция принимает данные и заполняет таблицу `tableWidget_4` в пользовательском интерфейсе. Каждая строка данных добавляется в таблицу, при этом все значения конвертируются в строки, если это необходимо. Пустые значения пропускаются.
        """
        logger.info("Запуск функции fill_sales_table")
        self.ui.tableWidget_4.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                if value is not None:
                    self.ui.tableWidget_4.setItem(row, col, QTableWidgetItem(str(value)))



    def fill_ticket_table(self, data):
        """
        Заполнение таблицы билетов данными.

        Параметры:
            data (list): Список данных для отображения в таблице, где каждая строка состоит из метки и словаря значений.
                Пример структуры данных: [("взрослый", {"sum": 10, "t_1": 5, "t_2": 3, "t_3": 2}), ...]

        Возвращаемое значение:
            None: Функция не возвращает значений, а только заполняет таблицу в интерфейсе.

        Описание:
            Функция принимает данные о билетах и заполняет таблицу `tableWidget_3` в пользовательском интерфейсе.
            Для каждого элемента в данных создается строка таблицы, где:
            - Первая колонка отображает метку (например, тип билета),
            - Вторая колонка отображает общее количество билетов (`sum`),
            - Третья, четвертая и пятая колонки отображают количество билетов для различных временных интервалов (`t_1`, `t_2`, `t_3`).
        """
        logger.info("Запуск функции fill_ticket_table")
        self.ui.tableWidget_3.setRowCount(len(data))
        for row, (label, values) in enumerate(data):
            self.ui.tableWidget_3.setItem(row, 0, QTableWidgetItem(label))
            self.ui.tableWidget_3.setItem(row, 1, QTableWidgetItem(f"{values['sum']}"))
            self.ui.tableWidget_3.setItem(row, 2, QTableWidgetItem(f"{values['t_1']}"))
            self.ui.tableWidget_3.setItem(row, 3, QTableWidgetItem(f"{values['t_2']}"))
            self.ui.tableWidget_3.setItem(row, 4, QTableWidgetItem(f"{values['t_3']}"))

    def main_otchet_administratora(self) -> None:
        """
        Функция формирует отчет администратора.

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции main_otchet_administratora")
        path: str = "./otchet.pdf"
        path = os.path.realpath(path)
        row: int = self.ui.tableWidget_3.rowCount()
        if row >= 1:
            # Удаляем предыдущий файл
            os.system("TASKKILL /F /IM SumatraPDF.exe")
            if os.path.exists(path):
                os.remove(path)
            dt1, dt2 = self.get_date_range_from_ui()
            ticket_summary = system.ticket_price_summary
            otchet.otchet_administratora(dt1, dt2, ticket_summary)
            os.startfile(path)

    def main_otchet_kassira(self) -> None:
        """
        Функция формирует отчет кассира, используя данные из system.sales_data_summary
        для конкретного рабочего места (по имени компьютера).

        Параметры:
            self: object
                Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции main_otchet_kassira")
        path: str = "./otchet.pdf"
        path = os.path.realpath(path)
        # Удаляем предыдущий файл
        if os.path.exists(path):
            os.remove(path)
        # Проверяем, есть ли данные о продажах в system.sales_data_summary
        if not hasattr(system, 'sales_data_summary') or not system.sales_data_summary:
            logger.error("Нет данных о продажах для отчета кассира")
            return
        # Получаем имя текущего компьютера
        current_pc_name = system.pc_name
        # Фильтруем данные по имени текущего ПК
        filtered_sales_data = [
            row for row in system.sales_data_summary if row[0] == current_pc_name
        ]
        # Если данных по текущему ПК нет, выводим ошибку
        if not filtered_sales_data:
            logger.error(f"Нет данных о продажах для ПК с именем {current_pc_name}")
            return
        # Извлекаем нужные данные из filtered_sales_data
        total_sales_card = filtered_sales_data[0][1]  # Банковская карта
        total_sales_cash = filtered_sales_data[0][2]  # Наличные
        total_returns_card = filtered_sales_data[0][3]  # Возврат (банковская карта)
        total_returns_cash = filtered_sales_data[0][4]  # Возврат (наличные)
        # Формируем данные для отчета
        values = [
            str(total_sales_card),
            str(total_sales_cash),
            str(total_returns_card),
            str(total_returns_cash)
        ]

        # Получаем даты для отчета
        dt1, dt2 = self.get_date_range_from_ui()

        # Получаем информацию о кассире
        kassir = system.user  # Предполагаем, что данные о кассире хранятся в system.user

        # Вызываем функцию для формирования отчета
        otchet.otchet_kassira(values, dt1, dt2, kassir)

        # Открываем файл отчета
        os.startfile(path)


class Payment:
    """Класс типов платежа (перечисление)"""

    Card: int = 101
    Cash: int = 102
    Offline: int = 100


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    auth = AuthForm()
    auth.show()
    auth.ui.label_9.setText(system.database)
    sys.exit(app.exec())
