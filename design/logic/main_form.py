from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMenuBar,
    QPushButton,
    QRadioButton,
    QStatusBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(Qt.ApplicationModal)
        MainWindow.resize(1718, 1080)
        MainWindow.setMaximumSize(QSize(1920, 1080))
        self.action = QAction(MainWindow)
        self.action.setObjectName("action")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setGeometry(QRect(10, 10, 1901, 1080))
        self.tabWidget.setMaximumSize(QSize(1920, 1080))
        self.visitors = QWidget()
        self.visitors.setObjectName("visitors")
        self.label = QLabel(self.visitors)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(220, 10, 51, 31))
        self.line = QFrame(self.visitors)
        self.line.setObjectName("line")
        self.line.setGeometry(QRect(200, 10, 20, 31))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.pushButton_2 = QPushButton(self.visitors)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setGeometry(QRect(0, 10, 94, 31))
        self.pushButton_3 = QPushButton(self.visitors)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setGeometry(QRect(100, 10, 94, 31))
        self.lineEdit_2 = QLineEdit(self.visitors)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setGeometry(QRect(270, 10, 391, 31))
        self.comboBox_3 = QComboBox(self.visitors)
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_3.setGeometry(QRect(670, 10, 171, 31))
        self.pushButton = QPushButton(self.visitors)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QRect(850, 10, 94, 31))
        self.tableWidget = QTableWidget(self.visitors)
        if self.tableWidget.columnCount() < 9:
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
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setGeometry(QRect(0, 50, 1701, 941))
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabWidget.addTab(self.visitors, "")
        self.sales = QWidget()
        self.sales.setObjectName("sales")
        self.line_2 = QFrame(self.sales)
        self.line_2.setObjectName("line_2")
        self.line_2.setGeometry(QRect(100, 10, 20, 31))
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.tableWidget_2 = QTableWidget(self.sales)
        if self.tableWidget_2.columnCount() < 8:
            self.tableWidget_2.setColumnCount(8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(0, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(1, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(2, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(3, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(4, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(5, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(6, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(7, __qtablewidgetitem16)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setGeometry(QRect(0, 50, 1901, 941))
        self.tableWidget_2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.groupBox_3 = QGroupBox(self.sales)
        self.groupBox_3.setObjectName("groupBox_3")
        self.groupBox_3.setGeometry(QRect(120, 0, 551, 41))
        self.radioButton = QRadioButton(self.groupBox_3)
        self.radioButton.setObjectName("radioButton")
        self.radioButton.setGeometry(QRect(0, 20, 89, 20))
        self.radioButton.setChecked(True)
        self.radioButton_2 = QRadioButton(self.groupBox_3)
        self.radioButton_2.setObjectName("radioButton_2")
        self.radioButton_2.setGeometry(QRect(80, 20, 89, 20))
        self.radioButton_3 = QRadioButton(self.groupBox_3)
        self.radioButton_3.setObjectName("radioButton_3")
        self.radioButton_3.setGeometry(QRect(150, 20, 61, 20))
        self.pushButton_13 = QPushButton(self.groupBox_3)
        self.pushButton_13.setObjectName("pushButton_13")
        self.pushButton_13.setGeometry(QRect(450, 10, 94, 28))
        self.radioButton_7 = QRadioButton(self.groupBox_3)
        self.radioButton_7.setObjectName("radioButton_7")
        self.radioButton_7.setGeometry(QRect(220, 20, 41, 20))
        self.dateEdit_3 = QDateEdit(self.groupBox_3)
        self.dateEdit_3.setObjectName("dateEdit_3")
        self.dateEdit_3.setGeometry(QRect(270, 20, 95, 22))
        self.dateEdit_3.setCalendarPopup(True)
        self.checkBox = QCheckBox(self.groupBox_3)
        self.checkBox.setObjectName("checkBox")
        self.checkBox.setGeometry(QRect(370, 20, 75, 20))
        self.pushButton_23 = QPushButton(self.sales)
        self.pushButton_23.setObjectName("pushButton_23")
        self.pushButton_23.setGeometry(QRect(0, 10, 111, 31))
        font = QFont()
        font.setBold(True)
        self.pushButton_23.setFont(font)
        self.tabWidget.addTab(self.sales, "")
        self.add_services = QWidget()
        self.add_services.setObjectName("add_services")
        self.groupBox_4 = QGroupBox(self.add_services)
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setGeometry(QRect(120, 0, 321, 41))
        self.radioButton_4 = QRadioButton(self.groupBox_4)
        self.radioButton_4.setObjectName("radioButton_4")
        self.radioButton_4.setGeometry(QRect(0, 20, 89, 20))
        self.radioButton_4.setChecked(True)
        self.radioButton_5 = QRadioButton(self.groupBox_4)
        self.radioButton_5.setObjectName("radioButton_5")
        self.radioButton_5.setGeometry(QRect(80, 20, 89, 20))
        self.radioButton_6 = QRadioButton(self.groupBox_4)
        self.radioButton_6.setObjectName("radioButton_6")
        self.radioButton_6.setGeometry(QRect(150, 20, 61, 20))
        self.pushButton_14 = QPushButton(self.groupBox_4)
        self.pushButton_14.setObjectName("pushButton_14")
        self.pushButton_14.setGeometry(QRect(220, 10, 94, 28))
        self.tableWidget_5 = QTableWidget(self.add_services)
        if self.tableWidget_5.columnCount() < 8:
            self.tableWidget_5.setColumnCount(8)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(0, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(1, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(2, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(3, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(4, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(5, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(6, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        self.tableWidget_5.setHorizontalHeaderItem(7, __qtablewidgetitem24)
        self.tableWidget_5.setObjectName("tableWidget_5")
        self.tableWidget_5.setGeometry(QRect(0, 50, 1901, 941))
        self.tableWidget_5.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pushButton_20 = QPushButton(self.add_services)
        self.pushButton_20.setObjectName("pushButton_20")
        self.pushButton_20.setGeometry(QRect(0, 10, 94, 31))
        self.pushButton_20.setFont(font)
        self.line_3 = QFrame(self.add_services)
        self.line_3.setObjectName("line_3")
        self.line_3.setGeometry(QRect(100, 10, 20, 31))
        self.line_3.setFrameShape(QFrame.VLine)
        self.line_3.setFrameShadow(QFrame.Sunken)
        self.tabWidget.addTab(self.add_services, "")
        self.statistic = QWidget()
        self.statistic.setObjectName("statistic")
        self.groupBox_5 = QGroupBox(self.statistic)
        self.groupBox_5.setObjectName("groupBox_5")
        self.groupBox_5.setGeometry(QRect(-10, 70, 600, 350))
        self.tableWidget_3 = QTableWidget(self.groupBox_5)
        if self.tableWidget_3.columnCount() < 8:
            self.tableWidget_3.setColumnCount(8)
        __qtablewidgetitem25 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(0, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(1, __qtablewidgetitem26)
        __qtablewidgetitem27 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(2, __qtablewidgetitem27)
        __qtablewidgetitem28 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(3, __qtablewidgetitem28)
        __qtablewidgetitem29 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(4, __qtablewidgetitem29)
        __qtablewidgetitem30 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(5, __qtablewidgetitem30)
        __qtablewidgetitem31 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(6, __qtablewidgetitem31)
        __qtablewidgetitem32 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(7, __qtablewidgetitem32)
        self.tableWidget_3.setObjectName("tableWidget_3")
        self.tableWidget_3.setGeometry(QRect(10, 20, 581, 321))
        self.tableWidget_3.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_3.horizontalHeader().setDefaultSectionSize(115)
        self.groupBox_7 = QGroupBox(self.statistic)
        self.groupBox_7.setObjectName("groupBox_7")
        self.groupBox_7.setGeometry(QRect(0, 10, 321, 61))
        self.layoutWidget = QWidget(self.groupBox_7)
        self.layoutWidget.setObjectName("layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 20, 299, 26))
        self.horizontalLayout_2 = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.dateEdit_2 = QDateEdit(self.layoutWidget)
        self.dateEdit_2.setObjectName("dateEdit_2")
        self.dateEdit_2.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.dateEdit_2)

        self.dateEdit = QDateEdit(self.layoutWidget)
        self.dateEdit.setObjectName("dateEdit")
        self.dateEdit.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.dateEdit)

        self.pushButton_17 = QPushButton(self.layoutWidget)
        self.pushButton_17.setObjectName("pushButton_17")

        self.horizontalLayout_2.addWidget(self.pushButton_17)

        self.groupBox_6 = QGroupBox(self.statistic)
        self.groupBox_6.setObjectName("groupBox_6")
        self.groupBox_6.setGeometry(QRect(600, 70, 1091, 350))
        self.tableWidget_4 = QTableWidget(self.groupBox_6)
        if self.tableWidget_4.columnCount() < 7:
            self.tableWidget_4.setColumnCount(7)
        __qtablewidgetitem33 = QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(0, __qtablewidgetitem33)
        __qtablewidgetitem34 = QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(1, __qtablewidgetitem34)
        __qtablewidgetitem35 = QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(2, __qtablewidgetitem35)
        __qtablewidgetitem36 = QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(3, __qtablewidgetitem36)
        __qtablewidgetitem37 = QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(4, __qtablewidgetitem37)
        __qtablewidgetitem38 = QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(5, __qtablewidgetitem38)
        __qtablewidgetitem39 = QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(6, __qtablewidgetitem39)
        self.tableWidget_4.setObjectName("tableWidget_4")
        self.tableWidget_4.setGeometry(QRect(10, 20, 1071, 321))
        self.tableWidget_4.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_4.horizontalHeader().setDefaultSectionSize(140)
        self.pushButton_18 = QPushButton(self.statistic)
        self.pushButton_18.setObjectName("pushButton_18")
        self.pushButton_18.setGeometry(QRect(320, 20, 111, 51))
        font1 = QFont()
        font1.setBold(False)
        self.pushButton_18.setFont(font1)
        self.pushButton_19 = QPushButton(self.statistic)
        self.pushButton_19.setObjectName("pushButton_19")
        self.pushButton_19.setGeometry(QRect(440, 20, 111, 51))
        self.pushButton_19.setFont(font1)
        self.tabWidget.addTab(self.statistic, "")
        self.cashbox = QWidget()
        self.cashbox.setObjectName("cashbox")
        self.groupBox = QGroupBox(self.cashbox)
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setGeometry(QRect(10, 20, 401, 411))
        self.pushButton_11 = QPushButton(self.groupBox)
        self.pushButton_11.setObjectName("pushButton_11")
        self.pushButton_11.setGeometry(QRect(140, 90, 121, 61))
        self.pushButton_11.setAcceptDrops(False)
        self.pushButton_11.setAutoExclusive(True)
        self.pushButton_11.setFlat(False)
        self.pushButton_8 = QPushButton(self.groupBox)
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_8.setGeometry(QRect(270, 20, 121, 61))
        self.pushButton_8.setAcceptDrops(False)
        self.pushButton_8.setAutoExclusive(True)
        self.pushButton_8.setFlat(False)
        self.pushButton_6 = QPushButton(self.groupBox)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.setGeometry(QRect(10, 90, 121, 61))
        self.pushButton_5 = QPushButton(self.groupBox)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setGeometry(QRect(10, 20, 121, 61))
        self.pushButton_9 = QPushButton(self.groupBox)
        self.pushButton_9.setObjectName("pushButton_9")
        self.pushButton_9.setGeometry(QRect(270, 90, 121, 61))
        self.pushButton_9.setAcceptDrops(False)
        self.pushButton_9.setAutoExclusive(True)
        self.pushButton_9.setFlat(False)
        self.pushButton_10 = QPushButton(self.groupBox)
        self.pushButton_10.setObjectName("pushButton_10")
        self.pushButton_10.setGeometry(QRect(10, 160, 121, 61))
        self.pushButton_10.setAcceptDrops(False)
        self.pushButton_10.setAutoExclusive(True)
        self.pushButton_10.setFlat(False)
        self.pushButton_7 = QPushButton(self.groupBox)
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_7.setGeometry(QRect(140, 20, 121, 61))
        self.pushButton_7.setAcceptDrops(False)
        self.pushButton_7.setAutoExclusive(True)
        self.pushButton_7.setFlat(False)
        self.pushButton_15 = QPushButton(self.groupBox)
        self.pushButton_15.setObjectName("pushButton_15")
        self.pushButton_15.setGeometry(QRect(140, 160, 121, 61))
        self.pushButton_15.setAcceptDrops(False)
        self.pushButton_15.setAutoExclusive(True)
        self.pushButton_15.setFlat(False)
        self.pushButton_24 = QPushButton(self.groupBox)
        self.pushButton_24.setObjectName("pushButton_24")
        self.pushButton_24.setGeometry(QRect(140, 280, 121, 61))
        self.pushButton_24.setAcceptDrops(False)
        self.pushButton_24.setAutoExclusive(True)
        self.pushButton_24.setFlat(False)
        self.pushButton_25 = QPushButton(self.groupBox)
        self.pushButton_25.setObjectName("pushButton_25")
        self.pushButton_25.setGeometry(QRect(270, 280, 121, 61))
        self.pushButton_25.setAcceptDrops(False)
        self.pushButton_25.setAutoExclusive(True)
        self.pushButton_25.setFlat(False)
        self.line_4 = QFrame(self.groupBox)
        self.line_4.setObjectName("line_4")
        self.line_4.setGeometry(QRect(7, 230, 381, 20))
        self.line_4.setFrameShape(QFrame.HLine)
        self.line_4.setFrameShadow(QFrame.Sunken)
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(10, 250, 151, 16))
        self.lineEdit = QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setGeometry(QRect(10, 308, 113, 31))
        self.pushButton_26 = QPushButton(self.groupBox)
        self.pushButton_26.setObjectName("pushButton_26")
        self.pushButton_26.setGeometry(QRect(140, 350, 121, 61))
        self.pushButton_26.setAcceptDrops(False)
        self.pushButton_26.setAutoExclusive(True)
        self.pushButton_26.setFlat(False)
        self.groupBox_2 = QGroupBox(self.cashbox)
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setGeometry(QRect(420, 20, 401, 411))
        self.pushButton_16 = QPushButton(self.groupBox_2)
        self.pushButton_16.setObjectName("pushButton_16")
        self.pushButton_16.setGeometry(QRect(10, 20, 121, 61))
        self.pushButton_16.setAcceptDrops(False)
        self.pushButton_16.setAutoExclusive(True)
        self.pushButton_16.setFlat(False)
        self.pushButton_21 = QPushButton(self.groupBox_2)
        self.pushButton_21.setObjectName("pushButton_21")
        self.pushButton_21.setGeometry(QRect(140, 20, 121, 61))
        self.pushButton_21.setAcceptDrops(False)
        self.pushButton_21.setAutoExclusive(True)
        self.pushButton_21.setFlat(False)
        self.pushButton_22 = QPushButton(self.groupBox_2)
        self.pushButton_22.setObjectName("pushButton_22")
        self.pushButton_22.setGeometry(QRect(270, 20, 121, 61))
        self.pushButton_22.setAcceptDrops(False)
        self.pushButton_22.setAutoExclusive(True)
        self.pushButton_22.setFlat(False)
        self.pushButton_12 = QPushButton(self.groupBox_2)
        self.pushButton_12.setObjectName("pushButton_12")
        self.pushButton_12.setGeometry(QRect(10, 90, 121, 61))
        self.pushButton_12.setAcceptDrops(False)
        self.pushButton_12.setAutoExclusive(True)
        self.pushButton_12.setFlat(False)
        self.pushButton_27 = QPushButton(self.groupBox_2)
        self.pushButton_27.setObjectName("pushButton_27")
        self.pushButton_27.setGeometry(QRect(140, 90, 121, 61))
        self.pushButton_27.setAcceptDrops(False)
        self.pushButton_27.setAutoExclusive(True)
        self.pushButton_27.setFlat(False)
        self.pushButton_28 = QPushButton(self.groupBox_2)
        self.pushButton_28.setObjectName("pushButton_28")
        self.pushButton_28.setGeometry(QRect(270, 90, 121, 61))
        self.pushButton_28.setAcceptDrops(False)
        self.pushButton_28.setAutoExclusive(True)
        self.pushButton_28.setFlat(False)
        self.tabWidget.addTab(self.cashbox, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1718, 22))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.action)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "PyMASL", None)
        )
        self.action.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u041e \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0435",
                None,
            )
        )
        self.label.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0424\u0438\u043b\u044c\u0442\u0440:", None
            )
        )
        self.pushButton_2.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None
            )
        )
        self.pushButton_3.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c", None
            )
        )
        self.comboBox_3.setItemText(
            0,
            QCoreApplication.translate(
                "MainWindow",
                "\u0424\u0430\u043c\u0438\u043b\u0438\u044f+\u0418\u043c\u044f",
                None,
            ),
        )
        self.comboBox_3.setItemText(
            1,
            QCoreApplication.translate(
                "MainWindow", "\u0424\u0430\u043c\u0438\u043b\u0438\u044f", None
            ),
        )
        self.comboBox_3.setItemText(
            2,
            QCoreApplication.translate(
                "MainWindow",
                "\u2116 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0430",
                None,
            ),
        )
        self.comboBox_3.setItemText(
            3,
            QCoreApplication.translate(
                "MainWindow", "\u0418\u043d\u0432\u0430\u043b\u0438\u0434", None
            ),
        )
        self.comboBox_3.setItemText(
            4,
            QCoreApplication.translate(
                "MainWindow",
                "\u041c\u043d\u043e\u0433\u043e\u0434\u0435\u0442\u043d\u044b\u0439",
                None,
            ),
        )

        self.pushButton.setText(
            QCoreApplication.translate(
                "MainWindow", "\u041d\u0430\u0439\u0442\u0438", None
            )
        )
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0424\u0430\u043c\u0438\u043b\u0438\u044f", None
            )
        )
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("MainWindow", "\u0418\u043c\u044f", None)
        )
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate(
                "MainWindow", "\u041e\u0442\u0447\u0435\u0441\u0442\u0432\u043e", None
            )
        )
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0414\u0430\u0442\u0430 \u0440\u043e\u0436\u0434.", None
            )
        )
        ___qtablewidgetitem4 = self.tableWidget.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(
            QCoreApplication.translate("MainWindow", "\u041f\u043e\u043b", None)
        )
        ___qtablewidgetitem5 = self.tableWidget.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0422\u0435\u043b\u0435\u0444\u043e\u043d", None
            )
        )
        ___qtablewidgetitem6 = self.tableWidget.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(
            QCoreApplication.translate("MainWindow", "Email", None)
        )
        ___qtablewidgetitem7 = self.tableWidget.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(
            QCoreApplication.translate("MainWindow", "\u0424\u043b\u0430\u0433", None)
        )
        ___qtablewidgetitem8 = self.tableWidget.horizontalHeaderItem(8)
        ___qtablewidgetitem8.setText(
            QCoreApplication.translate("MainWindow", "id", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.visitors),
            QCoreApplication.translate(
                "MainWindow",
                "\u041f\u043e\u0441\u0435\u0442\u0438\u0442\u0435\u043b\u0438",
                None,
            ),
        )
        ___qtablewidgetitem9 = self.tableWidget_2.horizontalHeaderItem(0)
        ___qtablewidgetitem9.setText(
            QCoreApplication.translate(
                "MainWindow", "N \u043f\u0440\u043e\u0434\u0430\u0436\u0438", None
            )
        )
        ___qtablewidgetitem10 = self.tableWidget_2.horizontalHeaderItem(1)
        ___qtablewidgetitem10.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0424\u0430\u043c\u0438\u043b\u0438\u044f \u043a\u043b\u0438\u0435\u043d\u0442\u0430",
                None,
            )
        )
        ___qtablewidgetitem11 = self.tableWidget_2.horizontalHeaderItem(2)
        ___qtablewidgetitem11.setText(
            QCoreApplication.translate("MainWindow", "\u0426\u0435\u043d\u0430", None)
        )
        ___qtablewidgetitem12 = self.tableWidget_2.horizontalHeaderItem(3)
        ___qtablewidgetitem12.setText(
            QCoreApplication.translate("MainWindow", "\u0414\u0430\u0442\u0430", None)
        )
        ___qtablewidgetitem13 = self.tableWidget_2.horizontalHeaderItem(4)
        ___qtablewidgetitem13.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0421\u0442\u0430\u0442\u0443\u0441", None
            )
        )
        ___qtablewidgetitem14 = self.tableWidget_2.horizontalHeaderItem(5)
        ___qtablewidgetitem14.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0421\u043a\u0438\u0434\u043a\u0430", None
            )
        )
        ___qtablewidgetitem15 = self.tableWidget_2.horizontalHeaderItem(6)
        ___qtablewidgetitem15.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0418\u043c\u044f \u041f\u041a", None
            )
        )
        ___qtablewidgetitem16 = self.tableWidget_2.horizontalHeaderItem(7)
        ___qtablewidgetitem16.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0422\u0438\u043f \u043e\u043f\u043b\u0430\u0442\u044b",
                None,
            )
        )
        self.groupBox_3.setTitle(
            QCoreApplication.translate(
                "MainWindow",
                "\u0424\u0438\u043b\u044c\u0442\u0440 \u0437\u0430 \u043f\u0435\u0440\u0438\u043e\u0434",
                None,
            )
        )
        self.radioButton.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0441\u0435\u0433\u043e\u0434\u043d\u044f", None
            )
        )
        self.radioButton_2.setText(
            QCoreApplication.translate("MainWindow", "3 \u0434\u043d\u044f", None)
        )
        self.radioButton_3.setText(
            QCoreApplication.translate("MainWindow", "7 \u0434\u043d\u0435\u0439", None)
        )
        self.pushButton_13.setText(
            QCoreApplication.translate(
                "MainWindow", "\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c", None
            )
        )
        self.radioButton_7.setText(
            QCoreApplication.translate("MainWindow", "\u0434\u0430\u0442\u0430", None)
        )
        self.checkBox.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0412\u043e\u0437\u0432\u0440\u0430\u0442\u044b", None
            )
        )
        self.pushButton_23.setText(
            QCoreApplication.translate(
                "MainWindow", "\u041d\u043e\u0432\u0430\u044f", None
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.sales),
            QCoreApplication.translate(
                "MainWindow", "\u041f\u0440\u043e\u0434\u0430\u0436\u0438", None
            ),
        )
        self.groupBox_4.setTitle(
            QCoreApplication.translate(
                "MainWindow",
                "\u0424\u0438\u043b\u044c\u0442\u0440 \u0437\u0430 \u043f\u0435\u0440\u0438\u043e\u0434",
                None,
            )
        )
        self.radioButton_4.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0441\u0435\u0433\u043e\u0434\u043d\u044f", None
            )
        )
        self.radioButton_5.setText(
            QCoreApplication.translate("MainWindow", "3 \u0434\u043d\u044f", None)
        )
        self.radioButton_6.setText(
            QCoreApplication.translate("MainWindow", "7 \u0434\u043d\u0435\u0439", None)
        )
        self.pushButton_14.setText(
            QCoreApplication.translate(
                "MainWindow", "\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c", None
            )
        )
        ___qtablewidgetitem17 = self.tableWidget_5.horizontalHeaderItem(0)
        ___qtablewidgetitem17.setText(
            QCoreApplication.translate(
                "MainWindow", "N \u043f\u0440\u043e\u0434\u0430\u0436\u0438", None
            )
        )
        ___qtablewidgetitem18 = self.tableWidget_5.horizontalHeaderItem(1)
        ___qtablewidgetitem18.setText(
            QCoreApplication.translate(
                "MainWindow", "N \u043a\u043b\u0438\u0435\u043d\u0442\u0430", None
            )
        )
        ___qtablewidgetitem19 = self.tableWidget_5.horizontalHeaderItem(2)
        ___qtablewidgetitem19.setText(
            QCoreApplication.translate("MainWindow", "\u0426\u0435\u043d\u0430", None)
        )
        ___qtablewidgetitem20 = self.tableWidget_5.horizontalHeaderItem(3)
        ___qtablewidgetitem20.setText(
            QCoreApplication.translate("MainWindow", "\u0414\u0430\u0442\u0430", None)
        )
        ___qtablewidgetitem21 = self.tableWidget_5.horizontalHeaderItem(4)
        ___qtablewidgetitem21.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0421\u0442\u0430\u0442\u0443\u0441", None
            )
        )
        ___qtablewidgetitem22 = self.tableWidget_5.horizontalHeaderItem(5)
        ___qtablewidgetitem22.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0421\u043a\u0438\u0434\u043a\u0430", None
            )
        )
        ___qtablewidgetitem23 = self.tableWidget_5.horizontalHeaderItem(6)
        ___qtablewidgetitem23.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0418\u043c\u044f \u041f\u041a", None
            )
        )
        ___qtablewidgetitem24 = self.tableWidget_5.horizontalHeaderItem(7)
        ___qtablewidgetitem24.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0422\u0438\u043f \u043e\u043f\u043b\u0430\u0442\u044b",
                None,
            )
        )
        self.pushButton_20.setText(
            QCoreApplication.translate(
                "MainWindow", "\u041d\u043e\u0432\u0430\u044f", None
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.add_services),
            QCoreApplication.translate(
                "MainWindow",
                "\u0414\u043e\u043f.\u0443\u0441\u043b\u0443\u0433\u0438",
                None,
            ),
        )
        self.groupBox_5.setTitle(
            QCoreApplication.translate(
                "MainWindow",
                "\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e\u0441\u0435\u0449\u0435\u043d\u0438\u0439",
                None,
            )
        )
        ___qtablewidgetitem25 = self.tableWidget_3.horizontalHeaderItem(0)
        ___qtablewidgetitem25.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0422\u0438\u043f \u0431\u0438\u043b\u0435\u0442\u0430",
                None,
            )
        )
        ___qtablewidgetitem26 = self.tableWidget_3.horizontalHeaderItem(1)
        ___qtablewidgetitem26.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0412\u0441\u0435\u0433\u043e", None
            )
        )
        ___qtablewidgetitem27 = self.tableWidget_3.horizontalHeaderItem(2)
        ___qtablewidgetitem27.setText(
            QCoreApplication.translate("MainWindow", "1 \u0447.", None)
        )
        ___qtablewidgetitem28 = self.tableWidget_3.horizontalHeaderItem(3)
        ___qtablewidgetitem28.setText(
            QCoreApplication.translate("MainWindow", "2 \u0447.", None)
        )
        ___qtablewidgetitem29 = self.tableWidget_3.horizontalHeaderItem(4)
        ___qtablewidgetitem29.setText(
            QCoreApplication.translate("MainWindow", "3 \u0447.", None)
        )
        ___qtablewidgetitem30 = self.tableWidget_3.horizontalHeaderItem(5)
        ___qtablewidgetitem30.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0441\u0443\u043c\u043c\u0430 1 \u0447.", None
            )
        )
        ___qtablewidgetitem31 = self.tableWidget_3.horizontalHeaderItem(6)
        ___qtablewidgetitem31.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0441\u0443\u043c\u043c\u0430 2 \u0447.", None
            )
        )
        ___qtablewidgetitem32 = self.tableWidget_3.horizontalHeaderItem(7)
        ___qtablewidgetitem32.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0441\u0443\u043c\u043c\u0430 3 \u0447.", None
            )
        )
        self.groupBox_7.setTitle(
            QCoreApplication.translate(
                "MainWindow",
                "\u041f\u0435\u0440\u0438\u043e\u0434 \u0432\u0440\u0435\u043c\u0435\u043d\u0438",
                None,
            )
        )
        self.pushButton_17.setText(
            QCoreApplication.translate(
                "MainWindow", "\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c", None
            )
        )
        self.groupBox_6.setTitle(
            QCoreApplication.translate(
                "MainWindow",
                "\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u0440\u043e\u0434\u0430\u0436",
                None,
            )
        )
        ___qtablewidgetitem33 = self.tableWidget_4.horizontalHeaderItem(0)
        ___qtablewidgetitem33.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0418\u043c\u044f \u041f\u041a", None
            )
        )
        ___qtablewidgetitem34 = self.tableWidget_4.horizontalHeaderItem(1)
        ___qtablewidgetitem34.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0411\u0430\u043d\u043a\u043e\u0432\u0441\u043a\u0430\u044f \u043a\u0430\u0440\u0442\u0430",
                None,
            )
        )
        ___qtablewidgetitem35 = self.tableWidget_4.horizontalHeaderItem(2)
        ___qtablewidgetitem35.setText(
            QCoreApplication.translate(
                "MainWindow", "\u041d\u0430\u043b\u0438\u0447\u043d\u044b\u0435", None
            )
        )
        ___qtablewidgetitem36 = self.tableWidget_4.horizontalHeaderItem(3)
        ___qtablewidgetitem36.setText(
            QCoreApplication.translate(
                "MainWindow", "\u0412\u0441\u0435\u0433\u043e", None
            )
        )
        ___qtablewidgetitem37 = self.tableWidget_4.horizontalHeaderItem(4)
        ___qtablewidgetitem37.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0412\u043e\u0437\u0432\u0440\u0430\u0442 \u0431\u0430\u043d\u043a",
                None,
            )
        )
        ___qtablewidgetitem38 = self.tableWidget_4.horizontalHeaderItem(5)
        ___qtablewidgetitem38.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0412\u043e\u0437\u0432\u0440\u0430\u0442 \u043d\u0430\u043b\u0438\u0447\u043d\u044b\u0435",
                None,
            )
        )
        ___qtablewidgetitem39 = self.tableWidget_4.horizontalHeaderItem(6)
        ___qtablewidgetitem39.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0412\u0441\u0435\u0433\u043e \u0432\u043e\u0437\u0432\u0440\u0430\u0442\u043e\u0432",
                None,
            )
        )
        self.pushButton_18.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u041e\u0442\u0447\u0435\u0442 \u043a\u0430\u0441\u0441\u0438\u0440\u0430",
                None,
            )
        )
        self.pushButton_19.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u041e\u0442\u0447\u0435\u0442\u0430\n"
                " \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440\u0430",
                None,
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.statistic),
            QCoreApplication.translate(
                "MainWindow",
                "\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430",
                None,
            ),
        )
        self.groupBox.setTitle(
            QCoreApplication.translate(
                "MainWindow",
                "\u041e\u043f\u0435\u0440\u0430\u0446\u0438\u0438 \u0441 \u041a\u041a\u0422",
                None,
            )
        )
        self.pushButton_11.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u041a\u043e\u043f\u0438\u044f \u043f\u043e\u0441\u043b.\n"
                "\u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430",
                None,
            )
        )
        self.pushButton_8.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e\n"
                "\u041a\u041a\u0422",
                None,
            )
        )
        self.pushButton_6.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u041e\u0442\u0447\u0435\u0442 \u0441 \u0433\u0430\u0448\u0435\u043d\u0438\u0435\u043c\n"
                "(z-\u043e\u0442\u0447\u0435\u0442)",
                None,
            )
        )
        self.pushButton_5.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u041e\u0442\u0447\u0435\u0442 \u0431\u0435\u0437 \u0433\u0430\u0448\u0435\u043d\u0438\u044f\n"
                "(x-\u043e\u0442\u0447\u0435\u0442)",
                None,
            )
        )
        self.pushButton_9.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f\n"
                " \u041a\u041a\u0422",
                None,
            )
        )
        self.pushButton_10.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0421\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435\n"
                "\u043a\u0430\u0441\u0441\u043e\u0432\u043e\u0439 \u0441\u043c\u0435\u043d\u044b",
                None,
            )
        )
        self.pushButton_7.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0421\u0442\u0430\u0442\u0443\u0441\n"
                " \u0438\u043d\u0444\u043e\u0440\u043c.\n"
                "\u043e\u0431\u043c\u0435\u043d\u0430 \u0441 \u041e\u0424\u0414",
                None,
            )
        )
        self.pushButton_15.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0414\u043e\u043f\u0435\u0447\u0430\u0442\u0430\u0442\u044c\n"
                "\u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442",
                None,
            )
        )
        self.pushButton_24.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0412\u043d\u0435\u0441\u0435\u043d\u0438\u0435\n"
                "\u0434\u0435\u043d\u0435\u0433",
                None,
            )
        )
        self.pushButton_25.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0412\u044b\u043f\u043b\u0430\u0442\u0430\n"
                "\u0434\u0435\u043d\u0435\u0433",
                None,
            )
        )
        self.label_2.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u041d\u0435\u0444\u0438\u0441\u043a\u0430\u043b\u044c\u043d\u044b\u0435 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0438",
                None,
            )
        )
        self.lineEdit.setText("")
        self.pushButton_26.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c \u0431\u0430\u043b\u0430\u043d\u0441\n"
                "\u043a\u0430\u0441\u0441\u044b",
                None,
            )
        )
        self.groupBox_2.setTitle(
            QCoreApplication.translate(
                "MainWindow",
                "\u041e\u043f\u0435\u0440\u0430\u0446\u0438\u0438 \u0441 \u0431\u0430\u043d\u043a\u043e\u0432\u0441\u043a\u0438\u043c \u0442\u0435\u0440\u043c\u0438\u043d\u0430\u043b\u043e\u043c",
                None,
            )
        )
        self.pushButton_16.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0421\u0432\u0435\u0440\u043a\u0430 \u0438\u0442\u043e\u0433\u043e\u0432\n"
                "(\u0437\u0430\u043a\u0440\u044b\u0442\u0438\u0435\n"
                "\u0431\u0430\u043d\u043a\u043e\u0432\u0441\u043a\u043e\u0439 \u0441\u043c\u0435\u043d\u044b)",
                None,
            )
        )
        self.pushButton_21.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0421\u0432\u043e\u0434\u043d\u044b\u0439\n" "\u0447\u0435\u043a",
                None,
            )
        )
        self.pushButton_22.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u041a\u043e\u043d\u0442\u0440\u043e\u043b\u044c\u043d\u0430\u044f\n"
                "\u043b\u0435\u043d\u0442\u0430",
                None,
            )
        )
        self.pushButton_12.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u041a\u043e\u043f\u0438\u044f\n"
                "\u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0433\u043e \u0447\u0435\u043a\u0430",
                None,
            )
        )
        self.pushButton_27.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u0412\u044b\u0437\u043e\u0432\n" "\u043c\u0435\u043d\u044e",
                None,
            )
        )
        self.pushButton_28.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\u041f\u0435\u0447\u0430\u0442\u044c \u0440\u0430\u043d\u0435\u0435\n"
                "\u043f\u043e\u0434\u0433\u043e\u0442\u043e\u0432\u043b\u0435\u043d\u043d\u043e\u0433\u043e\n"
                "\u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430",
                None,
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.cashbox),
            QCoreApplication.translate(
                "MainWindow", "\u041a\u0430\u0441\u0441\u0430", None
            ),
        )
        self.menu.setTitle(
            QCoreApplication.translate("MainWindow", "\u041c\u0435\u043d\u044e", None)
        )

    # retranslateUi
