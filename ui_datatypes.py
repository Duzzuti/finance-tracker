from PyQt5.QtWidgets import QComboBox

class Combo:
    def __init__(self, default_item, choosed_event_func, func_get_items):
        self.boxes = []
        self.default = default_item
        self.choosed_event_func = choosed_event_func
        self.layout = False
        self.func_get_items = func_get_items
    
    def setLayout(self, layout):
        self.layout = layout
    
    def addComboBox(self):
        assert(self.layout != False), "set a layout with setLayout() first"
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
        assert(self.boxes != []), "no items to get, becuase there are no boxes. Pls add a box first"
        items = [self.boxes[0].itemText(i) for i in range(self.boxes[0].count())]
        if not(default):
            while (self.default in items):
                items.remove(self.default)
        return items

    def sort(self):
        items = self.getAllItems(default=True)
        items.sort(key=lambda x: "0" if x == self.default else x.lower())
        for box in self.boxes:
            box.currentTextChanged.disconnect(self.choosed_event_func)
            text = box.currentText()
            box.clear()
            box.addItems(items)
            box.setCurrentText(text)
            box.currentTextChanged.connect(self.choosed_event_func)

    def addItem(self, item, set_item=True, sort=True):
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
        return res


class Inputs:
    def __init__(self, input_list, true_func, false_func):
        self.input_dict = {}
        self.flag = False
        self.true_func = true_func
        self.false_func = false_func
        for i in input_list:
            self.input_dict[i] = False
    
    def setInput(self, input, bool):
        assert(input in self.input_dict), f"Input {input} is not in input dict"
        self.input_dict[input] = bool
        if not(self.flag) and bool and self.isAllInputs():
            self.true_func()
            self.flag = True
        
        elif self.flag and not(bool) and not(self.isAllInputs()):
            self.false_func()
            self.flag = False

    def isAllInputs(self):
        for input in self.input_dict:
            if self.input_dict[input] == False:
                return False
        return True
