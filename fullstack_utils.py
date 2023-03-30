"""
this module provides some utility functions and datatypes that can be used in frontend and backend
"""
from enum import Enum
from strings import ENG as STRINGS
from PyQt5.QtWidgets import QLineEdit

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
    PRODUCT = 2
