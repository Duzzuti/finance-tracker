"""
This module provides the ui of the programm
"""

import inspect
from strings import ENG as STRINGS
from fonts import FONTS
from constants import CONSTANTS
from backend import Backend
from ui_datatypes import Combo, Inputs

from PyQt5.QtWidgets import QGridLayout, QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QWidget
from PyQt5.QtWidgets import QSpinBox, QCalendarWidget, QLineEdit, QCompleter, QComboBox, QMessageBox, QScrollArea, QSizePolicy
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QDate, Qt

class Window(QDialog):
    """
    The window class contains the main Window of the Application using Pyqt5
    the window class talks with the backend to display the right things
    The app consists of a object of class window
    """
    def __init__(self, geometry=(100, 100, 600, 400)):
        """
        basic constructor is building the main window
        :param geometry: list<int<top>, int<left>, int<width>, int<height>>
        :return: void
        """
        super().__init__()  #initializes the Base Class (QDialog)
        assert(len(geometry) == 4 and all(map(lambda x: int == type(x), geometry)) == True), STRINGS.ERROR_WRONG_FORMAT_GEOMETRY+str(geometry)
        assert(all(map(lambda x: x > 0, geometry))), STRINGS.ERROR_GEOMETRY_LESS_ZERO+str(geometry)

        self.title = STRINGS.APP_TITLE
        self.icon = QtGui.QIcon(STRINGS.APP_ICON)
        self.top = geometry[0]
        self.left = geometry[1]
        self.width = geometry[2]
        self.height = geometry[3]

        self.backend = Backend(self)    #sets up the backend object to perform backend requests in the ui

        #sets up the ComboBox Objects
        #if you choose a category or a person a new ComboBox is spawning
        #if you add a category, its added on all category comboBoxes
        #these functionalities are encapsulated in these objects
        self.CatCombo = Combo(STRINGS.APP_NEW_TRANSACTION_DEFAULT_CATEGORY, self.Ecategory_choosed, self.backend.getCategories)
        self.FtpCombo = Combo(STRINGS.APP_NEW_TRANSACTION_DEFAULT_FTPERSON, self.Eftperson_choosed, self.backend.getPersonNames)
        self.WhyCombo = Combo(STRINGS.APP_NEW_TRANSACTION_DEFAULT_WHYPERSON, self.Ewhyperson_choosed, self.backend.getPersonNames)

        #input object is responsible for activating the submit button if all required inputs are given
        self.Inputs = Inputs([STRINGS.APP_NEW_TRANSACTION_PRODUCT_INPUT, STRINGS.APP_NEW_TRANSACTION_CASHFLOW_INPUT], self.activateTransSubmitButton, self.deactivateTransSubmitButton)

        #build the window
        self.InitWindow()

    def InitWindow(self):
        """
        this method is building the window
        :return: void
        """
        self.setWindowTitle(self.title)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(self.icon)
        self.grid = QGridLayout()       #sets the layout of the complete window

        self.createLayout()             #create the layout with all components

        self.setLayout(self.grid)

        self.show() #show the window
    
    def createLayout(self):
        """
        creates layout components and add UI components to that layout
        build the window
        :return: void
        """
        assert("grid" in map(lambda x: x[0], vars(self).items())), STRINGS.ERROR_GRID_NOT_DEFINED

        self.groupBox_transaction_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION, self)
        self.groupBox_transaction_label.setFont(FONTS.APP_NEW_TRANSACTION)
        self.groupBox_transaction = QGroupBox()
        self.layout_transaction = QVBoxLayout()
        
        self.groupBox_lastTransactions_label = QLabel(STRINGS.APP_LABEL_LAST_TRANSACTIONS, self)
        self.groupBox_lastTransactions_label.setFont(FONTS.APP_NEW_TRANSACTION)
        self.groupBox_lastTransactions = QGroupBox()
        self.layout_lastTransaction = QVBoxLayout()

        #adds the Widgets to the "new transaction" part of the window
        self.addWidgetsNewTrans()
        self.addWidgetsLastTrans()

        #sets the layouts and add these to the grid
        self.groupBox_transaction.setLayout(self.layout_transaction)
        self.grid.addWidget(self.groupBox_transaction_label, 0, 0)
        self.grid.addWidget(self.groupBox_transaction, 1, 0)

        self.groupBox_lastTransactions.setLayout(self.layout_lastTransaction)
        self.grid.addWidget(self.groupBox_lastTransactions_label, 0, 1)
        self.grid.addWidget(self.groupBox_lastTransactions, 1, 1)

    def addWidgetsNewTrans(self):
        """
        adds the Widgets to the "new transaction" part of the window
        builds up the "new transaction" part of the window and connects these widgets with the backend
        handles the behavior of these widgets too
        :return: void
        """

        #********************CALENDAR********************************
        self.trans_date_edit = QCalendarWidget(self)
        self.trans_date_edit.setMinimumDate(QDate(1900, 1, 1))
        self.trans_date_edit.setMaximumDate(QDate.currentDate())
        #removes the vertical header (week of the year) to save space
        self.trans_date_edit.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        #self.trans_date_edit.setMaximumWidth(400)
        self.layout_transaction.addWidget(self.trans_date_edit)

        #********************PRODUCT*********************************
        #holds the product label and input as well as the number label and input
        groupbox_prod_num = QGroupBox()
        hgrid_prod_num = QGridLayout()

        #product label
        self.trans_product_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_PRODUCT)
        hgrid_prod_num.addWidget(self.trans_product_label, 0, 0)

        #product input
        self.trans_product_edit = QLineEdit(self)
        self.trans_product_completer = QCompleter(self.backend.getProductNames())
        self.trans_product_edit.setCompleter(self.trans_product_completer)      #add an autocompleter
        self.trans_product_edit.textChanged.connect(self.Echange_product_text)
        hgrid_prod_num.addWidget(self.trans_product_edit, 1, 0)

        #********************NUMBER OF PRODUCTS**********************
        #number of products label
        self.trans_number_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_NUMBER)
        hgrid_prod_num.addWidget(self.trans_number_label, 0, 1)

        #number of products input
        self.trans_number_spin_box = QSpinBox(self)
        self.trans_number_spin_box.setValue(1)
        self.trans_number_spin_box.setMinimum(1)        #set minimum and maximum values
        self.trans_number_spin_box.setMaximum(1000000)
        self.trans_number_spin_box.valueChanged.connect(self.Esync_cashflows)
        hgrid_prod_num.addWidget(self.trans_number_spin_box, 1, 1)

        #completes this group
        groupbox_prod_num.setLayout(hgrid_prod_num)
        self.layout_transaction.addWidget(groupbox_prod_num)

        #********************CASHFLOW********************************
        #holds the labels and inputs for sign, cashflow per product and cashflow for transaction
        grid_cf = QGridLayout()
        groupbox_cf_full = QGroupBox()

        #meta label for the group
        self.trans_cf_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CF)
        self.trans_cf_label.setFont(FONTS.APP_NEW_TRANSACTION_CF)
        grid_cf.addWidget(self.trans_cf_label, 0, 0, 1, 3)

        #sign label
        self.trans_sign_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN)
        grid_cf.addWidget(self.trans_sign_label, 2, 0)

        #sign input
        self.trans_sign = QComboBox(self)
        self.trans_sign.setStyleSheet("combobox-popup: 0;")
        self.trans_sign.addItems([STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_PLUS, STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS])
        self.trans_sign.setCurrentText(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS)
        grid_cf.addWidget(self.trans_sign, 3, 0)

        #price per product label
        self.trans_ppp_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_PP)
        grid_cf.addWidget(self.trans_ppp_label, 2, 1)

        #full price label
        self.trans_fullp_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_FULL)
        grid_cf.addWidget(self.trans_fullp_label, 2, 2)

        #price per product input
        self.trans_ppp_edit = QLineEdit(self)
        self.trans_ppp_edit.textChanged.connect(self.Eenter_only_numbers)
        self.trans_ppp_edit.textChanged.connect(self.Esync_cashflows)
        self.trans_ppp_edit.textChanged.connect(self.Echanged_cashflow)
        grid_cf.addWidget(self.trans_ppp_edit, 3, 1)

        #full price input
        self.trans_fullp_edit = QLineEdit(self)
        self.trans_fullp_edit.textChanged.connect(self.Eenter_only_numbers)
        self.trans_fullp_edit.textChanged.connect(self.Esync_cashflows)
        self.trans_fullp_edit.textChanged.connect(self.Echanged_cashflow)
        grid_cf.addWidget(self.trans_fullp_edit, 3, 2)

        #sets up the layout for this group
        groupbox_cf_full.setLayout(grid_cf)
        self.layout_transaction.addWidget(groupbox_cf_full)

        #********************CATEGORY********************************
        groupbox_cat = QGroupBox()          #group for the whole category block
        groupbox_cat_choose = QGroupBox()   #group for the ComboBoxes where you can choose from
        groupbox_cat_new = QGroupBox()      #group for the components to add new categories
        hbox_cat = QHBoxLayout()            #layout for the whole category block
        self.vbox_cat = QVBoxLayout()       #layout for the ComboBoxes where you can choose from
        vbox_new_cat = QVBoxLayout()        #layout for the components to add new categories

        #Setting up the object for the category combo boxes
        self.CatCombo.setLayout(self.vbox_cat)
        self.CatCombo.addComboBox()     #adds a first box
        self.CatCombo.sort()

        #sets the layout for the ComboBoxes
        groupbox_cat_choose.setLayout(self.vbox_cat)
        hbox_cat.addWidget(groupbox_cat_choose)

        #add new category label
        self.trans_cat_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CAT)
        vbox_new_cat.addWidget(self.trans_cat_label)

        #add new category input
        self.trans_cat_edit = QLineEdit(self)
        self.trans_cat_edit.textChanged.connect(self.Echange_cat_text)
        vbox_new_cat.addWidget(self.trans_cat_edit)

        #add new category button
        self.trans_cat_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_ADD_CAT, self)
        #at default the button is disabled, you need to type at least 3 characters to activate it
        self.trans_cat_button.setEnabled(False)     
        self.trans_cat_button.setToolTip(STRINGS.TOOLTIP_TYPE_3_CHARS)
        self.trans_cat_button.clicked.connect(self.Eadd_category)
        vbox_new_cat.addWidget(self.trans_cat_button)

        #reset category button
        self.trans_reset_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_RESET_CAT, self)
        self.trans_reset_button.clicked.connect(self.Ereset_category)
        vbox_new_cat.addWidget(self.trans_reset_button)

        #sets the layouts of the category group
        groupbox_cat_new.setLayout(vbox_new_cat)
        hbox_cat.addWidget(groupbox_cat_new)
        groupbox_cat.setLayout(hbox_cat)
        self.layout_transaction.addWidget(groupbox_cat)

        #********************PERSONS*********************************
        groupbox_person = QGroupBox()       #group for the whole person choose and add block
        groupbox_ftp_choose = QGroupBox()   #group for the from/to person choose block
        groupbox_whyp_choose = QGroupBox()  #group for the why person choose block
        groupbox_person_new = QGroupBox()   #group for add person block
        grid_person = QGridLayout()         #layout for the whole person choose and add block
        self.vbox_ftp = QVBoxLayout()       #layout for the from/to person choose block
        self.vbox_whyp = QVBoxLayout()      #layout for the why person choose block
        grid_new_person = QGridLayout()     #layout for add person block

        #********************FROM_TO_PERSON**************************
        #Setting up the object for the from/to person combo boxes
        self.FtpCombo.setLayout(self.vbox_ftp)
        self.FtpCombo.addComboBox()     #add the first box
        self.FtpCombo.sort()

        #set the layout for the from/to person group
        groupbox_ftp_choose.setLayout(self.vbox_ftp)
        grid_person.addWidget(groupbox_ftp_choose, 0, 0)

        #********************WHY_PERSON******************************
        #Setting up the object for the why person combo boxes
        self.WhyCombo.setLayout(self.vbox_whyp)
        self.WhyCombo.addComboBox()     #add the first box
        self.WhyCombo.sort()

        #set the layout for the why person group
        groupbox_whyp_choose.setLayout(self.vbox_whyp)
        grid_person.addWidget(groupbox_whyp_choose, 0, 1)

        #********************ADD_RESET_PERSON************************
        #add person label
        self.trans_ftp_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_PERSON)
        grid_new_person.addWidget(self.trans_ftp_label, 0, 0)

        #add person input
        self.trans_person_edit = QLineEdit(self)
        self.trans_person_edit.textChanged.connect(self.Echange_person_text)
        #sets the size policies for a better look
        self.trans_person_edit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum))
        grid_new_person.addWidget(self.trans_person_edit, 0, 1)

        #add person to from/to persons button
        self.trans_ftp_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_ADD_PERSON_FTP, self)
        #at default the button is disabled, you need to type at least 3 characters to activate it
        self.trans_ftp_button.setEnabled(False) 
        self.trans_ftp_button.setToolTip(STRINGS.TOOLTIP_TYPE_3_CHARS)
        self.trans_ftp_button.clicked.connect(self.Eadd_ftperson)
        grid_new_person.addWidget(self.trans_ftp_button, 1, 0)

        #add person to why persons button
        self.trans_whyp_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_ADD_PERSON_WHYP, self)
        #at default the button is disabled, you need to type at least 3 characters to activate it
        self.trans_whyp_button.setEnabled(False)
        self.trans_whyp_button.setToolTip(STRINGS.TOOLTIP_TYPE_3_CHARS)
        self.trans_whyp_button.clicked.connect(self.Eadd_whyperson)
        grid_new_person.addWidget(self.trans_whyp_button, 1, 1)

        #reset persons button
        self.trans_reset_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_RESET_PERSON, self)
        self.trans_reset_button.clicked.connect(self.Ereset_person)
        grid_new_person.addWidget(self.trans_reset_button, 2, 0, 1, 2)

        #sets the layouts for the persons section
        groupbox_person_new.setLayout(grid_new_person)
        grid_person.addWidget(groupbox_person_new, 1, 0, 2, 0)
        groupbox_person.setLayout(grid_person)
        self.layout_transaction.addWidget(groupbox_person)

        #********************SUBMIT_BUTTON***************************
        #submit transaction button
        self.submit_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_SUBMIT)
        self.submit_button.setFont(FONTS.APP_NEW_TRANSACTION_SUBMIT)
        #at default the button is disabled, you need to fill out all required fields to activate it
        #this is monitored by the input object
        self.submit_button.setEnabled(False)
        self.submit_button.setToolTip(STRINGS.TOOLTIP_SUBMIT_BUTTON)
        self.submit_button.clicked.connect(self.Esubmit_transaction)
        self.layout_transaction.addWidget(self.submit_button)

    def addWidgetsLastTrans(self):
        self.scrollarea = QScrollArea()
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.scroll_widget = QWidget()
        self.scroll_vbox = QVBoxLayout()
        self.scroll_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.updateLastTrans()

        self.scroll_widget.setLayout(self.scroll_vbox)
        self.scrollarea.setWidget(self.scroll_widget)
        self.layout_lastTransaction.addWidget(self.scrollarea)

    def updateLastTrans(self):

        for i in reversed(range(self.scroll_vbox.count())): 
            widget = self.scroll_vbox.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        for transaction in self.backend.getTransactions():
            element_button = self.getTransactionButton(transaction)
            self.scroll_vbox.addWidget(element_button)  
        #self.scrollarea.setMinimumWidth(int(element_button.size().width()*1.1))  
   
    def getTransactionButton(self, transaction):
        element_button = QPushButton()
        element_layout = QGridLayout()

        label = QLabel(transaction.date.strftime("[%d %b %Y]")+"\t"+str(transaction.cashflow)+STRINGS.CURRENCY+"\t"+transaction.product.name, self)

        element_layout.addWidget(label, 0, 0)

        element_button.setLayout(element_layout)
        element_button.adjustSize()
        return element_button

    def activateTransSubmitButton(self):
        """
        activates the button which submits a new transaction
        :return: void
        """
        self.submit_button.setEnabled(True)

    def deactivateTransSubmitButton(self):
        """
        deactivates the button which submits a new transaction
        :return: void
        """
        self.submit_button.setEnabled(False)


    def Echanged_cashflow(self):
        """
        Event handler
        activates if the cashflow changed
        if a valid cashflow is detected sets the required field cashflow to true, if not its set to false
        (neccessary to activate the submit button)
        :return: void
        """
        try:
            fullp = float(self.trans_fullp_edit.text())
            if fullp > 0:   #a cashflow bigger 0 is required
                self.Inputs.setInput(STRINGS.APP_NEW_TRANSACTION_CASHFLOW_INPUT, True)
            else:
                raise ValueError
        except:
            self.Inputs.setInput(STRINGS.APP_NEW_TRANSACTION_CASHFLOW_INPUT, False)

    def Echange_product_text(self):
        """
        Event handler
        activates if the product text changed
        if a valid product name is detected sets the required field product to true, if not its set to false
        (neccessary to activate the submit button)
        :return: void
        """
        assert(type(self.sender()) == QLineEdit), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        text = self.sender().text()
        if len(text) - text.count(" ") > 0: #at least one visible character is required
            self.Inputs.setInput(STRINGS.APP_NEW_TRANSACTION_PRODUCT_INPUT, True)
        else:
            self.Inputs.setInput(STRINGS.APP_NEW_TRANSACTION_PRODUCT_INPUT, False)

    def Eenter_only_numbers(self):
        """
        Event handler
        activates if the text in an input changed
        if a non number related symbol is entered, this handler deletes it.
        Makes sure that the input is a non negative valid float
        :return: void
        """
        assert(type(self.sender()) == QLineEdit), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        edit = self.sender()
        if edit.text() == "":
            return
        last_char = edit.text()[-1]
        if last_char in STRINGS.COMMAS:     #only commas are allowed 
            #sets the right comma; the method accepts multiple commas given in COMMAS
            #but we will display only one COMMA. (other commas are replaced)
            if edit.text()[:-1].count(STRINGS.COMMA) == 0:
                edit.setText(edit.text()[:-1] + STRINGS.COMMA)
            else:
                edit.setText(edit.text()[:-1])
            return
        if not last_char in map(lambda x: str(x), range(10)):   #or numbers
            edit.setText(edit.text()[:-1])
            return

    def Esync_cashflows(self):
        """
        Event handler
        activates if the text in an cashflow input changed (or product number)
        syncs the cashflow by taking the changed input and the product number as the base to calculate the other cashflow input
        if the product number is changed, the base is the price per product and the full price gets synced
        :return: void
        """
        assert(self.sender() in (self.trans_ppp_edit, self.trans_fullp_edit, self.trans_number_spin_box)), STRINGS.ERROR_WRONG_SENDER+inspect.stack()[0][3]+", "+self.sender()
        edit = self.sender()
        #if the price per product was changed
        if edit == self.trans_ppp_edit:
            try:
                #gets the new value of the input
                value = float(edit.text())
            except:
                if not edit.text() in STRINGS.ZERO_STRINGS:
                    #some non valid inputs are read. The synchronization cannot be completed
                    print(STRINGS.ERROR_CONVERT_STRING_TO_INT+edit.text())
                    return
                #if we just got some blank text or a comma. We set the value to zero
                value = 0
            
            #gets the number of products (its a spinBox, that is why it has to be an int)
            number = self.trans_number_spin_box.value()

            #disconnect from this event handler to prevent recursion
            self.trans_fullp_edit.textChanged.disconnect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.disconnect(self.Esync_cashflows)

            assert(type(value) in (float, int) and type(number) in (float, int)), STRINGS.ERROR_NOT_TYPE_NUM+str(number)+", "+str(value)
            self.trans_fullp_edit.setText(str(value*number))    #sets the synced cashflow
            #connect to this event handler again
            self.trans_fullp_edit.textChanged.connect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.connect(self.Esync_cashflows)
        
        #if the full price was changed
        if edit == self.trans_fullp_edit:
            try:
                #gets the new value of the input
                value = float(edit.text())
            except:
                if not edit.text() in STRINGS.ZERO_STRINGS:
                    #some non valid inputs are read. The synchronization cannot be completed
                    print(STRINGS.ERROR_CONVERT_STRING_TO_INT+edit.text())
                    return
                #if we just got some blank text or a comma. We set the value to zero
                value = 0
            
            #gets the number of products (its a spinBox, that is why it has to be an int)
            number = self.trans_number_spin_box.value()

            #disconnect from this event handler to prevent recursion
            self.trans_fullp_edit.textChanged.disconnect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.disconnect(self.Esync_cashflows)

            assert(type(value) in (float, int) and type(number) in (float, int)), STRINGS.ERROR_NOT_TYPE_NUM+str(number)+", "+str(value)
            self.trans_ppp_edit.setText(str(value/number))      #sets the synced cashflow
            #connect to this event handler again
            self.trans_fullp_edit.textChanged.connect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.connect(self.Esync_cashflows)

        #if the product number was changed
        if edit == self.trans_number_spin_box:
            try:
                #gets the value of the price per product input
                value = float(self.trans_ppp_edit.text())
            except:
                if not self.trans_ppp_edit.text() in STRINGS.ZERO_STRINGS:
                    #some non valid inputs are read. The synchronization cannot be completed
                    print(STRINGS.ERROR_CONVERT_STRING_TO_INT+self.trans_ppp_edit.text())
                    return
                #if we just got some blank text or a comma. We set the value to zero
                value = 0
            #gets the number of products (its a spinBox, that is why it has to be an int)
            number = edit.value()
            #disconnect from this event handler to prevent recursion
            self.trans_fullp_edit.textChanged.disconnect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.disconnect(self.Esync_cashflows)
            assert(type(value) in (float, int) and type(number) in (float, int)), STRINGS.ERROR_NOT_TYPE_NUM+str(number)+", "+str(value)
            self.trans_fullp_edit.setText(str(value*number))                #sets the synced cashflow
            #connect to this event handler again
            self.trans_fullp_edit.textChanged.connect(self.Esync_cashflows)
            self.trans_ppp_edit.textChanged.connect(self.Esync_cashflows)
    
    def Ecategory_choosed(self):
        """
        Event handler
        activates if the user choosed a category in a ComboBox
        adds a new ComboBox if neccessary
        :return: void
        """
        assert(type(self.sender()) == QComboBox), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        if not self.CatCombo.isNoDefault():
            #if there are some ComboBoxes with the default category, no further boxes are added
            self.CatCombo.updateItems()    #sets the items correctly (you can only choose every option once) 
            return
            
        if CONSTANTS.MAX_CATEGORIES > self.CatCombo.getLen():
            #add a new box, if the max boxes are not reached yet
            self.CatCombo.addComboBox()

    def Eftperson_choosed(self):
        """
        Event handler
        activates if the user choosed a from/to person in a ComboBox
        adds a new ComboBox if neccessary
        :return: void
        """
        assert(type(self.sender()) == QComboBox), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        if not self.FtpCombo.isNoDefault():
            #if there are some ComboBoxes with the default category, no further boxes are added
            self.FtpCombo.updateItems()    #sets the items correctly (you can only choose every option once) 
            return
            
        if CONSTANTS.MAX_PERSONS > self.FtpCombo.getLen():
            #add a new box, if the max boxes are not reached yet
            self.FtpCombo.addComboBox()
    
    def Ewhyperson_choosed(self):
        """
        Event handler
        activates if the user choosed a from/to person in a ComboBox
        adds a new ComboBox if neccessary
        :return: void
        """
        assert(type(self.sender()) == QComboBox), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        if not self.WhyCombo.isNoDefault():
            #if there are some ComboBoxes with the default category, no further boxes are added
            self.WhyCombo.updateItems()    #sets the items correctly (you can only choose every option once) 
            return
            
        if CONSTANTS.MAX_PERSONS > self.WhyCombo.getLen():
            #add a new box, if the max boxes are not reached yet
            self.WhyCombo.addComboBox()

    def Echange_cat_text(self):
        """
        Event handler
        activates if the text in the add category input changed
        (neccessary to activate the add category button)
        :return: void
        """
        assert(type(self.sender()) == QLineEdit), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        text = self.sender().text()
        #activates the add category button if there are at least 3 non whitespace characters typed
        if len(text) - text.count(" ") >= 3:
            self.trans_cat_button.setEnabled(True)
        else:
            #deactivates the button otherwise
            self.trans_cat_button.setEnabled(False)

    def Echange_person_text(self):
        """
        Event handler
        activates if the text in the add person input changed
        (neccessary to activate the add from/to person and why person buttons)
        :return: void
        """
        assert(type(self.sender()) == QLineEdit), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        text = self.sender().text()
        if len(text) - text.count(" ") >= 3:
            #activates the add from/to and why person buttons if there are at least 3 non whitespace characters typed
            self.trans_ftp_button.setEnabled(True)
            self.trans_whyp_button.setEnabled(True)
        else:
            #deactivates the buttons otherwise
            self.trans_ftp_button.setEnabled(False)
            self.trans_whyp_button.setEnabled(False)

    def Eadd_category(self):
        """
        Event handler
        activates if a new category is added
        :return: void
        """
        assert(type(self.sender()) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        text = self.trans_cat_edit.text()
        #requests the backend about this new category, it will return a bool whether the category is accepted or not
        accepted = self.backend.addCategory(text)
        if accepted == False:
            #if its not accepted we get a Error message box
            msgbox = QMessageBox(self)
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.setWindowTitle(STRINGS.ERROR_CATEGORY_NOT_ACCEPTED)
            msgbox.setText(self.backend.getError())     #get the reason from the backend
            msgbox.exec()
            return
        
        #if its accepted, add this item to the combo boxes
        self.CatCombo.addItem(text)

    def Ereset_category(self):
        """
        Event handler
        activates if the categories are reseted
        :return: void
        """
        assert(type(self.sender()) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        self.CatCombo.reset()   #reset the ComboBoxes

    def Eadd_ftperson(self):
        """
        Event handler
        activates if a new from/to person is added
        :return: void
        """
        assert(type(self.sender()) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        text = self.trans_person_edit.text()
        #requests the backend about this new person, it will return a bool whether the person is accepted or not
        accepted = self.backend.addPerson(text)
        if accepted == False:
            #if its not accepted we get a Error message box
            msgbox = QMessageBox(self)
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.setWindowTitle(STRINGS.ERROR_PERSON_NOT_ACCEPTED)
            msgbox.setText(self.backend.getError())     #get the reason from the backend
            msgbox.exec()
            return
        
        #if its accepted, add this item to the combo boxes
        self.FtpCombo.addItem(text)     #add it to the from/to persons and set it if possible
        self.WhyCombo.addItem(text, set_item=False) #add it to the why persons but dont set it
    
    def Eadd_whyperson(self):
        """
        Event handler
        activates if a new why person is added
        :return: void
        """
        assert(type(self.sender()) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        text = self.trans_person_edit.text()
        #requests the backend about this new person, it will return a bool whether the person is accepted or not
        accepted = self.backend.addPerson(text)
        if accepted == False:
            #if its not accepted we get a Error message box
            msgbox = QMessageBox(self)
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.setWindowTitle(STRINGS.ERROR_PERSON_NOT_ACCEPTED)
            msgbox.setText(self.backend.getError())     #get the reason from the backend
            msgbox.exec()
            return
        
        #if its accepted, add this item to the combo boxes
        self.FtpCombo.addItem(text, set_item=False)     #add it to the from/to persons but dont set it
        self.WhyCombo.addItem(text)     #add it to the why persons and set it if possible

    def Ereset_person(self):
        """
        Event handler
        activates if the persons are reseted
        :return: void
        """
        assert(type(self.sender()) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        self.WhyCombo.reset()       #reset the ComboBoxes
        self.FtpCombo.reset()

    def Esubmit_transaction(self):
        """
        Event handler
        activates if the transaction is submitted
        gets all data from the form and sends it to the backend
        :return: void
        """
        assert(type(self.sender()) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        date = self.trans_date_edit.selectedDate().toPyDate()       #gets the date and convert it to datetime.date
        number = int(self.trans_number_spin_box.text())             #gets number of products
        product = self.trans_product_edit.text()                    #gets name of product
        sign = self.trans_sign.currentText()                        #gets sign of the cashflow
        assert(sign in (STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS, STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_PLUS)), STRINGS.ERROR_WRONG_SIGN_CONTENT+sign
        try:
            #gets cashflow
            full_cashflow = float(self.trans_fullp_edit.text())
        except:
            #cashflow is not a float, should not trigger, because if its not a float the submit button should be deactivated
            raise ValueError(STRINGS.ERROR_WRONG_CF_DATA+self.trans_fullp_edit.text())
        
        if sign == STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS:
            full_cashflow = -full_cashflow  #if the sign is negative, the cashflow is negative xd

        categories = self.CatCombo.getChoosenItems()    #getting the categories and persons
        ftpersons = self.FtpCombo.getChoosenItems()
        whypersons = self.WhyCombo.getChoosenItems()

        #sends the data to the backend
        self.backend.addTransaction(date, product, number, full_cashflow, categories, ftpersons, whypersons)
        self.updateLastTrans()

