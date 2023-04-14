"""
This module provides the ui of the programm
"""

import inspect

from strings import ENG as STRINGS
from gui_constants import FONTS, ICONS
from constants import CONSTANTS
from backend import Backend
from backend_datatypes import Transaction
from ui_datatypes import Combo, Inputs, TransactionList, InvestmentList
from fullstack_utils import SortEnum, utils, Filter

from PyQt5.QtWidgets import QGridLayout, QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QWidget, QSizePolicy
from PyQt5.QtWidgets import QSpinBox, QCalendarWidget, QLineEdit, QCompleter, QComboBox, QMessageBox, QScrollArea, QFileDialog, QTabWidget
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QDate, Qt

class Window(QDialog):
    """
    The window class contains the main Window of the Application using Pyqt5
    the window class talks with the backend to display the right things
    The app consists of a object of class window
    """
    def __init__(self):
        """
        basic constructor is building the main window
        :return: void
        """
        super().__init__()  #initializes the Base Class (QDialog)

        self.title = STRINGS.APP_TITLE
        self.icon = QtGui.QIcon(STRINGS.APP_ICON)

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
        self.setWindowIcon(self.icon)

        self.tab = QTabWidget()     #the tab widget is the main widget of the whole window
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.grid = QGridLayout()       #sets the layout of the complete window

        self.createFirstTabLayout()             #create the layout of the first tab with all components
        self.createSecondTabLayout()            #creates the layout for the second tab
        #add these tabs to the tab widgets
        self.tab.addTab(self.tab1, STRINGS.APP_TAB1)
        self.tab.addTab(self.tab2, STRINGS.APP_TAB2)

        self.grid.addWidget(self.tab)
        self.setLayout(self.grid)

        self.show() #show the window
    
    def createFirstTabLayout(self):
        """
        creates layout components and add UI components to that layout
        build the window
        :return: void
        """
        assert("grid" in map(lambda x: x[0], vars(self).items())), STRINGS.ERROR_GRID_NOT_DEFINED
        self.grid1 = QGridLayout()  #layout for the first tab
        #meta label for the form part of the window, where the user can edit and create new transactions
        self.groupBox_transaction_label = QLabel(STRINGS.APP_LABEL_NEW_TRANSACTION, self)
        self.groupBox_transaction_label.setFont(FONTS.BIG_ITALIC_BOLD)
        self.groupBox_transaction = QGroupBox()
        self.layout_transaction = QVBoxLayout()
        #meta label for the last transaction part of the window, the user can scroll through the past transaction, search and sort them
        self.groupBox_lastTransactions_label = QLabel(STRINGS.APP_LABEL_LAST_TRANSACTIONS, self)
        self.groupBox_lastTransactions_label.setFont(FONTS.BIG_ITALIC_BOLD)
        self.groupBox_lastTransactions = QGroupBox()
        self.layout_lastTransaction = QVBoxLayout()
        #meta label for the edit part of the window, the user can rename, delete and merge products, categories and persons
        self.groupBox_edit_label = QLabel(STRINGS.APP_LABEL_EDIT, self)
        self.groupBox_edit_label.setFont(FONTS.BIG_ITALIC_BOLD)
        self.groupBox_edit = QGroupBox()
        self.layout_edit = QVBoxLayout()
        self.layout_edit.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.addWidgetsNewTrans()       #adds the Widgets to the "new transaction" part of the window
        self.addWidgetsLastTrans()      #adds the Widgets to the "last transaction" part of the window
        self.addWidgetsEdit()           #adds the Widgets to the "edit" part of the window
        self.setToolTips()              #set the tooltips for the tab
        self.updateFilter()             #updates the filter (init the filter)

        #sets the layouts and add these to the grid
        self.groupBox_transaction.setLayout(self.layout_transaction)
        self.grid1.addWidget(self.groupBox_transaction_label, 0, 0)
        self.grid1.addWidget(self.groupBox_transaction, 1, 0)

        self.groupBox_lastTransactions.setLayout(self.layout_lastTransaction)
        self.grid1.addWidget(self.groupBox_lastTransactions_label, 0, 1)
        self.grid1.addWidget(self.groupBox_lastTransactions, 1, 1)

        self.groupBox_edit.setLayout(self.layout_edit)
        self.grid1.addWidget(self.groupBox_edit_label, 0, 2)
        self.grid1.addWidget(self.groupBox_edit, 1, 2)
        self.tab1.setLayout(self.grid1)

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
        self.trans_cf_label.setFont(FONTS.ITALIC)
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
        self.submit_button.setFont(FONTS.BIG_BOLD)
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
        #********************FILTER**********************************
        #creates the filter buttons
        layout_filter = QHBoxLayout()
        widget_filter = QWidget()
        #change filter button, opens a new window where the user can change the filter settings
        self.filter_button = QPushButton(STRINGS.APP_BUTTON_FILTER_OFF)
        self.filter_button.clicked.connect(self.Eopen_filter)
        layout_filter.addWidget(self.filter_button)
        #resets the filter button
        self.reset_fiter_button = QPushButton(STRINGS.APP_BUTTON_FILTER_RESET)
        self.reset_fiter_button.clicked.connect(self.Ereset_filter)
        layout_filter.addWidget(self.reset_fiter_button)

        #number of transactions label, shows the number of currently visible transactions (applied to the filter)
        self.num_trans_label = QLabel("Placeholder")
        layout_filter.addWidget(self.num_trans_label)

        widget_filter.setLayout(layout_filter)
        self.layout_lastTransaction.addWidget(widget_filter)

        #********************SORT************************************
        #creates the sort buttons
        layout_sort = QHBoxLayout()
        widget_sort = QWidget()
        #sort for date, cashflow or product name
        self.scroll_sort_date_button = QPushButton(STRINGS.APP_BUTTON_LAST_TRANSACTIONS_DATE)
        self.scroll_sort_cf_button = QPushButton(STRINGS.APP_BUTTON_LAST_TRANSACTIONS_CASHFLOW)
        self.scroll_sort_product_button = QPushButton(STRINGS.APP_BUTTON_LAST_TRANSACTIONS_PRODUCT)

        self.sort_buttons = [self.scroll_sort_date_button, self.scroll_sort_cf_button, self.scroll_sort_product_button]
        
        for sort_button in self.sort_buttons:
            #set some aesthetics and connect to the right event handler
            sort_button.setFont(FONTS.SMALL)
            sort_button.setIcon(ICONS.SORT_DEFAULT)
            layout_sort.addWidget(sort_button)
            sort_button.clicked.connect(self.Esort_transactions)

        widget_sort.setLayout(layout_sort)
        self.layout_lastTransaction.addWidget(widget_sort)

        #********************SCROLLAREA******************************
        #creates a scrollarea with a vertical scroll bar and no horizontal scroll bar
        self.scrollarea = QScrollArea()
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollarea.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        self.scroll_widget = QWidget()      #inner widget, holds the buttons
        self.scroll_vbox = QVBoxLayout()    #layout for the inner widget
        self.scroll_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)    #buttons should build up from the top

        self.TransList.setLayout(self.scroll_vbox)  #sets the layout inside the datatype
        self.sortTransactions(SortEnum.DATE, True)            #loads the buttons from the backend

        #sets the layout of the inner widget and sets this widget in the scrollarea, finally adds the scrollarea to the main layout
        self.scroll_widget.setLayout(self.scroll_vbox)
        self.scrollarea.setWidget(self.scroll_widget)
        self.layout_lastTransaction.addWidget(self.scrollarea)

        #********************IMPORT_EXPORT_CSV***********************
        #set buttons for loading/exporting
        load_export_hbox = QHBoxLayout()
        load_export_widget = QWidget()
        #import button
        self.load_trans_button = QPushButton(STRINGS.APP_BUTTON_LOAD)
        self.load_trans_button.clicked.connect(self.Eload_csv)
        load_export_hbox.addWidget(self.load_trans_button)
        #export button
        self.export_trans_button = QPushButton(STRINGS.APP_BUTTON_EXPORT)
        self.export_trans_button.clicked.connect(self.Eexport_csv)
        load_export_hbox.addWidget(self.export_trans_button)

        load_export_widget.setLayout(load_export_hbox)
        self.layout_lastTransaction.addWidget(load_export_widget)

    def addWidgetsEdit(self):
        """
        adds the Widgets to the "edit products, categories and persons" part of the window
        and connects these widgets with the backend
        handles the behavior of these widgets too
        :return: void
        """
        #********************RENAMING********************************
        #renaming label
        label_renaming = QLabel(STRINGS.APP_LABEL_RENAMING)
        label_renaming.setFont(FONTS.BIG_BOLD)
        #renaming groupbox
        self.layout_edit.addWidget(label_renaming)
        groupbox_renaming = QGroupBox()
        layout_renaming = QHBoxLayout()
        #********************PRODUCT********************************
        groupbox_renaming_product = QGroupBox()
        layout_renaming_product = QVBoxLayout()
        #product choose label
        label_renaming_pro = QLabel(STRINGS.APP_LABEL_RENAMING_PRODUCT)
        layout_renaming_product.addWidget(label_renaming_pro)
        #product choose edit
        self.edit_renaming_pro = QLineEdit()
        self.edit_renaming_pro_completer = QCompleter(self.backend.getProductNames())
        self.edit_renaming_pro_completer.setCaseSensitivity(False)
        self.edit_renaming_pro.setCompleter(self.edit_renaming_pro_completer)
        self.edit_renaming_pro.textChanged.connect(self.Eproduct_renaming)
        layout_renaming_product.addWidget(self.edit_renaming_pro)
        #product new name label
        label_renaming_pro_edit = QLabel(STRINGS.APP_LABEL_RENAMING_PRODUCT_EDIT)
        layout_renaming_product.addWidget(label_renaming_pro_edit)
        #product new name edit
        self.edit_renaming_pro_edit = QLineEdit()
        self.edit_renaming_pro_edit.setEnabled(False)
        self.edit_renaming_pro_edit.textChanged.connect(self.Eproduct_renaming_edit)
        layout_renaming_product.addWidget(self.edit_renaming_pro_edit)
        #product renaming button
        self.button_renaming_product = QPushButton(STRINGS.APP_BUTTON_RENAMING_PRODUCT)
        self.button_renaming_product.setEnabled(False)
        self.button_renaming_product.clicked.connect(self.Eproduct_renamed)
        layout_renaming_product.addWidget(self.button_renaming_product)

        groupbox_renaming_product.setLayout(layout_renaming_product)
        layout_renaming.addWidget(groupbox_renaming_product)

        #********************CATEGORY********************************
        groupbox_renaming_category = QGroupBox()
        layout_renaming_category = QVBoxLayout()
        #category choose label
        label_renaming_cat = QLabel(STRINGS.APP_LABEL_RENAMING_CATEGORY)
        layout_renaming_category.addWidget(label_renaming_cat)
        #category choose edit
        self.edit_renaming_cat = QLineEdit()
        self.edit_renaming_cat_completer = QCompleter(self.backend.getCategories())
        self.edit_renaming_cat_completer.setCaseSensitivity(False)
        self.edit_renaming_cat.setCompleter(self.edit_renaming_cat_completer)
        self.edit_renaming_cat.textChanged.connect(self.Ecategory_renaming)
        layout_renaming_category.addWidget(self.edit_renaming_cat)
        #category new name label
        label_renaming_cat_edit = QLabel(STRINGS.APP_LABEL_RENAMING_CATEGORY_EDIT)
        layout_renaming_category.addWidget(label_renaming_cat_edit)
        #category new name edit
        self.edit_renaming_cat_edit = QLineEdit()
        self.edit_renaming_cat_edit.setEnabled(False)
        self.edit_renaming_cat_edit.textChanged.connect(self.Ecategory_renaming_edit)
        layout_renaming_category.addWidget(self.edit_renaming_cat_edit)
        #category renaming button
        self.button_renaming_category = QPushButton(STRINGS.APP_BUTTON_RENAMING_CATEGORY)
        self.button_renaming_category.setEnabled(False)
        self.button_renaming_category.clicked.connect(self.Ecategory_renamed)
        layout_renaming_category.addWidget(self.button_renaming_category)

        groupbox_renaming_category.setLayout(layout_renaming_category)
        layout_renaming.addWidget(groupbox_renaming_category)

        #********************PERSON**********************************
        groupbox_renaming_person = QGroupBox()
        layout_renaming_person = QVBoxLayout()
        #person choose label
        label_renaming_per = QLabel(STRINGS.APP_LABEL_RENAMING_PERSON)
        layout_renaming_person.addWidget(label_renaming_per)
        #person choose edit
        self.edit_renaming_per = QLineEdit()
        self.edit_renaming_per_completer = QCompleter(self.backend.getPersonNames())
        self.edit_renaming_per_completer.setCaseSensitivity(False)
        self.edit_renaming_per.setCompleter(self.edit_renaming_per_completer)
        self.edit_renaming_per.textChanged.connect(self.Eperson_renaming)
        layout_renaming_person.addWidget(self.edit_renaming_per)
        #person new name label
        label_renaming_per_edit = QLabel(STRINGS.APP_LABEL_RENAMING_PERSON_EDIT)
        layout_renaming_person.addWidget(label_renaming_per_edit)
        #person new name edit
        self.edit_renaming_per_edit = QLineEdit()
        self.edit_renaming_per_edit.setEnabled(False)
        self.edit_renaming_per_edit.textChanged.connect(self.Eperson_renaming_edit)
        layout_renaming_person.addWidget(self.edit_renaming_per_edit)
        #person renaming button
        self.button_renaming_person = QPushButton(STRINGS.APP_BUTTON_RENAMING_PERSON)
        self.button_renaming_person.setEnabled(False)
        self.button_renaming_person.clicked.connect(self.Eperson_renamed)
        layout_renaming_person.addWidget(self.button_renaming_person)

        groupbox_renaming_person.setLayout(layout_renaming_person)
        layout_renaming.addWidget(groupbox_renaming_person)


        groupbox_renaming.setLayout(layout_renaming)
        self.layout_edit.addWidget(groupbox_renaming)

        #********************DELETING********************************
        #deleting label
        label_deleting = QLabel(STRINGS.APP_LABEL_DELETING)
        label_deleting.setFont(FONTS.BIG_BOLD)
        #deleting groupbox
        self.layout_edit.addWidget(label_deleting)
        groupbox_deleting = QGroupBox()
        layout_deleting = QHBoxLayout()
        #********************PRODUCT*********************************
        groupbox_deleting_product = QGroupBox()
        layout_deleting_product = QVBoxLayout()
        #product choose label
        label_deleting_pro = QLabel(STRINGS.APP_LABEL_DELETING_PRODUCT)
        layout_deleting_product.addWidget(label_deleting_pro)
        #product choose edit
        self.edit_deleting_pro = QLineEdit()
        self.edit_deleting_pro_completer = QCompleter(self.backend.getProductNames())
        self.edit_deleting_pro_completer.setCaseSensitivity(False)
        self.edit_deleting_pro.setCompleter(self.edit_deleting_pro_completer)
        self.edit_deleting_pro.textChanged.connect(self.Eproduct_deleting)
        layout_deleting_product.addWidget(self.edit_deleting_pro)
        #product deleting button
        self.button_deleting_product = QPushButton(STRINGS.APP_BUTTON_DELETING_PRODUCT)
        self.button_deleting_product.setEnabled(False)
        self.button_deleting_product.clicked.connect(self.Eproduct_deleted)
        layout_deleting_product.addWidget(self.button_deleting_product)

        groupbox_deleting_product.setLayout(layout_deleting_product)
        layout_deleting.addWidget(groupbox_deleting_product)

        #********************CATEGORY********************************
        groupbox_deleting_category = QGroupBox()
        layout_deleting_category = QVBoxLayout()
        #category choose label
        label_deleting_cat = QLabel(STRINGS.APP_LABEL_DELETING_CATEGORY)
        layout_deleting_category.addWidget(label_deleting_cat)
        #category choose edit
        self.edit_deleting_cat = QLineEdit()
        self.edit_deleting_cat_completer = QCompleter(self.backend.getCategories())
        self.edit_deleting_cat_completer.setCaseSensitivity(False)
        self.edit_deleting_cat.setCompleter(self.edit_deleting_cat_completer)
        self.edit_deleting_cat.textChanged.connect(self.Ecategory_deleting)
        layout_deleting_category.addWidget(self.edit_deleting_cat)
        #category deleting button
        self.button_deleting_category = QPushButton(STRINGS.APP_BUTTON_DELETING_CATEGORY)
        self.button_deleting_category.setEnabled(False)
        self.button_deleting_category.clicked.connect(self.Ecategory_deleted)
        layout_deleting_category.addWidget(self.button_deleting_category)

        groupbox_deleting_category.setLayout(layout_deleting_category)
        layout_deleting.addWidget(groupbox_deleting_category)

        #********************PERSON*******************************
        groupbox_deleting_person = QGroupBox()
        layout_deleting_person = QVBoxLayout()
        #person choose label
        label_deleting_per = QLabel(STRINGS.APP_LABEL_DELETING_PERSON)
        layout_deleting_person.addWidget(label_deleting_per)
        #person choose edit
        self.edit_deleting_per = QLineEdit()
        self.edit_deleting_per_completer = QCompleter(self.backend.getPersonNames())
        self.edit_deleting_per_completer.setCaseSensitivity(False)
        self.edit_deleting_per.setCompleter(self.edit_deleting_per_completer)
        self.edit_deleting_per.textChanged.connect(self.Eperson_deleting)
        layout_deleting_person.addWidget(self.edit_deleting_per)
        #person deleting button
        self.button_deleting_person = QPushButton(STRINGS.APP_BUTTON_DELETING_PERSON)
        self.button_deleting_person.setEnabled(False)
        self.button_deleting_person.clicked.connect(self.Eperson_deleted)
        layout_deleting_person.addWidget(self.button_deleting_person)

        groupbox_deleting_person.setLayout(layout_deleting_person)
        layout_deleting.addWidget(groupbox_deleting_person)


        groupbox_deleting.setLayout(layout_deleting)
        self.layout_edit.addWidget(groupbox_deleting)

        #********************MERGING*********************************
        #merging label
        label_merging = QLabel(STRINGS.APP_LABEL_MERGING)
        label_merging.setFont(FONTS.BIG_BOLD)
        #merging groupbox
        self.layout_edit.addWidget(label_merging)
        groupbox_merging = QGroupBox()
        layout_merging = QHBoxLayout()
        #********************PRODUCT*********************************
        groupbox_merging_product = QGroupBox()
        layout_merging_product = QVBoxLayout()
        #product choose label1
        label_merging_pro1 = QLabel(STRINGS.APP_LABEL_MERGING_PRODUCT1)
        layout_merging_product.addWidget(label_merging_pro1)
        #product choose edit1
        self.edit_merging_pro1 = QLineEdit()
        self.edit_merging_pro_completer = QCompleter(self.backend.getProductNames())
        self.edit_merging_pro_completer.setCaseSensitivity(False)
        self.edit_merging_pro1.setCompleter(self.edit_merging_pro_completer)
        self.edit_merging_pro1.textChanged.connect(self.Eproduct_merging)
        layout_merging_product.addWidget(self.edit_merging_pro1)
        #product choose label2
        label_merging_pro2 = QLabel(STRINGS.APP_LABEL_MERGING_PRODUCT1)
        layout_merging_product.addWidget(label_merging_pro2)
        #product choose edit2
        self.edit_merging_pro2 = QLineEdit()
        self.edit_merging_pro2.setCompleter(self.edit_merging_pro_completer)
        self.edit_merging_pro2.textChanged.connect(self.Eproduct_merging)
        layout_merging_product.addWidget(self.edit_merging_pro2)
        #product new name label
        label_merging_pro_edit = QLabel(STRINGS.APP_LABEL_MERGING_PRODUCT_EDIT)
        layout_merging_product.addWidget(label_merging_pro_edit)
        #product new name edit
        self.edit_merging_pro_edit = QLineEdit()
        self.edit_merging_pro_edit.setEnabled(False)
        self.edit_merging_pro_edit.textChanged.connect(self.Eproduct_merging_edit)
        layout_merging_product.addWidget(self.edit_merging_pro_edit)
        #product merging button
        self.button_merging_product = QPushButton(STRINGS.APP_BUTTON_MERGING_PRODUCT)
        self.button_merging_product.setEnabled(False)
        self.button_merging_product.clicked.connect(self.Eproduct_merged)
        layout_merging_product.addWidget(self.button_merging_product)

        groupbox_merging_product.setLayout(layout_merging_product)
        layout_merging.addWidget(groupbox_merging_product)

        #********************CATEGORY********************************
        groupbox_merging_category = QGroupBox()
        layout_merging_category = QVBoxLayout()
        #category choose label1
        label_merging_cat1 = QLabel(STRINGS.APP_LABEL_MERGING_CATEGORY1)
        layout_merging_category.addWidget(label_merging_cat1)
        #category choose edit1
        self.edit_merging_cat1 = QLineEdit()
        self.edit_merging_cat_completer = QCompleter(self.backend.getCategories())
        self.edit_merging_cat_completer.setCaseSensitivity(False)
        self.edit_merging_cat1.setCompleter(self.edit_merging_cat_completer)
        self.edit_merging_cat1.textChanged.connect(self.Ecategory_merging)
        layout_merging_category.addWidget(self.edit_merging_cat1)
        #category choose label2
        label_merging_cat2 = QLabel(STRINGS.APP_LABEL_MERGING_CATEGORY2)
        layout_merging_category.addWidget(label_merging_cat2)
        #category choose edit2
        self.edit_merging_cat2 = QLineEdit()
        self.edit_merging_cat2.setCompleter(self.edit_merging_cat_completer)
        self.edit_merging_cat2.textChanged.connect(self.Ecategory_merging)
        layout_merging_category.addWidget(self.edit_merging_cat2)
        #category new name label
        label_merging_cat_edit = QLabel(STRINGS.APP_LABEL_MERGING_CATEGORY_EDIT)
        layout_merging_category.addWidget(label_merging_cat_edit)
        #category new name edit
        self.edit_merging_cat_edit = QLineEdit()
        self.edit_merging_cat_edit.setEnabled(False)
        self.edit_merging_cat_edit.textChanged.connect(self.Ecategory_merging_edit)
        layout_merging_category.addWidget(self.edit_merging_cat_edit)
        #category merging button
        self.button_merging_category = QPushButton(STRINGS.APP_BUTTON_MERGING_CATEGORY)
        self.button_merging_category.setEnabled(False)
        self.button_merging_category.clicked.connect(self.Ecategory_merged)
        layout_merging_category.addWidget(self.button_merging_category)

        groupbox_merging_category.setLayout(layout_merging_category)
        layout_merging.addWidget(groupbox_merging_category)

        #********************PERSON**********************************
        groupbox_merging_person = QGroupBox()
        layout_merging_person = QVBoxLayout()
        #person choose label1
        label_merging_per1 = QLabel(STRINGS.APP_LABEL_MERGING_PERSON1)
        layout_merging_person.addWidget(label_merging_per1)
        #person choose edit1
        self.edit_merging_per1 = QLineEdit()
        self.edit_merging_per_completer = QCompleter(self.backend.getPersonNames())
        self.edit_merging_per_completer.setCaseSensitivity(False)
        self.edit_merging_per1.setCompleter(self.edit_merging_per_completer)
        self.edit_merging_per1.textChanged.connect(self.Eperson_merging)
        layout_merging_person.addWidget(self.edit_merging_per1)
        #person choose label2
        label_merging_per2 = QLabel(STRINGS.APP_LABEL_MERGING_PERSON2)
        layout_merging_person.addWidget(label_merging_per2)
        #person choose edit2
        self.edit_merging_per2 = QLineEdit()
        self.edit_merging_per2.setCompleter(self.edit_merging_per_completer)
        self.edit_merging_per2.textChanged.connect(self.Eperson_merging)
        layout_merging_person.addWidget(self.edit_merging_per2)
        #person new name label
        label_merging_per_edit = QLabel(STRINGS.APP_LABEL_MERGING_PERSON_EDIT)
        layout_merging_person.addWidget(label_merging_per_edit)
        #person new name edit
        self.edit_merging_per_edit = QLineEdit()
        self.edit_merging_per_edit.setEnabled(False)
        self.edit_merging_per_edit.textChanged.connect(self.Eperson_merging_edit)
        layout_merging_person.addWidget(self.edit_merging_per_edit)
        #person merging button
        self.button_merging_person = QPushButton(STRINGS.APP_BUTTON_MERGING_PERSON)
        self.button_merging_person.setEnabled(False)
        self.button_merging_person.clicked.connect(self.Eperson_merged)
        layout_merging_person.addWidget(self.button_merging_person)

        groupbox_merging_person.setLayout(layout_merging_person)
        layout_merging.addWidget(groupbox_merging_person)


        groupbox_merging.setLayout(layout_merging)
        self.layout_edit.addWidget(groupbox_merging)

    def createSecondTabLayout(self):
        """
        creates layout components and add UI components to that layout
        build the window
        :return: void
        """
        assert("grid" in map(lambda x: x[0], vars(self).items())), STRINGS.ERROR_GRID_NOT_DEFINED
        self.grid2 = QGridLayout()  #layout for the first tab
        self.grid2.addWidget(InvestTab(self.backend))   #add the invest widget that is handled in a own class
        self.tab2.setLayout(self.grid2)


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
        delete_button.setFont(FONTS.BIG_BOLD)
        delete_button.setStyleSheet("color:red")
        self.submit_layout.addWidget(delete_button)

        cancel_button = QPushButton(STRINGS.APP_BUTTON_EDIT_TRANSACTION_CANCEL)
        cancel_button.setFont(FONTS.BIG_BOLD)
        self.submit_layout.addWidget(cancel_button)

        #disconnect renaming ui components
        self.button_renaming_category.disconnect()
        self.button_renaming_person.disconnect()
        self.button_renaming_product.disconnect()
        self.button_deleting_category.disconnect()
        self.button_deleting_person.disconnect()
        self.button_deleting_product.disconnect()
        self.button_merging_category.disconnect()
        self.button_merging_person.disconnect()
        self.button_merging_product.disconnect()

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

        #connect renaming ui components
        self.button_renaming_category.clicked.connect(self.Ecategory_renamed)
        self.button_renaming_person.clicked.connect(self.Eperson_renamed)
        self.button_renaming_product.clicked.connect(self.Eproduct_renamed)
        self.button_deleting_category.clicked.connect(self.Ecategory_deleted)
        self.button_deleting_person.clicked.connect(self.Eperson_deleted)
        self.button_deleting_product.clicked.connect(self.Eproduct_deleted)
        self.button_merging_category.clicked.connect(self.Ecategory_merged)
        self.button_merging_person.clicked.connect(self.Eperson_merged)
        self.button_merging_product.clicked.connect(self.Eproduct_merged)

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
        for but in self.TransList.buttons_transaction_dict.keys():
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
        for but in self.TransList.buttons_transaction_dict.keys():
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
        self.num_trans_label.setText(str(self.TransList.getTransactionCount())+STRINGS.APP_LABEL_TRANSACTION_COUNT)

    def productsChanged(self):
        """
        this helper method is should be called if the products changed
        it will update stuff that needs updated products data
        :return: void
        """
        self.trans_product_completer = QCompleter(self.backend.getProductNames())
        self.trans_product_completer.setCaseSensitivity(False)
        self.trans_product_edit.setCompleter(self.trans_product_completer)      #add an autocompleter
        self.edit_renaming_pro_completer = QCompleter(self.backend.getProductNames())
        self.edit_renaming_pro_completer.setCaseSensitivity(False)
        self.edit_renaming_pro.setCompleter(self.edit_renaming_pro_completer)      #add an autocompleter
        self.edit_deleting_pro_completer = QCompleter(self.backend.getProductNames())
        self.edit_deleting_pro_completer.setCaseSensitivity(False)
        self.edit_deleting_pro.setCompleter(self.edit_deleting_pro_completer)      #add an autocompleter
        self.edit_merging_pro_completer = QCompleter(self.backend.getProductNames())
        self.edit_merging_pro_completer.setCaseSensitivity(False)
        self.edit_merging_pro1.setCompleter(self.edit_merging_pro_completer)      #add an autocompleter
        self.edit_merging_pro2.setCompleter(self.edit_merging_pro_completer)      #add an autocompleter
        self.TransList.updateLastTrans()    

    def categoriesChanged(self):
        """
        this helper method is should be called if the categories changed
        it will update stuff that needs updated categories data
        :return: void
        """
        self.edit_renaming_cat_completer = QCompleter(self.backend.getCategories())
        self.edit_renaming_cat_completer.setCaseSensitivity(False)
        self.edit_renaming_cat.setCompleter(self.edit_renaming_cat_completer)      #add an autocompleter
        self.edit_deleting_cat_completer = QCompleter(self.backend.getCategories())
        self.edit_deleting_cat_completer.setCaseSensitivity(False)
        self.edit_deleting_cat.setCompleter(self.edit_deleting_cat_completer)      #add an autocompleter
        self.edit_merging_cat_completer = QCompleter(self.backend.getCategories())
        self.edit_merging_cat_completer.setCaseSensitivity(False)
        self.edit_merging_cat1.setCompleter(self.edit_merging_cat_completer)      #add an autocompleter
        self.edit_merging_cat2.setCompleter(self.edit_merging_cat_completer)      #add an autocompleter
        self.CatCombo.updateItems()
    
    def personsChanged(self):
        """
        this helper method is should be called if the persons changed
        it will update stuff that needs updated persons data
        :return: void
        """
        self.edit_renaming_per_completer = QCompleter(self.backend.getPersonNames())
        self.edit_renaming_per_completer.setCaseSensitivity(False)
        self.edit_renaming_per.setCompleter(self.edit_renaming_per_completer)      #add an autocompleter
        self.edit_deleting_per_completer = QCompleter(self.backend.getPersonNames())
        self.edit_deleting_per_completer.setCaseSensitivity(False)
        self.edit_deleting_per.setCompleter(self.edit_deleting_per_completer)      #add an autocompleter
        self.edit_merging_per_completer = QCompleter(self.backend.getPersonNames())
        self.edit_merging_per_completer.setCaseSensitivity(False)
        self.edit_merging_per1.setCompleter(self.edit_merging_per_completer)      #add an autocompleter
        self.edit_merging_per2.setCompleter(self.edit_merging_per_completer)      #add an autocompleter
        self.FtpCombo.updateItems()
        self.WhyCombo.updateItems()


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
            value = utils.getNumberFromLineEdit(edit)
            
            #gets the number of products (its a spinBox, that is why it has to be an int)
            number = self.trans_number_spin_box.value()

            #disconnect from this event handler to prevent recursion
            self.trans_fullp_edit.textChanged.disconnect(self.Esync_cashflows)

            assert(type(value) in (float, int) and type(number) in (float, int)), STRINGS.ERROR_NOT_TYPE_NUM+str(number)+", "+str(value)
            self.trans_fullp_edit.setText(str(value*number))    #sets the synced cashflow
            #connect to this event handler again
            self.trans_fullp_edit.textChanged.connect(self.Esync_cashflows)
        
        #if the full price was changed
        if edit == self.trans_fullp_edit:
            value = utils.getNumberFromLineEdit(edit)
            
            #gets the number of products (its a spinBox, that is why it has to be an int)
            number = self.trans_number_spin_box.value()

            #disconnect from this event handler to prevent recursion
            self.trans_ppp_edit.textChanged.disconnect(self.Esync_cashflows)

            assert(type(value) in (float, int) and type(number) in (float, int)), STRINGS.ERROR_NOT_TYPE_NUM+str(number)+", "+str(value)
            self.trans_ppp_edit.setText(str(value/number))      #sets the synced cashflow
            #connect to this event handler again
            self.trans_ppp_edit.textChanged.connect(self.Esync_cashflows)

        #if the product number was changed
        if edit == self.trans_number_spin_box:
            value = utils.getNumberFromLineEdit(self.trans_ppp_edit)
            #gets the number of products (its a spinBox, that is why it has to be an int)
            number = edit.value()
            #disconnect from this event handler to prevent recursion
            self.trans_fullp_edit.textChanged.disconnect(self.Esync_cashflows)
            assert(type(value) in (float, int) and type(number) in (float, int)), STRINGS.ERROR_NOT_TYPE_NUM+str(number)+", "+str(value)
            self.trans_fullp_edit.setText(str(value*number))                #sets the synced cashflow
            #connect to this event handler again
            self.trans_fullp_edit.textChanged.connect(self.Esync_cashflows)
    
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
        self.categoriesChanged()

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
        self.personsChanged()
    
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
        self.personsChanged()

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
            self.productsChanged()
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
        self.productsChanged()
        
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
        self.productsChanged()
        self.categoriesChanged()
        self.personsChanged()

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
                self.productsChanged()
                self.categoriesChanged()
                self.personsChanged()

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

    def Ecategory_renaming(self):
        """
        event handler 
        activates if the user types something into the choose category field of the renamer
        :return: void
        """
        edit:QLineEdit = self.sender()
        assert(edit == self.edit_renaming_cat), STRINGS.getTypeErrorString(edit, "sender", self.edit_renaming_cat)
        if edit.text().lower() in  map(lambda x: x.lower(), self.edit_renaming_cat_completer.children()[0].stringList()):
            #user entered a valid category
            self.edit_renaming_cat_edit.setEnabled(True)
            if len(self.edit_renaming_cat_edit.text()) - self.edit_renaming_cat_edit.text().count(" ") >= 3:
                #user entered a valid new category name
                self.button_renaming_category.setEnabled(True)
        else:
            self.edit_renaming_cat_edit.setEnabled(False)
            self.button_renaming_category.setEnabled(False)

        if self.edit_renaming_cat_edit.text().lower() in map(lambda x: x.lower(), self.edit_renaming_cat_completer.children()[0].stringList()):
            #try to rename to an existing one
            self.button_renaming_category.setEnabled(False)
            return

    def Ecategory_renaming_edit(self):
        """
        event handler 
        activates if the user types something into the choose category edit field of the renamer
        :return: void
        """
        edit:QLineEdit = self.sender()
        assert(edit == self.edit_renaming_cat_edit), STRINGS.getTypeErrorString(edit, "sender", self.edit_renaming_cat_edit)
        if edit.text().lower() in map(lambda x: x.lower(), self.edit_renaming_cat_completer.children()[0].stringList()):
            #try to rename to an existing one
            self.button_renaming_category.setEnabled(False)
            return
        if len(edit.text()) - edit.text().count(" ") >= 3:
            #user entered a valid new category name
            self.button_renaming_category.setEnabled(True)
        else:
            self.button_renaming_category.setEnabled(False)
    
    def Ecategory_renamed(self):
        """
        event handler 
        activates if the user presses the rename button in the category renamer
        :return: void
        """
        edit:QPushButton = self.sender()
        assert(edit == self.button_renaming_category), STRINGS.getTypeErrorString(edit, "sender", self.button_renaming_category)
        assert(not(self.edit_mode)), STRINGS.ERROR_IN_EDIT_MODE
        category = self.edit_renaming_cat.text()
        new_category = self.edit_renaming_cat_edit.text()
        self.edit_renaming_cat_edit.setText("")
        self.edit_renaming_cat.setText("")
        self.backend.renameCategory(category.lower(), new_category)
        self.categoriesChanged()
        #show message that the renaming was successful
        msg = QMessageBox()
        msg.information(self, STRINGS.INFO_RENAMED_SUCCESSFUL, 
            STRINGS.INFO_RENAMED_SUCCESSFUL_PART1+STRINGS.INFO_RENAMED_SUCCESSFUL_CATEGORY_PART2+category+STRINGS.INFO_RENAMED_SUCCESSFUL_PART3+new_category)

    def Eperson_renaming(self):
        """
        event handler 
        activates if the user types something into the choose person field of the renamer
        :return: void
        """
        edit:QLineEdit = self.sender()
        assert(edit == self.edit_renaming_per), STRINGS.getTypeErrorString(edit, "sender", self.edit_renaming_per)
        if edit.text().lower() in map(lambda x: x.lower(), self.edit_renaming_per_completer.children()[0].stringList()):
            #user entered a valid person
            self.edit_renaming_per_edit.setEnabled(True)
            if len(self.edit_renaming_per_edit.text()) - self.edit_renaming_per_edit.text().count(" ") >= 3:
                #user entered a valid new person name
                self.button_renaming_person.setEnabled(True)
        else:
            self.edit_renaming_per_edit.setEnabled(False)
            self.button_renaming_person.setEnabled(False)
            
        if self.edit_renaming_per_edit.text().lower() in map(lambda x: x.lower(), self.edit_renaming_per_completer.children()[0].stringList()):
            #try to rename to an existing one
            self.button_renaming_person.setEnabled(False)
            return

    def Eperson_renaming_edit(self):
        """
        event handler 
        activates if the user types something into the choose person edit field of the renamer
        :return: void
        """
        edit:QLineEdit = self.sender()
        assert(edit == self.edit_renaming_per_edit), STRINGS.getTypeErrorString(edit, "sender", self.edit_renaming_per_edit)
        if edit.text().lower() in map(lambda x: x.lower(), self.edit_renaming_per_completer.children()[0].stringList()):
            #try to rename to an existing one
            self.button_renaming_person.setEnabled(False)
            return
        if len(edit.text()) - edit.text().count(" ") >= 3:
            #user entered a valid new person name
            self.button_renaming_person.setEnabled(True)
        else:
            self.button_renaming_person.setEnabled(False)
    
    def Eperson_renamed(self):
        """
        event handler 
        activates if the user presses the rename button in the person renamer
        :return: void
        """
        edit:QPushButton = self.sender()
        assert(edit == self.button_renaming_person), STRINGS.getTypeErrorString(edit, "sender", self.button_renaming_person)
        assert(not(self.edit_mode)), STRINGS.ERROR_IN_EDIT_MODE
        person = self.edit_renaming_per.text()
        new_person = self.edit_renaming_per_edit.text()
        self.edit_renaming_per_edit.setText("")
        self.edit_renaming_per.setText("")
        self.backend.renamePerson(person.lower(), new_person)
        self.personsChanged()
        #show message that the renaming was successful
        msg = QMessageBox()
        msg.information(self, STRINGS.INFO_RENAMED_SUCCESSFUL, 
            STRINGS.INFO_RENAMED_SUCCESSFUL_PART1+STRINGS.INFO_RENAMED_SUCCESSFUL_PERSON_PART2+person+STRINGS.INFO_RENAMED_SUCCESSFUL_PART3+new_person)

    def Eproduct_renaming(self):
        """
        event handler 
        activates if the user types something into the choose product field of the renamer
        :return: void
        """
        edit:QLineEdit = self.sender()
        assert(edit == self.edit_renaming_pro), STRINGS.getTypeErrorString(edit, "sender", self.edit_renaming_pro)
        if edit.text().lower() in map(lambda x: x.lower(), self.edit_renaming_pro_completer.children()[0].stringList()):
            #user entered a valid product
            self.edit_renaming_pro_edit.setEnabled(True)
            if len(self.edit_renaming_pro_edit.text()) - self.edit_renaming_pro_edit.text().count(" ") >= 3:
                #user entered a valid new product name
                self.button_renaming_product.setEnabled(True)
        else:
            self.edit_renaming_pro_edit.setEnabled(False)
            self.button_renaming_product.setEnabled(False)
            
        if self.edit_renaming_pro_edit.text().lower() in map(lambda x: x.lower(), self.edit_renaming_pro_completer.children()[0].stringList()):
            #try to rename to an existing one
            self.button_renaming_product.setEnabled(False)
            return

    def Eproduct_renaming_edit(self):
        """
        event handler 
        activates if the user types something into the choose product edit field of the renamer
        :return: void
        """
        edit:QLineEdit = self.sender()
        assert(edit == self.edit_renaming_pro_edit), STRINGS.getTypeErrorString(edit, "sender", self.edit_renaming_pro_edit)
        if edit.text().lower() in map(lambda x: x.lower(), self.edit_renaming_pro_completer.children()[0].stringList()):
            #try to rename to an existing one
            self.button_renaming_product.setEnabled(False)
            return
        if len(edit.text()) - edit.text().count(" ") >= 3:
            #user entered a valid new product name
            self.button_renaming_product.setEnabled(True)
        else:
            self.button_renaming_product.setEnabled(False)
    
    def Eproduct_renamed(self):
        """
        event handler 
        activates if the user presses the rename button in the product renamer
        :return: void
        """
        edit:QPushButton = self.sender()
        assert(edit == self.button_renaming_product), STRINGS.getTypeErrorString(edit, "sender", self.button_renaming_product)
        assert(not(self.edit_mode)), STRINGS.ERROR_IN_EDIT_MODE
        product = self.edit_renaming_pro.text()
        new_product = self.edit_renaming_pro_edit.text()
        self.edit_renaming_pro_edit.setText("")
        self.edit_renaming_pro.setText("")
        self.backend.renameProduct(product.lower(), new_product)
        self.productsChanged()
        #show message that the renaming was successful
        msg = QMessageBox()
        msg.information(self, STRINGS.INFO_RENAMED_SUCCESSFUL, 
            STRINGS.INFO_RENAMED_SUCCESSFUL_PART1+STRINGS.INFO_RENAMED_SUCCESSFUL_PRODUCT_PART2+product+STRINGS.INFO_RENAMED_SUCCESSFUL_PART3+new_product)

    def Ecategory_deleting(self):
        """
        event handler 
        activates if the user types something into the choose category field of the deleter
        :return: void
        """
        edit:QLineEdit = self.sender()
        assert(edit == self.edit_deleting_cat), STRINGS.getTypeErrorString(edit, "sender", self.edit_deleting_cat)
        if edit.text().lower() in  map(lambda x: x.lower(), self.edit_deleting_cat_completer.children()[0].stringList()):
            #user entered a valid category
            self.button_deleting_category.setEnabled(True)
        else:
            self.button_deleting_category.setEnabled(False)

    def Ecategory_deleted(self):
        """
        event handler 
        activates if the user presses the delete button in the category deleter
        :return: void
        """
        edit:QPushButton = self.sender()
        assert(edit == self.button_deleting_category), STRINGS.getTypeErrorString(edit, "sender", self.button_deleting_category)
        assert(not(self.edit_mode)), STRINGS.ERROR_IN_EDIT_MODE
        #disclaimer
        ret = QMessageBox.question(self, STRINGS.QUESTION_TITLE, STRINGS.QUESTION_DELETING_CATEGORY, QMessageBox.Yes | QMessageBox.No)
        if ret != QMessageBox.Yes:
            #user aborted the deletion
            return
        category = self.edit_deleting_cat.text()
        self.edit_deleting_cat.setText("")
        self.backend.deleteCategoryByName(category.lower())
        self.categoriesChanged()
        #show message that the deleting was successful
        msg = QMessageBox()
        msg.information(self, STRINGS.INFO_DELETED_SUCCESSFUL, 
            STRINGS.INFO_DELETED_SUCCESSFUL_PART1+STRINGS.INFO_DELETED_SUCCESSFUL_CATEGORY_PART2+category)

    def Eperson_deleting(self):
        """
        event handler 
        activates if the user types something into the choose person field of the deleter
        :return: void
        """
        edit:QLineEdit = self.sender()
        assert(edit == self.edit_deleting_per), STRINGS.getTypeErrorString(edit, "sender", self.edit_deleting_per)
        if edit.text().lower() in map(lambda x: x.lower(), self.edit_deleting_per_completer.children()[0].stringList()):
            #user entered a valid person
            self.button_deleting_person.setEnabled(True)
        else:
            self.button_deleting_person.setEnabled(False)
    
    def Eperson_deleted(self):
        """
        event handler 
        activates if the user presses the delete button in the person deleter
        :return: void
        """
        edit:QPushButton = self.sender()
        assert(edit == self.button_deleting_person), STRINGS.getTypeErrorString(edit, "sender", self.button_deleting_person)
        assert(not(self.edit_mode)), STRINGS.ERROR_IN_EDIT_MODE
        #disclaimer
        ret = QMessageBox.question(self, STRINGS.QUESTION_TITLE, STRINGS.QUESTION_DELETING_PERSON, QMessageBox.Yes | QMessageBox.No)
        if ret != QMessageBox.Yes:
            #user aborted the deletion
            return
        person = self.edit_deleting_per.text()
        self.edit_deleting_per.setText("")
        self.backend.deletePersonByName(person.lower())
        self.personsChanged()
        #show message that the deleting was successful
        msg = QMessageBox()
        msg.information(self, STRINGS.INFO_DELETED_SUCCESSFUL, 
            STRINGS.INFO_DELETED_SUCCESSFUL_PART1+STRINGS.INFO_DELETED_SUCCESSFUL_PERSON_PART2+person)

    def Eproduct_deleting(self):
        """
        event handler 
        activates if the user types something into the choose product field of the deleter
        :return: void
        """
        edit:QLineEdit = self.sender()
        assert(edit == self.edit_deleting_pro), STRINGS.getTypeErrorString(edit, "sender", self.edit_deleting_pro)
        if edit.text().lower() in map(lambda x: x.lower(), self.edit_deleting_pro_completer.children()[0].stringList()):
            #user entered a valid product
            self.button_deleting_product.setEnabled(True)
        else:
            self.button_deleting_product.setEnabled(False)
 
    def Eproduct_deleted(self):
        """
        event handler 
        activates if the user presses the delete button in the product deleter
        :return: void
        """
        edit:QPushButton = self.sender()
        assert(edit == self.button_deleting_product), STRINGS.getTypeErrorString(edit, "sender", self.button_deleting_product)
        assert(not(self.edit_mode)), STRINGS.ERROR_IN_EDIT_MODE
        #disclaimer
        ret = QMessageBox.question(self, STRINGS.QUESTION_TITLE, STRINGS.QUESTION_DELETING_PRODUCT, QMessageBox.Yes | QMessageBox.No)
        if ret != QMessageBox.Yes:
            #user aborted the deletion
            return
        product = self.edit_deleting_pro.text()
        self.edit_deleting_pro.setText("")
        self.backend.deleteProductByName(product.lower())
        self.productsChanged()
        #show message that the deleting was successful
        msg = QMessageBox()
        msg.information(self, STRINGS.INFO_DELETED_SUCCESSFUL, 
            STRINGS.INFO_DELETED_SUCCESSFUL_PART1+STRINGS.INFO_DELETED_SUCCESSFUL_PRODUCT_PART2+product)

    def Ecategory_merging(self):
        """
        event handler 
        activates if the user types something into the choose category field of the merger
        :return: void
        """
        edit:QLineEdit = self.sender()
        items = list(map(lambda x: x.lower(), self.edit_renaming_cat_completer.children()[0].stringList()))
        inds = []
        edits = [self.edit_merging_cat1, self.edit_merging_cat2]
        assert(edit in edits), STRINGS.getTypeErrorString(edit, "sender", edits)
        for edit in edits:
            if not(edit.text().lower() in items):
                #at least one input is not a right name
                self.edit_merging_cat_edit.setEnabled(False)
                self.button_merging_category.setEnabled(False)
                return
            else:
                if items.index(edit.text().lower()) in inds:
                    #both inputs are the same, merge not possible
                    self.edit_merging_cat_edit.setEnabled(False)
                    self.button_merging_category.setEnabled(False)
                    return
                inds.append(items.index(edit.text().lower()))

        #both inputs are right names, unlock the renamer and the button if the renamer already contains enough chars
        self.edit_merging_cat_edit.setEnabled(True)
        self.button_merging_category.setEnabled(False)
        if len(self.edit_merging_cat_edit.text()) - self.edit_merging_cat_edit.text().count(" ") >= 3:
            #user entered a valid new category name
            self.button_merging_category.setEnabled(True)    

    def Ecategory_merging_edit(self):
        """
        event handler 
        activates if the user types something into the choose category edit field of the merger
        :return: void
        """
        edit:QLineEdit = self.sender()
        assert(edit == self.edit_merging_cat_edit), STRINGS.getTypeErrorString(edit, "sender", self.edit_merging_cat_edit)
        if len(edit.text()) - edit.text().count(" ") >= 3:
            #user entered a valid new category name
            self.button_merging_category.setEnabled(True)
        else:
            self.button_merging_category.setEnabled(False)
    
    def Ecategory_merged(self):
        """
        event handler 
        activates if the user presses the merge button in the category merger
        :return: void
        """
        edit:QPushButton = self.sender()
        assert(edit == self.button_merging_category), STRINGS.getTypeErrorString(edit, "sender", self.button_merging_category)
        assert(not(self.edit_mode)), STRINGS.ERROR_IN_EDIT_MODE
        #disclaimer
        ret = QMessageBox.question(self, STRINGS.QUESTION_TITLE, STRINGS.QUESTION_MERGING_CATEGORY, QMessageBox.Yes | QMessageBox.No)
        if ret != QMessageBox.Yes:
            #user aborted the merge
            return
        category1 = self.edit_merging_cat1.text()
        category2 = self.edit_merging_cat2.text()
        new_category = self.edit_merging_cat_edit.text()
        self.edit_merging_cat_edit.setText("")
        self.edit_merging_cat1.setText("")
        self.edit_merging_cat2.setText("")
        self.backend.mergeCategory(category1.lower(), category2.lower(), new_category)
        self.categoriesChanged()
        #show message that the merging was successful
        msg = QMessageBox()
        msg.information(self, STRINGS.INFO_MERGED_SUCCESSFUL, 
            STRINGS.INFO_MERGED_SUCCESSFUL_PART1+STRINGS.INFO_MERGED_SUCCESSFUL_CATEGORY_PART2+category1+", "+category2+STRINGS.INFO_MERGED_SUCCESSFUL_PART3+new_category)

    def Eperson_merging(self):
        """
        event handler 
        activates if the user types something into the choose person field of the merger
        :return: void
        """
        edit:QLineEdit = self.sender()
        items = list(map(lambda x: x.lower(), self.edit_renaming_per_completer.children()[0].stringList()))
        inds = []
        edits = [self.edit_merging_per1, self.edit_merging_per2]
        assert(edit in edits), STRINGS.getTypeErrorString(edit, "sender", edits)
        for edit in edits:
            if not(edit.text().lower() in items):
                #at least one input is not a right name
                self.edit_merging_per_edit.setEnabled(False)
                self.button_merging_person.setEnabled(False)
                return
            else:
                if items.index(edit.text().lower()) in inds:
                    #both inputs are the same, merge not possible
                    self.edit_merging_per_edit.setEnabled(False)
                    self.button_merging_person.setEnabled(False)
                    return
                inds.append(items.index(edit.text().lower()))
        #both inputs are right names, unlock the renamer and the button if the renamer already contains enough chars
        self.edit_merging_per_edit.setEnabled(True)
        self.button_merging_person.setEnabled(False)
        if len(self.edit_merging_per_edit.text()) - self.edit_merging_per_edit.text().count(" ") >= 3:
            #user entered a valid new person name
            self.button_merging_person.setEnabled(True)    

    def Eperson_merging_edit(self):
        """
        event handler 
        activates if the user types something into the choose person edit field of the merger
        :return: void
        """
        edit:QLineEdit = self.sender()
        assert(edit == self.edit_merging_per_edit), STRINGS.getTypeErrorString(edit, "sender", self.edit_merging_per_edit)
        if len(edit.text()) - edit.text().count(" ") >= 3:
            #user entered a valid new person name
            self.button_merging_person.setEnabled(True)
        else:
            self.button_merging_person.setEnabled(False)
    
    def Eperson_merged(self):
        """
        event handler 
        activates if the user presses the merge button in the person merger
        :return: void
        """
        edit:QPushButton = self.sender()
        assert(edit == self.button_merging_person), STRINGS.getTypeErrorString(edit, "sender", self.button_merging_person)
        assert(not(self.edit_mode)), STRINGS.ERROR_IN_EDIT_MODE
        #disclaimer
        ret = QMessageBox.question(self, STRINGS.QUESTION_TITLE, STRINGS.QUESTION_MERGING_PERSON, QMessageBox.Yes | QMessageBox.No)
        if ret != QMessageBox.Yes:
            #user aborted the merge
            return
        person1 = self.edit_merging_per1.text()
        person2 = self.edit_merging_per2.text()
        new_person = self.edit_merging_per_edit.text()
        self.edit_merging_per_edit.setText("")
        self.edit_merging_per1.setText("")
        self.edit_merging_per2.setText("")
        self.backend.mergePerson(person1.lower(), person2.lower(), new_person)
        self.personsChanged()
        #show message that the merging was successful
        msg = QMessageBox()
        msg.information(self, STRINGS.INFO_MERGED_SUCCESSFUL, 
            STRINGS.INFO_MERGED_SUCCESSFUL_PART1+STRINGS.INFO_MERGED_SUCCESSFUL_PERSON_PART2+person1+", "+person2+STRINGS.INFO_MERGED_SUCCESSFUL_PART3+new_person)

    def Eproduct_merging(self):
        """
        event handler 
        activates if the user types something into the choose product field of the merger
        :return: void
        """
        edit:QLineEdit = self.sender()
        items = list(map(lambda x: x.lower(), self.edit_renaming_pro_completer.children()[0].stringList()))
        inds = []
        edits = [self.edit_merging_pro1, self.edit_merging_pro2]
        assert(edit in edits), STRINGS.getTypeErrorString(edit, "sender", edits)
        for edit in edits:
            if not(edit.text().lower() in items):
                #at least one input is not a right name
                self.edit_merging_pro_edit.setEnabled(False)
                self.button_merging_product.setEnabled(False)
                return
            else:
                if items.index(edit.text().lower()) in inds:
                    #both inputs are the same, merge not possible
                    self.edit_merging_pro_edit.setEnabled(False)
                    self.button_merging_product.setEnabled(False)
                    return
                inds.append(items.index(edit.text().lower()))

        #both inputs are right names, unlock the renamer and the button if the renamer already contains enough chars
        self.edit_merging_pro_edit.setEnabled(True)
        self.button_merging_product.setEnabled(False)
        if len(self.edit_merging_pro_edit.text()) - self.edit_merging_pro_edit.text().count(" ") >= 3:
            #user entered a valid new product name
            self.button_merging_product.setEnabled(True)  

    def Eproduct_merging_edit(self):
        """
        event handler 
        activates if the user types something into the choose product edit field of the merger
        :return: void
        """
        edit:QLineEdit = self.sender()
        assert(edit == self.edit_merging_pro_edit), STRINGS.getTypeErrorString(edit, "sender", self.edit_merging_pro_edit)
        if len(edit.text()) - edit.text().count(" ") >= 3:
            #user entered a valid new product name
            self.button_merging_product.setEnabled(True)
        else:
            self.button_merging_product.setEnabled(False)

    def Eproduct_merged(self):
        """
        event handler 
        activates if the user presses the merge button in the product merger
        :return: void
        """
        edit:QPushButton = self.sender()
        assert(edit == self.button_merging_product), STRINGS.getTypeErrorString(edit, "sender", self.button_merging_product)
        assert(not(self.edit_mode)), STRINGS.ERROR_IN_EDIT_MODE
        #disclaimer
        ret = QMessageBox.question(self, STRINGS.QUESTION_TITLE, STRINGS.QUESTION_MERGING_PRODUCT, QMessageBox.Yes | QMessageBox.No)
        if ret != QMessageBox.Yes:
            #user aborted the merge
            return
        product1 = self.edit_merging_pro1.text()
        product2 = self.edit_merging_pro2.text()
        new_product = self.edit_merging_pro_edit.text()
        self.edit_merging_pro_edit.setText("")
        self.edit_merging_pro1.setText("")
        self.edit_merging_pro2.setText("")
        self.backend.mergeProduct(product1.lower(), product2.lower(), new_product)
        self.productsChanged()
        #show message that the merging was successful
        msg = QMessageBox()
        msg.information(self, STRINGS.INFO_MERGED_SUCCESSFUL, 
            STRINGS.INFO_MERGED_SUCCESSFUL_PART1+STRINGS.INFO_MERGED_SUCCESSFUL_PRODUCT_PART2+product1+", "+product2+STRINGS.INFO_MERGED_SUCCESSFUL_PART3+new_product)


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
        self.main_label.setFont(FONTS.BIG_ITALIC_BOLD)
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
        self.date_label.setFont(FONTS.ITALIC_UNDERLINE)
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
        self.product_label.setFont(FONTS.ITALIC_UNDERLINE)
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
        self.cashflow_label.setFont(FONTS.ITALIC_UNDERLINE)
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
        self.category_label.setFont(FONTS.ITALIC_UNDERLINE)
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
        self.person_label.setFont(FONTS.ITALIC_UNDERLINE)
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
        self.submit_button.setFont(FONTS.BIG_BOLD)
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


class InvestTab(QWidget):
    """
    this widget is made of all ui components needed for the investment tab
    this widget just needs to be added to the layout of this tab
    """
    def __init__(self, backend):
        """
        basic constructor
        takes the backend as an argument to get to the data needed for this tab
        :param backend: object<Backend>
        :return: void
        """
        super().__init__()  #creates a widget (the widget that the object contains of)

        self.grid = QGridLayout()       #layout for the object
        self.grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.backend:Backend = backend  #saves the backend
        self.InvestmentList = InvestmentList(self.backend.getInvestments, self.Eedit_last_investment)
        self.Inputs = Inputs(["ticker", "number", "price"], self.activateSubmitButton, self.deactivateSubmitButton)
        self.mode = "buy"

        self.InitWidget()       #creates the base state of the widget

    def InitWidget(self):
        """
        this init method should be called in the constructor after creating a layout for the widget
        the ui components and base states are created
        :return: void
        """
        assert("grid" in map(lambda x: x[0], vars(self).items())), STRINGS.ERROR_GRID_NOT_DEFINED
        
        #********************FORM************************************
        #here you can enter a new investment or edit a past investment
        #label for the form
        self.label_form = QLabel(STRINGS.INVFORM_LABEL_NEW_INV)
        self.label_form.setFont(FONTS.BIG_ITALIC_BOLD)
        self.label_form.setFixedSize(self.label_form.sizeHint())
        self.grid.addWidget(self.label_form, 0, 0)
        
        self.addWidgetsForm()       #add the ui components to build the form
        self.addWidgetsLastInvestments()    #add the ui components to build the last investments part
        self.switchMode()      #switches to the set mode

        self.setLayout(self.grid)
        self.adjustSize()
    
    def addWidgetsForm(self):
        """
        adds the Widgets to the form part of the window
        you can create your investments here
        handles the behavior of these widgets too
        :return: void
        """
        assert("grid" in map(lambda x: x[0], vars(self).items())), STRINGS.ERROR_GRID_NOT_DEFINED
        #create the layout and widget for the whole form
        self.layout_form = QVBoxLayout()
        self.layout_form.setSpacing(20)
        self.widget_form = QGroupBox()

        #********************CALENDAR********************************
        #the user can select on which date the investment was made
        self.date_edit = QCalendarWidget()
        self.date_edit.setMinimumDate(QDate(1900, 1, 1))
        self.date_edit.setMaximumDate(QDate.currentDate())
        #removes the vertical header (week of the year) to save space
        self.date_edit.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.layout_form.addWidget(self.date_edit)

        #********************CHOSE_TRADE_TYPE************************
        #holds the comboBox for choosing the type of the transaction
        #the user can choose from trading types. There are "buy", "dividend" or "sell"
        group_trade_type = QGroupBox()
        layout_trade_type = QVBoxLayout()

        #creates the label for the trade type
        self.trade_type_label = QLabel(STRINGS.INVFORM_LABEL_TRADE_TYPE)
        self.trade_type_label.setFont(FONTS.ITALIC)
        layout_trade_type.addWidget(self.trade_type_label)

        #creates the combo from which the user can choose the trade type
        self.trade_type_combo = QComboBox()
        self.trade_type_combo.setMaxVisibleItems(20)
        self.trade_type_combo.setStyleSheet("combobox-popup: 0;")
        self.trade_type_combo.addItems([STRINGS.INVFORM_TYPE_BUY, STRINGS.INVFORM_TYPE_DIVIDEND, STRINGS.INVFORM_TYPE_SELL])
        self.trade_type_combo.setCurrentText(STRINGS.INVFORM_TYPE_BUY)
        self.trade_type_combo.currentTextChanged.connect(self.Eselect_trading_type)
        layout_trade_type.addWidget(self.trade_type_combo, alignment=Qt.AlignmentFlag.AlignLeft)

        group_trade_type.setLayout(layout_trade_type)
        self.layout_form.addWidget(group_trade_type)

        #********************YAHOO_TICKER****************************
        #holds the widget for the input of the ticker you bought or sold
        #the user can enter a yahoo ticker from the asset he bought
        #if the form is in sell or dividend mode, this input will be replaced by a combobox from which the user can choose a owned asset
        self.groupbox_ticker_num = QGroupBox()
        self.hgrid_ticker_num = QGridLayout()
        
        #ticker label
        self.ticker_label = QLabel(STRINGS.INVFORM_LABEL_TICKER)
        self.hgrid_ticker_num.addWidget(self.ticker_label, 0, 0)

        #ticker input
        self.ticker_edit = QLineEdit()
        self.ticker_completer = QCompleter(self.backend.getTickerNames())   #backend call to get the ticker names
        self.ticker_completer.setCaseSensitivity(False)
        self.ticker_edit.setCompleter(self.ticker_completer)      #add an autocompleter
        self.ticker_edit.textChanged.connect(self.Echange_ticker_text)
        self.hgrid_ticker_num.addWidget(self.ticker_edit, 1, 0)

        #********************NUMBER OF ASSETS************************
        #the user can enter the number of assets that are bought from the given ticker
        #if the form is in sell or dividend mode, the number is limited by the amount of owned assets
        #number of assets label
        self.number_label = QLabel(STRINGS.INVFORM_LABEL_NUMBER)
        self.hgrid_ticker_num.addWidget(self.number_label, 0, 1)

        #number of assets input
        self.number_edit = QLineEdit()
        self.number_edit.textChanged.connect(self.Eenter_only_positive_numbers)
        self.number_edit.textChanged.connect(self.Echange_number_text)
        self.number_edit.textChanged.connect(self.Esync_cashflows)
        self.hgrid_ticker_num.addWidget(self.number_edit, 1, 1)

        #completes this group
        self.groupbox_ticker_num.setLayout(self.hgrid_ticker_num)
        self.layout_form.addWidget(self.groupbox_ticker_num)

        #********************PRICE********************************
        #holds the labels and inputs for the price of the asset
        #the user can enter the price to which the asset was bought or sold (or the dividend in dividend mode)
        #the user can enter the price per asset or the price for the whole transaction (or dividend). They will be synced automatically
        grid_price = QGridLayout()
        groupbox_price_full = QGroupBox()

        #meta label for the group
        price_meta_widget = QWidget()
        self.price_meta_layout = QHBoxLayout()
        self.price_meta_layout.setContentsMargins(0,0,0,0)
        self.price_label = QLabel(STRINGS.INVFORM_LABEL_PRICE)
        self.price_label.setFont(FONTS.ITALIC)
        self.price_meta_layout.addWidget(self.price_label)

        price_meta_widget.setLayout(self.price_meta_layout)
        grid_price.addWidget(price_meta_widget, 0, 0, 1, 2)

        #price per asset label
        self.ppa_label = QLabel(STRINGS.INVFORM_LABEL_PRICE_PER_ASSET)
        grid_price.addWidget(self.ppa_label, 2, 1)

        #full price label
        self.fullp_label = QLabel(STRINGS.INVFORM_LABEL_PRICE_FULL)
        grid_price.addWidget(self.fullp_label, 2, 2)

        #price per asset input
        self.ppa_edit = QLineEdit()
        self.ppa_edit.textChanged.connect(self.Eenter_only_positive_numbers)
        self.ppa_edit.textChanged.connect(self.Echange_price_text)
        self.ppa_edit.textChanged.connect(self.Esync_cashflows)
        grid_price.addWidget(self.ppa_edit, 3, 1)

        #full price input
        self.fullp_edit = QLineEdit()
        self.fullp_edit.textChanged.connect(self.Eenter_only_positive_numbers)
        self.fullp_edit.textChanged.connect(self.Echange_price_text)
        self.fullp_edit.textChanged.connect(self.Esync_cashflows)
        grid_price.addWidget(self.fullp_edit, 3, 2)

        #sets up the layout for this group
        groupbox_price_full.setLayout(grid_price)
        self.layout_form.addWidget(groupbox_price_full)

        #********************FEES********************************
        #holds the labels and inputs for the fees and costs occured by the transaction
        #the user can enter the amount of other costs that are paid. 
        #the amount of trading fees for buying and selling and the taxes for dividends and selling
        self.grid_fee = QGridLayout()
        groupbox_fee_full = QGroupBox()

        #meta label for the group
        fee_meta_widget = QWidget()
        self.fee_meta_layout = QHBoxLayout()
        self.fee_meta_layout.setContentsMargins(0,0,0,0)
        self.fee_label = QLabel(STRINGS.INVFORM_LABEL_FEES)
        self.fee_label.setFont(FONTS.ITALIC)
        self.fee_meta_layout.addWidget(self.fee_label)

        fee_meta_widget.setLayout(self.fee_meta_layout)
        self.grid_fee.addWidget(fee_meta_widget, 0, 0, 1, 2)

        #trading fee label
        self.tradingfee_label = QLabel(STRINGS.INVFORM_LABEL_TRADINGFEE)
        self.grid_fee.addWidget(self.tradingfee_label, 2, 1)

        #trading fee input
        self.tradingfee_edit = QLineEdit()
        self.tradingfee_edit.textChanged.connect(self.Eenter_only_positive_numbers)
        self.grid_fee.addWidget(self.tradingfee_edit, 3, 1)

        #taxes label
        self.tax_label = QLabel(STRINGS.INVFORM_LABEL_TAX)
        self.grid_fee.addWidget(self.tax_label, 2, 2)
        
        #taxes input
        self.tax_edit = QLineEdit()
        self.tax_edit.textChanged.connect(self.Eenter_only_positive_numbers)
        self.grid_fee.addWidget(self.tax_edit, 3, 2)

        #sets up the layout for this group
        groupbox_fee_full.setLayout(self.grid_fee)
        self.layout_form.addWidget(groupbox_fee_full)

        #********************SUBMIT_BUTTON***************************
        #submit investment button
        self.submit_widget = QWidget()
        self.submit_layout = QHBoxLayout()

        self.submit_button = QPushButton(STRINGS.INVFORM_BUTTON_SUBMIT)
        self.submit_button.setFont(FONTS.BIG_BOLD)
        #at default the button is disabled, you need to fill out all required fields to activate it
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.Esubmit_investment)
        self.submit_layout.addWidget(self.submit_button)

        self.submit_widget.setLayout(self.submit_layout)
        self.layout_form.addWidget(self.submit_widget)

        self.widget_form.setLayout(self.layout_form)
        self.widget_form.setFixedSize(self.widget_form.sizeHint())
        
        self.grid.addWidget(self.widget_form, 1, 0)

    def addWidgetsLastInvestments(self):
        """
        adds the Widgets to the last investments part of the window
        you can see your investments here and click on them to edit
        handles the behavior of these widgets too
        :return: void
        """
        assert("grid" in map(lambda x: x[0], vars(self).items())), STRINGS.ERROR_GRID_NOT_DEFINED
        #create the layout and widget for the whole part
        self.layout_investments = QVBoxLayout()
        self.layout_investments.setSpacing(20)
        self.widget_investments = QGroupBox()
        #********************FILTER**********************************
        #creates the filter buttons
        layout_filter = QHBoxLayout()
        widget_filter = QWidget()
        #change filter button, opens a new window where the user can change the filter settings
        self.filter_button = QPushButton(STRINGS.APP_BUTTON_FILTER_OFF)
        self.filter_button.clicked.connect(self.Eopen_filter)
        layout_filter.addWidget(self.filter_button)
        #resets the filter button
        self.reset_fiter_button = QPushButton(STRINGS.APP_BUTTON_FILTER_RESET)
        self.reset_fiter_button.clicked.connect(self.Ereset_filter)
        layout_filter.addWidget(self.reset_fiter_button)

        #number of investments label, shows the number of currently visible trades (applied to the filter)
        self.num_trade_label = QLabel("Placeholder")
        layout_filter.addWidget(self.num_trade_label)

        widget_filter.setLayout(layout_filter)
        self.layout_investments.addWidget(widget_filter)

        #********************SORT************************************
        #creates the sort buttons
        layout_sort = QHBoxLayout()
        widget_sort = QWidget()
        #sort for date, price for the trade or short name
        self.scroll_sort_date_button = QPushButton(STRINGS.APP_BUTTON_LAST_TRANSACTIONS_DATE)
        self.scroll_sort_price_button = QPushButton(STRINGS.APP_BUTTON_LAST_TRANSACTIONS_CASHFLOW)
        self.scroll_sort_name_button = QPushButton(STRINGS.APP_BUTTON_LAST_TRANSACTIONS_PRODUCT)

        self.sort_buttons = [self.scroll_sort_date_button, self.scroll_sort_price_button, self.scroll_sort_name_button]
        
        for sort_button in self.sort_buttons:
            #set some aesthetics and connect to the right event handler
            sort_button.setFont(FONTS.SMALL)
            sort_button.setIcon(ICONS.SORT_DEFAULT)
            layout_sort.addWidget(sort_button)
            sort_button.clicked.connect(self.Esort_investments)

        widget_sort.setLayout(layout_sort)
        self.layout_investments.addWidget(widget_sort)

        #********************SCROLLAREA******************************
        #creates a scrollarea with a vertical scroll bar and no horizontal scroll bar
        self.scrollarea = QScrollArea()
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollarea.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        self.scroll_widget = QWidget()      #inner widget, holds the buttons
        self.scroll_vbox = QVBoxLayout()    #layout for the inner widget
        self.scroll_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)    #buttons should build up from the top

        self.InvestmentList.setLayout(self.scroll_vbox)  #sets the layout inside the datatype
        self.sortInvestments(SortEnum.DATE, True)            #loads the buttons from the backend

        #sets the layout of the inner widget and sets this widget in the scrollarea, finally adds the scrollarea to the main layout
        self.scroll_widget.setLayout(self.scroll_vbox)
        self.scrollarea.setWidget(self.scroll_widget)
        self.layout_investments.addWidget(self.scrollarea)

        #********************IMPORT_EXPORT_CSV***********************
        #set buttons for loading/exporting
        load_export_hbox = QHBoxLayout()
        load_export_widget = QWidget()
        #import button
        self.load_inv_button = QPushButton(STRINGS.APP_BUTTON_LOAD)
        self.load_inv_button.clicked.connect(self.Eload_csv)
        load_export_hbox.addWidget(self.load_inv_button)
        #export button
        self.export_inv_button = QPushButton(STRINGS.APP_BUTTON_EXPORT)
        self.export_inv_button.clicked.connect(self.Eexport_csv)
        load_export_hbox.addWidget(self.export_inv_button)

        load_export_widget.setLayout(load_export_hbox)
        self.layout_investments.addWidget(load_export_widget)

        self.widget_investments.setLayout(self.layout_investments)
        self.widget_investments.setFixedSize(self.widget_investments.sizeHint())
        self.grid.addWidget(self.widget_investments, 1, 1)

    def switchToBuyMode(self):
        """
        this method will change the ui of the form to match a buy
        this includes: renaming of labels, disabling and enabling input fields 
        and replacing the combo box for the assets with an input box
        :return: void
        """
        self.mode = "buy"
        self.wipeForm() #delete all data that is currently in the form (except date)
        #renaming labels
        self.ticker_label.setText(STRINGS.INVFORM_LABEL_TICKER)
        self.number_label.setText(STRINGS.INVFORM_LABEL_NUMBER)
        self.price_label.setText(STRINGS.INVFORM_LABEL_PRICE)
        self.ppa_label.setText(STRINGS.INVFORM_LABEL_PRICE_PER_ASSET)
        self.fullp_label.setText(STRINGS.INVFORM_LABEL_PRICE_FULL)
        #replace the combo box with an input box (the user can indeed buy an asset that he currently dont have)
        self.ticker_edit.deleteLater()
        self.ticker_edit = QLineEdit()
        self.ticker_completer = QCompleter(self.backend.getTickerNames())
        self.ticker_completer.setCaseSensitivity(False)
        self.ticker_edit.setCompleter(self.ticker_completer)      #add an autocompleter
        self.ticker_edit.textChanged.connect(self.Echange_ticker_text)
        self.hgrid_ticker_num.addWidget(self.ticker_edit, 1, 0)
        #disabling and enabling input fields 
        self.tradingfee_edit.setEnabled(True)       #in buy mode there are trading fees
        self.tax_edit.setEnabled(False)             #but no taxes
        
    def switchToDividendMode(self):
        """
        this method will change the ui of the form to match a dividend
        this includes: renaming of labels, disabling and enabling input fields 
        and replacing the input field with a combobox for the assets
        :return: void
        """
        self.mode = "dividend"
        self.wipeForm() #delete all data that is currently in the form (except date)
        #renaming labels
        self.ticker_label.setText(STRINGS.INVFORM_LABEL_SELECT_STOCK)
        self.number_label.setText(STRINGS.INVFORM_LABEL_NUMBER_DIV_SHARES)
        self.price_label.setText(STRINGS.INVFORM_LABEL_DIVIDEND_RECEIVED)
        self.ppa_label.setText(STRINGS.INVFORM_LABEL_DIVIDEND_PER_SHARE)
        self.fullp_label.setText(STRINGS.INVFORM_LABEL_DIVIDEND_FULL)
        #replace the input field from the buy mode with a comboBox (the user can only get a dividend from stocks he already owns)
        self.ticker_edit.deleteLater()
        self.ticker_edit = QComboBox()
        self.ticker_edit.setMaxVisibleItems(20)
        self.ticker_edit.setStyleSheet("combobox-popup: 0;")
        self.ticker_edit.addItems(self.backend.getAvailableShortNames())
        self.ticker_edit.currentTextChanged.connect(self.Eselect_asset)
        self.ticker_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.hgrid_ticker_num.addWidget(self.ticker_edit, 1, 0)
        #disabling and enabling input fields 
        self.tradingfee_edit.setEnabled(False)  #in dividend mode there are no trading fees
        self.tax_edit.setEnabled(True)          #but taxes

    def switchToSellMode(self):
        """
        this method will change the ui of the form to match a sell
        this includes: renaming of labels, disabling and enabling input fields 
        and replacing the input field with a combobox for the assets
        :return: void
        """
        self.mode = "sell"
        self.wipeForm() #delete all data that is currently in the form (except date)
        #renaming labels
        self.ticker_label.setText(STRINGS.INVFORM_LABEL_SELECT_STOCK)
        self.number_label.setText(STRINGS.INVFORM_LABEL_NUMBER)
        self.price_label.setText(STRINGS.INVFORM_LABEL_PRICE)
        self.ppa_label.setText(STRINGS.INVFORM_LABEL_PRICE_PER_ASSET)
        self.fullp_label.setText(STRINGS.INVFORM_LABEL_PRICE_FULL)
        #replace the input field from the buy mode with a comboBox (the user can only sell a stock he already owns)
        self.ticker_edit.deleteLater()
        self.ticker_edit = QComboBox()
        self.ticker_edit.setMaxVisibleItems(20)
        self.ticker_edit.setStyleSheet("combobox-popup: 0;")
        self.ticker_edit.addItems(self.backend.getAvailableShortNames())
        self.ticker_edit.currentTextChanged.connect(self.Eselect_asset)
        self.ticker_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.hgrid_ticker_num.addWidget(self.ticker_edit, 1, 0)
        #disabling and enabling input fields 
        self.tradingfee_edit.setEnabled(True)   #in sell mode there are trading fees
        self.tax_edit.setEnabled(True)          #and taxes

    def wipeForm(self):
        """
        this method deletes all data except the date out of the form
        :return: void
        """
        #before the text of an input field is set to an empty string, we have to check whether thats actually an input field
        #because in the different modes of the form there might be one input field replaced with some other non input field
        if type(self.ticker_edit) == QLineEdit:
            self.ticker_edit.setText("")
        if type(self.ppa_edit) == QLineEdit:
            self.ppa_edit.setText("")
        if type(self.fullp_edit) == QLineEdit:
            self.fullp_edit.setText("")
        if type(self.tax_edit) == QLineEdit:
            self.tax_edit.setText("")
        if type(self.number_edit) == QLineEdit:
            self.number_edit.setText("")
        if type(self.tradingfee_edit) == QLineEdit:
            self.tradingfee_edit.setText("")

    def sortInvestments(self, sortElement:SortEnum, up:bool=True):
        """
        this method sets the right icon for the sort buttons and makes sure the investments are sorted
        :param sortElement: object<SortEnum> after which category should be sorted?
        :param up: bool<from A-Z, new-old, or small-big>
        :return: void
        """
        #sets all icons to the default
        for sort_button in self.sort_buttons:
            sort_button.setIcon(ICONS.SORT_DEFAULT)

        #gets the right icon depending on the sort order
        icon = ICONS.SORT_UP if up else ICONS.SORT_DOWN
        self.sort_buttons[sortElement.value].setIcon(icon)  #sets that icon to the right button
        self.backend.sortInvestments(sortElement, up)  #sets the sort rule in the backend
        self.InvestmentList.updateLastInvestments()         #gets the new data from the backend and display it

    def activateSubmitButton(self):
        """
        activates the submit button, gets called after all required inputs are done
        :return: void
        """
        self.submit_button.setEnabled(True)
    
    def deactivateSubmitButton(self):
        """
        deactivates the submit button, gets called if not all required inputs are done
        :return: void
        """
        self.submit_button.setEnabled(False)

    def getDataFromForm(self):
        """
        gets the contents of the form and parse them to the right datatypes
        if some data are not readable (empty, or non number data) it returns 0 for that data
        :return: list[datetime.date<date of the transaction>, str<trade_type>, str<ticker>, float<number>, float<ppa>, float<tradingfee>, float<tax>]
        """
        date = self.date_edit.selectedDate().toPyDate()

        match self.trade_type_combo.currentText():
            case STRINGS.INVFORM_TYPE_BUY:
                trade_type = "buy"
            case STRINGS.INVFORM_TYPE_SELL:
                trade_type = "sell"
            case STRINGS.INVFORM_TYPE_DIVIDEND:
                trade_type = "dividend"
            case _:
                print("some invalid trading type "+self.trade_type_combo.currentText())
                raise ValueError
            
        if type(self.ticker_edit) == QLineEdit:
            #Buy mode
            assert(trade_type == "buy")
            ticker = self.ticker_edit.text().lower()
        else:
            assert(trade_type != "buy")
            ticker = self.backend.getTickerForName(self.ticker_edit.currentText()).lower()
        try:
            number = float(self.number_edit.text())
        except:
            number = 0.0
        try:
            ppa = float(self.ppa_edit.text())
        except:
            ppa = 0.0
        try:
            tradingfee = float(self.tradingfee_edit.text())
        except:
            tradingfee = 0.0
        try:
            tax = float(self.tax_edit.text())
        except:
            tax = 0.0
        return (date, trade_type, ticker, number, ppa, tradingfee, tax)

    def switchMode(self):
        match self.mode:
            #check which mode is selected and switch to that mode
            case "buy":
                self.switchToBuyMode()
            case "dividend":
                self.switchToDividendMode()
            case "sell":
                self.switchToSellMode()
            case _:
                #if not other case is met, the programm will land here
                #the selected text is not in the possible choices
                assert(False), STRINGS.ERROR_TRADE_TYPE_NOT_VALID+self.sender().currentText()

    def investmentChanged(self):
        self.switchMode()   #reload the form
        self.ticker_completer = QCompleter(self.backend.getTickerNames())   #backend call to get the ticker names
        self.ticker_completer.setCaseSensitivity(False)
        self.ticker_edit.setCompleter(self.ticker_completer)      #add an autocompleter
        self.InvestmentList.updateLastInvestments()


    def Eenter_only_positive_numbers(self):
        """
        Event handler
        activates if the text in an input changed
        if a non number related symbol is entered, this handler deletes it.
        Makes sure that the input is a non negative valid float
        :return: void
        """
        assert(type(self.sender()) == QLineEdit), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        self.sender().setText(utils.only_numbers(self.sender(), negatives=False))   #redirects to a event handler
    
    def Eenter_only__numbers(self):
        """
        Event handler
        activates if the text in an input changed
        if a non number related symbol is entered, this handler deletes it.
        Makes sure that the input is a valid float
        :return: void
        """
        assert(type(self.sender()) == QLineEdit), STRINGS.ERROR_WRONG_SENDER_TYPE+inspect.stack()[0][3]+", "+type(self.sender())
        self.sender().setText(utils.only_numbers(self.sender(), negatives=True))   #redirects to a event handler 

    def Esync_cashflows(self):
        """
        Event handler
        activates if the text in an cashflow input changed (or asset number)
        syncs the cashflow by taking the changed input and the asset number as the base to calculate the other cashflow input
        if the asset number is changed, the base is the price per asset and the full price gets synced
        :return: void
        """
        assert(self.sender() in (self.ppa_edit, self.fullp_edit, self.number_edit)), STRINGS.ERROR_WRONG_SENDER+inspect.stack()[0][3]+", "+self.sender()
        edit = self.sender()
        value = utils.getNumberFromLineEdit(edit)
        #if the price per asset was changed
        if edit == self.ppa_edit:
            #gets the number of assets
            number = utils.getNumberFromLineEdit(self.number_edit)

            #disconnect from this event handler to prevent recursion
            self.fullp_edit.textChanged.disconnect(self.Esync_cashflows)

            assert(type(value) in (float, int) and type(number) in (float, int)), STRINGS.ERROR_NOT_TYPE_NUM+str(number)+", "+str(value)
            self.fullp_edit.setText(str(value*number))    #sets the synced cashflow
            #connect to this event handler again
            self.fullp_edit.textChanged.connect(self.Esync_cashflows)
        
        #if the full price was changed
        if edit == self.fullp_edit:
            #gets the number of assets
            number = utils.getNumberFromLineEdit(self.number_edit)

            #disconnect from this event handler to prevent recursion
            self.ppa_edit.textChanged.disconnect(self.Esync_cashflows)

            assert(type(value) in (float, int) and type(number) in (float, int)), STRINGS.ERROR_NOT_TYPE_NUM+str(number)+", "+str(value)
            self.ppa_edit.setText(str(value/number))      #sets the synced cashflow
            #connect to this event handler again
            self.ppa_edit.textChanged.connect(self.Esync_cashflows)

        #if the product number was changed
        if edit == self.number_edit:
            number = value
            value = utils.getNumberFromLineEdit(self.ppa_edit)
            #disconnect from this event handler to prevent recursion
            self.fullp_edit.textChanged.disconnect(self.Esync_cashflows)
            assert(type(value) in (float, int) and type(number) in (float, int)), STRINGS.ERROR_NOT_TYPE_NUM+str(number)+", "+str(value)
            self.fullp_edit.setText(str(value*number))                #sets the synced cashflow
            #connect to this event handler again
            self.fullp_edit.textChanged.connect(self.Esync_cashflows)

    def Echange_ticker_text(self):
        """
        event handler
        activates if the user types something into the ticker input field (only in buy mode)
        :return: void
        """
        assert(self.sender() == self.ticker_edit and type(self.ticker_edit) == QLineEdit), STRINGS.getTypeErrorString(self.sender(), "sender", QLineEdit)
        if self.sender().text() != "":
            self.Inputs.setInput("ticker", True)
        else:
            self.Inputs.setInput("ticker", False)

    def Echange_number_text(self):
        """
        event handler
        activates if the user types something into the number input field
        :return: void
        """
        assert(self.sender() == self.number_edit), STRINGS.getTypeErrorString(self.sender(), "sender", self.number_edit)
        try:
            float(self.sender().text())
            self.Inputs.setInput("number", True)
        except:
            self.Inputs.setInput("number", False)

    def Echange_price_text(self):
        """
        event handler
        activates if the user types something into the price input fields
        :return: void
        """
        assert(self.sender() in [self.fullp_edit, self.ppa_edit]), STRINGS.getTypeErrorString(self.sender(), "sender", "price inputs")
        try:
            float(self.sender().text())
            self.Inputs.setInput("price", True)
        except:
            self.Inputs.setInput("price", False)


    def Eselect_trading_type(self):
        """
        event handler
        activates if the user selects an item from the trade type combo box
        change the form mode to the selected type
        :return: void
        """
        assert(self.sender() == self.trade_type_combo), STRINGS.getTypeErrorString(self.sender(), "sender", self.trade_type_combo)
        match self.sender().currentText():
            #check which text is selected and switch to that mode
            case STRINGS.INVFORM_TYPE_DIVIDEND:
                self.switchToDividendMode()
            case STRINGS.INVFORM_TYPE_BUY:
                self.switchToBuyMode()
            case STRINGS.INVFORM_TYPE_SELL:
                self.switchToSellMode()
            case _:
                #if not other case is met, the programm will land here
                #the selected text is not in the possible choices
                assert(False), STRINGS.ERROR_TRADE_TYPE_NOT_VALID+self.sender().currentText()

    def Eselect_asset(self):
        """
        event handler
        activates if the user selects a asset from the combo box in sell or dividend mode
        fills out the form with the data of that asset
        :return: void
        """
        assert(self.sender() == self.ticker_edit and type(self.ticker_edit) == QComboBox), STRINGS.getTypeErrorString(self.sender(), "sender", QComboBox)
        if self.sender().currentText() != "":
            self.Inputs.setInput("ticker", True)
        else:
            self.Inputs.setInput("ticker", False)

    def Esubmit_investment(self):
        """
        event handler
        activates if the user submits the investment
        verifies the data and adds the investment to the system
        :return: void
        """
        assert(self.sender() == self.submit_button), STRINGS.getTypeErrorString(self.sender(), "sender", self.submit_button)
        data = self.getDataFromForm()
        success = self.backend.addInvestment(data)
        if not success:
            QMessageBox.critical(self, STRINGS.CRITICAL_ADD_INVESTMENT_TITLE, self.backend.error_string)
        else:
            self.investmentChanged()


    def Eopen_filter(self):
        pass

    def Ereset_filter(self):
        pass

    def Esort_investments(self):
        pass

    def Eedit_last_investment(self):
        pass

    def Eload_csv(self):
        pass

    def Eexport_csv(self):
        pass