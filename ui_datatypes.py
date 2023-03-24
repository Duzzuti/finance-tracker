import inspect
from PyQt5.QtWidgets import QComboBox, QVBoxLayout
from strings import ENG as STRINGS
from constants import CONSTANTS

class Combo:
    def __init__(self, default_item, choosed_event_func, func_get_items):
        assert(type(default_item) == str), STRINGS.ERROR_WRONG_DEFAULT_ITEM_TYPE+str(default_item)
        assert(callable(choosed_event_func)), STRINGS.ERROR_WRONG_EVENT_FUNC_TYPE+str(choosed_event_func)
        assert(callable(func_get_items)), STRINGS.ERROR_WRONG_GET_ITEMS_FUNC_TYPE+str(func_get_items)
        self.boxes = []
        self.default = default_item
        self.choosed_event_func = choosed_event_func
        self.layout = False
        self.func_get_items = func_get_items
    
    def setLayout(self, layout):
        assert(type(layout) == QVBoxLayout), STRINGS.ERROR_WRONG_LAYOUT_TYPE+str(layout)
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
        assert(type(default) == bool), STRINGS.ERROR_WRONG_DEFAULT_ARG_TYPE+str(default)
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
        assert(type(item) == str), STRINGS.ERROR_WRONG_ITEM_TYPE+str(item)
        assert(type(set_item) == bool), STRINGS.ERROR_WRONG_SET_ITEM_TYPE+str(set_item)
        assert(type(sort) == bool), STRINGS.ERROR_WRONG_ARG_SORT_TYPE+str(sort)
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
        assert(callable(true_func)), STRINGS.ERROR_WRONG_TRUE_FUNC_TYPE+str(true_func)
        assert(callable(false_func)), STRINGS.ERROR_WRONG_FALSE_FUNC_TYPE+str(false_func)
        self.input_dict = {}
        self.flag = False
        self.true_func = true_func
        self.false_func = false_func
        for i in input_list:
            self.input_dict[i] = False
    
    def setInput(self, input, status):
        assert(type(input) == str), STRINGS.ERROR_WRONG_INPUT_ARG_TYPE+str(input)
        assert(type(status) == bool), STRINGS.ERROR_WRONG_STATUS_ARG_TYPE+str(status)
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
