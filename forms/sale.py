# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sale_2.ui'
##
## Created by: Qt User Interface Compiler version 6.1.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_Dialog_Sale(object):
    def setupUi(self, Dialog_Sale):
        if not Dialog_Sale.objectName():
            Dialog_Sale.setObjectName(u"Dialog_Sale")
        Dialog_Sale.resize(1027, 800)
        self.groupBox = QGroupBox(Dialog_Sale)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(0, 0, 601, 361))
        self.lineEdit = QLineEdit(self.groupBox)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(0, 30, 341, 30))
        self.pushButton = QPushButton(self.groupBox)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(340, 30, 94, 28))
        self.pushButton_2 = QPushButton(self.groupBox)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(440, 30, 94, 28))
        self.tableWidget = QTableWidget(self.groupBox)
        if (self.tableWidget.columnCount() < 6):
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
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(0, 60, 771, 331))
        self.layoutWidget = QWidget(self.groupBox)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(110, 0, 305, 27))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.radioButton = QRadioButton(self.layoutWidget)
        self.radioButton.setObjectName(u"radioButton")

        self.gridLayout.addWidget(self.radioButton, 0, 1, 1, 1)

        self.radioButton_2 = QRadioButton(self.layoutWidget)
        self.radioButton_2.setObjectName(u"radioButton_2")

        self.gridLayout.addWidget(self.radioButton_2, 0, 2, 1, 1)

        self.radioButton_3 = QRadioButton(self.layoutWidget)
        self.radioButton_3.setObjectName(u"radioButton_3")

        self.gridLayout.addWidget(self.radioButton_3, 0, 3, 1, 1)

        self.line = QFrame(Dialog_Sale)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(770, -10, 20, 801))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line_2 = QFrame(Dialog_Sale)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setGeometry(QRect(0, 390, 1031, 21))
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.tableWidget_2 = QTableWidget(Dialog_Sale)
        if (self.tableWidget_2.columnCount() < 6):
            self.tableWidget_2.setColumnCount(6)
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
        self.tableWidget_2.setObjectName(u"tableWidget_2")
        self.tableWidget_2.setGeometry(QRect(0, 400, 601, 401))
        self.label_2 = QLabel(Dialog_Sale)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(790, 10, 161, 20))
        self.label_3 = QLabel(Dialog_Sale)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(790, 409, 63, 20))
        self.pushButton_3 = QPushButton(Dialog_Sale)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(790, 610, 94, 28))
        self.pushButton_4 = QPushButton(Dialog_Sale)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(910, 760, 94, 28))
        self.label_4 = QLabel(Dialog_Sale)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(790, 40, 121, 20))
        self.label_5 = QLabel(Dialog_Sale)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(930, 40, 61, 20))
        self.label_6 = QLabel(Dialog_Sale)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(790, 70, 121, 20))
        self.label_7 = QLabel(Dialog_Sale)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(930, 70, 61, 20))
        self.label_8 = QLabel(Dialog_Sale)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(930, 100, 61, 20))
        self.label_9 = QLabel(Dialog_Sale)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(790, 100, 121, 20))
        self.pushButton_5 = QPushButton(Dialog_Sale)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setGeometry(QRect(790, 440, 94, 28))
        self.pushButton_6 = QPushButton(Dialog_Sale)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.pushButton_6.setGeometry(QRect(900, 440, 94, 28))
        self.pushButton_7 = QPushButton(Dialog_Sale)
        self.pushButton_7.setObjectName(u"pushButton_7")
        self.pushButton_7.setGeometry(QRect(790, 530, 94, 28))
        self.label_10 = QLabel(Dialog_Sale)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(790, 500, 63, 20))
        self.pushButton_8 = QPushButton(Dialog_Sale)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setGeometry(QRect(900, 530, 94, 28))
        self.label_11 = QLabel(Dialog_Sale)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(790, 580, 63, 20))
        self.tableWidget_3 = QTableWidget(Dialog_Sale)
        if (self.tableWidget_3.columnCount() < 1):
            self.tableWidget_3.setColumnCount(1)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(0, __qtablewidgetitem12)
        if (self.tableWidget_3.rowCount() < 3):
            self.tableWidget_3.setRowCount(3)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(0, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(1, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(2, __qtablewidgetitem15)
        self.tableWidget_3.setObjectName(u"tableWidget_3")
        self.tableWidget_3.setGeometry(QRect(790, 130, 231, 191))
        self.dateEdit = QDateEdit(Dialog_Sale)
        self.dateEdit.setObjectName(u"dateEdit")
        self.dateEdit.setGeometry(QRect(610, 440, 110, 30))
        self.dateEdit.setCalendarPopup(True)
        self.label_12 = QLabel(Dialog_Sale)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(610, 410, 131, 20))
        self.label_13 = QLabel(Dialog_Sale)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(610, 500, 161, 20))
        self.comboBox = QComboBox(Dialog_Sale)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QRect(610, 520, 78, 30))

        self.retranslateUi(Dialog_Sale)

        QMetaObject.connectSlotsByName(Dialog_Sale)
    # setupUi

    def retranslateUi(self, Dialog_Sale):
        Dialog_Sale.setWindowTitle(QCoreApplication.translate("Dialog_Sale", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog_Sale", u"\u041f\u043e\u0441\u0435\u0442\u0438\u0442\u0435\u043b\u0438", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog_Sale", u"\u041d\u0430\u0439\u0442\u0438", None))
        self.pushButton_2.setText(QCoreApplication.translate("Dialog_Sale", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Dialog_Sale", u"\u0424\u0430\u043c\u0438\u043b\u0438\u044f", None));
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Dialog_Sale", u"\u0418\u043c\u044f", None));
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Dialog_Sale", u"\u041e\u0442\u0447\u0435\u0441\u0442\u0432\u043e", None));
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Dialog_Sale", u"\u0412\u043e\u0437\u0440\u0430\u0441\u0442", None));
        ___qtablewidgetitem4 = self.tableWidget.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Dialog_Sale", u"\u0424\u043b\u0430\u0433", None));
        ___qtablewidgetitem5 = self.tableWidget.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Dialog_Sale", u"\u0422\u0435\u043b\u0435\u0444\u043e\u043d", None));
        self.label.setText(QCoreApplication.translate("Dialog_Sale", u"\u041f\u043e\u0438\u0441\u043a:", None))
        self.radioButton.setText(QCoreApplication.translate("Dialog_Sale", u"\u0424\u0430\u043c\u0438\u043b\u0438\u044f", None))
        self.radioButton_2.setText(QCoreApplication.translate("Dialog_Sale", u"\u0418\u043c\u044f", None))
        self.radioButton_3.setText(QCoreApplication.translate("Dialog_Sale", u"\u0422\u0435\u043b\u0435\u0444\u043e\u043d", None))
        ___qtablewidgetitem6 = self.tableWidget_2.horizontalHeaderItem(0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("Dialog_Sale", u"\u0424\u0430\u043c\u0438\u043b\u0438\u044f", None));
        ___qtablewidgetitem7 = self.tableWidget_2.horizontalHeaderItem(1)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("Dialog_Sale", u"\u0418\u043c\u044f", None));
        ___qtablewidgetitem8 = self.tableWidget_2.horizontalHeaderItem(2)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("Dialog_Sale", u"\u041e\u0442\u0447\u0435\u0441\u0442\u0432\u043e", None));
        ___qtablewidgetitem9 = self.tableWidget_2.horizontalHeaderItem(3)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("Dialog_Sale", u"\u0422\u0438\u043f \u0431\u0438\u043b\u0435\u0442\u0430", None));
        ___qtablewidgetitem10 = self.tableWidget_2.horizontalHeaderItem(4)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("Dialog_Sale", u"\u0426\u0435\u043d\u0430", None));
        ___qtablewidgetitem11 = self.tableWidget_2.horizontalHeaderItem(5)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("Dialog_Sale", u"\u0424\u043b\u0430\u0433", None));
        self.label_2.setText(QCoreApplication.translate("Dialog_Sale", u"\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e \u0437\u0430\u043a\u0430\u0437\u0435", None))
        self.label_3.setText(QCoreApplication.translate("Dialog_Sale", u"\u041e\u043f\u043b\u0430\u0442\u0430", None))
        self.pushButton_3.setText(QCoreApplication.translate("Dialog_Sale", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c", None))
        self.pushButton_4.setText(QCoreApplication.translate("Dialog_Sale", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
        self.label_4.setText(QCoreApplication.translate("Dialog_Sale", u"\u0412\u0437\u0440\u043e\u0441\u043b\u044b\u0439 \u0431\u0438\u043b\u0435\u0442:", None))
        self.label_5.setText(QCoreApplication.translate("Dialog_Sale", u"- \u0448\u0442.", None))
        self.label_6.setText(QCoreApplication.translate("Dialog_Sale", u"\u0414\u0435\u0442\u0441\u043a\u0438\u0439 \u0431\u0438\u043b\u0435\u0442:", None))
        self.label_7.setText(QCoreApplication.translate("Dialog_Sale", u"- \u0448\u0442.", None))
        self.label_8.setText(QCoreApplication.translate("Dialog_Sale", u"- \u0440\u0443\u0431.", None))
        self.label_9.setText(QCoreApplication.translate("Dialog_Sale", u"\u0421\u0443\u043c\u043c\u0430:", None))
        self.pushButton_5.setText(QCoreApplication.translate("Dialog_Sale", u"\u041e\u043f\u043b\u0430\u0442\u0430", None))
        self.pushButton_6.setText(QCoreApplication.translate("Dialog_Sale", u"\u0412\u043e\u0437\u0432\u0440\u0430\u0442", None))
        self.pushButton_7.setText(QCoreApplication.translate("Dialog_Sale", u"\u041f\u0435\u0447\u0430\u0442\u044c", None))
        self.label_10.setText(QCoreApplication.translate("Dialog_Sale", u"\u0411\u0438\u043b\u0435\u0442\u044b", None))
        self.pushButton_8.setText(QCoreApplication.translate("Dialog_Sale", u"\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440", None))
        self.label_11.setText(QCoreApplication.translate("Dialog_Sale", u"\u0417\u0430\u043a\u0430\u0437", None))
        ___qtablewidgetitem12 = self.tableWidget_3.horizontalHeaderItem(0)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("Dialog_Sale", u".", None));
        ___qtablewidgetitem13 = self.tableWidget_3.verticalHeaderItem(0)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("Dialog_Sale", u"\u0412\u0437\u0440\u043e\u0441\u043b\u044b\u0439", None));
        ___qtablewidgetitem14 = self.tableWidget_3.verticalHeaderItem(1)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("Dialog_Sale", u"\u0414\u0435\u0442\u0441\u043a\u0438\u0439", None));
        ___qtablewidgetitem15 = self.tableWidget_3.verticalHeaderItem(2)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("Dialog_Sale", u"\u0421\u0443\u043c\u043c\u0430", None));
        self.label_12.setText(QCoreApplication.translate("Dialog_Sale", u"\u0414\u0430\u0442\u0430 \u043f\u043e\u0441\u0435\u0449\u0435\u043d\u0438\u044f:", None))
        self.label_13.setText(QCoreApplication.translate("Dialog_Sale", u"\u041f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c:", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Dialog_Sale", u"1", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Dialog_Sale", u"2", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("Dialog_Sale", u"3", None))

    # retranslateUi

