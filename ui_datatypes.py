import inspect
from PyQt5.QtWidgets import QComboBox, QVBoxLayout
from strings import ENG as STRINGS
from constants import CONSTANTS

class Combo:
    def __init__(self, default_item, choosed_event_func, func_get_items):
        assert(type(default_item) == str), STRINGS.getTypeErrorString(default_item, "default_item", str)
        assert(callable(choosed_event_func)), STRINGS.getTypeErrorString(choosed_event_func, "choosed_event_func", "function")
        assert(callable(func_get_items)), STRINGS.getTypeErrorString(func_get_items, "func_get_items", "function")
        self.boxes = []
        self.default = default_item
        self.choosed_event_func = choosed_event_func
        self.layout = False
        self.func_get_items = func_get_items
    
    def setLayout(self, layout):
        assert(type(layout) == QVBoxLayout), STRINGS.getTypeErrorString(layout, "layout", QVBoxLayout)
        self.layout = layout
    
    def addComboBox(self):
        assert(self.layout != False), STRINGS.ERROR_NO_LAYOUT
        assert(self.getLen() < max(CONSTANTS.MAX_PERSONS, CONSTANTS.MAX_CATEGORIES)), STRINGS.ERROR_TOO_MANY_COMBOS + f"({self.getLen()}, {max(CONSTANTS.MAX_PERSONS, CONSTANTS.MAX_CATEGORIES)})"
        box = QComboBox()
        box.setMaxVisibleItems(20)
        box.setStyleSheet("combobox-popup: 0;")
        box.addItem(self.default)
        box.setCurrentText(self.default)
        box.addItems(self.func_get_items() if self.boxes == [] else self.getAllItems())
        box.currentTextChanged.connect(self.choosed_event_func)
        self.layout.addWidget(box)
        self.boxes.append(box)
    
    def getAllItems(self, default=False):
        assert(self.boxes != []), STRINGS.ERROR_NO_BOXES
        assert(type(default) == bool), STRINGS.getTypeErrorString(default, "default", bool)
        items = [self.boxes[0].itemText(i) for i in range(self.boxes[0].count())]
        if not(default):
            while (self.default in items):
                items.remove(self.default)
        assert(type(items) == list and all(map(lambda x: type(x) == str, items))), STRINGS.ERROR_WRONG_RETURN_ITEMS_TYPE+str(items)
        return items

    def sort(self):
        assert(self.boxes != []), STRINGS.ERROR_NO_BOXES
        items = self.getAllItems(default=True)
        items.sort(key=lambda x: "0" if x == self.default else x.lower())
        for box in self.boxes:
            box.currentTextChanged.disconnect(self.choosed_event_func)
            text = box.currentText()
            assert(text in items), STRINGS.ERROR_CHOOSED_TEXT_NOT_IN_ITEMS+text
            box.clear()
            box.addItems(items)
            box.setCurrentText(text)
            box.currentTextChanged.connect(self.choosed_event_func)

    def addItem(self, item, set_item=True, sort=True):
        assert(type(item) == str), STRINGS.getTypeErrorString(item, "item", str)
        assert(type(set_item) == bool), STRINGS.getTypeErrorString(set_item, "set_item", bool)
        assert(type(sort) == bool), STRINGS.getTypeErrorString(sort, "sort", bool)
        new_item_set = False
        for box in self.boxes:
            box.addItem(item)
            if set_item and new_item_set == False and box.currentText() == self.default:
                new_item_set = True
                box.setCurrentText(item)
        if sort:
            self.sort()
    
    def isNoDefault(self):
        for box in self.boxes:
            if box.currentText() == self.default:
                return False
        return True

    def getLen(self):
        return len(self.boxes)

    def reset(self):
        assert(self.getLen() > 0), STRINGS.ERROR_NO_BOXES
        box1 = self.boxes[0]
        box1.setCurrentText(self.default)
        for box in self.boxes[1:]:
            self.layout.removeWidget(box)
            box.deleteLater()
        self.boxes = [box1]

    def getChoosenItems(self):
        res = []
        for box in self.boxes:
            if box.currentText() != self.default:
                res.append(box.currentText())
        assert(type(res) == list and all(map(lambda x: type(x) == str, res))), STRINGS.ERROR_WRONG_RETURN_RES_TYPE+str(res)
        return res


class Inputs:
    def __init__(self, input_list, true_func, false_func):
        assert(type(input_list) == list and all(map(lambda x: type(x) == str, input_list))), STRINGS.ERROR_WRONG_INPUT_LIST_TYPE+str(input_list)
        assert(callable(true_func)), STRINGS.getTypeErrorString(true_func, "true_func", "function")
        assert(callable(false_func)), STRINGS.getTypeErrorString(false_func, "false_func", "function")
        self.input_dict = {}
        self.flag = False
        self.true_func = true_func
        self.false_func = false_func
        for i in input_list:
            self.input_dict[i] = False
    
    def setInput(self, input, status):
        assert(type(input) == str), STRINGS.getTypeErrorString(input, "input", str)
        assert(type(status) == bool), STRINGS.getTypeErrorString(status, "status", bool)
        assert(input in self.input_dict), STRINGS.ERROR_INPUT_NOT_IN_INPUTDICT+str(input)
        self.input_dict[input] = status
        if not(self.flag) and status and self.isAllInputs():
            self.true_func()
            self.flag = True
        
        elif self.flag and not(status) and not(self.isAllInputs()):
            self.false_func()
            self.flag = False

    def isAllInputs(self):
        for input in self.input_dict:
            if self.input_dict[input] == False:
                return False
        return True
