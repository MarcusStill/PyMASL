# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
QSize, Qt)
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGroupBox, QLabel, QPushButton, QCheckBox


class Ui_Dialog_Pay(object):
    def setupUi(self, Dialog_Pay):
        if not Dialog_Pay.objectName():
            Dialog_Pay.setObjectName(u"Dialog_Pay")
        Dialog_Pay.setWindowModality(Qt.ApplicationModal)
        Dialog_Pay.resize(231, 214)
        Dialog_Pay.setMinimumSize(QSize(10, 10))
        Dialog_Pay.setModal(False)
        self.groupBox = QGroupBox(Dialog_Pay)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(0, 0, 231, 251))
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(40, 10, 81, 21))
        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(140, 10, 71, 21))
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(True)
        self.label_2.setFont(font1)
        self.pushButton = QPushButton(self.groupBox)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(10, 40, 211, 41))
        font2 = QFont()
        font2.setPointSize(15)
        font2.setBold(False)
        self.pushButton.setFont(font2)
        self.pushButton_2 = QPushButton(self.groupBox)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(10, 90, 211, 41))
        font3 = QFont()
        font3.setPointSize(15)
        self.pushButton_2.setFont(font3)
        self.pushButton_3 = QPushButton(self.groupBox)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(10, 140, 211, 41))
        self.pushButton_3.setFont(font3)
        self.checkBox = QCheckBox(self.groupBox)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setGeometry(QRect(70, 190, 91, 20))
        font4 = QFont()
        font4.setPointSize(10)
        self.checkBox.setFont(font4)

        self.retranslateUi(Dialog_Pay)

        QMetaObject.connectSlotsByName(Dialog_Pay)
    # setupUi

    def retranslateUi(self, Dialog_Pay):
        Dialog_Pay.setWindowTitle(QCoreApplication.translate("Dialog_Pay", u"\u041e\u043f\u043b\u0430\u0442\u0430 \u043f\u0440\u043e\u0434\u0430\u0436\u0438", None))
        self.groupBox.setTitle("")
        self.label.setText(QCoreApplication.translate("Dialog_Pay", u"\u041a \u041e\u041f\u041b\u0410\u0422\u0415:", None))
        self.label_2.setText(QCoreApplication.translate("Dialog_Pay", u"0", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog_Pay", u"\u041d\u0410\u041b\u0418\u0427\u041d\u042b\u041c\u0418", None))
        self.pushButton_2.setText(QCoreApplication.translate("Dialog_Pay", u"\u041a\u0410\u0420\u0422\u041e\u0419", None))
        self.pushButton_3.setText(QCoreApplication.translate("Dialog_Pay", u"\u041a\u0410\u0420\u0422\u041e\u0419 OFFLINE", None))
        self.checkBox.setText(QCoreApplication.translate("Dialog_Pay", u"\u041f\u0435\u0447\u0430\u0442\u044c \u0447\u0435\u043a\u0430", None))
    # retranslateUi

