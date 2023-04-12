"""
this module provides some utility functions and datatypes that can be used in frontend and backend
"""
from enum import Enum
from strings import ENG as STRINGS
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import QDate

class utils:
    """
    this class holds the utility functions
    """
    def only_numbers(edit:QLineEdit, negatives:bool):
        """
        this method takes a lineedit and returnes a text that the lineedit can set to keep the input in a number format
        that means that non number characters, except comma and minus gets deleted, commas are set to a main comma set in STRINGS
        minus is only valid once at the beginning and only if the input field should accept negatives (param)
        the method requires that only one new character is added
        :param edit: QLineEdit<Input field, that holds the text>
        :param negatives: bool<are negatives allowed?>
        :return: str<text, that the lineEdit should set>
        """
        text = edit.text()
        for comma in STRINGS.COMMAS:
            text = text.replace(comma, STRINGS.COMMA)

        commas = 0
        for _char in text:
            if _char == "-":
                if negatives:
                    if text.startswith("-"):
                        if text.count("-") == 1:
                            continue
                return text[::-1].replace("-", "", 1)[::-1]
            elif _char == STRINGS.COMMA:
                commas += 1
                if commas > 1:
                    return text[::-1].replace(STRINGS.COMMA, "", 1)[::-1]
            elif not _char in list(map(str, range(10))):
                return text.replace(_char, "")
        return text


class SortEnum(Enum):
    """
    this enum holds the flags for the sort criteria
    """
    DATE = 0
    CASHFLOW = 1
    NAME = 2


class Filter:
    """
    the filter class is containing filter settings for transactions
    its used to filter or search for specific transactions
    """
    def __init__(self):
        """
        basic constructor, just sets up an open filter (all transactions are fullfilling this filter)
        :return: void
        """
        self.reset()
    
    def __str__(self):
        """
        just for debug purposes #DEGUBONLY
        prints the filter settings in a readable format
        :return: str<msg>
        """
        msg = f"MinDate: {self.minDate.toString('dd.MM.yyyy')}, MaxDate: {self.maxDate.toString('dd.MM.yyyy')}\n"
        msg += f"Min cashflow: {self.minCashflow}, Max cashflow: {self.maxCashflow}\n"
        msg += f"Min cashflow per product: {self.minCashflowPerProduct}, Max cashflow per product: {self.maxCashflowPerProduct}\n"
        msg += f"Absolute\n" if self.absoluteValues else f"Signed\n"
        msg += f"Product contains: {self.contains}, Product startswith: {self.startswith}\n"
        msg += f"Categories: {self.categories}\n"
        msg += f"From/to persons: {self.ftpersons}\n"
        msg += f"Why persons: {self.whypersons}\n"
        msg += f"Persons: {self.persons}\n"
        return msg

    def isStandard(self):
        """
        this method checks whether the current filter is open (all transactions are fullfilling this filter)
        :return: bool<is open/standard?>
        """
        return (self.minDate == QDate(1900, 1, 1) and
        self.maxDate == QDate.currentDate() and
        self.minCashflow == False and
        self.maxCashflow == False and
        self.minCashflowPerProduct == False and
        self.maxCashflowPerProduct == False and
        self.absoluteValues == True and
        self.contains == "" and
        self.startswith == "" and
        self.categories == [] and
        self.ftpersons == [] and
        self.whypersons == [] and
        self.persons == [])
    
    def reset(self):
        """
        resets the filter to the standard settings (all transactions are fullfilling this filter)
        :return: void
        """
        self.minDate = QDate(1900, 1, 1)
        self.maxDate = QDate.currentDate()
        self.minCashflow = False
        self.maxCashflow = False
        self.minCashflowPerProduct = False
        self.maxCashflowPerProduct = False
        self.absoluteValues = True
        self.contains = ""
        self.startswith = ""
        self.categories = []
        self.ftpersons = []
        self.whypersons = []
        self.persons = []

    def setMinDate(self, minDate:QDate):
        """
        setter for the minDate filter
        :param minDate: QDate<minimum Date for a transaction>
        :return: void
        """
        assert(type(minDate) == QDate), STRINGS.getTypeErrorString(minDate, "minDate", QDate)
        assert(QDate.currentDate() >= minDate >= QDate(1900, 1, 1)), STRINGS.ERROR_DATE_OUT_OF_RANGE+str(minDate)
        self.minDate = minDate
    
    def setMaxDate(self, maxDate:QDate):
        """
        setter for the maxDate filter
        :param maxDate: QDate<maximum Date for a transaction>
        :return: void
        """
        assert(type(maxDate) == QDate), STRINGS.getTypeErrorString(maxDate, "maxDate", QDate)
        assert(QDate.currentDate() >= maxDate >= QDate(1900, 1, 1)), STRINGS.ERROR_DATE_OUT_OF_RANGE+str(maxDate)
        self.maxDate = maxDate
    
    def setMinCashflow(self, minCashflow:float):
        """
        setter for the minCashflow filter
        :param minCashflow: float<minimum Cashflow, that a transaction needs to have>
        :return: void
        """
        assert(type(minCashflow) in [float, bool]), STRINGS.getTypeErrorString(minCashflow, "minCashflow", "float or bool")
        self.minCashflow = minCashflow

    def setMaxCashflow(self, maxCashflow:float):
        """
        setter for the maxCashflow filter
        :param maxCashflow: float<maximum Cashflow, that a transaction should have>
        :return: void
        """
        assert(type(maxCashflow) in [float, bool]), STRINGS.getTypeErrorString(maxCashflow, "maxCashflow", "float or bool")
        self.maxCashflow = maxCashflow

    def setMinCashflowPerProduct(self, minCashflowPerProduct:float):
        """
        setter for the minCashflowPerProduct filter
        :param minCashflowPerProduct: float<minimum Cashflow per product, that a transaction needs to have>
        :return: void
        """
        assert(type(minCashflowPerProduct) in [float, bool]), STRINGS.getTypeErrorString(minCashflowPerProduct, "minCashflowPerProduct", "float or bool")
        self.minCashflowPerProduct = minCashflowPerProduct

    def setMaxCashflowPerProduct(self, maxCashflowPerProduct:float):
        """
        setter for the maxCashflowPerProduct filter
        :param maxCashflowPerProduct: float<maximum Cashflow per product, that a transaction should have>
        :return: void
        """
        assert(type(maxCashflowPerProduct) in [float, bool]), STRINGS.getTypeErrorString(maxCashflowPerProduct, "maxCashflowPerProduct", "float or bool")
        self.maxCashflowPerProduct = maxCashflowPerProduct

    def setAbsoluteValues(self, absoluteValues:bool):
        """
        setter for the absoluteValues filter
        :param absoluteValues: bool<should be used absolute values for the cashflow filters?>
        :return: void
        """
        assert(type(absoluteValues) == bool), STRINGS.getTypeErrorString(absoluteValues, "absoluteValues", bool)
        self.absoluteValues = absoluteValues

    def setContains(self, contains:str):
        """
        setter for the contains filter
        :param contains: str<substring that the transaction needs to contain>
        :return: void
        """
        assert(type(contains) == str), STRINGS.getTypeErrorString(contains, "contains", str)
        self.contains = contains
    
    def setStartsWith(self, startswith:str):
        """
        setter for the startswith filter
        :param startswith: str<string that the transaction needs to start with>
        :return: void
        """
        assert(type(startswith) == str), STRINGS.getTypeErrorString(startswith, "startswith", str)
        self.startswith = startswith
    
    def setCategories(self, categories:list[str]):
        """
        setter for the categories filter
        :param categories: list<str<category that needs to be set in that transaction1>, ...>
        :return: void
        """
        assert(type(categories) == list and all(map(lambda x: type(x) == str, categories))), STRINGS.getListTypeErrorString(categories, "categories", str)
        self.categories = categories
    
    def setFtPersons(self, ftpersons:list[str]):
        """
        setter for the ftpersons filter
        :param ftpersons: list<str<Person name, that needs to be set as a from/to person1>, ...>
        :return: void
        """
        assert(type(ftpersons) == list and all(map(lambda x: type(x) == str, ftpersons))), STRINGS.getListTypeErrorString(ftpersons, "ftpersons", str)
        self.ftpersons = ftpersons
    
    def setWhyPersons(self, whypersons:list[str]):
        """
        setter for the whypersons filter
        :param whypersons: list<str<Person name, that needs to be set as a why person1>, ...>
        :return: void
        """
        assert(type(whypersons) == list and all(map(lambda x: type(x) == str, whypersons))), STRINGS.getListTypeErrorString(whypersons, "whypersons", str)
        self.whypersons = whypersons
    
    def setPersons(self, persons:list[str]):
        """
        setter for the persons filter
        :param persons: list<str<Person name, that needs to be set as a from/to or why person1>, ...>
        :return: void
        """
        assert(type(persons) == list and all(map(lambda x: type(x) == str, persons))), STRINGS.getListTypeErrorString(persons, "persons", str)
        self.persons = persons
