# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_form_15.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QFrame,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QRadioButton, QSizePolicy, QStatusBar,
    QTabWidget, QTableView, QTableWidget, QTableWidgetItem,
    QWidget, QAbstractItemView)

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
        self.label.setGeometry(QRect(220, 10, 51, 31))
        self.line = QFrame(self.visitors)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(200, 10, 20, 31))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.pushButton_2 = QPushButton(self.visitors)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(0, 10, 94, 31))
        self.pushButton_3 = QPushButton(self.visitors)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(100, 10, 94, 31))
        self.tableView = QTableView(self.visitors)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setGeometry(QRect(0, 50, 1681, 951))
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lineEdit_2 = QLineEdit(self.visitors)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setGeometry(QRect(270, 10, 391, 31))
        self.comboBox_2 = QComboBox(self.visitors)
        self.comboBox_2.setObjectName(u"comboBox_2")
        self.comboBox_2.setGeometry(QRect(670, 10, 171, 31))
        self.tabWidget.addTab(self.visitors, "")
        self.sales = QWidget()
        self.sales.setObjectName(u"sales")
        self.pushButton_12 = QPushButton(self.sales)
        self.pushButton_12.setObjectName(u"pushButton_12")
        self.pushButton_12.setGeometry(QRect(0, 10, 94, 31))
        font = QFont()
        font.setBold(True)
        self.pushButton_12.setFont(font)
        self.line_2 = QFrame(self.sales)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setGeometry(QRect(100, 10, 20, 31))
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.tableWidget_2 = QTableWidget(self.sales)
        if (self.tableWidget_2.columnCount() < 8):
            self.tableWidget_2.setColumnCount(8)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        self.tableWidget_2.setObjectName(u"tableWidget_2")
        self.tableWidget_2.setGeometry(QRect(0, 50, 1901, 961))
        self.tableWidget_2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.groupBox_3 = QGroupBox(self.sales)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(120, 0, 321, 41))
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
        self.groupBox_5 = QGroupBox(self.statistic)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setGeometry(QRect(-10, 70, 600, 350))
        self.tableWidget_3 = QTableWidget(self.groupBox_5)
        if (self.tableWidget_3.columnCount() < 5):
            self.tableWidget_3.setColumnCount(5)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(0, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(1, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(2, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(3, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(4, __qtablewidgetitem12)
        self.tableWidget_3.setObjectName(u"tableWidget_3")
        self.tableWidget_3.setGeometry(QRect(10, 20, 581, 321))
        self.tableWidget_3.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_3.horizontalHeader().setDefaultSectionSize(115)
        self.groupBox_7 = QGroupBox(self.statistic)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.groupBox_7.setGeometry(QRect(0, 10, 321, 61))
        self.layoutWidget = QWidget(self.groupBox_7)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 20, 299, 26))
        self.horizontalLayout_2 = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.dateEdit_2 = QDateEdit(self.layoutWidget)
        self.dateEdit_2.setObjectName(u"dateEdit_2")
        self.dateEdit_2.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.dateEdit_2)

        self.dateEdit = QDateEdit(self.layoutWidget)
        self.dateEdit.setObjectName(u"dateEdit")
        self.dateEdit.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.dateEdit)

        self.pushButton_17 = QPushButton(self.layoutWidget)
        self.pushButton_17.setObjectName(u"pushButton_17")

        self.horizontalLayout_2.addWidget(self.pushButton_17)

        self.groupBox_6 = QGroupBox(self.statistic)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.groupBox_6.setGeometry(QRect(600, 70, 600, 350))
        self.tableWidget_4 = QTableWidget(self.groupBox_6)
        if (self.tableWidget_4.columnCount() < 4):
            self.tableWidget_4.setColumnCount(4)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(0, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(1, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(2, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(3, __qtablewidgetitem16)
        self.tableWidget_4.setObjectName(u"tableWidget_4")
        self.tableWidget_4.setGeometry(QRect(10, 20, 581, 321))
        self.tableWidget_4.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_4.horizontalHeader().setDefaultSectionSize(140)
        self.pushButton_18 = QPushButton(self.statistic)
        self.pushButton_18.setObjectName(u"pushButton_18")
        self.pushButton_18.setGeometry(QRect(320, 20, 111, 51))
        self.pushButton_18.setFont(font)
        self.pushButton_19 = QPushButton(self.statistic)
        self.pushButton_19.setObjectName(u"pushButton_19")
        self.pushButton_19.setGeometry(QRect(440, 20, 111, 51))
        self.pushButton_19.setFont(font)
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
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u0424\u0438\u043b\u044c\u0442\u0440:", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.visitors), QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0441\u0435\u0442\u0438\u0442\u0435\u043b\u0438", None))
        self.pushButton_12.setText(QCoreApplication.translate("MainWindow", u"\u041d\u043e\u0432\u0430\u044f", None))
        ___qtablewidgetitem = self.tableWidget_2.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"N \u043f\u0440\u043e\u0434\u0430\u0436\u0438", None));
        ___qtablewidgetitem1 = self.tableWidget_2.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"N \u043a\u043b\u0438\u0435\u043d\u0442\u0430", None));
        ___qtablewidgetitem2 = self.tableWidget_2.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"\u0426\u0435\u043d\u0430", None));
        ___qtablewidgetitem3 = self.tableWidget_2.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"\u0414\u0430\u0442\u0430", None));
        ___qtablewidgetitem4 = self.tableWidget_2.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0430\u0442\u0443\u0441", None));
        ___qtablewidgetitem5 = self.tableWidget_2.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043a\u0438\u0434\u043a\u0430", None));
        ___qtablewidgetitem6 = self.tableWidget_2.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"\u0418\u043c\u044f \u041f\u041a", None));
        ___qtablewidgetitem7 = self.tableWidget_2.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"\u0422\u0438\u043f \u043e\u043f\u043b\u0430\u0442\u044b", None));
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"\u0424\u0438\u043b\u044c\u0442\u0440 \u0437\u0430 \u043f\u0435\u0440\u0438\u043e\u0434", None))
        self.radioButton.setText(QCoreApplication.translate("MainWindow", u"\u0441\u0435\u0433\u043e\u0434\u043d\u044f", None))
        self.radioButton_2.setText(QCoreApplication.translate("MainWindow", u"3 \u0434\u043d\u044f", None))
        self.radioButton_3.setText(QCoreApplication.translate("MainWindow", u"7 \u0434\u043d\u0435\u0439", None))
        self.pushButton_13.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sales), QCoreApplication.translate("MainWindow", u"\u041f\u0440\u043e\u0434\u0430\u0436\u0438", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e\u0441\u0435\u0449\u0435\u043d\u0438\u0439", None))
        ___qtablewidgetitem8 = self.tableWidget_3.horizontalHeaderItem(0)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"\u0422\u0438\u043f \u0431\u0438\u043b\u0435\u0442\u0430", None));
        ___qtablewidgetitem9 = self.tableWidget_3.horizontalHeaderItem(1)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0441\u0435\u0433\u043e", None));
        ___qtablewidgetitem10 = self.tableWidget_3.horizontalHeaderItem(2)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"1 \u0447.", None));
        ___qtablewidgetitem11 = self.tableWidget_3.horizontalHeaderItem(3)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"2 \u0447.", None));
        ___qtablewidgetitem12 = self.tableWidget_3.horizontalHeaderItem(4)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainWindow", u"3 \u0447.", None));
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", u"\u041f\u0435\u0440\u0438\u043e\u0434 \u0432\u0440\u0435\u043c\u0435\u043d\u0438", None))
        self.pushButton_17.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u0440\u043e\u0434\u0430\u0436", None))
        ___qtablewidgetitem13 = self.tableWidget_4.horizontalHeaderItem(0)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MainWindow", u"\u0418\u043c\u044f \u041f\u041a", None));
        ___qtablewidgetitem14 = self.tableWidget_4.horizontalHeaderItem(1)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MainWindow", u"\u0411\u0430\u043d\u043a\u043e\u0432\u0441\u043a\u0430\u044f \u043a\u0430\u0440\u0442\u0430", None));
        ___qtablewidgetitem15 = self.tableWidget_4.horizontalHeaderItem(2)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u043b\u0438\u0447\u043d\u044b\u0435", None));
        ___qtablewidgetitem16 = self.tableWidget_4.horizontalHeaderItem(3)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0441\u0435\u0433\u043e", None));
        self.pushButton_18.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u0447\u0435\u0442 \u043a\u0430\u0441\u0441\u0438\u0440\u0430", None))
        self.pushButton_19.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u0447\u0435\u0442\u0430\n"
" \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440\u0430", None))
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

