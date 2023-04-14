"""
this module holds constants that are used in the gui
"""
from PyQt5.QtGui import QFont, QIcon, QPixmap

class FONTS:
    """
    all used fonts of the program are stored here, you can easily change them
    """
    BIG_ITALIC_BOLD = QFont("Arial", 18, italic=True)
    BIG_ITALIC_BOLD.setBold(True)

    ITALIC = QFont("Arial", 12, italic=True)

    BIG_BOLD = QFont("Arial", 16)
    BIG_BOLD.setBold(True)

    SMALL = QFont("Arial", 10)
    SMALL_BOLD = QFont("Arial", 10)
    SMALL_BOLD.setBold(True)

    ITALIC_UNDERLINE = QFont("Arial", 13, italic=True)
    ITALIC_UNDERLINE.setUnderline(True)

class ICONS:
    """
    all icons and pixmaps that are used in the program are stored here
    """
    def compare(icon1:QIcon, icon2:QIcon, x:int=128, y:int=128):
        """
        this method compares two icons
        :param icon1: QIcon<the first icon that should be compared>
        :param icon2: QIcon<the second icon that should be compared>
        :param x: int<x dimension of the icons>
        :param y: int<y dimension of the icons>
        :return: bool<are the icons the same?>
        """
        return icon1.pixmap(x, y).toImage() == icon2.pixmap(x, y).toImage()
    
    SORT_DEFAULT = QIcon("media/sort_default.png")
    SORT_UP = QIcon("media/sort_up.png")
    SORT_DOWN = QIcon("media/sort_down.png")
    INFO = QIcon("media/info.png")
    INFO_PIXMAP = QPixmap("media/info.png")