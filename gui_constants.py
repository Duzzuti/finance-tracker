from PyQt5.QtGui import QFont, QIcon

class FONTS:
    APP_NEW_TRANSACTION = QFont("Arial", 18, italic=True)
    APP_NEW_TRANSACTION.setBold(True)

    APP_NEW_TRANSACTION_CF = QFont("Arial", 12, italic=True)

    APP_NEW_TRANSACTION_SUBMIT = QFont("Arial", 16)
    APP_NEW_TRANSACTION_SUBMIT.setBold(True)

    APP_LAST_TRANSACTION_SORT = QFont("Arial", 10)
    APP_LAST_TRANSACTION_SORT_ACTIVE = QFont("Arial", 10)
    APP_LAST_TRANSACTION_SORT_ACTIVE.setBold(True)

class ICONS:
    SORT_DEFAULT = QIcon("media/sort_default.png")
    SORT_UP = QIcon("media/sort_up.png")
    SORT_DOWN = QIcon("media/sort_down.png")