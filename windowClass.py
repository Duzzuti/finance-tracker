from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QIcon
import sys

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SUSPECT Window")
        self.setWindowIcon(QIcon("media/icon.png"))

        stylesheet = (
            'background-color:"#9adfff"'
        )
        self.setStyleSheet(stylesheet)


app = QApplication([])
window = Window()
window.show()

sys.exit(app.exec())