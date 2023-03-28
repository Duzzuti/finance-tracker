from PyQt5.QtWidgets import QApplication
import sys

App = QApplication(sys.argv)    #have to construct a Application first

from ui import Window

window = Window()
sys.exit(App.exec())