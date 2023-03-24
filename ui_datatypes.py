from PyQt5.QtWidgets import QComboBox

class Combo:
    def __init__(self, default_item, choosed_event_func, backend):
        self.boxes = []
        self.default = default_item
        self.choosed_event_func = choosed_event_func
        self.layout = False
        self.backend = backend
    
    def setLayout(self, layout):
        self.layout = layout
    
    def addComboBox(self):
        assert(self.layout != False), "set a layout with setLayout() first"
        box = QComboBox()
        box.setMaxVisibleItems(20)
        box.setStyleSheet("combobox-popup: 0;")
        box.addItem(self.default)
        box.setCurrentText(self.default)
        box.addItems(self.backend.getCategories())
        box.currentTextChanged.connect(self.choosed_event_func)
        self.layout.addWidget(box)
        self.boxes.append(box)
    
    def sort(self):
        items = [self.boxes[0].itemText(i) for i in range(self.boxes[0].count())]
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
