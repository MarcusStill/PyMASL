# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'client_old.ui'
##
## Created by: Qt User Interface Compiler version 6.1.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_Dialog_Client(object):
    def setupUi(self, Dialog_Client):
        if not Dialog_Client.objectName():
            Dialog_Client.setObjectName(u"Dialog_Client")
        Dialog_Client.resize(354, 344)
        self.toolBox = QToolBox(Dialog_Client)
        self.toolBox.setObjectName(u"toolBox")
        self.toolBox.setGeometry(QRect(10, 10, 331, 311))
        self.client = QWidget()
        self.client.setObjectName(u"client")
        self.client.setGeometry(QRect(0, 0, 331, 209))
        self.layoutWidget = QWidget(self.client)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 0, 333, 176))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.lineEdit = QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 2)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.lineEdit_2 = QLineEdit(self.layoutWidget)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 2)

        self.label_5 = QLabel(self.layoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)

        self.lineEdit_3 = QLineEdit(self.layoutWidget)
        self.lineEdit_3.setObjectName(u"lineEdit_3")

        self.gridLayout.addWidget(self.lineEdit_3, 2, 1, 1, 2)

        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 2)

        self.dateEdit = QDateEdit(self.layoutWidget)
        self.dateEdit.setObjectName(u"dateEdit")

        self.gridLayout.addWidget(self.dateEdit, 3, 2, 1, 1)

        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 3, 3, 1, 1)

        self.comboBox = QComboBox(self.layoutWidget)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.gridLayout.addWidget(self.comboBox, 3, 4, 1, 1)

        self.label_6 = QLabel(self.layoutWidget)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)

        self.lineEdit_4 = QLineEdit(self.layoutWidget)
        self.lineEdit_4.setObjectName(u"lineEdit_4")

        self.gridLayout.addWidget(self.lineEdit_4, 4, 1, 1, 2)

        self.toolBox.addItem(self.client, u"\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e \u043a\u043b\u0438\u0435\u043d\u0442\u0435")
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2.setGeometry(QRect(0, 0, 331, 209))
        self.toolBox.addItem(self.page_2, u"Page 2")
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.page_3.setGeometry(QRect(0, 0, 331, 209))
        self.toolBox.addItem(self.page_3, u"Page 3")
        self.pushButton = QPushButton(Dialog_Client)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(140, 310, 94, 28))
        self.pushButton_2 = QPushButton(Dialog_Client)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(250, 310, 94, 28))

        self.retranslateUi(Dialog_Client)

        self.toolBox.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog_Client)
    # setupUi

    def retranslateUi(self, Dialog_Client):
        Dialog_Client.setWindowTitle(QCoreApplication.translate("Dialog_Client", u"\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u043e", None))
        self.label.setText(QCoreApplication.translate("Dialog_Client", u"\u0424\u0430\u043c\u0438\u043b\u0438\u044f", None))
        self.label_2.setText(QCoreApplication.translate("Dialog_Client", u"\u0418\u043c\u044f", None))
        self.label_5.setText(QCoreApplication.translate("Dialog_Client", u"\u041e\u0442\u0447\u0435\u0441\u0442\u0432\u043e", None))
        self.label_3.setText(QCoreApplication.translate("Dialog_Client", u"\u0414\u0430\u0442\u0430 \u0440\u043e\u0436\u0434\u0435\u043d\u0438\u044f", None))
        self.label_4.setText(QCoreApplication.translate("Dialog_Client", u"\u041f\u043e\u043b", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Dialog_Client", u"-", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Dialog_Client", u"\u043c\u0443\u0436", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("Dialog_Client", u"\u0436\u0435\u043d", None))

        self.label_6.setText(QCoreApplication.translate("Dialog_Client", u"\u0422\u0435\u043b\u0435\u0444\u043e\u043d", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.client), QCoreApplication.translate("Dialog_Client", u"\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e \u043a\u043b\u0438\u0435\u043d\u0442\u0435", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), QCoreApplication.translate("Dialog_Client", u"Page 2", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3), QCoreApplication.translate("Dialog_Client", u"Page 3", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog_Client", u"Ok", None))
        self.pushButton_2.setText(QCoreApplication.translate("Dialog_Client", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

