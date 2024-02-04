from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
                            Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QLabel, QLineEdit,
                               QTabWidget, QTextEdit, QWidget)

class Ui_Dialog_Slip(object):
    def setupUi(self, Dialog_Slip):
        if not Dialog_Slip.objectName():
            Dialog_Slip.setObjectName(u"Dialog_Slip")
        Dialog_Slip.setWindowModality(Qt.ApplicationModal)
        Dialog_Slip.resize(395, 177)
        self.tabWidget = QTabWidget(Dialog_Slip)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(10, 10, 381, 171))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.label = QLabel(self.tab)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 461, 16))
        font = QFont()
        font.setBold(False)
        self.label.setFont(font)
        self.label_2 = QLabel(self.tab)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 30, 121, 16))
        self.label_3 = QLabel(self.tab)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 50, 121, 16))
        self.label_4 = QLabel(self.tab)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 80, 371, 51))
        self.lineEdit = QLineEdit(self.tab)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(170, 110, 201, 22))
        self.label_5 = QLabel(self.tab)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(140, 30, 221, 16))
        self.label_6 = QLabel(self.tab)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(140, 50, 221, 16))
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.textEdit = QTextEdit(self.tab_2)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(0, 0, 371, 131))
        self.tabWidget.addTab(self.tab_2, "")

        self.retranslateUi(Dialog_Slip)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog_Slip)
    # setupUi

    def retranslateUi(self, Dialog_Slip):
        Dialog_Slip.setWindowTitle(QCoreApplication.translate("Dialog_Slip", u"\u041e\u043a\u043d\u043e \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u0430 \u0441\u0432\u0435\u0434\u0435\u043d\u0438\u0439 \u043e \u043f\u0440\u043e\u0434\u0430\u0436\u0435", None))
        self.label.setText(QCoreApplication.translate("Dialog_Slip", u"\u041e\u043f\u043b\u0430\u0442\u0430 \u0431\u044b\u043b\u0430 \u043f\u0440\u043e\u0438\u0437\u0432\u0435\u0434\u0435\u043d\u0430 \u043a\u0430\u0440\u0442\u043e\u0439 \u0441\u043e \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u043c\u0438 \u0440\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u0430\u043c\u0438:", None))
        self.label_2.setText(QCoreApplication.translate("Dialog_Slip", u"- \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0435 \u0446\u0438\u0444\u0440\u044b:", None))
        self.label_3.setText(QCoreApplication.translate("Dialog_Slip", u"- \u043c\u0435\u0440\u0447\u0430\u043d\u0442:", None))
        self.label_4.setText(QCoreApplication.translate("Dialog_Slip", u"\u0414\u043b\u044f \u0432\u043e\u0437\u0432\u0440\u0430\u0442\u0430 \u043f\u043b\u0430\u0442\u0435\u0436\u0430 \u0442\u0435\u0440\u043c\u0438\u043d\u0430\u043b \u043f\u043e\u043f\u0440\u043e\u0441\u0438\u0442 \u0432\u0432\u0435\u0441\u0442\u0438 \u043d\u043e\u043c\u0435\u0440 \u0441\u0441\u044b\u043b\u043a\u0438.\n"
"\n"
"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0435 \u0446\u0438\u0444\u0440\u044b:", None))
        self.label_5.setText(QCoreApplication.translate("Dialog_Slip", u"-", None))
        self.label_6.setText(QCoreApplication.translate("Dialog_Slip", u"-", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Dialog_Slip", u"\u041a\u0440\u0430\u0442\u043a\u043e", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Dialog_Slip", u"\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u0435\u0435", None))
    # retranslateUi

