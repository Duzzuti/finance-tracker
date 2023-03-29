"""
This module provides the datatypes used by the ui
"""
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import QDate
from backend_datatypes import Transaction, Person
from strings import ENG as STRINGS
from constants import CONSTANTS


class Combo:
    """
    The Combo class encapsulated the ComboBoxes, which are used in the ui
    if the user chooses a category a new ComboBox appears
    the user can add an item to all Boxes at the same time
    These functionalities are provided in this class
    """
    def __init__(self, default_item:str, choosed_event_func:callable, func_get_items:callable):
        """
        basic constructor is setting up the Combo datatype
        :param default_item: str<Item which should be choosed at default and does not have any meaning (some descriptor string)>
        :param choosed_event_func: function<Event handler which should be called if a new Item is choosed>
        :param func_get_items: function<should return a list of items (strings), which are used in the combo boxes>
        :return: void
        """
        assert(type(default_item) == str), STRINGS.getTypeErrorString(default_item, "default_item", str)
        assert(callable(choosed_event_func)), STRINGS.getTypeErrorString(choosed_event_func, "choosed_event_func", "function")
        assert(callable(func_get_items)), STRINGS.getTypeErrorString(func_get_items, "func_get_items", "function")
        self.boxes = []         #holds all QComboBox objects
        self.default = default_item     #default item, placeholder, descriptor
        self.choosed_event_func = choosed_event_func
        self.layout = False     #no layout specified
        self.func_get_items = func_get_items
    
    def setLayout(self, layout:QVBoxLayout):
        """
        sets the layout which holds the ComboBoxes, has to be done before using this object
        :param layout: Some pyqt5 layout type<layout in which the boxes are added and removed>
        :return: void
        """
        assert(type(layout) == QVBoxLayout), STRINGS.getTypeErrorString(layout, "layout", QVBoxLayout)
        self.layout = layout
    
    def addComboBox(self):
        """
        adds a new ComboBox to the datatype
        :return: void
        """
        assert(self.layout != False), STRINGS.ERROR_NO_LAYOUT
        assert(self.getLen() < CONSTANTS.MAX_COMBOS), STRINGS.ERROR_TOO_MANY_COMBOS + f"({self.getLen()}, {CONSTANTS.MAX_COMBOS})"
        #generates the ComboBox with the right settings
        box = QComboBox()
        box.setMaxVisibleItems(20)
        box.setStyleSheet("combobox-popup: 0;")
        box.addItems(self.getAvailableItems()) #gets all available items from the function
        box.setCurrentText(self.default)
        box.currentTextChanged.connect(self.choosed_event_func) #set the event handler
        self.layout.addWidget(box)
        self.boxes.append(box)
    
    def getAllItems(self, default:bool=False):
        """
        gets all items from the first box
        :param default: bool<should the default item be included?>
        :return: list<str<item1>, ...>
        """
        assert(self.boxes != []), STRINGS.ERROR_NO_BOXES
        assert(type(default) == bool), STRINGS.getTypeErrorString(default, "default", bool)
        #gets all items of the first box
        items = [self.boxes[0].itemText(i) for i in range(self.boxes[0].count())]
        if not(default):
            #delete all default elements
            while (self.default in items):
                items.remove(self.default)
        assert(type(items) == list and all(map(lambda x: type(x) == str, items))), STRINGS.getListTypeErrorString(items, "items", str)
        return items

    def sort(self):
        """
        sorts the items in all boxes in alphabetical order
        :return: void
        """
        assert(self.boxes != []), STRINGS.ERROR_NO_BOXES
        for box in self.boxes:
            items = self.getAvailableItems()  #gets all available items
            text = box.currentText()    #saves the choosed item
            if text != self.default:
                items.append(text)          #adds the current items to the available items, if its not the default
            items.sort(key=lambda x: "0" if x == self.default else x.lower())   #sorts them
            #diconnect from the event handler first to avoid unexpected results
            box.currentTextChanged.disconnect(self.choosed_event_func)
            assert(text in items), STRINGS.ERROR_CHOOSED_TEXT_NOT_IN_ITEMS+text
            box.clear()         #clear the items
            box.addItems(items) #add the sorted item list
            box.setCurrentText(text)
            box.currentTextChanged.connect(self.choosed_event_func) #connect the event handler again

    def getAvailableItems(self):
        """
        gets all available items, that are all items that are not currently choosen by a combo box
        :return: list<str<available item1>, ...>
        """
        items = self.func_get_items()   #gets all items 
        items.append(self.default)      #adds the default item
        for selected_item in self.getChoosenItems():
            try:
                items.remove(selected_item)     #removes all choosen items
            except:
                pass
        return items

    def updateItems(self):
        """
        sets the items correctly for each box, gets all available items and sets them for each box
        :return: void
        """
        items = self.getAvailableItems()
        for box in self.boxes:
            set_item = box.currentText()    #the current item is obviously needed
            #diconnect from the event handler first to avoid unexpected results
            box.currentTextChanged.disconnect(self.choosed_event_func)
            box.clear()         #clear the items
            if set_item != self.default:
                box.addItems(items + [set_item]) #add the items and the current item
            else:
                #if the default item is choosen, its not going to be added a second time
                box.addItems(items)
            box.setCurrentText(set_item)
            box.currentTextChanged.connect(self.choosed_event_func) #connect the event handler again
        self.sort()

    def addItem(self, item:str, set_item:bool=True):
        """
        add a new item in all boxes
        :param item: str<item, that should be added>
        :param set_item: bool<should the new added item be choosed from one box, which has the default option choosed?>
        :return: void
        """
        assert(type(item) == str), STRINGS.getTypeErrorString(item, "item", str)
        assert(type(set_item) == bool), STRINGS.getTypeErrorString(set_item, "set_item", bool)
        new_item_set = False    #has the new item already been selected?
        for box in self.boxes:
            if set_item and new_item_set == False and box.currentText() == self.default:
                #if the new item has not been set and the user wants to set it and the current text is the default option
                new_item_set = True
                box.addItem(item)   #add the new item
                box.setCurrentText(item)    #set the item
                break
        else:
            for box in self.boxes:
                box.addItem(item)   #add the new item
 
        self.sort()     #sorts all items
    
    def isNoDefault(self):
        """
        checks whether a default option is currently selected, if thats the case, return false
        :return: bool<no default option is currently selected>
        """
        for box in self.boxes:
            if box.currentText() == self.default:
                return False
        return True

    def getLen(self):
        """
        getter for the length of the boxes list
        :return: int<number of boxes>
        """
        return len(self.boxes)

    def reset(self):
        """
        resets the combo boxes to the default
        (one combo box with the default option selected)
        :return: void
        """
        assert(self.getLen() > 0), STRINGS.ERROR_NO_BOXES
        box1 = self.boxes[0]    #saves the first box
        box1.setCurrentText(self.default)   #sets the option to default
        for box in self.boxes[1:]:
            #remove all other boxes
            self.layout.removeWidget(box)
            box.deleteLater()
        self.boxes = [box1]
        self.updateItems()      #sets the items up correctly (if you reset, you can choose all items with box 1)

    def getChoosenItems(self):
        """
        getter for the items that are choosen
        (ignores default options)
        :return: list<str<selected item1>, ...>
        """
        res = []
        for box in self.boxes:
            if box.currentText() != self.default:
                #saves the item, if its not the default
                res.append(box.currentText())
        
        assert(type(res) == list and all(map(lambda x: type(x) == str, res))), STRINGS.getListTypeErrorString(res, "res", str)
        return res

    def setItems(self, items:list[str]):
        """
        clears the current choosen items and chooses the given items
        :param items: list<str<item1>, ...> has to be in func_get_items
        :return: void
        """
        assert(len(items) <= CONSTANTS.MAX_COMBOS), STRINGS.ERROR_TOO_MANY_COMBOS+str(items)+", "+str(CONSTANTS.MAX_COMBOS)
        assert(type(items) == list and all(map(lambda x: type(x) == str, items))), STRINGS.getListTypeErrorString(items, "items", str)
        self.reset()
        for i in range(len(items)):
            try:
                self.boxes[i].setCurrentText(items[i])
            except:
                raise ValueError(STRINGS.ERROR_CHOOSED_TEXT_NOT_IN_ITEMS)+str(items[i])
        self.updateItems()  #sets the comboBox choices depending on the other comboBox' choosed items


class Inputs:
    """
    The Inputs class sets up a dictionary to track whether something, depending on requirements, is possible
    You can set up some requirements and set them to true or false. You can check whether all requirements are true or not
    """
    def __init__(self, input_list:list[str], true_func:callable, false_func:callable):
        """
        basic constructor is setting up the inputs datatype, you can provide a list with requirements and
        some functions to execute, if all requirements are met or not
        :param input_list: list<str<requirement1>, ... >
        :param true_func: function<gets called if all requirements are true>
        :param false_func: function<gets called if not all requirements are true>
        :return: void
        """
        assert(type(input_list) == list and all(map(lambda x: type(x) == str, input_list))), STRINGS.getListTypeErrorString(input_list, "input_list", str)
        assert(callable(true_func)), STRINGS.getTypeErrorString(true_func, "true_func", "function")
        assert(callable(false_func)), STRINGS.getTypeErrorString(false_func, "false_func", "function")
        self.input_dict = {}
        #this flag handles the function callings
        #if its true that means that all requirements were met and the true func got called
        #if its false that means that not all requirementes were met and the false func got called
        self.flag = False        
        self.true_func = true_func
        self.false_func = false_func
        for i in input_list:
            self.input_dict[i] = False  #sets all requirements to false
    
    def setInput(self, input:str, status:bool):
        """
        set a requirement (input) to status
        :param input: str<requirement>
        :param status: bool<is requirement met?>
        :return: void
        """
        assert(type(input) == str), STRINGS.getTypeErrorString(input, "input", str)
        assert(type(status) == bool), STRINGS.getTypeErrorString(status, "status", bool)
        assert(input in self.input_dict), STRINGS.ERROR_INPUT_NOT_IN_INPUTDICT+str(input)
        self.input_dict[input] = status
        if not(self.flag) and status and self.isAllInputs():
            #only call the true func, if the false func was called last and the new status is true and all requirements are met
            self.true_func()
            self.flag = True    #true func got called 
        
        elif self.flag and not(status) and not(self.isAllInputs()):
            #only call the false func, if the true func was called last and the new status is false and not all requirements are met
            self.false_func()
            self.flag = False   #false func got called

    def isAllInputs(self):
        """
        gets a bool whether all requirements are met or not
        :return: bool<are all requirement met?>
        """
        for input in self.input_dict:
            if self.input_dict[input] == False:
                return False
        return True


class TransactionList:
    """
    The TransactionList class sets up a list of PushButton objects, that are added in a scrollarea
    The PushButtons should represent the transactions the user has taken
    The user should be able to click on these buttons to view and edit that transaction
    """
    def __init__(self, func_get_transactions:callable, func_event_handler:callable):
        """
        basic constructor is setting up the TransactionList datatype, 
        you have to provide a function that returns a list of transactions which are displayed and an event handler for the buttons
        :param func_get_transactions: function<gets list of transaction objects>
        :param func_event_handler: function<event handler for pressing a button>
        :return: void
        """
        assert(callable(func_get_transactions)), STRINGS.getTypeErrorString(func_get_transactions, "func_get_transactions", "function")
        self.buttons = []   #list of PushButtons
        self.transactions = []  #list of Transaction objects coresponding to the button with the same index
        self.layout = None  #the layout that is used to add the PushButtons
        self.func_get_transactions = func_get_transactions
        self.func_event_handler = func_event_handler
    
    def setLayout(self, layout:QVBoxLayout):
        """
        sets the layout which holds the PushButtons, has to be done before using this object
        :param layout: Some pyqt5 layout type<layout in which the buttons are added and removed>
        :return: void
        """
        assert(type(layout) == QVBoxLayout), STRINGS.getTypeErrorString(layout, "layout", QVBoxLayout)
        self.layout = layout

    def updateLastTrans(self):
        """
        updates the buttons by getting the new transaction data from the backend
        :return: void
        """
        #WORK better system here, dont need to delete every button every time
        #deletes all current buttons
        assert(self.layout != False), STRINGS.ERROR_NO_LAYOUT
        for i in reversed(range(self.layout.count())): 
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.buttons = []
        self.transactions = []

        for transaction in self.func_get_transactions():
            #for each transaction get a PushButton object and add it to the layout
            element_button = self._getTransactionButton(transaction)
            self.layout.addWidget(element_button)  
            self.buttons.append(element_button)
            self.transactions.append(transaction)
        
    def getTransactionForButton(self, button:QPushButton):
        """
        getter for a transaction object coresponding to a given button
        :param button: object<PushButton>
        :return: object<Transaction>
        """
        assert(button in self.buttons), STRINGS.ERROR_BUTTON_NOT_FOUND
        ind = self.buttons.index(button)
        assert(len(self.transactions) >= ind+1), STRINGS.ERROR_TRANSACTION_OUT_OF_RANGE
        return self.transactions[ind]

    def _getTransactionButton(self, transaction:Transaction):
        """
        gets a PushButton object created using a transaction object. This method is labeling a button with transaction data
        :param transaction: object<Transaction>
        :return: object<PushButton>
        """
        assert(self.layout != False), STRINGS.ERROR_NO_LAYOUT
        assert(type(transaction) == Transaction), STRINGS.getTypeErrorString(transaction, "transaction", Transaction)
        
        element_button = QPushButton()
        element_layout = QHBoxLayout()  #layout for the button
        element_layout.setContentsMargins(10, 3, 10, 3)     #CHANGE

        #some label with transaction data
        date_string = transaction.date.strftime('[%d %b %Y]')
        cashflow_string = str(transaction.cashflow)+STRINGS.CURRENCY
        product_string = transaction.product.name
        date_label = QLabel(date_string)
        cashflow_label = QLabel(cashflow_string)
        product_label = QLabel(product_string)

        element_layout.addWidget(date_label)
        element_layout.addWidget(cashflow_label)
        element_layout.addWidget(product_label)

        element_button.setLayout(element_layout)
        element_button.adjustSize() #makes the content fit
        element_button.clicked.connect(self.func_event_handler)    #connect with event handler
        return element_button


class Filter:
    """
    the filter class is containing filter settings for transactions
    its used to filter or search for specific transactions
    """
    def __init__(self):
        """
        basic constructor, just sets up an open filter (all transactions are fullfilling this filter)
        :return: void
        """
        self.reset()
    
    def isStandard(self):
        """
        this method checks whether the current filter is open (all transactions are fullfilling this filter)
        :return: bool<is open/standard?>
        """
        return (self.minDate == QDate(1900, 1, 1) and
        self.maxDate == QDate.currentDate() and
        self.minCashflow == False and
        self.maxCashflow == False and
        self.minCashflowPerProduct == False and
        self.maxCashflowPerProduct == False and
        self.absoluteValues == True and
        self.contains == "" and
        self.startswith == "" and
        self.categories == [] and
        self.ftpersons == [] and
        self.whypersons == [] and
        self.persons == [])
    
    def reset(self):
        """
        resets the filter to the standard settings (all transactions are fullfilling this filter)
        :return: void
        """
        self.minDate = QDate(1900, 1, 1)
        self.maxDate = QDate.currentDate()
        self.minCashflow = False
        self.maxCashflow = False
        self.minCashflowPerProduct = False
        self.maxCashflowPerProduct = False
        self.absoluteValues = True
        self.contains = ""
        self.startswith = ""
        self.categories = []
        self.ftpersons = []
        self.whypersons = []
        self.persons = []

    def setMinDate(self, minDate:QDate):
        """
        setter for the minDate filter
        :param minDate: QDate<minimum Date for a transaction>
        :return: void
        """
        assert(type(minDate) == QDate), STRINGS.getTypeErrorString(minDate, "minDate", QDate)
        assert(QDate.currentDate() >= minDate >= QDate(1900, 1, 1)), STRINGS.ERROR_DATE_OUT_OF_RANGE+str(minDate)
        self.minDate = minDate
    
    def setMaxDate(self, maxDate:QDate):
        """
        setter for the maxDate filter
        :param maxDate: QDate<maximum Date for a transaction>
        :return: void
        """
        assert(type(maxDate) == QDate), STRINGS.getTypeErrorString(maxDate, "maxDate", QDate)
        assert(QDate.currentDate() >= maxDate >= QDate(1900, 1, 1)), STRINGS.ERROR_DATE_OUT_OF_RANGE+str(maxDate)
        self.maxDate = maxDate
    
    def setMinCashflow(self, minCashflow:float):
        """
        setter for the minCashflow filter
        :param minCashflow: float<minimum Cashflow, that a transaction needs to have>
        :return: void
        """
        assert(type(minCashflow) == float), STRINGS.getTypeErrorString(minCashflow, "minCashflow", float)
        self.minCashflow = minCashflow

    def setMaxCashflow(self, maxCashflow:float):
        """
        setter for the maxCashflow filter
        :param maxCashflow: float<maximum Cashflow, that a transaction should have>
        :return: void
        """
        assert(type(maxCashflow) == float), STRINGS.getTypeErrorString(maxCashflow, "maxCashflow", float)
        self.maxCashflow = maxCashflow

    def setMinCashflowPerProduct(self, minCashflowPerProduct:float):
        """
        setter for the minCashflowPerProduct filter
        :param minCashflowPerProduct: float<minimum Cashflow per product, that a transaction needs to have>
        :return: void
        """
        assert(type(minCashflowPerProduct) == float), STRINGS.getTypeErrorString(minCashflowPerProduct, "minCashflowPerProduct", float)
        self.minCashflowPerProduct = minCashflowPerProduct

    def setMaxCashflowPerProduct(self, maxCashflowPerProduct:float):
        """
        setter for the maxCashflowPerProduct filter
        :param maxCashflowPerProduct: float<maximum Cashflow per product, that a transaction should have>
        :return: void
        """
        assert(type(maxCashflowPerProduct) == float), STRINGS.getTypeErrorString(maxCashflowPerProduct, "maxCashflowPerProduct", float)
        self.maxCashflowPerProduct = maxCashflowPerProduct

    def setAbsoluteValues(self, absoluteValues:bool):
        """
        setter for the absoluteValues filter
        :param absoluteValues: bool<should be used absolute values for the cashflow filters?>
        :return: void
        """
        assert(type(absoluteValues) == bool), STRINGS.getTypeErrorString(absoluteValues, "absoluteValues", bool)
        self.absoluteValues = absoluteValues

    def setContains(self, contains:str):
        """
        setter for the contains filter
        :param contains: str<substring that the transaction needs to contain>
        :return: void
        """
        assert(type(contains) == str), STRINGS.getTypeErrorString(contains, "contains", str)
        self.contains = contains
    
    def setStartsWith(self, startswith:str):
        """
        setter for the startswith filter
        :param startswith: str<string that the transaction needs to start with>
        :return: void
        """
        assert(type(startswith) == str), STRINGS.getTypeErrorString(startswith, "startswith", str)
        self.startswith = startswith
    
    def setCategories(self, categories:list[str]):
        """
        setter for the categories filter
        :param categories: list<str<category that needs to be set in that transaction1>, ...>
        :return: void
        """
        assert(type(categories) == list and all(map(lambda x: type(x) == str, categories))), STRINGS.getListTypeErrorString(categories, "categories", str)
        self.categories = categories
    
    def setFtPersons(self, ftpersons:list[Person]):
        """
        setter for the ftpersons filter
        :param ftpersons: list<object<Person, that needs to be set as a from/to person1>, ...>
        :return: void
        """
        assert(type(ftpersons) == list and all(map(lambda x: type(x) == Person, ftpersons))), STRINGS.getListTypeErrorString(ftpersons, "ftpersons", Person)
        self.ftpersons = ftpersons
    
    def setWhyPersons(self, whypersons:list[Person]):
        """
        setter for the whypersons filter
        :param whypersons: list<object<Person, that needs to be set as a why person1>, ...>
        :return: void
        """
        assert(type(whypersons) == list and all(map(lambda x: type(x) == Person, whypersons))), STRINGS.getListTypeErrorString(whypersons, "whypersons", Person)
        self.whypersons = whypersons
    
    def setPersons(self, persons:list[Person]):
        """
        setter for the persons filter
        :param persons: list<object<Person, that needs to be set as a from/to or why person1>, ...>
        :return: void
        """
        assert(type(persons) == list and all(map(lambda x: type(x) == Person, persons))), STRINGS.getListTypeErrorString(persons, "persons", Person)
        self.persons = persons
