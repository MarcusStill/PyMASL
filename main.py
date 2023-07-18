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

from design.pay import Ui_Dialog_Pay

from design.sale import Ui_Dialog_Sale
from files import windows
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
        # self.ui.pushButton.clicked.connect(self.sale_search_clients)
        # self.ui.pushButton_2.clicked.connect(lambda: MainWindow.main_open_client(self))
        # self.ui.pushButton_11.clicked.connect(self.sale_edit_client)
        # self.ui.pushButton_3.clicked.connect(self.sale_save_selling)
        # self.ui.pushButton_4.clicked.connect(self.close)
        self.ui.pushButton_5.clicked.connect(
            lambda: self.sale_open_pay(self.ui.label_8.text()))
        # self.ui.pushButton_6.clicked.connect(self.sale_return_selling)
        # self.ui.pushButton_7.clicked.connect(self.sale_generate_saved_tickets)
        # self.ui.tableWidget.doubleClicked.connect(self.sale_add_client_to_selling)
        # cur_today = date.today()
        # self.ui.dateEdit.setDate(cur_today)
        # self.ui.dateEdit.dateChanged.connect(self.sale_calendar_color_change)
        # self.ui.comboBox.currentTextChanged.connect(self.sale_edit_selling)
        # self.ui.checkBox_2.stateChanged.connect(self.sale_check_discount_enabled)
        # self.ui.comboBox_2.currentTextChanged.connect(self.sale_edit_selling)
        # # адаптированный для пользователя фильтр
        # self.ui.comboBox_4.currentTextChanged.connect(self.sale_check_filter_update)
        # # KeyPressEvent
        # self.ui.tableWidget_2.keyPressEvent = self.sale_key_pressed
        # self.ui.pushButton_9.clicked.connect(self.sale_add_new_client)
        # self.ui.pushButton_10.clicked.connect(self.sale_edit_selling)
        # self.ui.tableWidget_3.doubleClicked.connect(self.sale_add_client_to_selling_2)

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