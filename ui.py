"""
This module provides the ui of the programm
"""

import os
import inspect
from strings import ENG as STRINGS
from gui_constants import FONTS, ICONS
from constants import CONSTANTS
from backend import Backend
from backend_datatypes import Transaction
from ui_datatypes import Combo, Inputs, TransactionList
from fullstack_utils import SortEnum, utils, Filter

from PyQt5.QtWidgets import QGridLayout, QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QWidget
from PyQt5.QtWidgets import QSpinBox, QCalendarWidget, QLineEdit, QCompleter, QComboBox, QMessageBox, QScrollArea, QFileDialog
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

        self.loading = False    #if the user loads data from a csv, this will be true
        self.loader = None      #holds the generator for loading data

        self.product_input_matched = False #does the user inputs a product name we already know?
        self.product_input_matched_content = None   #the form data that was entered before the user matched some product (to restore)
        self.tooltips_set = False   #are the tooltips are already set 
        self.edit_mode = False  #form is in edit mode?
        self.choosed_trans_button = False   #the button, which transaction is currently choosen

        self.filter = Filter()          #sets up the filter object to filter the transactions
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

        #transaction list object handles the scrollable transaction list ui component
        self.TransList = TransactionList(self.backend.getFilteredTransactions, self.Elast_trans_button_pressed)

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
        self.setToolTips()
        self.updateFilter()

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
        self.trans_date_edit = QCalendarWidget()
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
        self.trans_product_edit = QLineEdit()
        self.trans_product_completer = QCompleter(self.backend.getProductNames())
        self.trans_product_completer.setCaseSensitivity(False)
        self.trans_product_edit.setCompleter(self.trans_product_completer)      #add an autocompleter
        self.trans_product_edit.textChanged.connect(self.Echange_product_text)
        hgrid_prod_num.addWidget(self.trans_product_edit, 1, 0)

        #********************NUMBER OF PRODUCTS**********************
        #number of products label
        self.trans_number_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_NUMBER)
        hgrid_prod_num.addWidget(self.trans_number_label, 0, 1)

        #number of products input
        self.trans_number_spin_box = QSpinBox()
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
        cf_meta_widget = QWidget()
        self.cf_meta_layout = QHBoxLayout()
        self.cf_meta_layout.setContentsMargins(0,0,0,0)
        self.trans_cf_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CF)
        self.trans_cf_label.setFont(FONTS.APP_NEW_TRANSACTION_CF)
        self.cf_meta_layout.addWidget(self.trans_cf_label)

        cf_meta_widget.setLayout(self.cf_meta_layout)
        grid_cf.addWidget(cf_meta_widget, 0, 0, 1, 2)

        #sign label
        self.trans_sign_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN)
        grid_cf.addWidget(self.trans_sign_label, 2, 0)

        #sign input
        self.trans_sign = QComboBox()
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
        self.trans_ppp_edit = QLineEdit()
        self.trans_ppp_edit.textChanged.connect(self.Eenter_only_numbers)
        self.trans_ppp_edit.textChanged.connect(self.Esync_cashflows)
        self.trans_ppp_edit.textChanged.connect(self.Echanged_cashflow)
        grid_cf.addWidget(self.trans_ppp_edit, 3, 1)

        #full price input
        self.trans_fullp_edit = QLineEdit()
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
        add_cat_widget = QWidget()
        self.add_cat_layout = QHBoxLayout()
        self.add_cat_layout.setContentsMargins(0,0,0,0)
        self.trans_cat_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CAT)
        self.add_cat_layout.addWidget(self.trans_cat_label)

        add_cat_widget.setLayout(self.add_cat_layout)
        vbox_new_cat.addWidget(add_cat_widget)

        #add new category input
        self.trans_cat_edit = QLineEdit()
        self.trans_cat_edit.textChanged.connect(self.Echange_cat_text)
        vbox_new_cat.addWidget(self.trans_cat_edit)

        #add new category button
        self.trans_cat_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_ADD_CAT)
        #at default the button is disabled, you need to type at least 3 characters to activate it
        self.trans_cat_button.setEnabled(False)     
        self.trans_cat_button.clicked.connect(self.Eadd_category)
        vbox_new_cat.addWidget(self.trans_cat_button)

        #reset category button
        self.trans_reset_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_RESET_CAT)
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
        add_person_widget = QWidget()
        self.add_person_layout = QHBoxLayout()
        self.add_person_layout.setContentsMargins(0,0,0,0)
        self.trans_add_person_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_PERSON)
        self.add_person_layout.addWidget(self.trans_add_person_label)

        add_person_widget.setLayout(self.add_person_layout)
        grid_new_person.addWidget(add_person_widget, 0, 0)

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
        self.trans_ftp_button.clicked.connect(self.Eadd_ftperson)
        grid_new_person.addWidget(self.trans_ftp_button, 1, 0)

        #add person to why persons button
        self.trans_whyp_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_ADD_PERSON_WHYP, self)
        #at default the button is disabled, you need to type at least 3 characters to activate it
        self.trans_whyp_button.setEnabled(False)
        self.trans_whyp_button.clicked.connect(self.Eadd_whyperson)
        grid_new_person.addWidget(self.trans_whyp_button, 1, 1)

        #reset persons button
        self.person_reset_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_RESET_PERSON, self)
        self.person_reset_button.clicked.connect(self.Ereset_person)
        grid_new_person.addWidget(self.person_reset_button, 2, 0, 1, 2)

        #sets the layouts for the persons section
        groupbox_person_new.setLayout(grid_new_person)
        grid_person.addWidget(groupbox_person_new, 1, 0, 2, 0)
        groupbox_person.setLayout(grid_person)
        self.layout_transaction.addWidget(groupbox_person)

        #********************SUBMIT_BUTTON***************************
        #submit transaction button
        self.submit_widget = QWidget()
        self.submit_layout = QHBoxLayout()
        self.submit_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_SUBMIT)
        self.submit_button.setFont(FONTS.APP_NEW_TRANSACTION_SUBMIT)
        #at default the button is disabled, you need to fill out all required fields to activate it
        #this is monitored by the input object
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.Esubmit_transaction)
        self.submit_layout.addWidget(self.submit_button)
        self.submit_widget.setLayout(self.submit_layout)
        self.layout_transaction.addWidget(self.submit_widget)

    def addWidgetsLastTrans(self):
        """
        adds the Widgets to the "last transactions" part of the window. The buttons are handled in a datatype
        builds up the "last transactions" part of the window and connects these widgets with the backend
        handles the behavior of these widgets too
        :return: void
        """
        #creates the filter buttons
        layout_filter = QHBoxLayout()
        widget_filter = QWidget()
        self.filter_button = QPushButton(STRINGS.APP_BUTTON_FILTER_OFF)
        self.filter_button.clicked.connect(self.Eopen_filter)
        layout_filter.addWidget(self.filter_button)

        self.reset_fiter_button = QPushButton(STRINGS.APP_BUTTON_FILTER_RESET)
        self.reset_fiter_button.clicked.connect(self.Ereset_filter)
        layout_filter.addWidget(self.reset_fiter_button)

        #number of transactions label
        self.num_trans_label = QLabel("Placeholder")
        layout_filter.addWidget(self.num_trans_label)

        widget_filter.setLayout(layout_filter)
        self.layout_lastTransaction.addWidget(widget_filter)

        #creates the sort buttons
        layout_sort = QHBoxLayout()
        widget_sort = QWidget()
        
        self.scroll_sort_date_button = QPushButton(STRINGS.APP_BUTTON_LAST_TRANSACTIONS_DATE)
        self.scroll_sort_cf_button = QPushButton(STRINGS.APP_BUTTON_LAST_TRANSACTIONS_CASHFLOW)
        self.scroll_sort_product_button = QPushButton(STRINGS.APP_BUTTON_LAST_TRANSACTIONS_PRODUCT)

        self.sort_buttons = [self.scroll_sort_date_button, self.scroll_sort_cf_button, self.scroll_sort_product_button]
        
        for sort_button in self.sort_buttons:
            sort_button.setFont(FONTS.APP_LAST_TRANSACTION_SORT)
            sort_button.setIcon(ICONS.SORT_DEFAULT)
            layout_sort.addWidget(sort_button)
            sort_button.clicked.connect(self.Esort_transactions)

        widget_sort.setLayout(layout_sort)
        self.layout_lastTransaction.addWidget(widget_sort)

        #creates a scrollarea with a vertical scroll bar and no horizontal scroll bar
        self.scrollarea = QScrollArea()
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.scroll_widget = QWidget()      #inner widget, holds the buttons
        self.scroll_vbox = QVBoxLayout()    #layout for the inner widget
        self.scroll_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)    #buttons should build up from the top

        self.TransList.setLayout(self.scroll_vbox)  #sets the layout inside the datatype
        self.sortTransactions(SortEnum.DATE, True)            #loads the buttons from the backend

        #sets the layout of the inner widget and sets this widget in the scrollarea, finally adds the scrollarea to the main layout
        self.scroll_widget.setLayout(self.scroll_vbox)
        self.scrollarea.setWidget(self.scroll_widget)
        self.layout_lastTransaction.addWidget(self.scrollarea)

        #set buttons for loading/exporting
        load_export_hbox = QHBoxLayout()
        load_export_widget = QWidget()
        self.load_trans_button = QPushButton(STRINGS.APP_BUTTON_LOAD)
        self.load_trans_button.clicked.connect(self.Eload_csv)
        load_export_hbox.addWidget(self.load_trans_button)

        self.export_trans_button = QPushButton(STRINGS.APP_BUTTON_EXPORT)
        self.export_trans_button.clicked.connect(self.Eexport_csv)
        load_export_hbox.addWidget(self.export_trans_button)

        load_export_widget.setLayout(load_export_hbox)
        self.layout_lastTransaction.addWidget(load_export_widget)


    def enableEditMode(self, transaction:Transaction):
        """
        sets the window into edit mode
        That means it will load the transaction data into the form and change some button labels and event handlers
        it will add some buttons for canceling edit or accepting it (and leaving edit mode)
        Moreover there will be some style changes to tell the user that its edit mode
        :param transaction: object<Transaction> transaction to load
        :return: void
        """
        assert(type(transaction) == Transaction), STRINGS.getTypeErrorString(transaction, "transaction", Transaction)
        assert(self.choosed_trans_button != False), STRINGS.ERROR_NO_TRANSACTION_BUTTON_SET
        assert(type(self.choosed_trans_button) == QPushButton), STRINGS.getTypeErrorString(self.choosed_trans_button, "self.sender_button", QPushButton)
        assert(not self.edit_mode), STRINGS.ERROR_IN_EDIT_MODE
        self.edit_mode = True

        #loads the transaction data into the form
        self.trans_date_edit.setSelectedDate(QDate(transaction.date.year, transaction.date.month, transaction.date.day))    #date
        self.trans_product_edit.setText(transaction.product.name)   #product name
        self.trans_number_spin_box.setValue(transaction.number)     #product count
        self.trans_sign.setCurrentText(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_PLUS if transaction.cashflow > 0 else STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS)
        self.trans_fullp_edit.setText(str(abs(transaction.cashflow)))   #full cashflow (cashflow per product is autmotically synced)
        self.CatCombo.setItems(transaction.product.categories)          #categories
        self.FtpCombo.setItems(transaction.getFtPersonNames())          #from/to persons
        self.WhyCombo.setItems(transaction.getWhyPersonNames())         #why persons

        #make the gui look like edit mode
        self.choosed_trans_button.setStyleSheet("QPushButton {background-color:red;}")
        self.choosed_trans_button.adjustSize()
        self.groupBox_transaction.setStyleSheet("QGroupBox {background-color:#ffcccc;}")
        self.groupBox_transaction_label.setText(STRINGS.APP_LABEL_EDIT_TRANSACTION)

        self.submit_button.setText(STRINGS.APP_BUTTON_EDIT_TRANSACTION_SUBMIT)
        #adding some new buttons, and connecting to the right event handler
        self.submit_button.clicked.disconnect()
        self.submit_button.setEnabled(True)

        delete_button = QPushButton(STRINGS.APP_BUTTON_EDIT_TRANSACTION_DELETE)
        delete_button.setFont(FONTS.APP_NEW_TRANSACTION_SUBMIT)
        delete_button.setStyleSheet("color:red")
        self.submit_layout.addWidget(delete_button)

        cancel_button = QPushButton(STRINGS.APP_BUTTON_EDIT_TRANSACTION_CANCEL)
        cancel_button.setFont(FONTS.APP_NEW_TRANSACTION_SUBMIT)
        self.submit_layout.addWidget(cancel_button)

        #connect with event handler
        self.choosed_trans_button.clicked.disconnect()      #the choosen transaction should work as a cancel button too
        self.choosed_trans_button.clicked.connect(self.Eedit_cancel)
        self.submit_button.clicked.connect(self.Eedit_save_changes)
        delete_button.clicked.connect(self.Eedit_delete_transaction)
        cancel_button.clicked.connect(self.Eedit_cancel)
        self.deactivateNonEditModeButtons()

    def disableEditMode(self):
        """
        leaves the edit mode
        that means that the gui is looking normal again and all data inside the form gets wiped
        the event handlers will be connected correct again
        :return: void
        """
        assert(self.edit_mode), STRINGS.ERROR_NOT_IN_EDIT_MODE
        self.edit_mode = False

        self.activateNonFormButtons()

        #lets wipe some form data
        self.clearForm()

        #lets change the looking of the gui
        self.choosed_trans_button.setStyleSheet("")
        self.choosed_trans_button.adjustSize()
        self.groupBox_transaction.setStyleSheet("")
        self.groupBox_transaction_label.setText(STRINGS.APP_LABEL_NEW_TRANSACTION)

        self.submit_button.setText(STRINGS.APP_BUTTON_NEW_TRANSACTION_SUBMIT)
        for button in self.submit_widget.children():
            if button != None and button != self.submit_button and button != self.submit_layout:
                button.deleteLater()
        
        #connect to the right event handler
        self.choosed_trans_button.clicked.disconnect()
        self.choosed_trans_button.clicked.connect(self.Elast_trans_button_pressed)
        self.submit_button.clicked.disconnect()
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.Esubmit_transaction)

        self.choosed_trans_button = False           #this transaction button is no more active
        self.adjustSize()

    def setToolTips(self):
        """
        sets the tool tip for the ui components, adds icons too, you have to build the ui first
        :return: void
        """
        assert(not self.tooltips_set), STRINGS.ERROR_TOOLTIPS_ALREADY_SET
        self.tooltips_set = True
        self.trans_cat_button.setToolTip(STRINGS.TOOLTIP_TYPE_3_CHARS)
        self.trans_ftp_button.setToolTip(STRINGS.TOOLTIP_TYPE_3_CHARS)
        self.submit_button.setToolTip(STRINGS.TOOLTIP_SUBMIT_BUTTON)
        self.trans_whyp_button.setToolTip(STRINGS.TOOLTIP_TYPE_3_CHARS)
        self.trans_date_edit.setToolTip(STRINGS.TOOLTIP_CALENDAR)

        #add info icons
        cf_info_label = QLabel()
        cf_info_label.setPixmap(ICONS.INFO_PIXMAP.scaledToHeight(self.trans_cf_label.sizeHint().height()))
        self.cf_meta_layout.addWidget(cf_info_label)
        
        cat_info_label = QLabel()
        cat_info_label.setPixmap(ICONS.INFO_PIXMAP.scaledToHeight(self.trans_cat_label.sizeHint().height()))
        self.add_cat_layout.addWidget(cat_info_label)

        person_info_label = QLabel()
        person_info_label.setPixmap(ICONS.INFO_PIXMAP.scaledToHeight(self.trans_add_person_label.sizeHint().height()))
        self.add_person_layout.addWidget(person_info_label)

        cf_info_label.setToolTip(STRINGS.TOOLTIP_CASHFLOW)
        cat_info_label.setToolTip(STRINGS.TOOLTIP_CATEGORY)
        person_info_label.setToolTip(STRINGS.TOOLTIP_PERSON)

    def activateTransSubmitButton(self):
        """
        activates the button which submits a new transaction
        :return: void
        """
        assert(not self.edit_mode), STRINGS.ERROR_IN_EDIT_MODE
        self.submit_button.setEnabled(True)

    def deactivateTransSubmitButton(self):
        """
        deactivates the button which submits a new transaction
        :return: void
        """
        assert(not self.edit_mode), STRINGS.ERROR_IN_EDIT_MODE
        self.submit_button.setEnabled(False)

    def sortTransactions(self, sortElement:SortEnum, up:bool=True):
        """
        this method sets the right icon for the sort buttons and makes sure the transactions are sorted
        :param sortElement: object<SortEnum> after which category should be sorted?
        :param up: bool<from A-Z, new-old, or small-big>
        :return: void
        """
        #sets all icons to the default
        for sort_button in self.sort_buttons:
            sort_button.setIcon(ICONS.SORT_DEFAULT)

        #gets the right icon depending on the sort order
        icon = ICONS.SORT_UP if up else ICONS.SORT_DOWN
        self.sort_buttons[sortElement.value].setIcon(icon)    #sets that icon to the right button
        self.backend.sortTransactions(sortElement, up)  #sets the sort rule in the backend
        self.TransList.updateLastTrans()                #gets the new data from the backend and display it

    def deactivateNonFormButtons(self):
        """
        deactivates all buttons that are not in the form
        :return: void
        """
        self.filter = Filter()  #sets the default filter
        self.updateFilter()     #updates the filter in the backend
        for but in self.sort_buttons:
            but.setEnabled(False)
        self.filter_button.setEnabled(False)
        self.reset_fiter_button.setEnabled(False)
        for but in self.TransList.buttons:
            but.setEnabled(False)
        self.load_trans_button.setEnabled(False)
        self.export_trans_button.setEnabled(False)
    
    def deactivateNonEditModeButtons(self):
        """
        deactivates all buttons that are not used in edit mode
        :return: void
        """
        for but in self.sort_buttons:
            but.setEnabled(False)
        self.filter_button.setEnabled(False)
        self.reset_fiter_button.setEnabled(False)
        self.load_trans_button.setEnabled(False)
        self.export_trans_button.setEnabled(False)

    def activateNonFormButtons(self):
        """
        activates all buttons that are not in the form
        :return: void
        """
        for but in self.sort_buttons:
            but.setEnabled(True)
        self.filter_button.setEnabled(True)
        self.reset_fiter_button.setEnabled(True)
        for but in self.TransList.buttons:
            but.setEnabled(True)
        self.load_trans_button.setEnabled(True)
        self.export_trans_button.setEnabled(True)

    def loadNextData(self): #DEBUGONLY
        """
        loads the next data in the form while loading from a file
        :return: void
        """
        self.product_input_matched = False
        date, product_name, categories, number, cashflow_pp, cashflow_full, sign, ftpersons, whypersons = self.loader.__next__()
        print(date.isoformat())
        date = QDate.fromString(date.isoformat(), "yyyy-MM-dd")
        self.setForm(date=date, product_name=product_name, categories=categories, number=number, cashflow_per_product=cashflow_pp,
                     from_to_persons=ftpersons, why_persons=whypersons, take_persons_from_product=True)


    def addTransactionFromForm(self):
        """
        gets all data from the form and sends it to the backend as a new transaction
        :return: bool<success?>
        """
        transaction = self.getTransactionFromForm()
        if transaction != False:
            self.backend.addTransaction(transaction)
            ret = True
        else:
            ret = False
        self.TransList.updateLastTrans()    #update the buttons in the scrollarea showing the last transactions
        return ret

    def addTransactionFromTransaction(self, transaction:Transaction):
        """
        adds a given transaction to the system
        :return: void
        """
        assert(type(transaction) == Transaction), STRINGS.getTypeErrorString(transaction, "transaction", Transaction)
        self.backend.addTransaction(transaction)
        self.TransList.updateLastTrans()    #update the buttons in the scrollarea showing the last transactions

    def getTransactionFromForm(self, noexcept:bool=False):
        """
        gets all data from the form and returns a transaction object
        :param noexcept: bool<there should not be thrown any exception (unsafe)>
        :return: object<Transaction> or bool<False> if its not valid
        """
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
            if noexcept:
                #if we use this method not as a event handler followup we may want this behaviour
                full_cashflow = 0.0
            else:
                raise ValueError(STRINGS.ERROR_WRONG_CF_DATA+self.trans_fullp_edit.text())
        
        if sign == STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS:
            full_cashflow = -full_cashflow  #if the sign is negative, the cashflow is negative xd

        categories = self.CatCombo.getChoosenItems()    #getting the categories and persons
        ftpersons = self.FtpCombo.getChoosenItems()
        whypersons = self.WhyCombo.getChoosenItems()

        #sends the data to the backend
        return self.backend.getTransactionObject(date, product, number, full_cashflow, categories, ftpersons, whypersons)

    def getDictFromForm(self):
        """
        gets all data from the form and returns a dict, with that data
        :return: dict<data>
        """
        data_dict = {}
        data_dict["date"] = self.trans_date_edit.selectedDate().toPyDate()       #gets the date and convert it to datetime.date
        data_dict["number"] = int(self.trans_number_spin_box.text())             #gets number of products
        data_dict["product"] = self.trans_product_edit.text()                    #gets name of product
        sign = self.trans_sign.currentText()                        #gets sign of the cashflow
        assert(sign in (STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS, STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_PLUS)), STRINGS.ERROR_WRONG_SIGN_CONTENT+sign
        data_dict["sign"] = sign
        try:
            #gets cashflow
            data_dict["cashflow"] = float(self.trans_fullp_edit.text())
            data_dict["cashflow_per_product"] = data_dict["cashflow"] / data_dict["number"]
        except:
            #cashflow data is not valid or empty, we will asume 0
            data_dict["cashflow"] = 0.0
            data_dict["cashflow_per_product"] = 0.0

        if sign == STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS:
            data_dict["cashflow"] = -data_dict["cashflow"]  #if the sign is negative, the cashflow is negative xd
            data_dict["cashflow_per_product"] = -data_dict["cashflow_per_product"]

        data_dict["categories"] = self.CatCombo.getChoosenItems()    #getting the categories and persons
        data_dict["ftpersons"] = self.FtpCombo.getChoosenItems()
        data_dict["whypersons"] = self.WhyCombo.getChoosenItems()
        return data_dict

    def clearForm(self, clear_date:bool=True):
        """
        clears the form, resets all components, you can flag, whether the date in the calendar should be reseted as well
        :param clear_date: bool<should the date also be cleared?>
        :return: void
        """
        if clear_date:
            self.trans_date_edit.setSelectedDate(QDate.currentDate())
        self.trans_product_edit.setText("")
        self.trans_number_spin_box.setValue(1)
        self.trans_fullp_edit.setText("0.0")           #due to syncing the cashflow per product is automatically set to 0
        self.trans_sign.setCurrentText(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS)     #standard is a loss :(
        self.CatCombo.reset()
        self.FtpCombo.reset()
        self.WhyCombo.reset()

    def setForm(self, cashflow_per_product:float=None, categories:list[str]=None, from_to_persons:list[str]=None, why_persons:list[str]=None, 
                date:QDate=None, product_name:str=None, number:int=None, take_persons_from_product:bool=False):
        """
        sets the data given into the form
        :param cashflow_per_product: float<signed cashflow per product>
        :param categories: list<str<category1>, ...>
        :param from_to_persons: list<str<from/to person name 1>, ...>
        :param why_persons: list<str<why person name 1>, ...>
        :param date: QDate<date of the transaction>
        :param product_name: str<name of the product>
        :param number: int<number of products>
        :param take_persons_from_product: bool<loads the persons that are set on the last transaction with this product>
        :return: void
        """
        assert(type(take_persons_from_product) == bool), STRINGS.getTypeErrorString(take_persons_from_product, "take_persons_from_product", bool)
        assert(type(cashflow_per_product) in [float, type(None)]), STRINGS.getTypeErrorString(cashflow_per_product, "cashflow_per_product", float)
        assert(type(categories) == list and all(map(lambda x: type(x) == str, categories)) or categories == None), STRINGS.getListTypeErrorString(categories, "categories", str)
        assert(type(from_to_persons) == list and all(map(lambda x: type(x) == str, from_to_persons)) or from_to_persons == None), STRINGS.getListTypeErrorString(from_to_persons, "from_to_persons", str)
        assert(type(why_persons) == list and all(map(lambda x: type(x) == str, why_persons)) or why_persons == None), STRINGS.getListTypeErrorString(why_persons, "why_persons", str)
        assert(type(date) in [type(None), QDate]), STRINGS.getTypeErrorString(date, "date", QDate)
        assert(type(product_name) in [type(None), str]), STRINGS.getTypeErrorString(product_name, "product_name", str)
        assert(type(number) in [type(None), int]), STRINGS.getTypeErrorString(number, "number", int)

        #print(cashflow_per_product)
        #assert(cashflow_per_product != 0)
        assert(number != 0)
        assert(QDate(1900, 1, 1) <= date <= QDate.currentDate() if date != None else True)
        if take_persons_from_product:
            if from_to_persons != None:
                self.FtpCombo.setItems(from_to_persons)
            if why_persons != None:
                self.WhyCombo.setItems(why_persons)
        if categories != None:
            self.CatCombo.setItems(categories)
        if product_name != None:
            self.trans_product_edit.setText(product_name)
        if date != None:
            self.trans_date_edit.setSelectedDate(date)
        if number != None:
            self.trans_number_spin_box.setValue(number)
        if cashflow_per_product != None:
            if cashflow_per_product < 0:
                self.trans_sign.setCurrentText(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS)
            else:
                self.trans_sign.setCurrentText(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_PLUS)
            self.trans_ppp_edit.setText(str(abs(cashflow_per_product)))
        
        if not take_persons_from_product:
            if from_to_persons != None:
                self.FtpCombo.setItems(from_to_persons)
            if why_persons != None:
                self.WhyCombo.setItems(why_persons)

    def updateFilter(self):
        """
        update the settings based on the filter.
        should be called if the filter changed
        :return: void
        """
        #sets the right text
        if self.filter.isStandard():
            self.filter_button.setText(STRINGS.APP_BUTTON_FILTER_OFF)
        else:
            self.filter_button.setText(STRINGS.APP_BUTTON_FILTER_ON)
        self.backend.setFilter(self.filter)     #sets the new filter in the backend
        self.TransList.updateLastTrans()        #reloads the transactions to make the filter wor
        self.num_trans_label.setText(str(self.TransList.getTransactionCount())+STRINGS.LABEL_TRANSACTION_COUNT)


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
            if text.lower() in map(lambda x: x.lower(), self.trans_product_completer.children()[0].stringList()):
                #the user entered a item name that is already in the system
                self.product_input_matched = True
                #saves the current state, we want noexcept , because it could happen that some required inputs are empty, we will set 0 for them
                self.product_input_matched_content:dict = self.getDictFromForm()  
                product_trans:Transaction = self.backend.getLastTransactionByProductText(text.lower())  #gets the last transaction
                #set the loaded data into the form
                if product_trans:
                    ppp = product_trans.cashflow_per_product
                    categories = product_trans.product.categories
                    ftp = list(map(lambda x: x.name, product_trans.from_to_persons))
                    whyp =list(map(lambda x: x.name, product_trans.why_persons))
                    self.setForm(cashflow_per_product=ppp, categories=categories, from_to_persons=ftp, why_persons=whyp)
            elif self.product_input_matched:
                #we had a match but the user typed something else, we should set the form to the inputs we had before the match occured
                ppp = self.product_input_matched_content["cashflow_per_product"]
                categories = self.product_input_matched_content["categories"]
                ftp = list(map(lambda x: x.name, self.product_input_matched_content["ftpersons"]))
                whyp = list(map(lambda x: x.name, self.product_input_matched_content["whypersons"]))
                #set the old data 
                self.setForm(cashflow_per_product=ppp, categories=categories, from_to_persons=ftp, why_persons=whyp)
                self.product_input_matched = False
                self.product_input_matched_content = None
                
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
        self.sender().setText(utils.only_numbers(self.sender(), negatives=False))
    
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
            
        if CONSTANTS.MAX_COMBOS > self.CatCombo.getLen():
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
            
        if CONSTANTS.MAX_COMBOS > self.FtpCombo.getLen():
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
            
        if CONSTANTS.MAX_COMBOS > self.WhyCombo.getLen():
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
        assert(not self.edit_mode), STRINGS.ERROR_IN_EDIT_MODE
        if self.addTransactionFromForm():
            self.clearForm(clear_date=False)
            self.trans_product_completer = QCompleter(self.backend.getProductNames())
            self.trans_product_completer.setCaseSensitivity(False)
            self.trans_product_edit.setCompleter(self.trans_product_completer)      #add an autocompleter
            if self.loading:
                self.loadNextData()

    def Elast_trans_button_pressed(self):
        """
        event handler
        activates if a transaction button from the scrollarea is pressed
        gets the transaction conencted to that button and opens a view/edit transaction window
        :return: void
        """
        assert(type(self.sender()) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        but = self.sender()
        trans = self.TransList.getTransactionForButton(but)
        if self.edit_mode:
            #an other transaction was choosen, so we wanna switch to that
            self.disableEditMode()
        self.choosed_trans_button = but
        self.enableEditMode(trans)

    def Eedit_cancel(self):
        """
        event handler 
        activates if the user presses the cancel button
        leaves edit mode, clears the form
        :return: void
        """
        assert(type(self.sender()) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        assert(self.edit_mode), STRINGS.ERROR_NOT_IN_EDIT_MODE
        self.disableEditMode()

    def Eedit_save_changes(self):
        """
        event handler
        activates if the user wanna save the changes while editing a transaction
        its just deleting the transaction currently choosed from the system and adds a new one, with the current options
        :return: void
        """
        assert(type(self.sender()) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        assert(type(self.choosed_trans_button) == QPushButton), STRINGS.ERROR_NO_TRANSACTION_BUTTON_SET
        assert(self.edit_mode), STRINGS.ERROR_NOT_IN_EDIT_MODE
        #delete the old transaction
        old_trans = self.TransList.getTransactionForButton(self.choosed_trans_button)
        new_trans = self.getTransactionFromForm()
        if new_trans == False:
            print("transaction could not be added")
            return
        self.backend.deleteTransaction(old_trans)
        self.disableEditMode()
        #add the new one
        self.addTransactionFromTransaction(new_trans)
        self.TransList.updateLastTrans()
        
    def Eedit_delete_transaction(self):
        """
        event handler
        activates if the user clicks a delete transaction button
        its just deleting the transaction currently choosed from the system
        :return: void
        """
        assert(type(self.sender()) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        assert(type(self.choosed_trans_button) == QPushButton), STRINGS.ERROR_NO_TRANSACTION_BUTTON_SET
        assert(self.edit_mode), STRINGS.ERROR_NOT_IN_EDIT_MODE
        self.backend.deleteTransaction(self.TransList.getTransactionForButton(self.choosed_trans_button))
        self.disableEditMode()
        self.TransList.updateLastTrans()

    def Esort_transactions(self):
        """
        event handler
        activates if the user clicks a button, which should sort the transactions
        the handler calculates how the transaction should be sorted depending on the current states
        :return: void
        """
        assert(type(self.sender()) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        assert(self.sender() in self.sort_buttons), STRINGS.ERROR_SENDER_NOT_IN_SORT_BUTTONS
        assert(not self.edit_mode), STRINGS.ERROR_IN_EDIT_MODE
        sortElement:SortEnum = SortEnum(self.sort_buttons.index(self.sender()))
        up = True   #sort ascending
        if ICONS.compare(self.sender().icon(), ICONS.SORT_UP):
            up = False    #last time we sorted asc, so now we sort descending
        self.sortTransactions(sortElement, up)

    def Eopen_filter(self):
        """
        event handler
        activates if the user wants to set a filter for the transactions
        :return: void
        """
        self.filter = FilterWindow(self).filter     #sets the filter
        self.updateFilter()     #updates the filter, that will go to the backend and new data will be got
    
    def Ereset_filter(self):
        """
        event handler
        activates if the user wants to reset the filter for the transaction
        :return: void
        """
        self.filter = Filter()  #sets the default filter
        self.updateFilter()     #updates the filter in the backend

    def ETESTload_csv(self):    #DEBUGONLY
        """
        event handler
        activates if the user wanna load transactions from a csv file
        :return: void
        """
        self.loading = True
        self.deactivateNonFormButtons()
        self.loader = self.backend.loadFromCSV()
        self.loadNextData()

    def Eload_csv(self):
        """
        event handler
        activates if the user wanna load transactions from a csv file
        :return: void
        """
        #disclaimer that all transactions are deleted 
        msg = QMessageBox()
        but = msg.warning(self, STRINGS.WARNING_IMPORT_TRANSACTIONS_TITLE, STRINGS.WARNING_IMPORT_TRANSACTIONS, QMessageBox.Ok | QMessageBox.Cancel)
        if but == QMessageBox.Ok:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(self, 
                "Import File", "", "CSV Files (*.csv)", options = options)
            if fileName:
                #loads the new transactions
                if self.backend.loadFromCSV(fileName) == False:
                    #msg box that tells the user that the file is not in the right format, he has to import his old data
                    msg = QMessageBox()
                    msg.critical(self, STRINGS.CRITICAL_IMPORT_TRANSACTIONS_TITLE, STRINGS.CRITICAL_IMPORT_TRANSACTIONS)
                #updates all ui comonents which belong to the transactions
                self.TransList.updateLastTrans()
                self.CatCombo.updateItems()
                self.FtpCombo.updateItems()
                self.WhyCombo.updateItems()
                self.trans_product_completer = QCompleter(self.backend.getProductNames())
                self.trans_product_completer.setCaseSensitivity(False)
                self.trans_product_edit.setCompleter(self.trans_product_completer)      #add an autocompleter

    def Eexport_csv(self):
        """
        event handler 
        activates if the user wanna export the transactions
        :return: void
        """
        #diclaimer that this action will only save the transactions and not the user data
        msg = QMessageBox()
        but = msg.warning(self, STRINGS.WARNING_EXPORT_TRANSACTIONS_TITLE, STRINGS.WARNING_EXPORT_TRANSACTIONS, QMessageBox.Ok | QMessageBox.Cancel)
        if but == QMessageBox.Ok:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self, 
                "Save File", "", "CSV Files (*.csv)", options = options)
            if fileName:
                self.backend.export(fileName)


class FilterWindow(QDialog):
    """
    The FilterWindow class contains the Window used for filter transactions
    the FilterWindow class takes the MainWindow as an object to work with
    """
    def __init__(self, mainWindow:Window):
        """
        basic constructor is building the window. Takes the main window object to communicate (communicate with the backend as well)
        :param mainWindow: object<Window>
        :return: void
        """
        assert(type(mainWindow) == Window), STRINGS.getTypeErrorString(mainWindow, "mainWindow", Window)
        super().__init__()  #initializes the Base Class (QDialog)

        self.title = STRINGS.FWINDOW_TITLE

        self.ui = mainWindow
        self.backend = mainWindow.backend
        self.filter = mainWindow.filter     #saves the filter object from the MainWindow
        self.tooltips_set = False   #keeps track whether you already set the tooltips or not

        #sets up the combo boxes
        self.CatCombo = Combo(STRINGS.APP_NEW_TRANSACTION_DEFAULT_CATEGORY, self.Ecategory_choosed, self.backend.getCategories)
        self.FtpCombo = Combo(STRINGS.APP_NEW_TRANSACTION_DEFAULT_FTPERSON, self.Eftperson_choosed, self.backend.getPersonNames)
        self.WhyCombo = Combo(STRINGS.APP_NEW_TRANSACTION_DEFAULT_WHYPERSON, self.Ewhyperson_choosed, self.backend.getPersonNames)
        self.PersonCombo = Combo(STRINGS.APP_NEW_TRANSACTION_DEFAULT_PERSON, self.Eperson_choosed, self.backend.getPersonNames)


        #build the window
        self.InitWindow()

    def InitWindow(self):
        """
        this method is building the window
        :return: void
        """
        self.setWindowTitle(self.title)
        self.grid = QGridLayout()       #sets the layout of the complete window

        self.createLayout()             #create the layout with all components
        self.setToolTips()              #set the tooltips for the user

        self.setLayout(self.grid)

        self.exec() #show the window on top and make all other windows not clickable
    
    def createLayout(self):
        """
        creates layout components and add UI components to that layout
        build the window
        :return: void
        """
        assert("grid" in map(lambda x: x[0], vars(self).items())), STRINGS.ERROR_GRID_NOT_DEFINED
        self.addWidgets()   #add the widgets

    def addWidgets(self):
        """
        adds the Widgets to the window
        builds up the window and connects these widgets with there event handlers
        handles the behavior of these widgets too
        :return: void
        """
        #sets up the main label in a widget in order to add the tooltip later
        main_label_widget = QWidget()
        self.main_label_layout = QHBoxLayout()
        self.main_label_layout.setContentsMargins(0,0,0,0)
        self.main_label = QLabel(STRINGS.FWINDOW_LABEL)
        self.main_label.setFont(FONTS.APP_NEW_TRANSACTION)
        self.main_label_layout.addWidget(self.main_label)
        main_label_widget.setLayout(self.main_label_layout)
        self.grid.addWidget(main_label_widget, 0, 0)

        #********************CALENDAR********************************
        #holds the buttons connected with the CalendarWindow to choose a min and max date
        group_date = QGroupBox()
        layout_date = QGridLayout()

        #labels
        date_label_widget = QWidget()
        self.date_label_layout = QHBoxLayout()
        self.date_label_layout.setContentsMargins(0,0,0,0)
        self.date_label = QLabel(STRINGS.FWINDOW_LABEL_DATE)
        self.date_label.setFont(FONTS.FWINDOW)
        self.date_label_layout.addWidget(self.date_label)
        date_label_widget.setLayout(self.date_label_layout)
        layout_date.addWidget(date_label_widget, 0, 0)

        min_date_label = QLabel(STRINGS.FWINDOW_LABEL_MIN_DATE)
        layout_date.addWidget(min_date_label, 1, 0)
        max_date_label = QLabel(STRINGS.FWINDOW_LABEL_MAX_DATE)
        layout_date.addWidget(max_date_label, 1, 1)

        #calendar buttons
        self.min_date_button = QPushButton(self.filter.minDate.toString("dd.MM.yyyy"))
        self.min_date_button.clicked.connect(self.Eopen_calendar)
        layout_date.addWidget(self.min_date_button, 2, 0)

        self.max_date_button = QPushButton(self.filter.maxDate.toString("dd.MM.yyyy"))
        self.max_date_button.clicked.connect(self.Eopen_calendar)
        layout_date.addWidget(self.max_date_button, 2, 1)

        group_date.setLayout(layout_date)
        self.grid.addWidget(group_date, 1, 0)

        #********************PRODUCT*********************************
        #holds the buttons and labels for filtering by product name
        groupbox_prod = QGroupBox()
        grid_prod = QGridLayout()

        product_label_widget = QWidget()
        self.product_label_layout = QHBoxLayout()
        self.product_label_layout.setContentsMargins(0,0,0,0)
        self.product_label = QLabel(STRINGS.FWINDOW_LABEL_PRODUCT)
        self.product_label.setFont(FONTS.FWINDOW)
        self.product_label_layout.addWidget(self.product_label)
        product_label_widget.setLayout(self.product_label_layout)
        grid_prod.addWidget(product_label_widget, 0, 0)

        #product label
        self.product_contains_label = QLabel(STRINGS.FWINDOW_LABEL_PRODUCT_CONTAINS)
        grid_prod.addWidget(self.product_contains_label, 1, 0)

        #product completer
        self.product_completer = QCompleter(self.backend.getProductNames())
        self.product_completer.setCaseSensitivity(False)

        self.product_contains_edit = QLineEdit()
        self.product_contains_edit.setCompleter(self.product_completer)      #add an autocompleter
        grid_prod.addWidget(self.product_contains_edit, 2, 0)

        #start string filter
        self.product_start_label = QLabel(STRINGS.FWINDOW_LABEL_PRODUCT_STARTS)
        grid_prod.addWidget(self.product_start_label, 1, 1)

        self.product_start_edit = QLineEdit()
        self.product_start_edit.setCompleter(self.product_completer)      #add an autocompleter
        grid_prod.addWidget(self.product_start_edit, 2, 1)

        #completes this group
        groupbox_prod.setLayout(grid_prod)
        self.grid.addWidget(groupbox_prod, 2, 0)

        #********************CASHFLOW********************************
        #holds the buttons and labels for filtering by cashflow
        grid_cf = QGridLayout()
        groupbox_cf = QGroupBox()
        grid_cf.setSpacing(20)

        #meta label for the group
        cashflow_label_widget = QWidget()
        self.cashflow_label_layout = QHBoxLayout()
        self.cashflow_label_layout.setContentsMargins(0,0,0,0)
        self.cashflow_label = QLabel(STRINGS.FWINDOW_LABEL_CASHFLOW)
        self.cashflow_label.setFont(FONTS.FWINDOW)
        self.cashflow_label_layout.addWidget(self.cashflow_label)
        cashflow_label_widget.setLayout(self.cashflow_label_layout)
        grid_cf.addWidget(cashflow_label_widget, 0, 0)

        #absolute toggle button (should we consider absolute cashflow?)
        self.absolute_button = QPushButton("Placeholder")
        self.absolute_button.setCheckable(True)
        self.absolute_button.clicked.connect(self.Etoggle_absolute)
        grid_cf.addWidget(self.absolute_button, 2, 0)

        #min cashflow label
        self.min_cashflow_label = QLabel(STRINGS.FWINDOW_LABEL_CASHFLOW_MIN)
        grid_cf.addWidget(self.min_cashflow_label, 3, 0)

        #ax cashflow label
        self.max_cashflow_label = QLabel(STRINGS.FWINDOW_LABEL_CASHFLOW_MAX)
        grid_cf.addWidget(self.max_cashflow_label, 4, 0)

        #price per product label
        self.trans_ppp_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_PP)
        grid_cf.addWidget(self.trans_ppp_label, 2, 1)

        #full price label
        self.trans_fullp_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION_CF_FULL)
        grid_cf.addWidget(self.trans_fullp_label, 2, 2)

        #price per product input (minimum)
        self.min_ppp_edit = QLineEdit()
        self.min_ppp_edit.textChanged.connect(self.Eenter_only_numbers)
        grid_cf.addWidget(self.min_ppp_edit, 3, 1)

        #full price input (minimum)
        self.min_fullp_edit = QLineEdit()
        self.min_fullp_edit.textChanged.connect(self.Eenter_only_numbers)
        grid_cf.addWidget(self.min_fullp_edit, 3, 2)

        #price per product input (maximum)
        self.max_ppp_edit = QLineEdit()
        self.max_ppp_edit.textChanged.connect(self.Eenter_only_numbers)
        grid_cf.addWidget(self.max_ppp_edit, 4, 1)

        #full price input (maximum)
        self.max_fullp_edit = QLineEdit()
        self.max_fullp_edit.textChanged.connect(self.Eenter_only_numbers)
        grid_cf.addWidget(self.max_fullp_edit, 4, 2)

        #sets up the layout for this group
        groupbox_cf.setLayout(grid_cf)
        self.grid.addWidget(groupbox_cf, 3, 0)

        #********************CATEGORY********************************
        groupbox_cat = QGroupBox()          #group for the whole category block
        groupbox_cat_choose = QGroupBox()   #group for the ComboBoxes where you can choose from
        grid_cat = QGridLayout()            #layout for the whole category block
        self.vbox_cat = QVBoxLayout()       #layout for the ComboBoxes where you can choose from

        #Setting up the object for the category combo boxes
        self.CatCombo.setLayout(self.vbox_cat)
        self.CatCombo.addComboBox()     #adds a first box
        self.CatCombo.sort()

        #meta label for category
        category_label_widget = QWidget()
        self.category_label_layout = QHBoxLayout()
        self.category_label_layout.setContentsMargins(0,0,0,0)
        self.category_label = QLabel(STRINGS.FWINDOW_LABEL_CATEGORY)
        self.category_label.setFont(FONTS.FWINDOW)
        self.category_label_layout.addWidget(self.category_label)
        category_label_widget.setLayout(self.category_label_layout)
        grid_cat.addWidget(category_label_widget, 0, 0)

        #sets the layout for the ComboBoxes
        groupbox_cat_choose.setLayout(self.vbox_cat)
        grid_cat.addWidget(groupbox_cat_choose, 1, 0)

        #reset category button
        self.cat_reset_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_RESET_CAT)
        self.cat_reset_button.clicked.connect(self.Ereset_category)
        grid_cat.addWidget(self.cat_reset_button, 1, 1)

        #sets the layouts of the category group
        groupbox_cat.setLayout(grid_cat)
        self.grid.addWidget(groupbox_cat, 4, 0)

        #********************PERSONS*********************************
        groupbox_person = QGroupBox()       #group for the whole person choose and add block
        groupbox_ftp_choose = QGroupBox()   #group for the from/to person choose block
        groupbox_whyp_choose = QGroupBox()  #group for the why person choose block
        groupbox_p_choose = QGroupBox()     #group for the person choose block
        grid_person = QGridLayout()         #layout for the whole person choose and add block
        self.vbox_ftp = QVBoxLayout()       #layout for the from/to person choose block
        self.vbox_whyp = QVBoxLayout()      #layout for the why person choose block
        self.vbox_p = QVBoxLayout()         #layout for the person choose block

        #meta label person
        person_label_widget = QWidget()
        self.person_label_layout = QHBoxLayout()
        self.person_label_layout.setContentsMargins(0,0,0,0)
        self.person_label = QLabel(STRINGS.FWINDOW_LABEL_PERSON)
        self.person_label.setFont(FONTS.FWINDOW)
        self.person_label_layout.addWidget(self.person_label)
        person_label_widget.setLayout(self.person_label_layout)
        grid_person.addWidget(person_label_widget, 0, 0)

        #********************FROM_TO_PERSON**************************
        #Setting up the object for the from/to person combo boxes
        self.FtpCombo.setLayout(self.vbox_ftp)
        self.FtpCombo.addComboBox()     #add the first box
        self.FtpCombo.sort()

        #set the layout for the from/to person group
        groupbox_ftp_choose.setLayout(self.vbox_ftp)
        grid_person.addWidget(groupbox_ftp_choose, 1, 0)

        #********************WHY_PERSON******************************
        #Setting up the object for the why person combo boxes
        self.WhyCombo.setLayout(self.vbox_whyp)
        self.WhyCombo.addComboBox()     #add the first box
        self.WhyCombo.sort()

        #set the layout for the why person group
        groupbox_whyp_choose.setLayout(self.vbox_whyp)
        grid_person.addWidget(groupbox_whyp_choose, 1, 1)

        #********************PERSON**********************************
        #Setting up the object for the why person combo boxes
        self.PersonCombo.setLayout(self.vbox_p)
        self.PersonCombo.addComboBox()     #add the first box
        self.PersonCombo.sort()

        #set the layout for the why person group
        groupbox_p_choose.setLayout(self.vbox_p)
        grid_person.addWidget(groupbox_p_choose, 1, 2)

        #********************RESET_PERSON****************************
        #reset persons button
        self.person_reset_button = QPushButton(STRINGS.APP_BUTTON_NEW_TRANSACTION_RESET_PERSON, self)
        self.person_reset_button.clicked.connect(self.Ereset_person)
        grid_person.addWidget(self.person_reset_button, 2, 0, 2, 0)

        #sets the layouts for the persons section
        groupbox_person.setLayout(grid_person)
        self.grid.addWidget(groupbox_person, 5, 0)

        #********************SUBMIT_BUTTON***************************
        #submit transaction button
        self.submit_widget = QWidget()
        self.submit_layout = QHBoxLayout()
        self.submit_button = QPushButton(STRINGS.FWINDOW_LABEL_SET_FILTER)
        self.submit_button.setFont(FONTS.APP_NEW_TRANSACTION_SUBMIT)
        self.submit_button.clicked.connect(self.Esubmit_filter)
        self.submit_layout.addWidget(self.submit_button)
        self.submit_widget.setLayout(self.submit_layout)
        self.grid.addWidget(self.submit_widget, 6, 0)

        self.update(get_form_data=False)   #updates all widgets to the filter settings

    def setToolTips(self):
        """
        sets the tool tip for the ui components, adds icons too, you have to build the ui first
        :return: void
        """
        assert(not self.tooltips_set), STRINGS.ERROR_TOOLTIPS_ALREADY_SET
        self.tooltips_set = True

        #add info icons
        main_info_label = QLabel()
        main_info_label.setPixmap(ICONS.INFO_PIXMAP.scaledToHeight(self.main_label.sizeHint().height()))
        self.main_label_layout.addWidget(main_info_label, 10, alignment=Qt.AlignmentFlag.AlignLeft)

        date_info_label = QLabel()
        date_info_label.setPixmap(ICONS.INFO_PIXMAP.scaledToHeight(self.date_label.sizeHint().height()))
        self.date_label_layout.addWidget(date_info_label, alignment=Qt.AlignmentFlag.AlignLeft)

        product_info_label = QLabel()
        product_info_label.setPixmap(ICONS.INFO_PIXMAP.scaledToHeight(self.product_label.sizeHint().height()))
        self.product_label_layout.addWidget(product_info_label, 10, alignment=Qt.AlignmentFlag.AlignLeft)

        cf_info_label = QLabel()
        cf_info_label.setPixmap(ICONS.INFO_PIXMAP.scaledToHeight(self.cashflow_label.sizeHint().height()))
        self.cashflow_label_layout.addWidget(cf_info_label, alignment=Qt.AlignmentFlag.AlignLeft)
        
        cat_info_label = QLabel()
        cat_info_label.setPixmap(ICONS.INFO_PIXMAP.scaledToHeight(self.category_label.sizeHint().height()))
        self.category_label_layout.addWidget(cat_info_label, alignment=Qt.AlignmentFlag.AlignLeft)

        person_info_label = QLabel()
        person_info_label.setPixmap(ICONS.INFO_PIXMAP.scaledToHeight(self.person_label.sizeHint().height()))
        self.person_label_layout.addWidget(person_info_label, alignment=Qt.AlignmentFlag.AlignLeft)


        main_info_label.setToolTip(STRINGS.FTOOLTIP_MAIN)
        date_info_label.setToolTip(STRINGS.FTOOLTIP_DATE)
        product_info_label.setToolTip(STRINGS.FTOOLTIP_PRODUCT)
        cf_info_label.setToolTip(STRINGS.FTOOLTIP_CASHFLOW)
        cat_info_label.setToolTip(STRINGS.FTOOLTIP_CATEGORY)
        person_info_label.setToolTip(STRINGS.FTOOLTIP_PERSON)

    def updateFilterData(self):
        """
        gets the data from the form and saves it in the filter object
        if the user input cannot be saved as a float i.e ("-"), this method returns false to signal the caller, 
        that the data is not ready to submit
        :return: bool<submit-ready?>
        """
        self.filter.setContains(self.product_contains_edit.text())
        self.filter.setStartsWith(self.product_start_edit.text())
        self.filter.setCategories(self.CatCombo.getChoosenItems())
        self.filter.setFtPersons(self.FtpCombo.getChoosenItems())
        self.filter.setWhyPersons(self.WhyCombo.getChoosenItems())
        self.filter.setPersons(self.PersonCombo.getChoosenItems())
        self.filter.setAbsoluteValues(not self.absolute_button.isChecked())
        try:
            min_cf = False if self.min_fullp_edit.text() == "" else float(self.min_fullp_edit.text())
            max_cf = False if self.max_fullp_edit.text() == "" else float(self.max_fullp_edit.text())
            min_cf_pp = False if self.min_ppp_edit.text() == "" else float(self.min_ppp_edit.text())
            max_cf_pp = False if self.max_ppp_edit.text() == "" else float(self.max_ppp_edit.text())
        except:
            return False
        
        self.filter.setMinCashflow(min_cf)
        self.filter.setMaxCashflow(max_cf)
        self.filter.setMinCashflowPerProduct(min_cf_pp)
        self.filter.setMaxCashflowPerProduct(max_cf_pp)
        return True

    def update(self, get_form_data=True):
        """
        this method is updating the contents of the form based on the current filter settings
        :param get_form_data: bool<the current data from the form should be used? (disable at the first call)>
        :return: void
        """
        if get_form_data:
            self.updateFilterData() #updates the filter with the data from the form
        self.min_date_button.setText(self.filter.minDate.toString("dd.MM.yyyy"))
        self.max_date_button.setText(self.filter.maxDate.toString("dd.MM.yyyy"))
        self.absolute_button.setText(STRINGS.FWINDOW_ABSOLUTE if self.filter.absoluteValues else STRINGS.FWINDOW_RELATIVE)
        self.absolute_button.setChecked(False if self.filter.absoluteValues else True)
        self.product_contains_edit.setText(self.filter.contains)
        self.product_start_edit.setText(self.filter.startswith)
        if type(self.filter.minCashflow) != bool:
            #filter is set
            self.min_fullp_edit.setText(str(self.filter.minCashflow))
        if type(self.filter.maxCashflow) != bool:
            #filter is set
            self.max_fullp_edit.setText(str(self.filter.maxCashflow))
        if type(self.filter.minCashflowPerProduct) != bool:
            #filter is set
            self.min_ppp_edit.setText(str(self.filter.minCashflowPerProduct))
        if type(self.filter.maxCashflowPerProduct) != bool:
            #filter is set
            self.max_ppp_edit.setText(str(self.filter.maxCashflowPerProduct))

        self.CatCombo.setItems(self.filter.categories)
        self.FtpCombo.setItems(self.filter.ftpersons)
        self.WhyCombo.setItems(self.filter.whypersons)
        self.PersonCombo.setItems(self.filter.persons)

    def Eenter_only_numbers(self):
        """
        Event handler
        activates if the text in an input changed
        if a non number related symbol is entered, this handler deletes it.
        Makes sure that the input is a non negative valid float
        :return: void
        """
        assert(type(self.sender()) == QLineEdit), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        self.sender().setText(utils.only_numbers(self.sender(), negatives=not self.filter.absoluteValues))

    def Ereset_category(self):
        """
        Event handler
        activates if the categories are reseted
        :return: void
        """
        assert(type(self.sender()) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        self.CatCombo.reset()   #reset the ComboBoxes

    def Ereset_person(self):
        """
        Event handler
        activates if the persons are reseted
        :return: void
        """
        assert(type(self.sender()) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        self.WhyCombo.reset()       #reset the ComboBoxes
        self.FtpCombo.reset()
        self.PersonCombo.reset()

    def Esubmit_filter(self):
        """
        event handler, 
        does close the window and saves the current filter settings
        the caller can now look into self.filter to get the data
        :return: void
        """
        if self.updateFilterData():
            self.close()
        else:
            print("could not convert cashflow to float")

    def Eopen_calendar(self):
        """
        event handler
        activates if the user wants to select a date for the filter
        :return: void
        """
        sender = self.sender()
        assert(type(sender) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(sender)
        assert(sender == self.max_date_button or sender == self.min_date_button), STRINGS.ERROR_WRONG_SENDER+inspect.stack()[0][3]+", "+str(sender)
        if sender == self.min_date_button:
            #user selected the minimum date
            choosed_date = CalendarWindow(self.filter.minDate).date
            self.filter.setMinDate(choosed_date)
        elif sender == self.max_date_button:
            #user selected the maximum date
            choosed_date = CalendarWindow(self.filter.maxDate).date
            self.filter.setMaxDate(choosed_date)
        self.update()       #updates the gui (write the new dates on the buttons)

    def Etoggle_absolute(self):
        """
        event handler
        activates if the user wants to switch between absolute and relative cashflow values
        :return: void
        """
        sender = self.sender()
        assert(type(sender) == QPushButton), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(sender)
        assert(sender == self.absolute_button), STRINGS.ERROR_WRONG_SENDER+inspect.stack()[0][3]+", "+str(sender)
        self.update()

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
            
        if CONSTANTS.MAX_COMBOS > self.CatCombo.getLen():
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
            
        if CONSTANTS.MAX_COMBOS > self.FtpCombo.getLen():
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
            
        if CONSTANTS.MAX_COMBOS > self.WhyCombo.getLen():
            #add a new box, if the max boxes are not reached yet
            self.WhyCombo.addComboBox()

    def Eperson_choosed(self):
        """
        Event handler
        activates if the user choosed a person in a ComboBox
        adds a new ComboBox if neccessary
        :return: void
        """
        assert(type(self.sender()) == QComboBox), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        if not self.PersonCombo.isNoDefault():
            #if there are some ComboBoxes with the default category, no further boxes are added
            self.PersonCombo.updateItems()    #sets the items correctly (you can only choose every option once) 
            return
            
        if CONSTANTS.MAX_COMBOS > self.PersonCombo.getLen():
            #add a new box, if the max boxes are not reached yet
            self.PersonCombo.addComboBox()


class CalendarWindow(QDialog):
    """
    The CalendarWindow class contains the Window with only a calendar, that is automatically closed if a date is choosen
    """
    def __init__(self, startDate:QDate):
        """
        basic constructor is building the window.
        :param startDate: QDate<Date that is currently selected>
        :return: void
        """
        assert(type(startDate) == QDate), STRINGS.getTypeErrorString(startDate, "startDate", QDate)
        super().__init__()  #initializes the Base Class (QDialog)

        self.title = STRINGS.CWINDOW_TITLE

        self.start_date = startDate
        self.date = None

        #build the window
        self.InitWindow()

        self.exec() #show the window on top and make all other windows not clickable
        if self.date == None:
            #user didnt select any date (take the start date (no new date selected))
            self.date = self.start_date

    def InitWindow(self):
        """
        this method is building the window
        :return: void
        """
        self.setWindowTitle(self.title)
        self.grid = QGridLayout()       #sets the layout of the complete window

        self.createLayout()             #create the layout with all components

        self.setLayout(self.grid)
    
    def createLayout(self):
        """
        creates layout with only a calendar
        :return: void
        """
        assert("grid" in map(lambda x: x[0], vars(self).items())), STRINGS.ERROR_GRID_NOT_DEFINED
        self.calendar = QCalendarWidget()
        self.calendar.setMaximumDate(QDate.currentDate())
        self.calendar.setMinimumDate(QDate(1900, 1, 1))
        self.calendar.setSelectedDate(self.start_date)
        self.calendar.selectionChanged.connect(self.Eselected)
        self.grid.addWidget(self.calendar, 0, 0)

    def Eselected(self):
        """
        event handler 
        activates if the user selects a date, it will save that date and close the window
        :return: void
        """
        self.date = self.calendar.selectedDate()
        self.close()
