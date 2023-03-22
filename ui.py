import easygui
import datetime
from strings import ENG
from backend import Backend

class UI:
    def __init__(self):
        self.backend = Backend()

    def run(self):
        while True:
            response = easygui.buttonbox(ENG.MAIN_MENU_MESSAGE, ENG.MAIN_MENU_TITLE, 
                choices=[
                    ENG.MAIN_MENU_CHOICE_ADD_TRANSACTION
                ])
            
            if response == None or response == False:
                return False
            
            elif response == ENG.MAIN_MENU_CHOICE_ADD_TRANSACTION:
                if self.addTransaction(self):
                    return True
    
    def addTransaction(self):
        today = datetime.date.today()
        while True:
            response = easygui.multenterbox(ENG.ADD_TRANSACTION_MESSAGE, ENG.ADD_TRANSACTION_TITLE, 
                fields=[
                    ENG.ADD_TRANSACTION_ENTER_DATE,
                    ENG.ADD_TRANSACTION_ENTER_NUMBER,
                    ENG.ADD_TRANSACTION_ENTER_CASHFLOW_PER_PRODUCT
                ], 
                values=[
                    today.isoformat(),
                    "1",
                    "-0.00"
                ])
            
            if response == None or response == False:
                return False
            
            date, number, cashflow_pp = response

            try:
                date = datetime.date.fromisoformat(date)
                number = int(number)
                cashflow_pp = float(cashflow_pp)
                if date > today or number <= 0 or cashflow_pp != 0:
                    raise ValueError
            except:
                easygui.msgbox(ENG.INVALID_DATA_MESSAGE, ENG.INVALID_DATA_TITLE)
                continue
            

            formatted_response = date, number, cashflow_pp
            if self.backend.addTransaction(formatted_response):
                return True