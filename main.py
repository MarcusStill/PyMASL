from datetime import datetime, date
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QCheckBox
from PySide6.QtCore import Qt
from forms.authorization import Ui_Dialog
from forms.main_form import Ui_MainWindow
from forms.client import Ui_Dialog_Client
from forms.sale import Ui_Dialog_Sale
from models.client import Client
from models.user import User
from sqlalchemy import create_engine, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from connect import connect
import kkt


engine = create_engine("postgresql://postgres:secret@localhost:5432/masl", echo=True)
Base = declarative_base(bind=engine)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class MainWindow(QMainWindow):
    """Главная форма"""
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        """Открыть окно добавления нового клиента"""
        self.ui.pushButton_2.clicked.connect(self.openClient)
        """Отображение всех клиентов"""
        self.ui.pushButton_4.clicked.connect(self.buttonAllClient)
        self.ui.tableWidget.doubleClicked.connect(self.search_selected_item)
        self.ui.pushButton_3.clicked.connect(self.search_selected_item)
        self.ui.pushButton.clicked.connect(self.search_client)
        self.ui.pushButton_8.clicked.connect(kkt.get_info)
        self.ui.pushButton_11.clicked.connect(kkt.last_document)
        self.ui.pushButton_9.clicked.connect(kkt.get_time)
        self.ui.pushButton_5.clicked.connect(kkt.report_x)
        self.ui.pushButton_7.clicked.connect(kkt.get_status_obmena)
        self.ui.pushButton_6.clicked.connect(kkt.smena_close())
        self.ui.pushButton_12.clicked.connect(self.openSale)


    def search_client(self):
        """Поиск клиента"""
        combo_active_item = self.ui.comboBox.currentText()
        print(combo_active_item)
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


    def search_selected_item(self):
        """Поиск выделенной строки в таблице и открытие формы с найденными данными"""
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


    def openClient(self):
        """Открываем форму с данными клиента"""
        client = ClientForm()
        client.show()
        client.exec_()


    def openSale(self):
        """Открываем форму с продажей"""
        sale = SaleForm()
        sale.buttonAllClient()
        sale.show()
        sale.exec_()


    def buttonAllClient(self):
        """Очищаем tableWidget"""
        self.ui.tableWidget.setRowCount(0)
        session = Session()
        clients = session.query(Client).order_by(Client.id)
        for client in clients:
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


class AuthForm(QDialog):
    """Форма авторизации"""
    """Проверяем есть ли в таблице user запись с указанными полями"""
    def logincheck(self):
        session = Session()
        result = session.query(User).filter(and_(User.login == self.ui.lineEdit.text(), User.login == self.ui.lineEdit_2.text())).first()
        session.close()
        if result:
            self.openMain()


    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        """Проверяем статус соединения с БД"""
        db_version = connect()
        if db_version:
            self.ui.label_3.setText('установлено')
        else:
            self.ui.label_3.setText('ошибка!')
        self.ui.pushButton.clicked.connect(self.logincheck)
        self.ui.pushButton_2.clicked.connect(self.close)


    def openMain(self):
        """После закрытия окна авторизации открываем главную форму"""
        auth.close()
        window = MainWindow()
        window.buttonAllClient()
        window.show()
        window.exec_()


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


    def buttonSave(self):
        """Сохраняем информацию о новом клиенте"""
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


    def buttonAllClient(self):
        """Выводим в tableWidget список всех клиентов"""
        session = Session()
        clients = session.query(Client).order_by(Client.id)
        for client in clients:
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


class SaleForm(QDialog):
    """Форма с данными клиента"""
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_Sale()
        self.ui.setupUi(self)
        self.ui.pushButton_3.clicked.connect(self.close)
        self.ui.pushButton_4.clicked.connect(self.close)
        self.ui.pushButton_5.clicked.connect(self.check_ticket_generate)
        self.ui.tableWidget.doubleClicked.connect(self.search_selected_item)
        self.ui.tableWidget_2.doubleClicked.connect(self.edit_sale)
        cur_today = date.today()
        self.ui.dateEdit.setDate(cur_today)
        self.ui.checkBox_2.setChecked(Qt.Checked)


    def buttonAllClient(self):
        """Выводим в tableWidget список всех клиентов"""
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


    def search_selected_item(self):
        """Поиск выделенной строки в таблице и открытие формы с найденными данными"""
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
            if age >= 14:
                type_ticket = 'взрослый'
            else:
                type_ticket = 'детский'
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
            """Заполняем таблицу с итоговой информацией"""


    def edit_sale(self):
        """Обновляем таблицу заказа при двойном клике по ней"""
        kol_adult = 0
        kol_child = 0
        price_adult = 0
        price_child = 0
        time_ticket = self.ui.comboBox.currentText()
        sale = 0
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
                kol_adult += 1
                price_adult = self.ui.tableWidget_2.item(row, 4).text()
            else:
                kol_child += 1
                price_child = self.ui.tableWidget_2.item(row, 4).text()
        self.ui.label_5.setText(str(kol_adult))
        self.ui.label_7.setText(str(kol_child))
        """применяем скидку"""
        discount = int(self.ui.comboBox_2.currentText())
        if sale >= 0:
            new_price = sale - (sale/100 * discount)
            new_price = int(new_price)
            print('new_price', new_price)
            self.ui.label_8.setText(str(new_price))
        """Сохраняем продажу"""
        new_sale = (kol_adult, int(price_adult), kol_child, int(price_child), new_price)
        # """Номер выделенной ячейки"""
        # x = self.ui.tableWidget_2.currentRow()
        # y = self.ui.tableWidget_2.currentColumn()
        # print('row', x, 'col', y)
        return new_sale


    def check_ticket_generate(self):
        new_sale = self.edit_sale()
        kkt.check_open_2(new_sale)



if __name__ == "__main__":
    app = QApplication()

    auth = AuthForm()
    auth.show()

    sys.exit(app.exec_())
