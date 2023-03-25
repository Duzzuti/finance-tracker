import datetime
from strings import ENG as STRINGS
from PyQt5.QtWidgets import QMessageBox
from backend_datatypes import Product, Person, Transaction

class Backend:
    def __init__(self, ui):
        self.ui = ui
        self.error_string = ""
        self.products = []
        self.categories = []
        self.persons = []
        self.transactions = []

    def getProductNames(self):
        return sorted(list(map(lambda x: x.name, self.products)))

    def getCategories(self):
        return sorted(self.categories)

    def addCategory(self, category):
        assert(type(category) == str), STRINGS.getTypeErrorString(category, "category", str)
        assert(len(category) - category.count(" ") >= 3), STRINGS.ERROR_CATEGORY_CONTAINS_NOT_ENOUGH_CHAR+str(category)
        if category.lower() in map(lambda x: x.lower(), self.categories):
            self.error_string = f"cannot add category '{category}' because its already added"
            return False
        self.categories.append(category)
        return True

    def getError(self):
        return "No error was specified" if self.error_string == False else self.error_string

    def getPersonNames(self):
        return sorted(map(lambda x: x.name, self.persons), key=lambda x: x.lower())

    def addPerson(self, person_text):
        assert(type(person_text) == str), STRINGS.getTypeErrorString(person_text, "person_text", str)
        assert(len(person_text) - person_text.count(" ") >= 3), STRINGS.ERROR_PERSON_CONTAINS_NOT_ENOUGH_CHAR+str(person_text)
        if person_text.lower() in map(lambda x: x.name.lower(), self.persons):
            self.error_string = f"cannot add person '{person_text}' because its already added"
            return False
        self.persons.append(Person(person_text))
        return True

    def addTransaction(self, date, product, number, full_cf, categories, ftpersons, whypersons):
        assert(type(date) == datetime.date), STRINGS.getTypeErrorString(date, "date", datetime.date)
        assert(date <= datetime.date.today()), STRINGS.ERROR_DATE_OUT_OF_RANGE+str(date)
        assert(type(product) == str), STRINGS.getTypeErrorString(product, "product", str)
        assert(len(product) - product.count(" ") > 0), STRINGS.ERROR_PRODUCT_CONTAINS_NO_CHAR+str(product)
        assert(type(number) == int), STRINGS.getTypeErrorString(number, "number", int)
        assert(number > 0), STRINGS.ERROR_NUMBER_ZERO_OR_LESS+str(number)
        assert(type(full_cf) == float), STRINGS.getTypeErrorString(full_cf, "full_cf", int)
        assert(full_cf != 0), STRINGS.ERROR_CASHFLOW_ZERO+str(full_cf)
        assert(type(categories) == list and all(map(lambda x: type(x) == str, categories))), STRINGS.getListTypeErrorString(categories, "categories", str)
        assert(all(map(lambda x: x in self.getCategories(), categories))), STRINGS.ERROR_NOT_ALL_CATEGORIES_ARE_VALID+str(categories)
        assert(type(ftpersons) == list and all(map(lambda x: type(x) == str, ftpersons))), STRINGS.getListTypeErrorString(ftpersons, "ftpersons", str)
        assert(all(map(lambda x: x in self.getPersonNames(), ftpersons))), STRINGS.ERROR_NOT_ALL_FTPERSONS_ARE_VALID+str(ftpersons)
        assert(type(whypersons) == list and all(map(lambda x: type(x) == str, whypersons))), STRINGS.getListTypeErrorString(whypersons, "whypersons", str)
        assert(all(map(lambda x: x in self.getPersonNames(), whypersons))), STRINGS.ERROR_NOT_ALL_WHYPERSONS_ARE_VALID+str(whypersons)
        print(f"DATE: {date}")
        print(f"PRODUCT: {product}")
        print(f"NUMBER: {number}")
        print(f"FULL CASHFLOW: {full_cf}")
        print(f"CATEGORIES: {categories}")
        print(f"FTPERSONS: {ftpersons}")
        print(f"WHYPERSONS: {whypersons}")

        product_names_lower = list(map(lambda x: x.name.lower(), self.products))
        if product.lower() in product_names_lower:
            ind = product_names_lower.index(product.lower())
            if self.products[ind].categories != categories:
                ret = QMessageBox.question(self.ui, STRINGS.ERROR_PRODUCT_CATEGORIES_DONT_MATCH, STRINGS.QUESTION_OVERRIDE_OTHER_PRODUCT_CATEGORIES, QMessageBox.Yes | QMessageBox.No)
                if ret == QMessageBox.Yes:
                    self._setCategoriesToProduct(product.lower(), categories)
                else:
                    msgbox = QMessageBox(self.ui)
                    msgbox.setText(STRINGS.INFO_TRANSACTION_WAS_NOT_ADDED)
                    msgbox.exec()
                    return

        ftperson_objects = []
        whyperson_objects = []

        ftpersons_lower = list(map(lambda x: x.lower(), ftpersons))
        whypersons_lower = list(map(lambda x: x.lower(), whypersons))

        for person in self.persons:
            if not(ftpersons_lower or whypersons_lower):
                break
            if person.name.lower() in ftpersons_lower:
                ftperson_objects.append(person)
                ftpersons_lower.remove(person.name.lower())
            if person.name.lower() in whypersons_lower:
                whyperson_objects.append(person)
                whypersons_lower.remove(person.name.lower())
        
        while ftpersons_lower:
            person_name = ftpersons[list(map(lambda x: x.lower(), ftpersons)).index(ftpersons_lower[0])]
            ftperson_objects.append(Person(person_name))
            ftpersons_lower.pop(0)
        
        while whypersons_lower:
            person_name = whypersons[list(map(lambda x: x.lower(), whypersons)).index(whypersons_lower[0])]
            whyperson_objects.append(Person(person_name))
            whypersons_lower.pop(0)

        product_obj = self._addProduct(product, categories)
        self._addTransaction(date, product_obj, number, full_cf, ftperson_objects, whyperson_objects)
    
    def _setCategoriesToProduct(self, product_name_lower, categories):
        assert(type(product_name_lower) == str), STRINGS.getTypeErrorString(product_name_lower, "product_name_lower", str)
        assert(product_name_lower == product_name_lower.lower()), STRINGS.ERROR_WRONG_PRODUCT_NAME_FORMAT+str(product_name_lower)
        assert(type(categories) == list and all(map(lambda x: type(x) == str, categories))), STRINGS.getListTypeErrorString(categories, "categories", str)

        for product in self.products:
            if product.name.lower() == product_name_lower:
                product.categories = categories

    def _addProduct(self, product_name, categories):
        assert(type(product_name) == str), STRINGS.getTypeErrorString(product_name, "product_name", str)
        assert(type(categories) == list and all(map(lambda x: type(x) == str, categories))), STRINGS.getListTypeErrorString(categories, "categories", str)

        for product in self.products:
            if product.name.lower() == product_name.lower():
                product_name = product.name
                assert(product.categories == categories), STRINGS.ERROR_PRODUCT_CATEGORIES_DONT_MATCH
                break
        product_obj = Product(product_name, categories)
        self.products.append(product_obj)
        return product_obj

    def _addTransaction(self, date, product_obj, product_number, fullcf, ftperson_objects, whyperson_objects):
        
        self.transactions.append(Transaction(date, product_obj, product_number, fullcf, ftperson_objects, whyperson_objects))