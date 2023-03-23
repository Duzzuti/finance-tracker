import datetime
from strings import ENG
from fonts import FONTS
from backend import Backend

from PyQt5.QtWidgets import QRadioButton, QGridLayout, QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QDialog
from PyQt5.QtWidgets import QSpinBox, QCalendarWidget, QLineEdit, QCompleter
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRect, QDate
from PyQt5.QtGui import QPixmap, QFont

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
        self.groupBox_transaction_label = QLabel(ENG.APP_LABEL_NEW_TRANSACTION, self)
        self.groupBox_transaction_label.setFont(FONTS.APP_NEW_TRANSACTION)
        self.groupBox_transaction = QGroupBox()
        self.layout_transaction = QVBoxLayout()

        self.addWidgets()
        self.groupBox_transaction.setLayout(self.layout_transaction)
        self.grid.addWidget(self.groupBox_transaction_label, 0, 0)
        self.grid.addWidget(self.groupBox_transaction, 1, 0)
    
    def addWidgets(self):
        self.trans_date_edit = QCalendarWidget(self)
        self.trans_date_edit.setMinimumDate(QDate(1900, 1, 1))
        self.trans_date_edit.setMaximumDate(QDate.currentDate())
        self.trans_date_edit.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        #self.trans_date_edit.setMaximumWidth(400)
        self.layout_transaction.addWidget(self.trans_date_edit)

        self.trans_number_spin_box = QSpinBox(self)
        self.trans_number_spin_box.setValue(1)
        self.trans_number_spin_box.setMaximum(1000000)
        self.trans_number_spin_box.valueChanged.connect(self.Esync_cashflows)
        self.layout_transaction.addWidget(self.trans_number_spin_box)

        groupbox_cf = QGroupBox(ENG.APP_LABEL_NEW_TRANSACTION_CF)
        cf_grid = QGridLayout()

        self.trans_ppp_label = QLabel(ENG.APP_LABEL_NEW_TRANSACTION_CF_PP)
        cf_grid.addWidget(self.trans_ppp_label, 0, 0)

        self.trans_fullp_label = QLabel(ENG.APP_LABEL_NEW_TRANSACTION_CF_FULL)
        cf_grid.addWidget(self.trans_fullp_label, 0, 1)

        self.trans_ppp_edit = QLineEdit(self)
        self.trans_ppp_edit.textChanged.connect(self.Eenter_only_numbers)
        self.trans_ppp_edit.textChanged.connect(self.Esync_cashflows)
        cf_grid.addWidget(self.trans_ppp_edit, 1, 0)

        self.trans_fullp_edit = QLineEdit(self)
        self.trans_fullp_edit.textChanged.connect(self.Eenter_only_numbers)
        self.trans_fullp_edit.textChanged.connect(self.Esync_cashflows)
        cf_grid.addWidget(self.trans_fullp_edit, 1,1)

        groupbox_cf.setLayout(cf_grid)
        self.layout_transaction.addWidget(groupbox_cf)

        self.trans_product_edit = QLineEdit(self)
        self.trans_product_completer = QCompleter(self.backend.getProductNames())
        self.trans_product_edit.setCompleter(self.trans_product_completer)
        self.layout_transaction.addWidget(self.trans_product_edit)


    def Eenter_only_numbers(self):
        self.comma = '.'
        edit = self.sender()
        if edit.text() == "":
            return
        last_char = edit.text()[-1]
        if last_char in [".", ","]:
            if edit.text()[:-1].count(self.comma) == 0:
                edit.setText(edit.text()[:-1] + self.comma)
            else:
                edit.setText(edit.text()[:-1])
            return
        if edit.text() == "-":
            return
        if not last_char in map(lambda x: str(x), range(10)):
            edit.setText(edit.text()[:-1])
            return
      
    def Esync_cashflows(self):
        edit = self.sender()
        if edit == self.trans_ppp_edit:
            try:
                value = float(edit.text())
            except:
                if not edit.text() in ["-", ""]:
                    print("Could not convert str to int "+edit.text())
                return
            
            number = self.trans_number_spin_box.value()

            self.trans_fullp_edit.textChanged.disconnect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.disconnect(self.Esync_cashflows)
            self.trans_fullp_edit.setText(str(value*number))
            self.trans_fullp_edit.textChanged.connect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.connect(self.Esync_cashflows)
        
        if edit == self.trans_fullp_edit:
            try:
                value = float(edit.text())
            except:
                if not edit.text() in ["-", ""]:
                    print("Could not convert str to int "+edit.text())
                return
            
            number = self.trans_number_spin_box.value()

            self.trans_fullp_edit.textChanged.disconnect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.disconnect(self.Esync_cashflows)
            self.trans_ppp_edit.setText(str(value/number))
            self.trans_fullp_edit.textChanged.connect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.connect(self.Esync_cashflows)

        if edit == self.trans_number_spin_box:
            try:
                value = float(self.trans_ppp_edit.text())
            except:
                if not self.trans_ppp_edit.text() in ["-", ""]:
                    print("Could not convert str to int "+self.trans_ppp_edit.text())
                return
            
            number = edit.value()

            self.trans_fullp_edit.textChanged.disconnect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.disconnect(self.Esync_cashflows)
            self.trans_fullp_edit.setText(str(value*number))
            self.trans_fullp_edit.textChanged.connect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.connect(self.Esync_cashflows)