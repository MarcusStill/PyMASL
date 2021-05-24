import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QWidget, QVBoxLayout, QComboBox
from forms.authorization import Ui_Dialog
from forms.main_form import Ui_MainWindow
from forms.client import Ui_Dialog_Client

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from  models.client import Client

engine = create_engine("postgresql://postgres:secret@localhost:5432/masl", echo=True)
Base = declarative_base(bind=engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton_2.clicked.connect(self.openClient)


    def openClient(self):
        client = ClientForm()
        client.show()
        client.exec_()


class AuthForm(QDialog):
    def __init__(self):
        super(AuthForm, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.openMain)
        self.ui.pushButton_2.clicked.connect(self.close)


    def openMain(self):
        auth.close()
        window = MainWindow()
        window.show()
        window.exec_()


class ClientForm(QDialog):
    def __init__(self):
        super(ClientForm, self).__init__()
        self.ui = Ui_Dialog_Client()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.buttonSave)
        self.ui.pushButton_2.clicked.connect(self.close)

    def buttonSave(self):
        session = Session()
        add_client = Client(first_name=str(self.ui.lineEdit.text()),
                            last_name=str(self.ui.lineEdit_2.text()),
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


if __name__ == "__main__":
    app = QApplication()

    auth = AuthForm()
    auth.show()

    sys.exit(app.exec_())
