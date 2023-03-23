from ui import Window
from PyQt5.QtWidgets import QApplication
import sys

App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())