"""
This module provides the datatypes used by the ui
"""
from PyQt5.QtWidgets import QComboBox, QVBoxLayout
from strings import ENG as STRINGS
from constants import CONSTANTS

class Combo:
    """
    The Combo class encapsulated the ComboBoxes, which are used in the ui
    if the user chooses a category a new ComboBox appears
    the user can add an item to all Boxes at the same time
    These functionalities are provided in this class
    """
    def __init__(self, default_item, choosed_event_func, func_get_items):
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
    
    def setLayout(self, layout):
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
        assert(self.getLen() < max(CONSTANTS.MAX_PERSONS, CONSTANTS.MAX_CATEGORIES)), STRINGS.ERROR_TOO_MANY_COMBOS + f"({self.getLen()}, {max(CONSTANTS.MAX_PERSONS, CONSTANTS.MAX_CATEGORIES)})"
        #generates the ComboBox with the right settings
        box = QComboBox()
        box.setMaxVisibleItems(20)
        box.setStyleSheet("combobox-popup: 0;")
        box.addItems(self.getAvailableItems()) #gets all available items from the function
        box.setCurrentText(self.default)
        box.currentTextChanged.connect(self.choosed_event_func) #set the event handler
        self.layout.addWidget(box)
        self.boxes.append(box)
    
    def getAllItems(self, default=False):
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

    def addItem(self, item, set_item=True):
        """
        add a new item in all boxes
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


class Inputs:
    """
    The Inputs class sets up a dictionary to track whether something, depending on requirements, is possible
    You can set up some requirements and set them to true or false. You can check whether all requirements are true or not
    """
    def __init__(self, input_list, true_func, false_func):
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
    
    def setInput(self, input, status):
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
