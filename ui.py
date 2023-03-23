import datetime
from strings import ENG
from backend import Backend

from PyQt5.QtWidgets import QRadioButton, QGridLayout, QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QDialog
from PyQt5.QtWidgets import QSpinBox, QCalendarWidget, QLineEdit, QCompleter
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRect, QDate
from PyQt5.QtGui import QPixmap

class Window(QDialog):
    def __init__(self, geometry=(100, 100, 600, 400)):
        super().__init__()

        self.title = ENG.APP_TITLE
        self.icon = QtGui.QIcon(ENG.APP_ICON)
        self.top = geometry[0]
        self.left = geometry[1]
        self.width = geometry[2]
        self.height = geometry[3]

        self.backend = Backend()

        self.InitWindow()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(self.icon)
        self.grid = QGridLayout()

        self.createLayout()

        self.setLayout(self.grid)

        self.show()
    
    def createLayout(self):
        self.groupBox_transaction = QGroupBox(ENG.APP_LABEL_NEW_TRANSACTION)
        self.gridlayout_transaction = QGridLayout()

        self.addWidgets()
        self.groupBox_transaction.setLayout(self.gridlayout_transaction)
        self.grid.addWidget(self.groupBox_transaction, 0, 0)
    
    def addWidgets(self):
        self.trans_date_edit = QCalendarWidget(self)
        self.trans_date_edit.setMinimumDate(QDate(1900, 1, 1))
        self.trans_date_edit.setMaximumDate(QDate.currentDate())
        self.trans_date_edit.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        #self.trans_date_edit.setMaximumWidth(400)
        self.gridlayout_transaction.addWidget(self.trans_date_edit, 0, 0)

        self.trans_number_spin_box = QSpinBox(self)
        self.trans_number_spin_box.setValue(1)
        self.gridlayout_transaction.addWidget(self.trans_number_spin_box, 1, 0)

        self.trans_ppp_edit = QLineEdit(self)
        self.trans_ppp_edit.textChanged.connect(self.Eenter_only_numbers)
        self.gridlayout_transaction.addWidget(self.trans_ppp_edit, 2, 0)

        self.trans_fullp_edit = QLineEdit(self)
        self.trans_fullp_edit.textChanged.connect(self.Eenter_only_numbers)
        self.gridlayout_transaction.addWidget(self.trans_fullp_edit, 3, 0)

        self.trans_product_edit = QLineEdit(self)
        self.trans_product_completer = QCompleter(self.backend.getProductNames())
        self.trans_product_edit.setCompleter(self.trans_product_completer)
        self.gridlayout_transaction.addWidget(self.trans_product_edit, 4, 0)


    def Eenter_only_numbers(self):
        self.comma = ','
        but = self.sender()
        if but.text() == "":
            return
        last_char = but.text()[-1]
        if last_char in [".", ","]:
            if but.text()[:-1].count(self.comma) == 0:
                but.setText(but.text()[:-1] + self.comma)
            else:
                but.setText(but.text()[:-1])
            return
        if not last_char in map(lambda x: str(x), range(10)):
            but.setText(but.text()[:-1])
            return
      