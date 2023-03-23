import datetime
import time
from strings import ENG
from fonts import FONTS
from constants import CONSTANTS
from backend import Backend

from PyQt5.QtWidgets import QRadioButton, QGridLayout, QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QDialog
from PyQt5.QtWidgets import QSpinBox, QCalendarWidget, QLineEdit, QCompleter, QComboBox, QMessageBox
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

        self.category_boxes = []

        self.backend = Backend()

        self.InitWindow()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        #self.setGeometry(self.left, self.top, self.width, self.height)
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
        self.layout_transaction.setSpacing(30)

        self.addWidgets()

        self.groupBox_transaction.setLayout(self.layout_transaction)
        self.grid.addWidget(self.groupBox_transaction_label, 0, 0)
        self.grid.addWidget(self.groupBox_transaction, 1, 0)
    
    def addWidgets(self):
        #********************CALENDAR********************************
        self.trans_date_edit = QCalendarWidget(self)
        self.trans_date_edit.setMinimumDate(QDate(1900, 1, 1))
        self.trans_date_edit.setMaximumDate(QDate.currentDate())
        self.trans_date_edit.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        #self.trans_date_edit.setMaximumWidth(400)
        self.layout_transaction.addWidget(self.trans_date_edit)

        #********************NUMBER OF PRODUCTS**********************
        vbox_num = QVBoxLayout()
        groupbox_num = QGroupBox()

        self.trans_number_label = QLabel(ENG.APP_LABEL_NEW_TRANSACTION_NUMBER)
        vbox_num.addWidget(self.trans_number_label)

        self.trans_number_spin_box = QSpinBox(self)
        self.trans_number_spin_box.setValue(1)
        self.trans_number_spin_box.setMinimum(1)
        self.trans_number_spin_box.setMaximum(1000000)
        self.trans_number_spin_box.valueChanged.connect(self.Esync_cashflows)
        vbox_num.addWidget(self.trans_number_spin_box)

        groupbox_num.setLayout(vbox_num)
        self.layout_transaction.addWidget(groupbox_num)

        #********************CASHFLOW********************************
        vbox_cf = QVBoxLayout()
        groupbox_cf_full = QGroupBox()

        self.trans_cf_label = QLabel(ENG.APP_LABEL_NEW_TRANSACTION_CF)
        vbox_cf.addWidget(self.trans_cf_label)
        
        groupbox_cf = QGroupBox()
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
        vbox_cf.addWidget(groupbox_cf)
        groupbox_cf_full.setLayout(vbox_cf)
        self.layout_transaction.addWidget(groupbox_cf_full)

        #********************PRODUCT*********************************
        vbox = QVBoxLayout()
        groupbox_product = QGroupBox()

        self.trans_product_label = QLabel(ENG.APP_LABEL_NEW_TRANSACTION_PRODUCT)
        vbox.addWidget(self.trans_product_label)

        self.trans_product_edit = QLineEdit(self)
        self.trans_product_completer = QCompleter(self.backend.getProductNames())
        self.trans_product_edit.setCompleter(self.trans_product_completer)
        vbox.addWidget(self.trans_product_edit)

        groupbox_product.setLayout(vbox)
        self.layout_transaction.addWidget(groupbox_product)

        #********************CATEGORY********************************
        groupbox_cat = QGroupBox()
        groupbox_cat_choose = QGroupBox()
        groupbox_cat_new = QGroupBox()
        hbox_cat = QHBoxLayout()
        self.vbox_cat = QVBoxLayout()
        vbox_new_cat = QVBoxLayout()

        self.trans_main_category = QComboBox(self)
        self.trans_main_category.setMaxVisibleItems(20)
        self.trans_main_category.setStyleSheet("combobox-popup: 0;")
        self.trans_main_category.addItem(ENG.APP_NEW_TRANSACTION_DEFAULT_CATEGORY)
        self.trans_main_category.setCurrentText(ENG.APP_NEW_TRANSACTION_DEFAULT_CATEGORY)
        self.trans_main_category.addItems(self.backend.getCategories())
        self.trans_main_category.currentTextChanged.connect(self.Ecategory_choosed)
        self.vbox_cat.addWidget(self.trans_main_category)

        self.category_boxes.append(self.trans_main_category)
        self.sortCombos()

        groupbox_cat_choose.setLayout(self.vbox_cat)
        hbox_cat.addWidget(groupbox_cat_choose)

        self.trans_cat_label = QLabel(ENG.APP_LABEL_NEW_TRANSACTION_CAT)
        vbox_new_cat.addWidget(self.trans_cat_label)

        self.trans_cat_edit = QLineEdit(self)
        self.trans_cat_edit.textChanged.connect(self.Echange_cat_text)
        vbox_new_cat.addWidget(self.trans_cat_edit)

        self.trans_cat_button = QPushButton(ENG.APP_BUTTON_NEW_TRANSACTION_ADD_CAT, self)
        self.trans_cat_button.setEnabled(False)
        self.trans_cat_button.setToolTip("Type at least 3 characters")
        self.trans_cat_button.clicked.connect(self.Eadd_category)
        vbox_new_cat.addWidget(self.trans_cat_button)

        self.trans_reset_button = QPushButton(ENG.APP_BUTTON_NEW_TRANSACTION_RESET_CAT, self)
        self.trans_reset_button.clicked.connect(self.Ereset_category)
        vbox_new_cat.addWidget(self.trans_reset_button)

        groupbox_cat_new.setLayout(vbox_new_cat)
        hbox_cat.addWidget(groupbox_cat_new)
        groupbox_cat.setLayout(hbox_cat)
        self.layout_transaction.addWidget(groupbox_cat)


    def addCategoryToCombos(self, category_text):
        new_cat_set = False
        for combo in self.category_boxes:
            combo.addItem(category_text)
            if new_cat_set == False and combo.currentText() == ENG.APP_NEW_TRANSACTION_DEFAULT_CATEGORY:
                new_cat_set = True
                combo.setCurrentText(category_text)
        self.sortCombos()

    def sortCombos(self):
        categories = [self.category_boxes[0].itemText(i) for i in range(self.category_boxes[0].count())]
        categories.sort(key=lambda x: "0" if x == ENG.APP_NEW_TRANSACTION_DEFAULT_CATEGORY else x.lower())
        for combo in self.category_boxes:
            combo.currentTextChanged.disconnect(self.Ecategory_choosed)
            text = combo.currentText()
            combo.clear()
            combo.addItems(categories)
            combo.setCurrentText(text)
            combo.currentTextChanged.connect(self.Ecategory_choosed)


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
    
    def Ecategory_choosed(self):
        activated_cat = self.sender()
        text = activated_cat.currentText()
        if text == ENG.APP_NEW_TRANSACTION_DEFAULT_CATEGORY:
            return
        for combo in self.category_boxes:
            if combo.currentText() == ENG.APP_NEW_TRANSACTION_DEFAULT_CATEGORY:
                return
            
        if CONSTANTS.MAX_CATEGORIES > len(self.category_boxes):
            category = QComboBox(self)
            category.setMaxVisibleItems(20)
            category.setStyleSheet("combobox-popup: 0;")
            category.addItem(ENG.APP_NEW_TRANSACTION_DEFAULT_CATEGORY)
            category.setCurrentText(ENG.APP_NEW_TRANSACTION_DEFAULT_CATEGORY)
            category.addItems(self.backend.getCategories())
            category.currentTextChanged.connect(self.Ecategory_choosed)
            self.vbox_cat.addWidget(category)

            self.category_boxes.append(category)

    def Echange_cat_text(self):
        text = self.sender().text()
        if len(text) - text.count(" ") >= 3:
            self.trans_cat_button.setEnabled(True)
        else:
            self.trans_cat_button.setEnabled(False)

    def Eadd_category(self):
        text = self.trans_cat_edit.text()
        accepted = self.backend.addCategory(text)
        if accepted == False:
            msgbox = QMessageBox(self)
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.setWindowTitle("Category is not accepted")
            msgbox.setText(self.backend.getError())
            msgbox.exec()
            return
        
        self.addCategoryToCombos(text)

    def Ereset_category(self):
        combo1 = self.category_boxes[0]
        combo1.setCurrentText(ENG.APP_NEW_TRANSACTION_DEFAULT_CATEGORY)
        for combo in self.category_boxes[1:]:
            self.vbox_cat.removeWidget(combo)
            combo.deleteLater()
        self.category_boxes = [combo1]
