from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QPushButton


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(447, 230)
        self.label = QLabel(Dialog)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(200, 70, 47, 20))
        self.lineEdit = QLineEdit(Dialog)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setGeometry(QRect(262, 60, 181, 30))
        self.lineEdit_2 = QLineEdit(Dialog)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setGeometry(QRect(262, 100, 181, 30))
        self.lineEdit_2.setEchoMode(QLineEdit.Password)
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(200, 110, 56, 20))
        self.pushButton = QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QRect(190, 170, 94, 28))
        self.pushButton_2 = QPushButton(Dialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setGeometry(QRect(290, 170, 85, 28))
        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.label_4.setGeometry(QRect(10, 10, 181, 181))
        self.label_4.setPixmap(QPixmap("../../TestProject/files/logo.png"))
        self.label_4.setScaledContents(True)
        self.label_5 = QLabel(Dialog)
        self.label_5.setObjectName("label_5")
        self.label_5.setGeometry(QRect(90, 10, 301, 21))
        self.label_5.setAlignment(Qt.AlignCenter)
        self.label_5.setWordWrap(True)
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.label_3.setGeometry(QRect(320, 140, 121, 20))
        self.line = QFrame(Dialog)
        self.line.setObjectName("line")
        self.line.setGeometry(QRect(0, 200, 441, 16))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.label_6 = QLabel(Dialog)
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(10, 210, 81, 20))
        self.label_6.setTextFormat(Qt.RichText)
        self.label_7 = QLabel(Dialog)
        self.label_7.setObjectName("label_7")
        self.label_7.setGeometry(QRect(80, 210, 41, 20))
        self.label_8 = QLabel(Dialog)
        self.label_8.setObjectName("label_8")
        self.label_8.setGeometry(QRect(350, 210, 21, 20))
        self.label_9 = QLabel(Dialog)
        self.label_9.setObjectName("label_9")
        self.label_9.setGeometry(QRect(380, 210, 61, 20))

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(
            QCoreApplication.translate(
                "Dialog",
                "PyMASL - \u0410\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u044f",
                None,
            )
        )
        self.label.setText(
            QCoreApplication.translate(
                "Dialog", "\u041b\u043e\u0433\u0438\u043d:", None
            )
        )
        self.label_2.setText(
            QCoreApplication.translate(
                "Dialog", "\u041f\u0430\u0440\u043e\u043b\u044c:", None
            )
        )
        self.pushButton.setText(QCoreApplication.translate("Dialog", "Ok", None))
        self.pushButton_2.setText(
            QCoreApplication.translate(
                "Dialog", "\u041e\u0442\u043c\u0435\u043d\u0430", None
            )
        )
        self.label_4.setText("")
        self.label_5.setText(
            QCoreApplication.translate(
                "Dialog",
                "\u041a\u043e\u0440\u043f\u043e\u0440\u0430\u0442\u0438\u0432\u043d\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u043e\u043d\u043d\u0430\u044f \u0441\u0438\u0441\u0442\u0435\u043c\u0430 PyMASL",
                None,
            )
        )
        self.label_3.setText("")
        self.label_6.setText(
            QCoreApplication.translate(
                "Dialog", "\u0412\u0435\u0440\u0441\u0438\u044f \u041f\u041e:", None
            )
        )
        self.label_7.setText(QCoreApplication.translate("Dialog", "0.0.1", None))
        self.label_8.setText(
            QCoreApplication.translate("Dialog", "\u0411\u0414:", None)
        )
        self.label_9.setText(QCoreApplication.translate("Dialog", "-", None))

    # retranslateUi
