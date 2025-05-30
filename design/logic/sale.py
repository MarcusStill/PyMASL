from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFrame,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)


class Ui_Dialog_Sale(object):
    def setupUi(self, Dialog_Sale):
        if not Dialog_Sale.objectName():
            Dialog_Sale.setObjectName("Dialog_Sale")
        Dialog_Sale.setWindowModality(Qt.ApplicationModal)
        Dialog_Sale.resize(963, 787)
        self.groupBox = QGroupBox(Dialog_Sale)
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setGeometry(QRect(0, 0, 621, 431))
        self.lineEdit = QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setGeometry(QRect(300, 30, 201, 30))
        self.lineEdit.setMaximumSize(QSize(261, 30))
        self.pushButton_2 = QPushButton(self.groupBox)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setGeometry(QRect(10, 17, 61, 41))
        font = QFont()
        font.setPointSize(9)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setAutoDefault(False)
        self.comboBox_4 = QComboBox(self.groupBox)
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.setObjectName("comboBox_4")
        self.comboBox_4.setGeometry(QRect(200, 30, 91, 30))
        self.comboBox_4.setMaximumSize(QSize(91, 30))
        self.tableWidget = QTableWidget(self.groupBox)
        if self.tableWidget.columnCount() < 6:
            self.tableWidget.setColumnCount(6)
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
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setGeometry(QRect(10, 60, 611, 371))
        font1 = QFont()
        font1.setPointSize(11)
        self.tableWidget.setFont(font1)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pushButton = QPushButton(self.groupBox)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QRect(510, 17, 51, 41))
        self.pushButton.setAutoDefault(True)
        self.pushButton_9 = QPushButton(self.groupBox)
        self.pushButton_9.setObjectName("pushButton_9")
        self.pushButton_9.setGeometry(QRect(70, 17, 61, 41))
        self.pushButton_11 = QPushButton(self.groupBox)
        self.pushButton_11.setObjectName("pushButton_11")
        self.pushButton_11.setGeometry(QRect(130, 17, 61, 41))
        self.pushButton_12 = QPushButton(self.groupBox)
        self.pushButton_12.setObjectName("pushButton_12")
        self.pushButton_12.setGeometry(QRect(560, 17, 61, 41))
        self.pushButton_12.setAutoDefault(False)
        self.line = QFrame(Dialog_Sale)
        self.line.setObjectName("line")
        self.line.setGeometry(QRect(620, -10, 20, 801))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line_2 = QFrame(Dialog_Sale)
        self.line_2.setObjectName("line_2")
        self.line_2.setGeometry(QRect(10, 430, 951, 20))
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.tableWidget_2 = QTableWidget(Dialog_Sale)
        if self.tableWidget_2.columnCount() < 9:
            self.tableWidget_2.setColumnCount(9)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(2, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(3, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(4, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(5, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(6, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(7, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(8, __qtablewidgetitem14)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setGeometry(QRect(10, 450, 611, 331))
        self.tableWidget_2.setFont(font1)
        self.tableWidget_2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_2.horizontalHeader().setDefaultSectionSize(100)
        self.label_2 = QLabel(Dialog_Sale)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(780, 450, 51, 20))
        font2 = QFont()
        font2.setPointSize(13)
        font2.setBold(True)
        self.label_2.setFont(font2)
        self.pushButton_3 = QPushButton(Dialog_Sale)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setGeometry(QRect(640, 670, 80, 52))
        font3 = QFont()
        font3.setPointSize(10)
        self.pushButton_3.setFont(font3)
        self.pushButton_4 = QPushButton(Dialog_Sale)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setGeometry(QRect(880, 730, 80, 52))
        self.pushButton_4.setFont(font3)
        self.label_4 = QLabel(Dialog_Sale)
        self.label_4.setObjectName("label_4")
        self.label_4.setGeometry(QRect(640, 510, 71, 41))
        self.label_4.setFont(font1)
        self.label_5 = QLabel(Dialog_Sale)
        self.label_5.setObjectName("label_5")
        self.label_5.setGeometry(QRect(730, 520, 21, 20))
        self.label_5.setFont(font1)
        self.label_6 = QLabel(Dialog_Sale)
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(640, 550, 61, 51))
        self.label_6.setFont(font1)
        self.label_7 = QLabel(Dialog_Sale)
        self.label_7.setObjectName("label_7")
        self.label_7.setGeometry(QRect(730, 570, 21, 20))
        self.label_7.setFont(font1)
        self.label_8 = QLabel(Dialog_Sale)
        self.label_8.setObjectName("label_8")
        self.label_8.setGeometry(QRect(740, 600, 41, 20))
        font4 = QFont()
        font4.setPointSize(11)
        font4.setBold(True)
        self.label_8.setFont(font4)
        self.label_9 = QLabel(Dialog_Sale)
        self.label_9.setObjectName("label_9")
        self.label_9.setGeometry(QRect(640, 600, 211, 20))
        self.label_9.setFont(font4)
        self.pushButton_5 = QPushButton(Dialog_Sale)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setGeometry(QRect(880, 610, 80, 52))
        self.pushButton_5.setFont(font3)
        self.pushButton_6 = QPushButton(Dialog_Sale)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.setGeometry(QRect(800, 670, 80, 52))
        self.pushButton_6.setFont(font3)
        self.pushButton_7 = QPushButton(Dialog_Sale)
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_7.setGeometry(QRect(720, 730, 80, 52))
        self.pushButton_7.setFont(font3)
        self.pushButton_8 = QPushButton(Dialog_Sale)
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_8.setGeometry(QRect(800, 730, 80, 52))
        self.pushButton_8.setFont(font3)
        self.dateEdit = QDateEdit(Dialog_Sale)
        self.dateEdit.setObjectName("dateEdit")
        self.dateEdit.setGeometry(QRect(640, 20, 110, 30))
        self.dateEdit.setCalendarPopup(True)
        self.label_12 = QLabel(Dialog_Sale)
        self.label_12.setObjectName("label_12")
        self.label_12.setGeometry(QRect(640, 0, 131, 20))
        self.label_13 = QLabel(Dialog_Sale)
        self.label_13.setObjectName("label_13")
        self.label_13.setGeometry(QRect(760, 0, 51, 20))
        self.comboBox = QComboBox(Dialog_Sale)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setGeometry(QRect(760, 20, 51, 30))
        self.label_14 = QLabel(Dialog_Sale)
        self.label_14.setObjectName("label_14")
        self.label_14.setGeometry(QRect(710, 630, 81, 21))
        self.label_14.setFont(font3)
        self.checkBox_2 = QCheckBox(Dialog_Sale)
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_2.setEnabled(True)
        self.checkBox_2.setGeometry(QRect(640, 630, 61, 25))
        self.checkBox_2.setFont(font3)
        self.comboBox_2 = QComboBox(Dialog_Sale)
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.setEnabled(False)
        self.comboBox_2.setGeometry(QRect(790, 630, 51, 30))
        self.comboBox_2.setFont(font3)
        self.label_17 = QLabel(Dialog_Sale)
        self.label_17.setObjectName("label_17")
        self.label_17.setGeometry(QRect(940, 520, 21, 20))
        self.label_17.setFont(font1)
        self.label_18 = QLabel(Dialog_Sale)
        self.label_18.setObjectName("label_18")
        self.label_18.setGeometry(QRect(850, 510, 81, 41))
        self.label_18.setFont(font1)
        self.label_19 = QLabel(Dialog_Sale)
        self.label_19.setObjectName("label_19")
        self.label_19.setGeometry(QRect(940, 570, 21, 20))
        self.label_19.setFont(font1)
        self.label_20 = QLabel(Dialog_Sale)
        self.label_20.setObjectName("label_20")
        self.label_20.setGeometry(QRect(850, 550, 71, 51))
        self.label_20.setFont(font1)
        self.checkBox_3 = QCheckBox(Dialog_Sale)
        self.checkBox_3.setObjectName("checkBox_3")
        self.checkBox_3.setGeometry(QRect(820, 20, 21, 21))
        self.checkBox_3.setFont(font3)
        self.checkBox_3.setAcceptDrops(False)
        self.checkBox_3.setAutoRepeat(False)
        self.label_21 = QLabel(Dialog_Sale)
        self.label_21.setObjectName("label_21")
        self.label_21.setGeometry(QRect(850, 10, 121, 41))
        self.label_21.setFont(font3)
        self.label_22 = QLabel(Dialog_Sale)
        self.label_22.setObjectName("label_22")
        self.label_22.setGeometry(QRect(850, 480, 101, 16))
        font5 = QFont()
        font5.setPointSize(11)
        font5.setBold(False)
        font5.setUnderline(True)
        font5.setStrikeOut(False)
        self.label_22.setFont(font5)
        self.pushButton_10 = QPushButton(Dialog_Sale)
        self.pushButton_10.setObjectName("pushButton_10")
        self.pushButton_10.setGeometry(QRect(720, 670, 80, 52))
        self.pushButton_10.setFont(font3)
        self.tableWidget_3 = QTableWidget(Dialog_Sale)
        if self.tableWidget_3.columnCount() < 5:
            self.tableWidget_3.setColumnCount(5)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(0, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(1, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(2, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(3, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(4, __qtablewidgetitem19)
        self.tableWidget_3.setObjectName("tableWidget_3")
        self.tableWidget_3.setGeometry(QRect(630, 60, 331, 371))
        self.tableWidget_3.setFont(font1)
        self.tableWidget_3.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.label_3 = QLabel(Dialog_Sale)
        self.label_3.setObjectName("label_3")
        self.label_3.setGeometry(QRect(640, 480, 161, 20))
        font6 = QFont()
        font6.setPointSize(11)
        font6.setBold(False)
        font6.setItalic(False)
        font6.setUnderline(True)
        self.label_3.setFont(font6)
        self.pushButton_13 = QPushButton(Dialog_Sale)
        self.pushButton_13.setObjectName("pushButton_13")
        self.pushButton_13.setGeometry(QRect(640, 730, 80, 52))
        self.pushButton_13.setFont(font3)
        self.pushButton_14 = QPushButton(Dialog_Sale)
        self.pushButton_14.setObjectName("pushButton_14")
        self.pushButton_14.setGeometry(QRect(880, 670, 80, 52))
        font7 = QFont()
        font7.setPointSize(8)
        font7.setKerning(True)
        self.pushButton_14.setFont(font7)

        self.retranslateUi(Dialog_Sale)

        self.pushButton.setDefault(True)
        self.pushButton_12.setDefault(False)

        QMetaObject.connectSlotsByName(Dialog_Sale)

    # setupUi

    def retranslateUi(self, Dialog_Sale):
        Dialog_Sale.setWindowTitle(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u041e\u043a\u043d\u043e \u043f\u0440\u043e\u0434\u0430\u0436\u0438",
                None,
            )
        )
        self.groupBox.setTitle(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u044f \u0441 \u043a\u043b\u0438\u0435\u043d\u0442\u0430\u043c\u0438                         \u041f\u043e\u0438\u0441\u043a \u0441 \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u043c \u0444\u0438\u043b\u044c\u0442\u0440\u043e\u043c",
                None,
            )
        )
        self.pushButton_2.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u0421\u043e\u0437\u0434\u0430\u0442\u044c\n"
                " \u043d\u043e\u0432\u043e\u0433\u043e",
                None,
            )
        )
        self.comboBox_4.setItemText(
            0,
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u0424\u0430\u043c\u0438\u043b\u0438\u044f+\u0418\u043c\u044f",
                None,
            ),
        )
        self.comboBox_4.setItemText(
            1,
            QCoreApplication.translate(
                "Dialog_Sale", "\u0424\u0430\u043c\u0438\u043b\u0438\u044f", None
            ),
        )
        self.comboBox_4.setItemText(
            2,
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u2116 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0430",
                None,
            ),
        )
        self.comboBox_4.setItemText(
            3,
            QCoreApplication.translate(
                "Dialog_Sale", "\u0418\u043d\u0432\u0430\u043b\u0438\u0434", None
            ),
        )
        self.comboBox_4.setItemText(
            4,
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u041c\u043d\u043e\u0433\u043e\u0434\u0435\u0442\u043d\u044b\u0439",
                None,
            ),
        )

        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0424\u0430\u043c\u0438\u043b\u0438\u044f", None
            )
        )
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("Dialog_Sale", "\u0418\u043c\u044f", None)
        )
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0412\u043e\u0437\u0440\u0430\u0441\u0442", None
            )
        )
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(
            QCoreApplication.translate("Dialog_Sale", "\u0424\u043b\u0430\u0433", None)
        )
        ___qtablewidgetitem4 = self.tableWidget.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0422\u0435\u043b\u0435\u0444\u043e\u043d", None
            )
        )
        ___qtablewidgetitem5 = self.tableWidget.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(
            QCoreApplication.translate("Dialog_Sale", "id", None)
        )
        self.pushButton.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u041d\u0430\u0439\u0442\u0438", None
            )
        )
        self.pushButton_9.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c\n"
                "\u0441\u043e\u0437\u0434\u0430\u043d-\u0433\u043e",
                None,
            )
        )
        self.pushButton_11.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c", None
            )
        )
        self.pushButton_12.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u041e\u0447\u0438\u0441\u0442\u0438\u0442\u044c", None
            )
        )
        ___qtablewidgetitem6 = self.tableWidget_2.horizontalHeaderItem(0)
        ___qtablewidgetitem6.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0424\u0430\u043c\u0438\u043b\u0438\u044f", None
            )
        )
        ___qtablewidgetitem7 = self.tableWidget_2.horizontalHeaderItem(1)
        ___qtablewidgetitem7.setText(
            QCoreApplication.translate("Dialog_Sale", "\u0418\u043c\u044f", None)
        )
        ___qtablewidgetitem8 = self.tableWidget_2.horizontalHeaderItem(2)
        ___qtablewidgetitem8.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u0422\u0438\u043f \u0431\u0438\u043b\u0435\u0442\u0430",
                None,
            )
        )
        ___qtablewidgetitem9 = self.tableWidget_2.horizontalHeaderItem(3)
        ___qtablewidgetitem9.setText(
            QCoreApplication.translate("Dialog_Sale", "\u0426\u0435\u043d\u0430", None)
        )
        ___qtablewidgetitem10 = self.tableWidget_2.horizontalHeaderItem(4)
        ___qtablewidgetitem10.setText(
            QCoreApplication.translate("Dialog_Sale", "\u0424\u043b\u0430\u0433", None)
        )
        ___qtablewidgetitem11 = self.tableWidget_2.horizontalHeaderItem(5)
        ___qtablewidgetitem11.setText(
            QCoreApplication.translate("Dialog_Sale", "id", None)
        )
        ___qtablewidgetitem12 = self.tableWidget_2.horizontalHeaderItem(6)
        ___qtablewidgetitem12.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0412\u043e\u0437\u0440\u0430\u0441\u0442", None
            )
        )
        ___qtablewidgetitem13 = self.tableWidget_2.horizontalHeaderItem(7)
        ___qtablewidgetitem13.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0421\u043a\u0438\u0434\u043a\u0430", None
            )
        )
        ___qtablewidgetitem14 = self.tableWidget_2.horizontalHeaderItem(8)
        ___qtablewidgetitem14.setText(
            QCoreApplication.translate("Dialog_Sale", "-", None)
        )
        self.label_2.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0412\u0441\u0435\u0433\u043e", None
            )
        )
        self.pushButton_3.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c",
                None,
            )
        )
        self.pushButton_4.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u041e\u0442\u043c\u0435\u043d\u0430", None
            )
        )
        self.label_4.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u0412\u0437\u0440\u043e\u0441\u043b\u044b\u0439\n"
                "\u0431\u0438\u043b\u0435\u0442, \u0448\u0442.:",
                None,
            )
        )
        self.label_5.setText(QCoreApplication.translate("Dialog_Sale", "-", None))
        self.label_6.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u0414\u0435\u0442\u0441\u043a\u0438\u0439\n"
                "\u0431\u0438\u043b\u0435\u0442, \u0448\u0442.:",
                None,
            )
        )
        self.label_7.setText(QCoreApplication.translate("Dialog_Sale", "-", None))
        self.label_8.setText(QCoreApplication.translate("Dialog_Sale", "-", None))
        self.label_9.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u0421\u0443\u043c\u043c\u0430, \u0440\u0443\u0431.:",
                None,
            )
        )
        self.pushButton_5.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u041e\u043f\u043b\u0430\u0442\u0430", None
            )
        )
        self.pushButton_6.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0412\u043e\u0437\u0432\u0440\u0430\u0442", None
            )
        )
        self.pushButton_7.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u041f\u0435\u0447\u0430\u0442\u044c\n"
                "\u0431\u0438\u043b\u0435\u0442\u043e\u0432",
                None,
            )
        )
        self.pushButton_8.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\n"
                "\u0431\u0438\u043b\u0435\u0442\u043e\u0432",
                None,
            )
        )
        self.label_12.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u0414\u0430\u0442\u0430 \u043f\u043e\u0441\u0435\u0449\u0435\u043d\u0438\u044f:",
                None,
            )
        )
        self.label_13.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0412\u0440\u0435\u043c\u044f:", None
            )
        )
        self.comboBox.setItemText(
            0, QCoreApplication.translate("Dialog_Sale", "1", None)
        )
        self.comboBox.setItemText(
            1, QCoreApplication.translate("Dialog_Sale", "2", None)
        )
        self.comboBox.setItemText(
            2, QCoreApplication.translate("Dialog_Sale", "3", None)
        )

        self.label_14.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0420\u0430\u0437\u043c\u0435\u0440 (%):", None
            )
        )
        self.checkBox_2.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0421\u043a\u0438\u0434\u043a\u0430", None
            )
        )
        self.comboBox_2.setItemText(
            0, QCoreApplication.translate("Dialog_Sale", "0", None)
        )
        self.comboBox_2.setItemText(
            1, QCoreApplication.translate("Dialog_Sale", "5", None)
        )
        self.comboBox_2.setItemText(
            2, QCoreApplication.translate("Dialog_Sale", "10", None)
        )
        self.comboBox_2.setItemText(
            3, QCoreApplication.translate("Dialog_Sale", "15", None)
        )
        self.comboBox_2.setItemText(
            4, QCoreApplication.translate("Dialog_Sale", "20", None)
        )
        self.comboBox_2.setItemText(
            5, QCoreApplication.translate("Dialog_Sale", "25", None)
        )
        self.comboBox_2.setItemText(
            6, QCoreApplication.translate("Dialog_Sale", "30", None)
        )
        self.comboBox_2.setItemText(
            7, QCoreApplication.translate("Dialog_Sale", "35", None)
        )
        self.comboBox_2.setItemText(
            8, QCoreApplication.translate("Dialog_Sale", "40", None)
        )
        self.comboBox_2.setItemText(
            9, QCoreApplication.translate("Dialog_Sale", "45", None)
        )
        self.comboBox_2.setItemText(
            10, QCoreApplication.translate("Dialog_Sale", "50", None)
        )
        self.comboBox_2.setItemText(
            11, QCoreApplication.translate("Dialog_Sale", "60", None)
        )
        self.comboBox_2.setItemText(
            12, QCoreApplication.translate("Dialog_Sale", "70", None)
        )
        self.comboBox_2.setItemText(
            13, QCoreApplication.translate("Dialog_Sale", "80", None)
        )
        self.comboBox_2.setItemText(
            14, QCoreApplication.translate("Dialog_Sale", "90", None)
        )
        self.comboBox_2.setItemText(
            15, QCoreApplication.translate("Dialog_Sale", "100", None)
        )

        self.label_17.setText(QCoreApplication.translate("Dialog_Sale", "-", None))
        self.label_18.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u0412\u0437\u0440\u043e\u0441\u043b\u044b\u0439\n"
                "\u0431\u0438\u043b\u0435\u0442, \u0448\u0442.:",
                None,
            )
        )
        self.label_19.setText(QCoreApplication.translate("Dialog_Sale", "-", None))
        self.label_20.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u0414\u0435\u0442\u0441\u043a\u0438\u0439\n"
                "\u0431\u0438\u043b\u0435\u0442, \u0448\u0442.:",
                None,
            )
        )
        self.checkBox_3.setText("")
        self.label_21.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u041f\u0440\u043e\u0434\u043b\u0435\u043d\u0438\u0435 \u0432 \u0434\u0435\u043d\u044c\n"
                "\u043c\u043d\u043e\u0433\u043e\u0434\u0435\u0442\u043d\u044b\u0445",
                None,
            )
        )
        self.label_22.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u041c\u043d\u043e\u0433\u043e\u0434\u0435\u0442\u043d\u044b\u0435",
                None,
            )
        )
        self.pushButton_10.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c", None
            )
        )
        ___qtablewidgetitem15 = self.tableWidget_3.horizontalHeaderItem(0)
        ___qtablewidgetitem15.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0424\u0430\u043c\u0438\u043b\u0438\u044f", None
            )
        )
        ___qtablewidgetitem16 = self.tableWidget_3.horizontalHeaderItem(1)
        ___qtablewidgetitem16.setText(
            QCoreApplication.translate("Dialog_Sale", "\u0418\u043c\u044f", None)
        )
        ___qtablewidgetitem17 = self.tableWidget_3.horizontalHeaderItem(2)
        ___qtablewidgetitem17.setText(
            QCoreApplication.translate(
                "Dialog_Sale", "\u0412\u043e\u0437\u0440\u0430\u0441\u0442", None
            )
        )
        ___qtablewidgetitem18 = self.tableWidget_3.horizontalHeaderItem(3)
        ___qtablewidgetitem18.setText(
            QCoreApplication.translate("Dialog_Sale", "\u0424\u043b\u0430\u0433", None)
        )
        ___qtablewidgetitem19 = self.tableWidget_3.horizontalHeaderItem(4)
        ___qtablewidgetitem19.setText(
            QCoreApplication.translate("Dialog_Sale", "id", None)
        )
        self.label_3.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u041e\u0431\u044b\u0447\u043d\u044b\u0435 \u043f\u043e\u0441\u0435\u0442\u0438\u0442\u0435\u043b\u0438",
                None,
            )
        )
        self.pushButton_13.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\n"
                "\u0441\u043b\u0438\u043f-\u0447\u0435\u043a\u0430",
                None,
            )
        )
        self.pushButton_14.setText(
            QCoreApplication.translate(
                "Dialog_Sale",
                "\u041e\u0442\u043c\u0435\u043d\u0430\n"
                "(\u0434\u043b\u044f \u043e\u0442\u043a\u0440.\n"
                "\u0431\u0430\u043d\u043a. \u0441\u043c\u0435\u043d\u044b)",
                None,
            )
        )

    # retranslateUi
