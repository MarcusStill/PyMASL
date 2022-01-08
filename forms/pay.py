from PySide6.QtCore import QRect, QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QGroupBox
from PySide6.QtGui import Qt, QFont


class Ui_Dialog_Pay(object):
    def setupUi(self, Dialog_Pay):
        if not Dialog_Pay.objectName():
            Dialog_Pay.setObjectName(u"Dialog_Pay")
        Dialog_Pay.setWindowModality(Qt.ApplicationModal)
        Dialog_Pay.resize(424, 254)
        Dialog_Pay.setMinimumSize(QSize(10, 10))
        Dialog_Pay.setModal(False)
        self.groupBox = QGroupBox(Dialog_Pay)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(0, 0, 231, 251))
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 81, 21))
        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 40, 101, 21))
        self.label_3.setFont(font)
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(110, 10, 71, 21))
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(True)
        self.label_2.setFont(font1)
        self.lineEdit = QLineEdit(self.groupBox)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(110, 40, 113, 22))
        font2 = QFont()
        font2.setBold(True)
        self.lineEdit.setFont(font2)
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 70, 101, 21))
        self.label_4.setFont(font)
        self.pushButton = QPushButton(self.groupBox)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(10, 110, 211, 41))
        font3 = QFont()
        font3.setPointSize(15)
        font3.setBold(False)
        self.pushButton.setFont(font3)
        self.pushButton_2 = QPushButton(self.groupBox)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(10, 160, 211, 41))
        font4 = QFont()
        font4.setPointSize(15)
        self.pushButton_2.setFont(font4)
        self.pushButton_3 = QPushButton(self.groupBox)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(10, 210, 211, 41))
        self.pushButton_3.setFont(font4)
        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(110, 70, 101, 21))
        self.label_9.setFont(font1)
        self.groupBox_2 = QGroupBox(Dialog_Pay)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(230, 0, 191, 251))
        self.pushButton_4 = QPushButton(self.groupBox_2)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(0, 10, 91, 41))
        font5 = QFont()
        font5.setPointSize(20)
        self.pushButton_4.setFont(font5)
        self.pushButton_5 = QPushButton(self.groupBox_2)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setGeometry(QRect(0, 50, 91, 41))
        self.pushButton_5.setFont(font5)
        self.pushButton_6 = QPushButton(self.groupBox_2)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.pushButton_6.setGeometry(QRect(0, 90, 91, 41))
        self.pushButton_6.setFont(font5)
        self.pushButton_7 = QPushButton(self.groupBox_2)
        self.pushButton_7.setObjectName(u"pushButton_7")
        self.pushButton_7.setGeometry(QRect(0, 130, 91, 41))
        self.pushButton_7.setFont(font5)
        self.pushButton_8 = QPushButton(self.groupBox_2)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setGeometry(QRect(0, 170, 91, 41))
        self.pushButton_8.setFont(font5)
        self.pushButton_9 = QPushButton(self.groupBox_2)
        self.pushButton_9.setObjectName(u"pushButton_9")
        self.pushButton_9.setGeometry(QRect(0, 210, 91, 41))
        self.pushButton_9.setFont(font5)
        self.pushButton_10 = QPushButton(self.groupBox_2)
        self.pushButton_10.setObjectName(u"pushButton_10")
        self.pushButton_10.setGeometry(QRect(100, 10, 91, 241))
        self.pushButton_10.setFont(font5)

        self.retranslateUi(Dialog_Pay)

        QMetaObject.connectSlotsByName(Dialog_Pay)
    # setupUi

    def retranslateUi(self, Dialog_Pay):
        Dialog_Pay.setWindowTitle(QCoreApplication.translate("Dialog_Pay", u"\u041e\u043f\u043b\u0430\u0442\u0430 \u043f\u0440\u043e\u0434\u0430\u0436\u0438", None))
        self.groupBox.setTitle("")
        self.label.setText(QCoreApplication.translate("Dialog_Pay", u"\u041a \u041e\u041f\u041b\u0410\u0422\u0415:", None))
        self.label_3.setText(QCoreApplication.translate("Dialog_Pay", u"\u041f\u041e\u041b\u0423\u0427\u0415\u041d\u041e:", None))
        self.label_2.setText(QCoreApplication.translate("Dialog_Pay", u"0", None))
        self.label_4.setText(QCoreApplication.translate("Dialog_Pay", u"\u0421\u0414\u0410\u0427\u0410:", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog_Pay", u"\u041d\u0410\u041b\u0418\u0427\u041d\u042b\u041c\u0418", None))
        self.pushButton_2.setText(QCoreApplication.translate("Dialog_Pay", u"\u041a\u0410\u0420\u0422\u041e\u0419", None))
        self.pushButton_3.setText(QCoreApplication.translate("Dialog_Pay", u"\u041a\u0410\u0420\u0422\u041e\u0419 OFFLINE", None))
        self.label_9.setText(QCoreApplication.translate("Dialog_Pay", u"0", None))
        self.groupBox_2.setTitle("")
        self.pushButton_4.setText(QCoreApplication.translate("Dialog_Pay", u"50", None))
        self.pushButton_5.setText(QCoreApplication.translate("Dialog_Pay", u"100", None))
        self.pushButton_6.setText(QCoreApplication.translate("Dialog_Pay", u"200", None))
        self.pushButton_7.setText(QCoreApplication.translate("Dialog_Pay", u"500", None))
        self.pushButton_8.setText(QCoreApplication.translate("Dialog_Pay", u"1000", None))
        self.pushButton_9.setText(QCoreApplication.translate("Dialog_Pay", u"2000", None))
        self.pushButton_10.setText(QCoreApplication.translate("Dialog_Pay", u"\u041e\n"
"\u0422\n"
"\u041c\n"
"\u0415\n"
"\u041d\n"
"\u0410", None))
    # retranslateUi

