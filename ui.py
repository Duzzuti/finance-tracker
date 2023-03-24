from strings import ENG as STRINGS
from fonts import FONTS
from constants import CONSTANTS
from backend import Backend
from ui_datatypes import Combo, Inputs

from PyQt5.QtWidgets import QGridLayout, QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QDialog
from PyQt5.QtWidgets import QSpinBox, QCalendarWidget, QLineEdit, QCompleter, QComboBox, QMessageBox
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QDate

class Window(QDialog):
    def __init__(self, geometry=(100, 100, 600, 400)):
        super().__init__()

        self.title = STRINGS.APP_TITLE
        self.icon = QtGui.QIcon(STRINGS.APP_ICON)
        self.top = geometry[0]
        self.left = geometry[1]
        self.width = geometry[2]
        self.height = geometry[3]

        self.backend = Backend()

        self.CatCombo = Combo(STRINGS.APP_NEW_TRANSACTION_DEFAULT_CATEGORY, self.Ecategory_choosed, self.backend.getCategories)
        self.FtpCombo = Combo(STRINGS.APP_NEW_TRANSACTION_DEFAULT_FTPERSON, self.Eftperson_choosed, self.backend.getPersons)
        self.WhyCombo = Combo(STRINGS.APP_NEW_TRANSACTION_DEFAULT_WHYPERSON, self.Ewhyperson_choosed, self.backend.getPersons)

        self.Inputs = Inputs([STRINGS.APP_NEW_TRANSACTION_PRODUCT_INPUT, STRINGS.APP_NEW_TRANSACTION_CASHFLOW_INPUT], self.activateTransSubmitButton, self.deactivateTransSubmitButton)

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
        self.groupBox_transaction_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION, self)
        self.groupBox_transaction_label.setFont(FONTS.APP_NEW_TRANSACTION)
        self.groupBox_transaction = QGroupBox()
        self.layout_transaction = QVBoxLayout()
        #self.layout_transaction.setSpacing(30)

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

        #********************PRODUCT*********************************
        groupbox_prod_num = QGroupBox()
        hgrid_prod_num = QGridLayout()

        self.trans_product_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_PRODUCT)
        hgrid_prod_num.addWidget(self.trans_product_label, 0, 0)

        self.trans_product_edit = QLineEdit(self)
        self.trans_product_completer = QCompleter(self.backend.getProductNames())
        self.trans_product_edit.setCompleter(self.trans_product_completer)
        self.trans_product_edit.textChanged.connect(self.Echange_product_text)
        hgrid_prod_num.addWidget(self.trans_product_edit, 1, 0)

        #********************NUMBER OF PRODUCTS**********************

        self.trans_number_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_NUMBER)
        hgrid_prod_num.addWidget(self.trans_number_label, 0, 1)

        self.trans_number_spin_box = QSpinBox(self)
        self.trans_number_spin_box.setValue(1)
        self.trans_number_spin_box.setMinimum(1)
        self.trans_number_spin_box.setMaximum(1000000)
        self.trans_number_spin_box.valueChanged.connect(self.Esync_cashflows)
        hgrid_prod_num.addWidget(self.trans_number_spin_box, 1, 1)

        groupbox_prod_num.setLayout(hgrid_prod_num)
        self.layout_transaction.addWidget(groupbox_prod_num)

        #********************CASHFLOW********************************
        grid_cf = QGridLayout()
        groupbox_cf_full = QGroupBox()

        self.trans_cf_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CF)
        self.trans_cf_label.setFont(FONTS.APP_NEW_TRANSACTION_CF)
        grid_cf.addWidget(self.trans_cf_label, 0, 0, 1, 3)

        self.trans_sign_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN)
        grid_cf.addWidget(self.trans_sign_label, 2, 0)

        self.trans_sign = QComboBox(self)
        self.trans_sign.setStyleSheet("combobox-popup: 0;")
        self.trans_sign.addItems([STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_PLUS, STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS])
        self.trans_sign.setCurrentText(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS)
        grid_cf.addWidget(self.trans_sign, 3, 0)

        self.trans_ppp_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_PP)
        grid_cf.addWidget(self.trans_ppp_label, 2, 1)

        self.trans_fullp_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_FULL)
        grid_cf.addWidget(self.trans_fullp_label, 2, 2)

        self.trans_ppp_edit = QLineEdit(self)
        self.trans_ppp_edit.textChanged.connect(self.Eenter_only_numbers)
        self.trans_ppp_edit.textChanged.connect(self.Esync_cashflows)
        self.trans_ppp_edit.textChanged.connect(self.Echanged_cashflow)
        grid_cf.addWidget(self.trans_ppp_edit, 3, 1)

        self.trans_fullp_edit = QLineEdit(self)
        self.trans_fullp_edit.textChanged.connect(self.Eenter_only_numbers)
        self.trans_fullp_edit.textChanged.connect(self.Esync_cashflows)
        self.trans_fullp_edit.textChanged.connect(self.Echanged_cashflow)
        grid_cf.addWidget(self.trans_fullp_edit, 3, 2)

        groupbox_cf_full.setLayout(grid_cf)
        self.layout_transaction.addWidget(groupbox_cf_full)

        #********************CATEGORY********************************
        groupbox_cat = QGroupBox()
        groupbox_cat_choose = QGroupBox()
        groupbox_cat_new = QGroupBox()
        hbox_cat = QHBoxLayout()
        self.vbox_cat = QVBoxLayout()
        vbox_new_cat = QVBoxLayout()

        self.CatCombo.setLayout(self.vbox_cat)
        self.CatCombo.addComboBox()
        self.CatCombo.sort()

        groupbox_cat_choose.setLayout(self.vbox_cat)
        hbox_cat.addWidget(groupbox_cat_choose)

        self.trans_cat_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CAT)
        vbox_new_cat.addWidget(self.trans_cat_label)

        self.trans_cat_edit = QLineEdit(self)
        self.trans_cat_edit.textChanged.connect(self.Echange_cat_text)
        vbox_new_cat.addWidget(self.trans_cat_edit)

        self.trans_cat_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_ADD_CAT, self)
        self.trans_cat_button.setEnabled(False)
        self.trans_cat_button.setToolTip(STRINGS.TOOLTIP_TYPE_3_CHARS)
        self.trans_cat_button.clicked.connect(self.Eadd_category)
        vbox_new_cat.addWidget(self.trans_cat_button)

        self.trans_reset_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_RESET_CAT, self)
        self.trans_reset_button.clicked.connect(self.Ereset_category)
        vbox_new_cat.addWidget(self.trans_reset_button)

        groupbox_cat_new.setLayout(vbox_new_cat)
        hbox_cat.addWidget(groupbox_cat_new)
        groupbox_cat.setLayout(hbox_cat)
        self.layout_transaction.addWidget(groupbox_cat)

        #********************FROM_TO_PERSON********************************
        groupbox_person = QGroupBox()
        groupbox_ftp_choose = QGroupBox()
        groupbox_whyp_choose = QGroupBox()
        groupbox_person_new = QGroupBox()
        grid_person = QGridLayout()
        self.vbox_ftp = QVBoxLayout()
        self.vbox_whyp = QVBoxLayout()
        grid_new_person = QGridLayout()

        self.FtpCombo.setLayout(self.vbox_ftp)
        self.FtpCombo.addComboBox()
        self.FtpCombo.sort()

        groupbox_ftp_choose.setLayout(self.vbox_ftp)
        grid_person.addWidget(groupbox_ftp_choose, 0, 0)

        #********************WHY_PERSON******************************

        self.WhyCombo.setLayout(self.vbox_whyp)
        self.WhyCombo.addComboBox()
        self.WhyCombo.sort()

        groupbox_whyp_choose.setLayout(self.vbox_whyp)
        grid_person.addWidget(groupbox_whyp_choose, 0, 1)

        #********************ADD_PERSON******************************

        self.trans_ftp_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_PERSON)
        grid_new_person.addWidget(self.trans_ftp_label, 0, 0)

        self.trans_person_edit = QLineEdit(self)
        self.trans_person_edit.textChanged.connect(self.Echange_person_text)
        self.trans_person_edit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum))
        grid_new_person.addWidget(self.trans_person_edit, 0, 1)

        self.trans_ftp_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_ADD_PERSON_FTP, self)
        self.trans_ftp_button.setEnabled(False)
        self.trans_ftp_button.setToolTip(STRINGS.TOOLTIP_TYPE_3_CHARS)
        self.trans_ftp_button.clicked.connect(self.Eadd_ftperson)
        grid_new_person.addWidget(self.trans_ftp_button, 1, 0)

        self.trans_whyp_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_ADD_PERSON_WHYP, self)
        self.trans_whyp_button.setEnabled(False)
        self.trans_whyp_button.setToolTip(STRINGS.TOOLTIP_TYPE_3_CHARS)
        self.trans_whyp_button.clicked.connect(self.Eadd_whyperson)
        grid_new_person.addWidget(self.trans_whyp_button, 1, 1)

        self.trans_reset_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_RESET_PERSON, self)
        self.trans_reset_button.clicked.connect(self.Ereset_person)
        grid_new_person.addWidget(self.trans_reset_button, 2, 0, 1, 2)

        groupbox_person_new.setLayout(grid_new_person)
        grid_person.addWidget(groupbox_person_new, 1, 0, 2, 0)
        groupbox_person.setLayout(grid_person)
        self.layout_transaction.addWidget(groupbox_person)

        self.submit_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_SUBMIT)
        self.submit_button.setFont(FONTS.APP_NEW_TRANSACTION_SUBMIT)
        self.submit_button.setEnabled(False)
        self.submit_button.setToolTip(STRINGS.TOOLTIP_SUBMIT_BUTTON)
        self.submit_button.clicked.connect(self.Esubmit_transaction)
        self.layout_transaction.addWidget(self.submit_button)

    def activateTransSubmitButton(self):
        self.submit_button.setEnabled(True)

    def deactivateTransSubmitButton(self):
        self.submit_button.setEnabled(False)


    def Echanged_cashflow(self):
        try:
            ppp = float(self.trans_ppp_edit.text())
            if ppp > 0:
                self.Inputs.setInput(STRINGS.APP_NEW_TRANSACTION_CASHFLOW_INPUT, True)
            else:
                raise ValueError
        except:
            self.Inputs.setInput(STRINGS.APP_NEW_TRANSACTION_CASHFLOW_INPUT, False)
            return

    def Echange_product_text(self):
        text = self.sender().text()
        if len(text) - text.count(" ") > 0:
            self.Inputs.setInput(STRINGS.APP_NEW_TRANSACTION_PRODUCT_INPUT, True)
        else:
            self.Inputs.setInput(STRINGS.APP_NEW_TRANSACTION_PRODUCT_INPUT, False)

    def Eenter_only_numbers(self):
        edit = self.sender()
        if edit.text() == "":
            return
        last_char = edit.text()[-1]
        if last_char in STRINGS.COMMAS:
            if edit.text()[:-1].count(STRINGS.COMMA) == 0:
                edit.setText(edit.text()[:-1] + STRINGS.COMMA)
            else:
                edit.setText(edit.text()[:-1])
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
                if not edit.text() in STRINGS.ZERO_STRINGS:
                    print(STRINGS.ERROR_CONVERT_STRING_TO_INT+edit.text())
                    return
                value = 0
            
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
                if not edit.text() in STRINGS.ZERO_STRINGS:
                    print(STRINGS.ERROR_CONVERT_STRING_TO_INT+edit.text())
                    return
                value = 0
            
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
                if not self.trans_ppp_edit.text() in STRINGS.ZERO_STRINGS:
                    print(STRINGS.ERROR_CONVERT_STRING_TO_INT+self.trans_ppp_edit.text())
                    return
                value = 0
            
            number = edit.value()

            self.trans_fullp_edit.textChanged.disconnect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.disconnect(self.Esync_cashflows)
            self.trans_fullp_edit.setText(str(value*number))
            self.trans_fullp_edit.textChanged.connect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.connect(self.Esync_cashflows)
    
    def Ecategory_choosed(self):
        activated_cat = self.sender()
        text = activated_cat.currentText()
        if not self.CatCombo.isNoDefault():
            return
            
        if CONSTANTS.MAX_CATEGORIES > self.CatCombo.getLen():
            self.CatCombo.addComboBox()

    def Eftperson_choosed(self):
        activated_ftperson = self.sender()
        text = activated_ftperson.currentText()
        if not self.FtpCombo.isNoDefault():
            return
            
        if CONSTANTS.MAX_PERSONS > self.FtpCombo.getLen():
            self.FtpCombo.addComboBox()
    
    def Ewhyperson_choosed(self):
        activated_whyperson = self.sender()
        text = activated_whyperson.currentText()
        if not self.WhyCombo.isNoDefault():
            return
            
        if CONSTANTS.MAX_PERSONS > self.WhyCombo.getLen():
            self.WhyCombo.addComboBox()

    def Echange_cat_text(self):
        text = self.sender().text()
        if len(text) - text.count(" ") >= 3:
            self.trans_cat_button.setEnabled(True)
        else:
            self.trans_cat_button.setEnabled(False)

    def Echange_person_text(self):
        text = self.sender().text()
        if len(text) - text.count(" ") >= 3:
            self.trans_ftp_button.setEnabled(True)
            self.trans_whyp_button.setEnabled(True)
        else:
            self.trans_ftp_button.setEnabled(False)
            self.trans_whyp_button.setEnabled(False)

    def Eadd_category(self):
        text = self.trans_cat_edit.text()
        accepted = self.backend.addCategory(text)
        if accepted == False:
            msgbox = QMessageBox(self)
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.setWindowTitle(STRINGS.ERROR_CATEGORY_NOT_ACCEPTED)
            msgbox.setText(self.backend.getError())
            msgbox.exec()
            return
        
        self.CatCombo.addItem(text)

    def Ereset_category(self):
        self.CatCombo.reset()

    def Eadd_ftperson(self):
        text = self.trans_person_edit.text()
        accepted = self.backend.addPerson(text)
        if accepted == False:
            msgbox = QMessageBox(self)
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.setWindowTitle(STRINGS.ERROR_PERSON_NOT_ACCEPTED)
            msgbox.setText(self.backend.getError())
            msgbox.exec()
            return
        
        self.FtpCombo.addItem(text)
        self.WhyCombo.addItem(text, set_item=False)
    
    def Eadd_whyperson(self):
        text = self.trans_person_edit.text()
        accepted = self.backend.addPerson(text)
        if accepted == False:
            msgbox = QMessageBox(self)
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.setWindowTitle(STRINGS.ERROR_PERSON_NOT_ACCEPTED)
            msgbox.setText(self.backend.getError())
            msgbox.exec()
            return
        
        self.FtpCombo.addItem(text, set_item=False)
        self.WhyCombo.addItem(text)

    def Ereset_person(self):
        self.WhyCombo.reset()
        self.FtpCombo.reset()

    def Esubmit_transaction(self):
        date = self.trans_date_edit.selectedDate().toPyDate()
        number = int(self.trans_number_spin_box.text())
        product = self.trans_product_edit.text()
        sign = self.trans_sign.currentText()
        try:
            full_cashflow = float(self.trans_fullp_edit.text())
        except:
            raise ValueError(STRINGS.ERROR_WRONG_CF_DATA+self.trans_fullp_edit.text())
        
        if sign == STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS:
            full_cashflow = -full_cashflow

        categories = self.CatCombo.getChoosenItems()
        ftpersons = self.FtpCombo.getChoosenItems()
        whypersons = self.WhyCombo.getChoosenItems()

        self.backend.addTransaction(date, product, number, full_cashflow, categories, ftpersons, whypersons)

