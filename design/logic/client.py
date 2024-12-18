from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QToolBox,
    QWidget,
)


class Ui_Dialog_Client(object):
    def setupUi(self, Dialog_Client):
        if not Dialog_Client.objectName():
            Dialog_Client.setObjectName("Dialog_Client")
        Dialog_Client.setWindowModality(Qt.ApplicationModal)
        Dialog_Client.resize(346, 266)
        self.toolBox = QToolBox(Dialog_Client)
        self.toolBox.setObjectName("toolBox")
        self.toolBox.setGeometry(QRect(10, 10, 341, 261))
        self.client = QWidget()
        self.client.setObjectName("client")
        self.client.setGeometry(QRect(0, 0, 341, 231))
        self.layoutWidget = QWidget(self.client)
        self.layoutWidget.setObjectName("layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 0, 333, 181))
        self.formLayout = QFormLayout(self.layoutWidget)
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.dateEdit = QDateEdit(self.layoutWidget)
        self.dateEdit.setObjectName("dateEdit")

        self.gridLayout.addWidget(self.dateEdit, 3, 2, 1, 1)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.lineEdit_3 = QLineEdit(self.layoutWidget)
        self.lineEdit_3.setObjectName("lineEdit_3")

        self.gridLayout.addWidget(self.lineEdit_3, 2, 1, 1, 2)

        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName("label_4")

        self.gridLayout.addWidget(self.label_4, 3, 3, 1, 1)

        self.comboBox = QComboBox(self.layoutWidget)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName("comboBox")

        self.gridLayout.addWidget(self.comboBox, 3, 4, 1, 1)

        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName("label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_6 = QLabel(self.layoutWidget)
        self.label_6.setObjectName("label_6")

        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)

        self.lineEdit_2 = QLineEdit(self.layoutWidget)
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 2)

        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName("label_3")

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 2)

        self.lineEdit_4 = QLineEdit(self.layoutWidget)
        self.lineEdit_4.setObjectName("lineEdit_4")

        self.gridLayout.addWidget(self.lineEdit_4, 4, 1, 1, 2)

        self.label_5 = QLabel(self.layoutWidget)
        self.label_5.setObjectName("label_5")

        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)

        self.lineEdit = QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName("lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 2)

        self.label_8 = QLabel(self.layoutWidget)
        self.label_8.setObjectName("label_8")

        self.gridLayout.addWidget(self.label_8, 4, 3, 1, 1)

        self.comboBox_2 = QComboBox(self.layoutWidget)
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.setObjectName("comboBox_2")

        self.gridLayout.addWidget(self.comboBox_2, 4, 4, 1, 1)

        self.pushButton_3 = QPushButton(self.layoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")

        self.gridLayout.addWidget(self.pushButton_3, 0, 3, 1, 1)

        self.pushButton_4 = QPushButton(self.layoutWidget)
        self.pushButton_4.setObjectName("pushButton_4")

        self.gridLayout.addWidget(self.pushButton_4, 0, 4, 1, 1)

        self.formLayout.setLayout(0, QFormLayout.SpanningRole, self.gridLayout)

        self.label_7 = QLabel(self.layoutWidget)
        self.label_7.setObjectName("label_7")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_7)

        self.lineEdit_5 = QLineEdit(self.layoutWidget)
        self.lineEdit_5.setObjectName("lineEdit_5")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.lineEdit_5)

        self.toolBox.addItem(
            self.client,
            "\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e \u043a\u043b\u0438\u0435\u043d\u0442\u0435",
        )
        self.layoutWidget1 = QWidget(Dialog_Client)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(80, 230, 183, 30))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton = QPushButton(self.layoutWidget1)
        self.pushButton.setObjectName("pushButton")

        self.horizontalLayout.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.layoutWidget1)
        self.pushButton_2.setObjectName("pushButton_2")

        self.horizontalLayout.addWidget(self.pushButton_2)

        QWidget.setTabOrder(self.lineEdit, self.lineEdit_2)
        QWidget.setTabOrder(self.lineEdit_2, self.lineEdit_3)
        QWidget.setTabOrder(self.lineEdit_3, self.dateEdit)
        QWidget.setTabOrder(self.dateEdit, self.lineEdit_4)
        QWidget.setTabOrder(self.lineEdit_4, self.comboBox)
        QWidget.setTabOrder(self.comboBox, self.comboBox_2)
        QWidget.setTabOrder(self.comboBox_2, self.lineEdit_5)
        QWidget.setTabOrder(self.lineEdit_5, self.pushButton)
        QWidget.setTabOrder(self.pushButton, self.pushButton_2)
        QWidget.setTabOrder(self.pushButton_2, self.pushButton_4)
        QWidget.setTabOrder(self.pushButton_4, self.pushButton_3)

        self.retranslateUi(Dialog_Client)

        self.toolBox.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(Dialog_Client)

    # setupUi

    def retranslateUi(self, Dialog_Client):
        Dialog_Client.setWindowTitle(
            QCoreApplication.translate(
                "Dialog_Client",
                "\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u043e",
                None,
            )
        )
        self.label_2.setText(
            QCoreApplication.translate("Dialog_Client", "\u0418\u043c\u044f *", None)
        )
        self.label_4.setText(
            QCoreApplication.translate("Dialog_Client", "\u041f\u043e\u043b", None)
        )
        self.comboBox.setItemText(
            0, QCoreApplication.translate("Dialog_Client", "-", None)
        )
        self.comboBox.setItemText(
            1, QCoreApplication.translate("Dialog_Client", "\u043c\u0443\u0436", None)
        )
        self.comboBox.setItemText(
            2, QCoreApplication.translate("Dialog_Client", "\u0436\u0435\u043d", None)
        )

        self.label.setText(
            QCoreApplication.translate(
                "Dialog_Client", "\u0424\u0430\u043c\u0438\u043b\u0438\u044f *", None
            )
        )
        self.label_6.setText(
            QCoreApplication.translate(
                "Dialog_Client", "\u0422\u0435\u043b\u0435\u0444\u043e\u043d", None
            )
        )
        self.label_3.setText(
            QCoreApplication.translate(
                "Dialog_Client",
                "\u0414\u0430\u0442\u0430 \u0440\u043e\u0436\u0434\u0435\u043d\u0438\u044f",
                None,
            )
        )
        self.label_5.setText(
            QCoreApplication.translate(
                "Dialog_Client",
                "\u041e\u0442\u0447\u0435\u0441\u0442\u0432\u043e",
                None,
            )
        )
        self.label_8.setText(
            QCoreApplication.translate(
                "Dialog_Client", "\u041b\u044c\u0433\u043e\u0442\u0430", None
            )
        )
        self.comboBox_2.setItemText(
            0, QCoreApplication.translate("Dialog_Client", "-", None)
        )
        self.comboBox_2.setItemText(
            1, QCoreApplication.translate("Dialog_Client", "\u0438", None)
        )
        self.comboBox_2.setItemText(
            2, QCoreApplication.translate("Dialog_Client", "\u043c", None)
        )

        self.pushButton_3.setText(
            QCoreApplication.translate(
                "Dialog_Client",
                "\u041a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u0442\u044c",
                None,
            )
        )
        self.pushButton_4.setText(
            QCoreApplication.translate(
                "Dialog_Client",
                "\u0412\u0441\u0442\u0430\u0432\u0438\u0442\u044c",
                None,
            )
        )
        self.label_7.setText(
            QCoreApplication.translate("Dialog_Client", "E-mail", None)
        )
        self.toolBox.setItemText(
            self.toolBox.indexOf(self.client),
            QCoreApplication.translate(
                "Dialog_Client",
                "\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e \u043a\u043b\u0438\u0435\u043d\u0442\u0435",
                None,
            ),
        )
        self.pushButton.setText(
            QCoreApplication.translate(
                "Dialog_Client",
                "\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c",
                None,
            )
        )
        self.pushButton_2.setText(
            QCoreApplication.translate(
                "Dialog_Client", "\u041e\u0442\u043c\u0435\u043d\u0430", None
            )
        )

    # retranslateUi
