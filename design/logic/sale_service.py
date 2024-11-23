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


class Ui_Dialog_Sale_Service(object):
    def setupUi(self, Dialog_Sale_Service):
        if not Dialog_Sale_Service.objectName():
            Dialog_Sale_Service.setObjectName("Dialog_Sale_Service")
        Dialog_Sale_Service.setWindowModality(Qt.WindowModality.ApplicationModal)
        Dialog_Sale_Service.resize(963, 787)
        self.groupBox = QGroupBox(Dialog_Sale_Service)
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setGeometry(QRect(0, 0, 437, 431))
        self.pushButton_2 = QPushButton(self.groupBox)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setGeometry(QRect(5, 17, 61, 41))
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
        if self.tableWidget.columnCount() < 4:
            self.tableWidget.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setGeometry(QRect(0, 60, 437, 371))
        font1 = QFont()
        font1.setPointSize(11)
        self.tableWidget.setFont(font1)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.pushButton_9 = QPushButton(self.groupBox)
        self.pushButton_9.setObjectName("pushButton_9")
        self.pushButton_9.setGeometry(QRect(70, 17, 61, 41))
        self.pushButton_11 = QPushButton(self.groupBox)
        self.pushButton_11.setObjectName("pushButton_11")
        self.pushButton_11.setGeometry(QRect(135, 17, 61, 41))
        self.lineEdit = QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setGeometry(QRect(295, 30, 131, 30))
        self.lineEdit.setMaximumSize(QSize(261, 30))
        self.line_2 = QFrame(Dialog_Sale_Service)
        self.line_2.setObjectName("line_2")
        self.line_2.setGeometry(QRect(0, 430, 1041, 20))
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)
        self.tableWidget_2 = QTableWidget(Dialog_Sale_Service)
        if self.tableWidget_2.columnCount() < 6:
            self.tableWidget_2.setColumnCount(6)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(2, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(3, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(4, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(5, __qtablewidgetitem9)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setGeometry(QRect(440, 60, 521, 371))
        self.tableWidget_2.setFont(font1)
        self.tableWidget_2.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWidget_2.horizontalHeader().setDefaultSectionSize(100)
        self.label_2 = QLabel(Dialog_Sale_Service)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(760, 450, 51, 20))
        font2 = QFont()
        font2.setPointSize(13)
        font2.setBold(True)
        self.label_2.setFont(font2)
        self.pushButton_3 = QPushButton(Dialog_Sale_Service)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setGeometry(QRect(630, 660, 80, 52))
        font3 = QFont()
        font3.setPointSize(10)
        self.pushButton_3.setFont(font3)
        self.pushButton_4 = QPushButton(Dialog_Sale_Service)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setGeometry(QRect(870, 720, 80, 52))
        self.pushButton_4.setFont(font3)
        self.label_4 = QLabel(Dialog_Sale_Service)
        self.label_4.setObjectName("label_4")
        self.label_4.setGeometry(QRect(630, 530, 71, 41))
        self.label_4.setFont(font1)
        self.label_5 = QLabel(Dialog_Sale_Service)
        self.label_5.setObjectName("label_5")
        self.label_5.setGeometry(QRect(720, 540, 21, 20))
        self.label_5.setFont(font1)
        self.label_6 = QLabel(Dialog_Sale_Service)
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(630, 570, 71, 51))
        self.label_6.setFont(font1)
        self.label_7 = QLabel(Dialog_Sale_Service)
        self.label_7.setObjectName("label_7")
        self.label_7.setGeometry(QRect(720, 590, 21, 20))
        self.label_7.setFont(font1)
        self.label_8 = QLabel(Dialog_Sale_Service)
        self.label_8.setObjectName("label_8")
        self.label_8.setGeometry(QRect(730, 630, 91, 20))
        font4 = QFont()
        font4.setPointSize(11)
        font4.setBold(True)
        self.label_8.setFont(font4)
        self.label_9 = QLabel(Dialog_Sale_Service)
        self.label_9.setObjectName("label_9")
        self.label_9.setGeometry(QRect(630, 630, 211, 20))
        self.label_9.setFont(font4)
        self.pushButton_5 = QPushButton(Dialog_Sale_Service)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setGeometry(QRect(870, 600, 80, 52))
        self.pushButton_5.setFont(font3)
        self.pushButton_6 = QPushButton(Dialog_Sale_Service)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.setGeometry(QRect(790, 660, 80, 52))
        self.pushButton_6.setFont(font3)
        self.pushButton_7 = QPushButton(Dialog_Sale_Service)
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_7.setGeometry(QRect(710, 720, 80, 52))
        self.pushButton_7.setFont(font3)
        self.pushButton_8 = QPushButton(Dialog_Sale_Service)
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_8.setGeometry(QRect(790, 720, 80, 52))
        self.pushButton_8.setFont(font3)
        self.dateEdit_1 = QDateEdit(Dialog_Sale_Service)
        self.dateEdit_1.setObjectName("dateEdit_1")
        self.dateEdit_1.setGeometry(QRect(840, 30, 110, 30))
        self.dateEdit_1.setCalendarPopup(True)
        self.label_12 = QLabel(Dialog_Sale_Service)
        self.label_12.setObjectName("label_12")
        self.label_12.setGeometry(QRect(800, 10, 111, 20))
        self.checkBox_2 = QCheckBox(Dialog_Sale_Service)
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_2.setEnabled(True)
        self.checkBox_2.setGeometry(QRect(800, 30, 21, 21))
        self.checkBox_2.setFont(font3)
        self.pushButton_10 = QPushButton(Dialog_Sale_Service)
        self.pushButton_10.setObjectName("pushButton_10")
        self.pushButton_10.setGeometry(QRect(710, 660, 80, 52))
        self.pushButton_10.setFont(font3)
        self.tableWidget_3 = QTableWidget(Dialog_Sale_Service)
        if self.tableWidget_3.columnCount() < 8:
            self.tableWidget_3.setColumnCount(8)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(0, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(1, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(2, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(3, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(4, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(5, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(6, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(7, __qtablewidgetitem17)
        self.tableWidget_3.setObjectName("tableWidget_3")
        self.tableWidget_3.setGeometry(QRect(0, 440, 621, 341))
        self.tableWidget_3.setFont(font1)
        self.tableWidget_3.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.label_3 = QLabel(Dialog_Sale_Service)
        self.label_3.setObjectName("label_3")
        self.label_3.setGeometry(QRect(630, 470, 161, 20))
        font5 = QFont()
        font5.setPointSize(11)
        font5.setBold(False)
        font5.setItalic(False)
        font5.setUnderline(True)
        self.label_3.setFont(font5)
        self.pushButton_13 = QPushButton(Dialog_Sale_Service)
        self.pushButton_13.setObjectName("pushButton_13")
        self.pushButton_13.setGeometry(QRect(630, 720, 80, 52))
        self.pushButton_13.setFont(font3)
        self.pushButton_14 = QPushButton(Dialog_Sale_Service)
        self.pushButton_14.setObjectName("pushButton_14")
        self.pushButton_14.setGeometry(QRect(870, 660, 80, 52))
        font6 = QFont()
        font6.setPointSize(8)
        font6.setKerning(True)
        self.pushButton_14.setFont(font6)
        self.pushButton = QPushButton(Dialog_Sale_Service)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QRect(430, 20, 58, 41))
        self.pushButton.setAutoDefault(True)
        self.pushButton_12 = QPushButton(Dialog_Sale_Service)
        self.pushButton_12.setObjectName("pushButton_12")
        self.pushButton_12.setGeometry(QRect(490, 20, 58, 41))
        self.pushButton_12.setAutoDefault(False)
        self.lineEdit_2 = QLineEdit(Dialog_Sale_Service)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setGeometry(QRect(630, 490, 211, 30))
        self.lineEdit_2.setMaximumSize(QSize(261, 30))

        self.retranslateUi(Dialog_Sale_Service)

        self.pushButton.setDefault(True)
        self.pushButton_12.setDefault(False)

        QMetaObject.connectSlotsByName(Dialog_Sale_Service)

    # setupUi

    def retranslateUi(self, Dialog_Sale_Service):
        Dialog_Sale_Service.setWindowTitle(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u041e\u043a\u043d\u043e \u043f\u0440\u043e\u0434\u0430\u0436\u0438",
                None,
            )
        )
        self.groupBox.setTitle(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u044f \u0441 \u043a\u043b\u0438\u0435\u043d\u0442\u0430\u043c\u0438                         \u041f\u043e\u0438\u0441\u043a \u0441 \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u043c \u0444\u0438\u043b\u044c\u0442\u0440\u043e\u043c",
                None,
            )
        )
        self.pushButton_2.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0421\u043e\u0437\u0434\u0430\u0442\u044c\n"
                " \u043d\u043e\u0432\u043e\u0433\u043e",
                None,
            )
        )
        self.comboBox_4.setItemText(
            0,
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0424\u0430\u043c\u0438\u043b\u0438\u044f+\u0418\u043c\u044f",
                None,
            ),
        )
        self.comboBox_4.setItemText(
            1,
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0424\u0430\u043c\u0438\u043b\u0438\u044f",
                None,
            ),
        )
        self.comboBox_4.setItemText(
            2,
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u2116 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0430",
                None,
            ),
        )
        self.comboBox_4.setItemText(
            3,
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0418\u043d\u0432\u0430\u043b\u0438\u0434",
                None,
            ),
        )
        self.comboBox_4.setItemText(
            4,
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u041c\u043d\u043e\u0433\u043e\u0434\u0435\u0442\u043d\u044b\u0439",
                None,
            ),
        )

        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0424\u0430\u043c\u0438\u043b\u0438\u044f",
                None,
            )
        )
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service", "\u0418\u043c\u044f", None
            )
        )
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0422\u0435\u043b\u0435\u0444\u043e\u043d",
                None,
            )
        )
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(
            QCoreApplication.translate("Dialog_Sale_Service", "id", None)
        )
        self.pushButton_9.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c\n"
                "\u0441\u043e\u0437\u0434\u0430\u043d-\u0433\u043e",
                None,
            )
        )
        self.pushButton_11.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c",
                None,
            )
        )
        ___qtablewidgetitem4 = self.tableWidget_2.horizontalHeaderItem(0)
        ___qtablewidgetitem4.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435",
                None,
            )
        )
        ___qtablewidgetitem5 = self.tableWidget_2.horizontalHeaderItem(1)
        ___qtablewidgetitem5.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service", "\u041a\u043e\u043b-\u0432\u043e", None
            )
        )
        ___qtablewidgetitem6 = self.tableWidget_2.horizontalHeaderItem(2)
        ___qtablewidgetitem6.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service", "\u0426\u0435\u043d\u0430", None
            )
        )
        ___qtablewidgetitem7 = self.tableWidget_2.horizontalHeaderItem(3)
        ___qtablewidgetitem7.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service", "\u041f\u0435\u0447\u0430\u0442\u044c", None
            )
        )
        ___qtablewidgetitem8 = self.tableWidget_2.horizontalHeaderItem(4)
        ___qtablewidgetitem8.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service", "\u0412\u0437\u0440.\u0431\u0438\u043b.", None
            )
        )
        ___qtablewidgetitem9 = self.tableWidget_2.horizontalHeaderItem(5)
        ___qtablewidgetitem9.setText(
            QCoreApplication.translate("Dialog_Sale_Service", "id", None)
        )
        self.label_2.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service", "\u0412\u0441\u0435\u0433\u043e", None
            )
        )
        self.pushButton_3.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c",
                None,
            )
        )
        self.pushButton_4.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service", "\u041e\u0442\u043c\u0435\u043d\u0430", None
            )
        )
        self.label_4.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0412\u0437\u0440\u043e\u0441\u043b\u044b\u0439\n"
                "\u0431\u0438\u043b\u0435\u0442, \u0448\u0442.:",
                None,
            )
        )
        self.label_5.setText(
            QCoreApplication.translate("Dialog_Sale_Service", "-", None)
        )
        self.label_6.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0414\u0435\u0442\u0441\u043a\u0438\u0439\n"
                "\u0431\u0438\u043b\u0435\u0442, \u0448\u0442.:",
                None,
            )
        )
        self.label_7.setText(
            QCoreApplication.translate("Dialog_Sale_Service", "-", None)
        )
        self.label_8.setText(
            QCoreApplication.translate("Dialog_Sale_Service", "-", None)
        )
        self.label_9.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0421\u0443\u043c\u043c\u0430, \u0440\u0443\u0431.:",
                None,
            )
        )
        self.pushButton_5.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service", "\u041e\u043f\u043b\u0430\u0442\u0430", None
            )
        )
        self.pushButton_6.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0412\u043e\u0437\u0432\u0440\u0430\u0442",
                None,
            )
        )
        self.pushButton_7.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u041f\u0435\u0447\u0430\u0442\u044c\n"
                "\u0431\u0438\u043b\u0435\u0442\u043e\u0432",
                None,
            )
        )
        self.pushButton_8.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\n"
                "\u0431\u0438\u043b\u0435\u0442\u043e\u0432",
                None,
            )
        )
        self.label_12.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u0414\u0430\u0442\u0430 \u043f\u043e\u0441\u0435\u0449\u0435\u043d\u0438\u044f:",
                None,
            )
        )
        self.checkBox_2.setText("")
        self.pushButton_10.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c",
                None,
            )
        )
        ___qtablewidgetitem10 = self.tableWidget_3.horizontalHeaderItem(0)
        ___qtablewidgetitem10.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435",
                None,
            )
        )
        ___qtablewidgetitem11 = self.tableWidget_3.horizontalHeaderItem(1)
        ___qtablewidgetitem11.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service", "\u0426\u0435\u043d\u0430", None
            )
        )
        ___qtablewidgetitem12 = self.tableWidget_3.horizontalHeaderItem(2)
        ___qtablewidgetitem12.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435",
                None,
            )
        )
        ___qtablewidgetitem13 = self.tableWidget_3.horizontalHeaderItem(3)
        ___qtablewidgetitem13.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u041f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c",
                None,
            )
        )
        ___qtablewidgetitem14 = self.tableWidget_3.horizontalHeaderItem(4)
        ___qtablewidgetitem14.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service", "Min \u043a\u043e\u043b-\u0432\u043e", None
            )
        )
        ___qtablewidgetitem15 = self.tableWidget_3.horizontalHeaderItem(5)
        ___qtablewidgetitem15.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service", "Max \u043a\u043e\u043b-\u0432\u043e", None
            )
        )
        ___qtablewidgetitem16 = self.tableWidget_3.horizontalHeaderItem(6)
        ___qtablewidgetitem16.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service", "\u0411\u0438\u043b\u0435\u0442", None
            )
        )
        ___qtablewidgetitem17 = self.tableWidget_3.horizontalHeaderItem(7)
        ___qtablewidgetitem17.setText(
            QCoreApplication.translate("Dialog_Sale_Service", "id", None)
        )
        self.label_3.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u041f\u043e\u0441\u0435\u0442\u0438\u0442\u0435\u043b\u044c",
                None,
            )
        )
        self.pushButton_13.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\n"
                "\u0441\u043b\u0438\u043f-\u0447\u0435\u043a\u0430",
                None,
            )
        )
        self.pushButton_14.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u041e\u0442\u043c\u0435\u043d\u0430\n"
                "(\u0434\u043b\u044f \u043e\u0442\u043a\u0440.\n"
                "\u0431\u0430\u043d\u043a. \u0441\u043c\u0435\u043d\u044b)",
                None,
            )
        )
        self.pushButton.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service", "\u041d\u0430\u0439\u0442\u0438", None
            )
        )
        self.pushButton_12.setText(
            QCoreApplication.translate(
                "Dialog_Sale_Service",
                "\u041e\u0447\u0438\u0441\u0442\u0438\u0442\u044c",
                None,
            )
        )

    # retranslateUi
