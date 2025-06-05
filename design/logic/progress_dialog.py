from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize, Qt)
from PySide6.QtWidgets import (QLabel, QProgressBar,
                               QVBoxLayout)

class Ui_ProgressDialog(object):
    def setupUi(self, ProgressDialog):
        if not ProgressDialog.objectName():
            ProgressDialog.setObjectName(u"ProgressDialog")
        ProgressDialog.resize(300, 127)
        ProgressDialog.setMinimumSize(QSize(300, 100))
        self.verticalLayout = QVBoxLayout(ProgressDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_status = QLabel(ProgressDialog)
        self.label_status.setObjectName(u"label_status")
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label_status)

        self.progressBar = QProgressBar(ProgressDialog)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)

        self.verticalLayout.addWidget(self.progressBar)


        self.retranslateUi(ProgressDialog)

        QMetaObject.connectSlotsByName(ProgressDialog)
    # setupUi

    def retranslateUi(self, ProgressDialog):
        ProgressDialog.setWindowTitle(QCoreApplication.translate("ProgressDialog", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u0435...", None))
        self.label_status.setText(QCoreApplication.translate("ProgressDialog", u"\u041d\u0430\u0447\u0430\u043b\u043e \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0438...", None))
    # retranslateUi

