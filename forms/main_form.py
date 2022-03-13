# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_form_9.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGroupBox,
    QHeaderView, QLabel, QLineEdit, QMainWindow,
    QMenu, QMenuBar, QPushButton, QRadioButton,
    QSizePolicy, QStatusBar, QTabWidget, QTableWidget,
    QTableWidgetItem, QWidget, QAbstractItemView)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.ApplicationModal)
        MainWindow.resize(1920, 1080)
        self.action = QAction(MainWindow)
        self.action.setObjectName(u"action")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(10, 10, 1901, 1080))
        self.tabWidget.setMaximumSize(QSize(1920, 1080))
        self.visitors = QWidget()
        self.visitors.setObjectName(u"visitors")
        self.label = QLabel(self.visitors)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(230, -1, 63, 31))
        self.comboBox = QComboBox(self.visitors)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QRect(287, 0, 91, 30))
        self.lineEdit = QLineEdit(self.visitors)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(380, 0, 311, 30))
        self.pushButton = QPushButton(self.visitors)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(700, 0, 94, 28))
        self.tableWidget = QTableWidget(self.visitors)
        if (self.tableWidget.columnCount() < 9):
            self.tableWidget.setColumnCount(9)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(8, __qtablewidgetitem8)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(10, 30, 1881, 941))
        self.line = QFrame(self.visitors)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(210, 0, 20, 31))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.pushButton_2 = QPushButton(self.visitors)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(10, 0, 94, 28))
        self.pushButton_3 = QPushButton(self.visitors)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(110, 0, 94, 28))
        self.pushButton_4 = QPushButton(self.visitors)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(810, 0, 94, 28))
        self.tabWidget.addTab(self.visitors, "")
        self.sales = QWidget()
        self.sales.setObjectName(u"sales")
        self.pushButton_12 = QPushButton(self.sales)
        self.pushButton_12.setObjectName(u"pushButton_12")
        self.pushButton_12.setGeometry(QRect(0, 10, 94, 28))
        font = QFont()
        font.setBold(True)
        self.pushButton_12.setFont(font)
        self.tableWidget_2 = QTableWidget(self.sales)
        if (self.tableWidget_2.columnCount() < 4):
            self.tableWidget_2.setColumnCount(4)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(0, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(1, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(2, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(3, __qtablewidgetitem12)
        self.tableWidget_2.setObjectName(u"tableWidget_2")
        self.tableWidget_2.setGeometry(QRect(-10, 50, 1901, 961))
        self.tableWidget_2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.groupBox_3 = QGroupBox(self.sales)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(110, 0, 321, 41))
        self.radioButton = QRadioButton(self.groupBox_3)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setGeometry(QRect(0, 20, 89, 20))
        self.radioButton.setChecked(True)
        self.radioButton_2 = QRadioButton(self.groupBox_3)
        self.radioButton_2.setObjectName(u"radioButton_2")
        self.radioButton_2.setGeometry(QRect(80, 20, 89, 20))
        self.radioButton_3 = QRadioButton(self.groupBox_3)
        self.radioButton_3.setObjectName(u"radioButton_3")
        self.radioButton_3.setGeometry(QRect(150, 20, 61, 20))
        self.pushButton_13 = QPushButton(self.groupBox_3)
        self.pushButton_13.setObjectName(u"pushButton_13")
        self.pushButton_13.setGeometry(QRect(220, 10, 94, 28))
        self.tabWidget.addTab(self.sales, "")
        self.statistic = QWidget()
        self.statistic.setObjectName(u"statistic")
        self.pushButton_14 = QPushButton(self.statistic)
        self.pushButton_14.setObjectName(u"pushButton_14")
        self.pushButton_14.setGeometry(QRect(0, 10, 94, 28))
        self.tabWidget.addTab(self.statistic, "")
        self.cashbox = QWidget()
        self.cashbox.setObjectName(u"cashbox")
        self.groupBox = QGroupBox(self.cashbox)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(10, 20, 371, 231))
        self.pushButton_11 = QPushButton(self.groupBox)
        self.pushButton_11.setObjectName(u"pushButton_11")
        self.pushButton_11.setGeometry(QRect(130, 90, 111, 61))
        self.pushButton_11.setAcceptDrops(False)
        self.pushButton_11.setAutoExclusive(True)
        self.pushButton_11.setFlat(False)
        self.pushButton_8 = QPushButton(self.groupBox)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setGeometry(QRect(250, 20, 111, 61))
        self.pushButton_8.setAcceptDrops(False)
        self.pushButton_8.setAutoExclusive(True)
        self.pushButton_8.setFlat(False)
        self.pushButton_6 = QPushButton(self.groupBox)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.pushButton_6.setGeometry(QRect(10, 90, 111, 61))
        self.pushButton_5 = QPushButton(self.groupBox)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setGeometry(QRect(10, 20, 111, 61))
        self.pushButton_9 = QPushButton(self.groupBox)
        self.pushButton_9.setObjectName(u"pushButton_9")
        self.pushButton_9.setGeometry(QRect(250, 90, 111, 61))
        self.pushButton_9.setAcceptDrops(False)
        self.pushButton_9.setAutoExclusive(True)
        self.pushButton_9.setFlat(False)
        self.pushButton_10 = QPushButton(self.groupBox)
        self.pushButton_10.setObjectName(u"pushButton_10")
        self.pushButton_10.setGeometry(QRect(10, 160, 111, 61))
        self.pushButton_10.setAcceptDrops(False)
        self.pushButton_10.setAutoExclusive(True)
        self.pushButton_10.setFlat(False)
        self.pushButton_7 = QPushButton(self.groupBox)
        self.pushButton_7.setObjectName(u"pushButton_7")
        self.pushButton_7.setGeometry(QRect(130, 20, 111, 61))
        self.pushButton_7.setAcceptDrops(False)
        self.pushButton_7.setAutoExclusive(True)
        self.pushButton_7.setFlat(False)
        self.pushButton_15 = QPushButton(self.groupBox)
        self.pushButton_15.setObjectName(u"pushButton_15")
        self.pushButton_15.setGeometry(QRect(130, 160, 111, 61))
        self.pushButton_15.setAcceptDrops(False)
        self.pushButton_15.setAutoExclusive(True)
        self.pushButton_15.setFlat(False)
        self.groupBox_2 = QGroupBox(self.cashbox)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(390, 20, 371, 231))
        self.pushButton_16 = QPushButton(self.groupBox_2)
        self.pushButton_16.setObjectName(u"pushButton_16")
        self.pushButton_16.setGeometry(QRect(10, 20, 111, 61))
        self.pushButton_16.setAcceptDrops(False)
        self.pushButton_16.setAutoExclusive(True)
        self.pushButton_16.setFlat(False)
        self.tabWidget.addTab(self.cashbox, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1920, 22))
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
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"id", None));
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"\u0424\u0430\u043c\u0438\u043b\u0438\u044f", None));
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"\u0418\u043c\u044f", None));
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u0447\u0435\u0441\u0442\u0432\u043e", None));
        ___qtablewidgetitem4 = self.tableWidget.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043b", None));
        ___qtablewidgetitem5 = self.tableWidget.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"\u0414\u0430\u0442\u0430 \u0440\u043e\u0436\u0434.", None));
        ___qtablewidgetitem6 = self.tableWidget.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f", None));
        ___qtablewidgetitem7 = self.tableWidget.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"\u0422\u0435\u043b\u0435\u0444\u043e\u043d", None));
        ___qtablewidgetitem8 = self.tableWidget.horizontalHeaderItem(8)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"E-mail", None));
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c \u0432\u0441\u0435\u0445", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.visitors), QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0441\u0435\u0442\u0438\u0442\u0435\u043b\u0438", None))
        self.pushButton_12.setText(QCoreApplication.translate("MainWindow", u"\u041d\u043e\u0432\u0430\u044f", None))
        ___qtablewidgetitem9 = self.tableWidget_2.horizontalHeaderItem(0)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"id", None));
        ___qtablewidgetitem10 = self.tableWidget_2.horizontalHeaderItem(1)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"id_client", None));
        ___qtablewidgetitem11 = self.tableWidget_2.horizontalHeaderItem(2)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"price", None));
        ___qtablewidgetitem12 = self.tableWidget_2.horizontalHeaderItem(3)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainWindow", u"datetime", None));
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"\u041f\u0440\u043e\u0434\u0430\u0436\u0438 \u0437\u0430 \u043f\u0435\u0440\u0438\u043e\u0434", None))
        self.radioButton.setText(QCoreApplication.translate("MainWindow", u"\u0441\u0435\u0433\u043e\u0434\u043d\u044f", None))
        self.radioButton_2.setText(QCoreApplication.translate("MainWindow", u"3 \u0434\u043d\u044f", None))
        self.radioButton_3.setText(QCoreApplication.translate("MainWindow", u"7 \u0434\u043d\u0435\u0439", None))
        self.pushButton_13.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sales), QCoreApplication.translate("MainWindow", u"\u041f\u0440\u043e\u0434\u0430\u0436\u0438", None))
        self.pushButton_14.setText(QCoreApplication.translate("MainWindow", u"Search all", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.statistic), QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u041e\u043f\u0435\u0440\u0430\u0446\u0438\u0438 \u0441 \u041a\u041a\u041c", None))
        self.pushButton_11.setText(QCoreApplication.translate("MainWindow", u"\u041a\u043e\u043f\u0438\u044f \u043f\u043e\u0441\u043b.\n"
"\u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430", None))
        self.pushButton_8.setText(QCoreApplication.translate("MainWindow", u"\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e\n"
"\u041a\u041a\u0422", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u0447\u0435\u0442 \u0441 \u0433\u0430\u0448\u0435\u043d\u0438\u0435\u043c\n"
"(z-\u043e\u0442\u0447\u0435\u0442)", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u0447\u0435\u0442 \u0431\u0435\u0437 \u0433\u0430\u0448\u0435\u043d\u0438\u044f\n"
"(x-\u043e\u0442\u0447\u0435\u0442)", None))
        self.pushButton_9.setText(QCoreApplication.translate("MainWindow", u"\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f\n"
" \u041a\u041a\u0422", None))
        self.pushButton_10.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435\n"
"\u043a\u0430\u0441\u0441\u043e\u0432\u043e\u0439 \u0441\u043c\u0435\u043d\u044b", None))
        self.pushButton_7.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0430\u0442\u0443\u0441\n"
" \u0438\u043d\u0444\u043e\u0440\u043c.\n"
"\u043e\u0431\u043c\u0435\u043d\u0430 \u0441 \u041e\u0424\u0414", None))
        self.pushButton_15.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u043f\u0435\u0447\u0430\u0442\u0430\u0442\u044c\n"
"\u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"\u041e\u043f\u0435\u0440\u0430\u0446\u0438\u0438 \u0441 \u0431\u0430\u043d\u043a\u043e\u0432\u0441\u043a\u0438\u043c \u0442\u0435\u0440\u043c\u0438\u043d\u0430\u043b\u043e\u043c", None))
        self.pushButton_16.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0432\u0435\u0440\u043a\u0430\n"
"\u0438\u0442\u043e\u0433\u043e\u0432", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.cashbox), QCoreApplication.translate("MainWindow", u"\u041a\u0430\u0441\u0441\u0430", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u041c\u0435\u043d\u044e", None))
    # retranslateUi

