# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_form.ui'
##
## Created by: Qt User Interface Compiler version 6.1.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1043, 666)
        self.action = QAction(MainWindow)
        self.action.setObjectName(u"action")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(10, 10, 1021, 611))
        self.visitors = QWidget()
        self.visitors.setObjectName(u"visitors")
        self.label = QLabel(self.visitors)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(550, -1, 63, 31))
        self.comboBox = QComboBox(self.visitors)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QRect(607, 0, 91, 30))
        self.lineEdit = QLineEdit(self.visitors)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(700, 0, 311, 30))
        self.pushButton = QPushButton(self.visitors)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(10, 0, 94, 28))
        self.tableWidget = QTableWidget(self.visitors)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(10, 30, 1001, 531))
        self.line = QFrame(self.visitors)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(530, 0, 20, 31))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.pushButton_2 = QPushButton(self.visitors)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(110, 0, 94, 28))
        self.pushButton_3 = QPushButton(self.visitors)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(210, 0, 94, 28))
        self.pushButton_4 = QPushButton(self.visitors)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(310, 0, 94, 28))
        self.tabWidget.addTab(self.visitors, "")
        self.sales = QWidget()
        self.sales.setObjectName(u"sales")
        self.tabWidget.addTab(self.sales, "")
        self.tickets = QWidget()
        self.tickets.setObjectName(u"tickets")
        self.tabWidget.addTab(self.tickets, "")
        self.cashbox = QWidget()
        self.cashbox.setObjectName(u"cashbox")
        self.tabWidget.addTab(self.cashbox, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1043, 30))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.action)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PyMASL", None))
        self.action.setText(QCoreApplication.translate("MainWindow", u"\u041e \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0435", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0438\u0441\u043a:", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"\u0442\u0435\u043b\u0435\u0444\u043e\u043d", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"\u0444\u0430\u043c\u0438\u043b\u0438\u044f", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"\u0438\u043c\u044f", None))

        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0439\u0442\u0438", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Search all", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.visitors), QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0441\u0435\u0442\u0438\u0442\u0435\u043b\u0438", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sales), QCoreApplication.translate("MainWindow", u"\u041f\u0440\u043e\u0434\u0430\u0436\u0438", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tickets), QCoreApplication.translate("MainWindow", u"\u0411\u0438\u043b\u0435\u0442\u044b", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.cashbox), QCoreApplication.translate("MainWindow", u"\u041a\u0430\u0441\u0441\u0430", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u041c\u0435\u043d\u044e", None))
    # retranslateUi

