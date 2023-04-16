"""
this module is handling the backend of the application
it is providing some api methods, that are used by the frontend
"""
import datetime
import time
import math
import pandas
import pickle
from cryptography.fernet import Fernet
import base64
import hashlib
import yahooquery
from threading import Thread
from strings import ENG as STRINGS
from PyQt5.QtWidgets import QMessageBox
from backend_datatypes import Product, Person, Transaction, Investment, Asset
from fullstack_utils import SortEnum, Filter

def Dsave(func):
    """
    decorator, which runs the function and executes a save afterwards
    """
    def wrapper_save(self, *args):
        ret = func(self, *args)
        Thread(target=self._save).start()
        return ret
    return wrapper_save

def DsortTrans(func):
    """
    decorator, which runs the function and executes a sort afterwards
    """
    def wrapper_sort_trans(self, *args):
        ret = func(self, *args)
        Thread(target=self.sortTransactions, args=(self.sortCriteriaTrans[0], self.sortCriteriaTrans[1])).start()
        return ret
    return wrapper_sort_trans

def DsortInv(func):
    """
    decorator, which runs the function and executes a sort afterwards
    """
    def wrapper_sort_inv(self, *args):
        ret = func(self, *args)
        Thread(target=self.sortInvestments, args=(self.sortCriteriaInv[0], self.sortCriteriaInv[1])).start()
        return ret
    return wrapper_sort_inv

def Dbenchmark(func):   #DEBUGONLY
    """
    decorator, which runs the function and prints the runtime
    """
    def wrapper_bench(self, *args, **kwargs):
        start = time.perf_counter()
        ret = func(self, *args, **kwargs)
        print(func.__name__+" \tneeded "+str(time.perf_counter() - start)+"s")
        return ret
    return wrapper_bench


class Backend:
    """
    the backend class holds all backend functionalities as well as the api methods to the frontend
    the object are passed to the frontend classes that uses the backend to encapsulate it
    this class uses some extern datatypes defined in backend_datatypes
    """
    def __init__(self, ui, load:bool=True):
        """
        basic constructor is setting up the objects needed in the backend
        :param ui: object<Window>, we need some ui, to display messages like errors or information
        :return: void
        """
        self.ui = ui            #the ui object
        self.error_string = ""  #the last occured error as a string
        self.products = []      #a list that holds product objects of all known products
        self.categories = []    #a list that holds some strings representing all known categories
        self.persons = []       #a list that holds person objects of all known persons
        self.transactions = []  #a list that holds transaction objects of all known transactions

        self.transactionFilter = Filter()   #sets up a filter object for the backend
        #if the user dont want to set a own password, this pass is used
        #its obviously not safe, because its written in plain text, but this prevents the user from changing the data in the data files
        # (because they are not readable)
        #if the user has a password set, he will input it on the start and exchange this password  
        self.setNewPassword("jsa0pidfhuj89awhfp9ghqwp9fh9awgh8p9wrghf98ahgwf98gep89")    #standard password

        self.sortCriteriaTrans = [SortEnum.DATE.value, True]
        self.initInvestments()
        if load:
            self._load()
            self._save()    
        self.clean(full=True)

    def setNewPassword(self, password:str):
        """
        setter
        sets a new password and hash
        :param password: str<new password>
        :return: void
        """
        self._password = password
        self._key = self._gen_fernet_key(self._password.encode("utf-8"))

    def TEST(self): #DEBUGONLY
        self.transactions = (Transaction(datetime.date(2022, 1, 1), Product("product1", categories=["cat1", "cat2", "cat3"]), 5, 7.25, [Person("pers1"), Person("pers2")], [Person("pers3"), Person("pers4")]))
        self.categories=["cat1", "cat2", "cat3"]
        self.persons = [Person("pers1"), Person("pers2")]
        self.persons += [Person("pers3"), Person("pers4")]

    def getError(self):
        """
        gets a message of the last occured error (or declining some action, like adding a new category)
        :return: str<last occured error message>
        """
        return "No error was specified" if self.error_string == False else self.error_string

    def getProductNames(self):
        """
        getter for all product names, that are returned sorted
        :return: sorted list<str<productName1>, ...>
        """
        return sorted(list(map(lambda x: x.name, self.products)))

    def getCategories(self):
        """
        getter for all category names, that are returned sorted
        :return: sorted list<str<categoryName1>, ...>
        """
        return sorted(self.categories)

    def getPersonNames(self):
        """
        getter for all person names, that are returned sorted
        :return: sorted list<str<personName1>, ...>
        """
        return sorted(map(lambda x: x.name, self.persons), key=lambda x: x.lower())

    def getTransactions(self):
        """
        generator for all transactions
        :return: Generator<object<Transaction>>
        """
        for trans in self.transactions:
            yield trans

    def getFilteredTransactions(self):
        """
        generator for all transactions that met the requirements of the filter
        :return: Generator<object<Transaction>>
        """
        for trans in self.transactions:
            if self.isTransactionFilter(trans):
                yield trans

    def isTransactionFilter(self, transaction:Transaction):
        """
        a bulk of if statements to check, whether a given transaction is valid with the filter applied
        :param transaction: object<Transaction>
        :return: bool<is transaction valid?>
        """
        assert(type(transaction) == Transaction), STRINGS.getTypeErrorString(transaction, "transaction", Transaction)
        if not(self.transactionFilter.minDate <= transaction.date <= self.transactionFilter.maxDate):
            return False
        if not(self.transactionFilter.contains.lower() in transaction.product.name.lower()):
            return False
        if not(transaction.product.name.lower().startswith(self.transactionFilter.startswith.lower())):
            return False
        if self.transactionFilter.absoluteValues:
            if type(self.transactionFilter.minCashflow) != bool:
                #filter set
                if not(abs(self.transactionFilter.minCashflow) <= abs(transaction.cashflow)):
                    return False
            if type(self.transactionFilter.maxCashflow) != bool:
                #filter set
                if not(abs(self.transactionFilter.maxCashflow) >= abs(transaction.cashflow)):
                    return False
            if type(self.transactionFilter.minCashflowPerProduct) != bool:
                #filter set
                if not(abs(self.transactionFilter.minCashflowPerProduct) <= abs(transaction.cashflow_per_product)):
                    return False
            if type(self.transactionFilter.maxCashflowPerProduct) != bool:
                #filter set
                if not(abs(self.transactionFilter.maxCashflowPerProduct) >= abs(transaction.cashflow_per_product)):
                    return False
        else:
            if type(self.transactionFilter.minCashflow) != bool:
                #filter set
                if not(self.transactionFilter.minCashflow <= transaction.cashflow):
                    return False
            if type(self.transactionFilter.maxCashflow) != bool:
                #filter set
                if not(self.transactionFilter.maxCashflow >= transaction.cashflow):
                    return False
            if type(self.transactionFilter.minCashflowPerProduct) != bool:
                #filter set
                if not(self.transactionFilter.minCashflowPerProduct <= transaction.cashflow_per_product):
                    return False
            if type(self.transactionFilter.maxCashflowPerProduct) != bool:
                #filter set
                if not(self.transactionFilter.maxCashflowPerProduct >= transaction.cashflow_per_product):
                    return False
        if not(any(map(lambda x: x.lower() in map(lambda x: x.lower(), transaction.product.categories), self.transactionFilter.categories))) and \
                                self.transactionFilter.categories != []:
            return False
        if not(any(map(lambda x: x.lower() in map(lambda x: x.name.lower(), transaction.from_to_persons), self.transactionFilter.ftpersons))) and \
                                self.transactionFilter.ftpersons != []:
            return False
        if not(any(map(lambda x: x.lower() in map(lambda x: x.name.lower(), transaction.why_persons), self.transactionFilter.whypersons))) and \
                                self.transactionFilter.whypersons != []:
            return False
        if not(any(map(lambda x: x.lower() in map(lambda x: x.name.lower(), transaction.why_persons) or
                                 x.lower() in map(lambda x: x.name.lower(), transaction.from_to_persons), self.transactionFilter.persons))) and \
                                self.transactionFilter.persons != []:
            return False
        return True

    def getLastTransactionByProductText(self, product_name:str):
        """
        gets the last (most recent) transaction with a specific product name
        :param product_name: str<name of the product>
        :return: object<Transaction> or bool<False> if no transaction was found
        """
        product_name = product_name.lower()
        date_sorted_transactions = sorted(self.transactions, key=lambda x: x.date, reverse=True)
        for transaction in date_sorted_transactions:
            if transaction.product.name.lower() == product_name:
                return transaction
        return False

    def setFilter(self, filter:Filter):
        """
        setter for the filter
        :param filter: object<Filter>
        :return: void
        """
        assert(type(filter) == Filter), STRINGS.getTypeErrorString(filter, "filter", Filter)
        self.transactionFilter = filter

    @Dsave
    def addCategory(self, category:str):
        """
        adds a new category to the existing ones
        returns a bool, whether the category was added or not
        :param category: str<name of the category that should be added>
        :return: bool<category added?>
        """
        assert(type(category) == str), STRINGS.getTypeErrorString(category, "category", str)
        assert(len(category) - category.count(" ") >= 3), STRINGS.ERROR_CATEGORY_CONTAINS_NOT_ENOUGH_CHAR+str(category)
        if category.lower() in map(lambda x: x.lower(), self.categories):
            #dont add the category because its already added (ignoring case)
            self.error_string = f"cannot add category '{category}' because its already added"
            return False
        self.categories.append(category)
        return True

    @Dsave
    def addPerson(self, person_text:str):
        """
        adds a new person to the existing ones
        returns a bool, whether the person was added or not
        :param person_text: str<name of the person that should be added>
        :return: bool<person added?>
        """
        assert(type(person_text) == str), STRINGS.getTypeErrorString(person_text, "person_text", str)
        assert(len(person_text) - person_text.count(" ") >= 3), STRINGS.ERROR_PERSON_CONTAINS_NOT_ENOUGH_CHAR+str(person_text)
        if person_text.lower() in map(lambda x: x.name.lower(), self.persons):
            #dont add the person because its already added (ignoring case)
            self.error_string = f"cannot add person '{person_text}' because its already added"
            return False
        self.persons.append(Person(person_text))
        return True

    def getTransactionObject(self, date:datetime.date, product_name:str, number:int, full_cf:float, 
                       categories:list[str], ftpersons:list[str], whypersons:list[str]):
        """
        verifys the given data and returns a Transaction object to that data
        :param date: datetime.date<date of the transaction>
        :param product_name: str<name of the product>
        :param number: int<product count>
        :param full_cf: float<cashflow that are occured due to the transaction>
        :param categories: list<str<category choosed1>, ...>
        :param ftpersons: list<str<ftperson choosed1>, ...>
        :param whypersons: list<str<whyperson choosed1>, ...>
        :return: object<Transaction> or bool<False> if its not valid
        """
        assert(type(date) == datetime.date), STRINGS.getTypeErrorString(date, "date", datetime.date)
        assert(date <= datetime.date.today()), STRINGS.ERROR_DATE_OUT_OF_RANGE+str(date)
        assert(type(product_name) == str), STRINGS.getTypeErrorString(product_name, "product_name", str)
        assert(len(product_name) - product_name.count(" ") > 0), STRINGS.ERROR_PRODUCT_CONTAINS_NO_CHAR+str(product_name)
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
        assert(len(set(categories)) == len(categories)), STRINGS.ERROR_CATEGORY_NOT_UNIQUE+str(categories)
        assert(len(set(ftpersons)) == len(ftpersons)), STRINGS.ERROR_FTPERSON_NOT_UNIQUE+str(ftpersons)
        assert(len(set(whypersons)) == len(whypersons)), STRINGS.ERROR_WHYPERSON_NOT_UNIQUE+str(whypersons)

        product_obj = self._getProductByName(product_name)
        if product_obj != False:
            #product is already known (ignoring case)
            if product_obj.categories != categories:
                #if the categories differ, ask the user whether override the categories or cancel this transaction
                ret = QMessageBox.question(self.ui, STRINGS.ERROR_PRODUCT_CATEGORIES_DONT_MATCH, STRINGS.QUESTION_OVERRIDE_OTHER_PRODUCT_CATEGORIES, QMessageBox.Yes | QMessageBox.No)
                if ret == QMessageBox.Yes:
                    #override all previous categories
                    self._setCategoriesToProduct(product_name.lower(), categories)
                else:
                    #cancel transaction
                    msgbox = QMessageBox(self.ui)
                    msgbox.setText(STRINGS.INFO_TRANSACTION_WAS_NOT_ADDED)
                    msgbox.exec()
                    return False
                
        #stores the person objects that are choosen by the user
        ftperson_objects = []
        whyperson_objects = []

        #gets the lower case person names
        ftpersons_lower = list(map(lambda x: x.lower(), ftpersons))
        whypersons_lower = list(map(lambda x: x.lower(), whypersons))

        for person in self.persons:
            #goes through all person objects and try to find the persons the user choosed
            if not(ftpersons_lower or whypersons_lower):
                #if all persons are found break
                break
            if person.name.lower() in ftpersons_lower:
                #if a from/to person is found
                ftperson_objects.append(person)             #append the person object of the right person
                ftpersons_lower.remove(person.name.lower()) #remove the person string that are found
            if person.name.lower() in whypersons_lower:
                #if a why person is found
                whyperson_objects.append(person)            #append the person object of the right person
                whypersons_lower.remove(person.name.lower())#remove the person string that are found   
        
        assert(ftpersons_lower == []), STRINGS.ERROR_NOT_KNOWN_FTPERSON_CHOOSEN+str(ftpersons_lower)
        assert(whypersons_lower == []), STRINGS.ERROR_NOT_KNOWN_WHYPERSON_CHOOSEN+str(whypersons_lower)

        if product_obj == False:
            #add the choosen product if its not known
            product_obj = self._addProduct(product_name, categories)
        return Transaction(date, product_obj, number, full_cf, ftperson_objects, whyperson_objects)

    @Dsave
    @DsortTrans
    def addTransaction(self, transaction:Transaction):
        """
        adds a new transaction to the existing ones, pls validate it first with getTransactionObject
        :param transaction: object<Transaction>
        :return: void
        """
        assert(type(transaction) == Transaction), STRINGS.getTypeErrorString(transaction, "transaction", Transaction)

        #add the validated transaction
        self.transactions.append(transaction)

    @Dsave
    @DsortTrans
    def deleteTransaction(self, transaction:Transaction):
        """
        deletes a given transaction from the system
        :param transaction: object<Transaction>
        :return: void
        """
        assert(type(transaction) == Transaction), STRINGS.getTypeErrorString(transaction, "transaction", Transaction)
        assert(transaction in self.transactions), STRINGS.ERROR_TRANSACTION_NOT_IN_LIST+str(transaction)+str(self.transactions)
        self.transactions.remove(transaction)
        self.clean(full=False, transaction=transaction)

    def deleteProduct(self, product:Product):
        """
        deletes the given product taking into account that we have case insensitivity
        :param product: object<Product>
        :return: void
        """
        name_lower = product.name.lower()
        for _product in self.products:
            if _product.name.lower() == name_lower:
                self.products.remove(_product)
                return

    @Dsave
    @DsortTrans
    def renameCategory(self, category:str, new_category:str):
        """
        renames the given category to the new_category name
        :param category: str<category, that you want to rename>
        :param new_category: str<new category name>
        :return: void
        """
        assert(category.lower() in map(lambda x: x.lower(), self.categories)), STRINGS.ERROR_CATEGORY_NOT_FOUND
        assert(len(new_category) - new_category.count(" ") >= 3), STRINGS.ERROR_CATEGORY_CONTAINS_NOT_ENOUGH_CHAR
        category = category.lower()
        #change the category inside the transactions
        for transaction in self.transactions:
            if category in map(lambda x: x.lower(), transaction.product.categories):
                transaction.product.categories.pop(list(map(lambda x: x.lower(), transaction.product.categories)).index(category))
                transaction.product.categories.append(new_category)

        #changes the category list
        self.categories.pop(list(map(lambda x: x.lower(), self.categories)).index(category))
        self.categories.append(new_category)

    @Dsave
    @DsortTrans
    def renamePerson(self, person_name:str, new_person_name:str):
        """
        renames the given person to the new_person_name
        :param person_name: str<name of the person, that you want to rename>
        :param new_person_name: str<new person name>
        :return: void
        """
        assert(person_name.lower() in map(lambda x: x.name.lower(), self.persons)), STRINGS.ERROR_PERSON_NOT_FOUND
        assert(len(new_person_name) - new_person_name.count(" ") >= 3), STRINGS.ERROR_PERSON_CONTAINS_NOT_ENOUGH_CHAR
        person_name = person_name.lower()
        #change the persons inside the transactions
        for transaction in self.transactions:
            if person_name in transaction.getLowerFtPersonNames(_sorted=False):
                person = transaction.from_to_persons.pop(transaction.getLowerFtPersonNames(_sorted=False).index(person_name))
                person.name = new_person_name
                transaction.from_to_persons.append(person)

            if person_name in transaction.getLowerWhyPersonNames(_sorted=False):
                person = transaction.why_persons.pop(transaction.getLowerWhyPersonNames(_sorted=False).index(person_name))
                person.name = new_person_name
                transaction.why_persons.append(person)

        #changes the person list
        #it can happen that the list is changed correctly, because we are changing the name of the person object inside the transactions
        #these objects are likely just a reference to the persons list, that means that they have already been changed
        if person_name in map(lambda x: x.name.lower(), self.persons):
            person = self.persons.pop(list(map(lambda x: x.name.lower(), self.persons)).index(person_name))
            person.name = new_person_name
            self.persons.append(person)

    @Dsave
    @DsortTrans
    def renameProduct(self, product_name:str, new_product_name:str):
        """
        renames the given product to the new_product_name
        :param product_name: str<name of the product, that you want to rename>
        :param new_product_name: str<new product name>
        :return: void
        """
        assert(product_name.lower() in map(lambda x: x.name.lower(), self.products)), STRINGS.ERROR_PRODUCT_NOT_FOUND
        assert(len(new_product_name) - new_product_name.count(" ") >= 1), STRINGS.ERROR_PRODUCT_CONTAINS_NOT_ENOUGH_CHAR
        product_name = product_name.lower()
        #change the products inside the transactions
        for transaction in self.transactions:
            if product_name == transaction.product.name.lower():
                transaction.product.name = new_product_name

        #changes the prodcut list
        #it can happen that the list is changed correctly, because we are changing the name of the product object inside the transactions
        #these objects are likely just a reference to the products list, that means that they have already been changed
        if product_name in map(lambda x: x.name.lower(), self.products):
            product = self.persons.pop(list(map(lambda x: x.name.lower(), self.products)).index(product_name))
            product.name = new_product_name
            self.persons.append(product)

    @Dsave
    @DsortTrans
    def deleteCategoryByName(self, category:str):
        """
        deletes the given category from the system
        :param category: str<category, that you want to delete>
        :return: void
        """
        assert(category.lower() in map(lambda x: x.lower(), self.categories)), STRINGS.ERROR_CATEGORY_NOT_FOUND
        category = category.lower()
        #delete the category from the transactions
        for transaction in self.transactions:
            if category in map(lambda x: x.lower(), transaction.product.categories):
                transaction.product.categories.pop(list(map(lambda x: x.lower(), transaction.product.categories)).index(category))

        #changes the category list
        self.categories.pop(list(map(lambda x: x.lower(), self.categories)).index(category))

    @Dsave
    @DsortTrans
    def deletePersonByName(self, person_name:str):
        """
        deletes the given person from the system
        :param person_name: str<name of the person, that you want to delete>
        :return: void
        """
        assert(person_name.lower() in map(lambda x: x.name.lower(), self.persons)), STRINGS.ERROR_PERSON_NOT_FOUND
        person_name = person_name.lower()
        #delete the persons from the transactions
        for transaction in self.transactions:
            if person_name in transaction.getLowerFtPersonNames(_sorted=False):
                transaction.from_to_persons.pop(transaction.getLowerFtPersonNames(_sorted=False).index(person_name))

            if person_name in transaction.getLowerWhyPersonNames(_sorted=False):
                transaction.why_persons.pop(transaction.getLowerWhyPersonNames(_sorted=False).index(person_name))

        #delete from the person list
        #it can happen that the list is changed correctly, because we are deleting the person object inside the transactions
        #these objects are likely just a reference to the persons list, that means that they have already been deleted
        if person_name in map(lambda x: x.name.lower(), self.persons):
            self.persons.pop(list(map(lambda x: x.name.lower(), self.persons)).index(person_name))

    @Dsave
    @DsortTrans
    def deleteProductByName(self, product_name:str):
        """
        deletes the given product from the system
        :param product_name: str<name of the product, that you want to delete>
        :return: void
        """
        assert(product_name.lower() in map(lambda x: x.name.lower(), self.products)), STRINGS.ERROR_PRODUCT_NOT_FOUND
        product_name = product_name.lower()
        #deletes the transactions that have the given product
        for transaction in self.transactions.copy():
            if product_name == transaction.product.name.lower():
                self.transactions.remove(transaction)

        #change the prodcut list
        #it can happen that the list is changed correctly, because we are deleting the product object inside the transactions
        #these objects are likely just a reference to the products list, that means that they have already been deleted
        if product_name in map(lambda x: x.name.lower(), self.products):
            self.products.pop(list(map(lambda x: x.name.lower(), self.products)).index(product_name))

    @Dsave
    @DsortTrans
    def mergeCategory(self, category1:str, category2:str, new_category:str):
        """
        merges two given categories into a new one and name it like new_category
        this will take affect on all past transactions
        :param category1: str<category1, that you want to merge>
        :param category2: str<category2, that you want to merge>
        :param new_category: str<new category name>
        :return: void
        """
        assert(category1.lower() in map(lambda x: x.lower(), self.categories)), STRINGS.ERROR_CATEGORY_NOT_FOUND
        assert(category2.lower() in map(lambda x: x.lower(), self.categories)), STRINGS.ERROR_CATEGORY_NOT_FOUND
        assert(len(new_category) - new_category.count(" ") >= 3), STRINGS.ERROR_CATEGORY_CONTAINS_NOT_ENOUGH_CHAR
        category1 = category1.lower()
        category2 = category2.lower()
        #delete the category from the transactions
        for transaction in self.transactions:
            cats_lower = list(map(lambda x: x.lower(), transaction.product.categories))
            in_list = False     #true if some of the categories that you wanna merge are in the transaction
            if category1 in cats_lower:
                in_list = True
                transaction.product.categories.pop(cats_lower.index(category1))
                cats_lower = list(map(lambda x: x.lower(), transaction.product.categories))
            if category2 in cats_lower:
                in_list = True
                transaction.product.categories.pop(cats_lower.index(category2))
            if in_list:
                #at least one category was in the transaction
                transaction.product.categories.append(new_category)

        #changes the category list
        try:
            self.categories.pop(list(map(lambda x: x.lower(), self.categories)).index(category1))
        except:
            pass
        try:
            self.categories.pop(list(map(lambda x: x.lower(), self.categories)).index(category2))
        except:
            pass
        self.categories.append(new_category)

    @Dsave
    @DsortTrans
    def mergePerson(self, person1:str, person2:str, new_person:str):
        """
        merges two given persons into a new one and name it like new_person
        this will take affect on all past transactions
        the first person will take the attributes over to the new person 
        :param person1: str<person1, that you want to merge>
        :param person2: str<person2, that you want to merge>
        :param new_person: str<new person name>
        :return: void
        """
        assert(person1.lower() in map(lambda x: x.name.lower(), self.persons)), STRINGS.ERROR_PERSON_NOT_FOUND
        assert(person2.lower() in map(lambda x: x.name.lower(), self.persons)), STRINGS.ERROR_PERSON_NOT_FOUND
        assert(len(new_person) - new_person.count(" ") >= 3), STRINGS.ERROR_PERSON_CONTAINS_NOT_ENOUGH_CHAR
        person1 = person1.lower()
        person2 = person2.lower()
        #changes the person list
        person = self.persons.pop(list(map(lambda x: x.name.lower(), self.persons)).index(person1))
        self.persons.pop(list(map(lambda x: x.name.lower(), self.persons)).index(person2))
        person.name = new_person
        self.persons.append(person)
        #delete the person from the transactions
        for transaction in self.transactions:
            ftpers_lower = list(map(lambda x: x.name.lower(), transaction.from_to_persons))
            whypers_lower = list(map(lambda x: x.name.lower(), transaction.why_persons))
            in_ftlist = False     #true if some of the persons that you wanna merge are in the ftpersons of the transaction
            in_whylist = False     #true if some of the persons that you wanna merge are in the whypersons of the transaction
            if person1 in ftpers_lower:
                in_ftlist = True
                transaction.from_to_persons.pop(ftpers_lower.index(person1))
                ftpers_lower = list(map(lambda x: x.name.lower(), transaction.from_to_persons))
            if person2 in ftpers_lower:
                in_ftlist = True
                transaction.from_to_persons.pop(ftpers_lower.index(person2))
            if in_ftlist:
                #at least one person was in the ftperosns of the transaction
                transaction.from_to_persons.append(person)
            if person1 in whypers_lower:
                in_whylist = True
                transaction.why_persons.pop(whypers_lower.index(person1))
                whypers_lower = list(map(lambda x: x.name.lower(), transaction.why_persons))
            if person2 in whypers_lower:
                in_whylist = True
                transaction.why_persons.pop(whypers_lower.index(person2))
            if in_whylist:
                #at least one person was in the whyperosns of the transaction
                transaction.why_persons.append(person)

    @Dsave
    @DsortTrans
    def mergeProduct(self, product1:str, product2:str, new_product:str):
        """
        merges two given products into a new one and name it like new_product
        this will take affect on all past transactions
        the first product will take the attributes over to the new product 
        :param product1: str<product1, that you want to merge>
        :param product2: str<product2, that you want to merge>
        :param new_product: str<new product name>
        :return: void
        """
        assert(product1.lower() in map(lambda x: x.name.lower(), self.products)), STRINGS.ERROR_PRODUCT_NOT_FOUND
        assert(product2.lower() in map(lambda x: x.name.lower(), self.products)), STRINGS.ERROR_PRODUCT_NOT_FOUND
        assert(len(new_product) - new_product.count(" ") >= 1), STRINGS.ERROR_PRODUCT_CONTAINS_NOT_ENOUGH_CHAR
        product1 = product1.lower()
        product2 = product2.lower()
        #changes the product list
        product = self.products.pop(list(map(lambda x: x.name.lower(), self.products)).index(product1))
        self.products.pop(list(map(lambda x: x.name.lower(), self.products)).index(product2))
        product.name = new_product
        self.products.append(product)
        #delete the product from the transactions
        for transaction in self.transactions:
            if transaction.product.name.lower() in [product1, product2]:
                #we got a product
                transaction.product = product

    def sortTransactions(self, sortElement:SortEnum, up:bool):
        """
        sorts the transactions given the sort criteria. should also sort new adds too
        :param sortElement: object<SortEnum>
        :param up: bool<ascending?>
        :return: void
        """
        self.sortCriteriaTrans = [sortElement, up]
        if sortElement == SortEnum.NAME:
            self.transactions.sort(key=lambda x: x.product.name.lower(), reverse=not(up))
        elif sortElement == SortEnum.CASHFLOW:
            self.transactions.sort(key=lambda x: x.cashflow, reverse=up)
        elif sortElement == SortEnum.DATE:
            self.transactions.sort(key=lambda x: x.date, reverse=up)
        else:
            assert(False), STRINGS.ERROR_SORTELEMENT_OUT_OF_RANGE+str(sortElement)

    def clean(self, full:bool, transaction:Transaction=None):
        """
        cleans up the data: deletes not longer needed products 
        you can do a full clean or if you have a transaction that is no longer in the system, we check whether that product is anywhere else
        :param full: bool<Full clean?>
        :param transaction: object<Transaction>, deleted_transaction, only neccessary if full == False
        :return: void
        """
        assert(type(full) == bool), STRINGS.getTypeErrorString(full, "full", bool)
        assert(type(transaction) == Transaction or (transaction == None and full)), STRINGS.getTypeErrorString(transaction, "transaction", Transaction)
        if full:
            neededProducts = []
            for _transaction in self.transactions:
                neededProducts.append(_transaction.product.name.lower())
            for product in self.products.copy():
                if not product.name.lower() in neededProducts:
                    self.deleteProduct(product)
        else:
            for _transaction in self.transactions:
                if _transaction.product.name.lower() == transaction.product.name.lower():
                    return
            else:
                self.deleteProduct(transaction.product)

    def TESTloadFromCSV(self):  #DEBUGONLY
        """
        this function is for debug purposes only
        for loading from csvs normaly use loadFromCSV()
        """
        print("This is the csv loader")
        print("You can load transaction data from a csv file")
        print("The csv file has to contain 8 columns with date, product name, product categories, number of products, cashflow per product, full cashflow, from/to persons, why persons")
        print("the csv has no header and multiple caegories or persons are separated with a comma")
        print("the separation character of the csv has to be a semicolon ';'")
        print("\n")
        while True:
            path = input("path to csv file: ")
            try: 
                df = pandas.read_csv(path, sep=";", header=None)
                break
            except:
                print(f"could not open {path}")

        for _, row in df.iterrows():
            if int(row[0].split("/")[2]) < 100:
                date = datetime.date(int(row[0].split("/")[2])+2000, int(row[0].split("/")[0]), int(row[0].split("/")[1]))
            else:
                date = datetime.date(int(row[0].split("/")[2]), int(row[0].split("/")[0]), int(row[0].split("/")[1]))
            product_name = "" if type(row[1]) == float and math.isnan(row[1]) else row[1]
            categories = [] if type(row[2]) == float and math.isnan(row[2]) else list(map(lambda x: x.strip(), row[2].split(",")))
            number = 1 if type(row[3]) == float and math.isnan(row[3]) else int(row[3])
            cashflow_pp = 0.0 if type(row[4]) == float and math.isnan(row[4]) else  float(row[4].split(" "+STRINGS.CURRENCY)[0].replace(STRINGS.BIG_NUMBER_SEPARATER, ""))
            cashflow_full = 0.0 if type(row[5]) == float and math.isnan(row[5]) else float(row[5].split(" "+STRINGS.CURRENCY)[0].replace(STRINGS.BIG_NUMBER_SEPARATER, ""))
            sign = STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS if cashflow_full < 0 or cashflow_pp < 0 else STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_PLUS
            ftpersons = [] if type(row[6]) == float and math.isnan(row[6]) else list(map(lambda x: x.strip(), row[6].split(",")))
            whypersons = [] if type(row[7]) == float and math.isnan(row[7]) else list(map(lambda x: x.strip(), row[7].split(",")))
            if sign == STRINGS.APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS:
                cashflow_pp = -abs(cashflow_pp)
                cashflow_full = -abs(cashflow_full)
            
            for category in categories:
                if category.lower() in map(lambda x: x.lower(), self.categories):
                    continue
                self.addCategory(category)
            for person in ftpersons + whypersons:
                if person.lower() in map(lambda x: x.name.lower() ,self.persons):
                    continue
                self.addPerson(person)

            yield [date, product_name, categories, number, cashflow_pp, cashflow_full, sign, ftpersons, whypersons]

    def loadFromCSV(self, fileName:str):
        """
        laods all transactions from a csv file
        the separation symbol has to be ";"
        :param fileName: str<path and file name of the csv>
        :return: void
        """
        assert(type(fileName) == str), STRINGS.getTypeErrorString(fileName, "fileName", str)
        if not fileName.endswith(".csv"):
            #if the ending is not correct, appending the right ending
            fileName += ".csv"
        self.transactions = []
        try:
            trans_df = pandas.read_csv(fileName, sep=";")
            for _, row in trans_df.iterrows():
                #if the category or person is not known, a new one has to be added
                cats = [] if type(row["categories"]) == float and math.isnan(row["categories"]) else row["categories"].split(",")
                for cat in cats:
                    if not cat in self.categories:
                        self.addCategory(cat)
                ftp = [] if type(row["ftpersons"]) == float else row["ftpersons"].split(",")
                for p in ftp:
                    if not p in self.persons:
                        self.addPerson(p)
                whyp = [] if type(row["whypersons"]) == float else row["whypersons"].split(",")
                for p in whyp:
                    if not p in self.persons:
                        self.addPerson(p)
                #gets the transaction object
                trans = self.getTransactionObject(
                    datetime.date.fromisoformat(row["date"]),
                    row["product"], 
                    int(row["number"]),
                    float(row["cashflow"]),
                    cats,
                    ftp,
                    whyp)
                if trans == False:
                    raise ValueError
                self.addTransaction(trans)
        except:
            self.transactions = []
            return False
        return True

    def export(self, fileName:str):
        """
        exports all transactions to a csv file
        this file can be loaded again with load from csv
        :param fileName: str<path and file name of the csv>
        :return: void
        """
        assert(type(fileName) == str), STRINGS.getTypeErrorString(fileName, "fileName", str)
        if not fileName.endswith(".csv"):
            #if the ending is not correct, appending the right ending
            fileName += ".csv"
        #set all transaction in a dataframe
        trans_df = pandas.DataFrame(
            {"date": map(lambda x: x.date, self.transactions), 
             "product": map(lambda x: x.product.name, self.transactions),
             "categories": map(lambda x: ",".join(x.product.categories), self.transactions),
             "number": map(lambda x: x.number, self.transactions),
             "cashflow_pp": map(lambda x: x.cashflow_per_product, self.transactions),
             "cashflow": map(lambda x: x.cashflow, self.transactions),
             "ftpersons": map(lambda x: ",".join(map(lambda y: y.name, x.from_to_persons)), self.transactions),
             "whypersons": map(lambda x: ",".join(map(lambda y: y.name, x.why_persons)), self.transactions)})
        #saves the data frame
        trans_df.to_csv(fileName, sep=";")

    def _getProductByName(self, product_name:str):
        """
        getter for a product object, that corresponds to a given name
        :param product_name: str<name of the product>
        :return: object<Product> or bool<False if no product is found>
        """
        for product in self.products:
            if product.name.lower() == product_name.lower():
                return product
        return False

    @Dsave
    def _setCategoriesToProduct(self, product_name:str, categories:list[str]):
        """
        sets a new set of categories to a product given by a name
        :param product_name: str<name of the product>
        :param categories: list<str<category1>, ...>
        :return: void
        """
        assert(type(product_name) == str), STRINGS.getTypeErrorString(product_name, "product_name", str)
        assert(type(categories) == list and all(map(lambda x: type(x) == str, categories))), STRINGS.getListTypeErrorString(categories, "categories", str)

        product = self._getProductByName(product_name)
        assert(product != False), STRINGS.ERROR_NO_PRODUCT_FOUND+str(product_name)
        product.categories = categories

    def _addProduct(self, product_name:str, categories:list[str]):
        """
        add a new product with a given name and categories
        returns the object of the new added product
        :param product_name: str<name of the product>
        :param categories: list<str<category1>, ...>
        :return: object<Product>
        """
        assert(type(product_name) == str), STRINGS.getTypeErrorString(product_name, "product_name", str)
        assert(type(categories) == list and all(map(lambda x: type(x) == str, categories))), STRINGS.getListTypeErrorString(categories, "categories", str)
        assert(self._getProductByName(product_name) == False), STRINGS.ERROR_PRODUCT_ALREADY_KNOWN+str(product_name)

        product_obj = Product(product_name, categories)
        self.products.append(product_obj)
        return product_obj

    def _gen_fernet_key(self, passcode:bytes) -> bytes:
        """
        this method uses a passcode and generates a hash out of it
        :param passcode: bytes<encoded password>
        :return: byte<hash>
        """
        assert isinstance(passcode, bytes)
        hlib = hashlib.md5()
        hlib.update(passcode)
        return base64.urlsafe_b64encode(hlib.hexdigest().encode('latin-1'))

    def _save(self):
        """
        saves, the backend object in a file
        :return: void
        """
        dumped_data = pickle.dumps([self.products, self.categories, self.persons, self.transactions, self.investments, self.current_assets, self.ticker_symbols, self.ticker_shares_dict])
        dec_file = open("data.fin", "wb")
        dec_file.write(Fernet(self._key).encrypt(dumped_data))
        dec_file.close()
    
    def _load(self):
        """
        loads, the backend object from a file
        :return: void
        """
        try:
            data_file = open("data.fin", "rb")
        except:
            print("no file to load from found")
            self.__init__(self.ui, load=False)
            return
        try:
            dumped_data = Fernet(self._key).decrypt(data_file.read())
        except:
            print("Some error with the key or loaded data")
            data_file.close()
            return
        data_file.close()
        try:
            saved = pickle.loads(dumped_data)
            self.products = saved[0]
            self.categories = saved[1]
            self.persons =  saved[2]
            self.transactions = saved[3]
            self.investments = saved[4]
            self.current_assets = saved[5]
            self.ticker_symbols = saved[6]
            self.ticker_shares_dict = saved[7]
        except:
            print("Some error occured with the old data")
        Thread(target=self.initAfterLoad).start()   #init the loaded data in an other thread
        

#***********************INVESTMENT******************************
    def initInvestments(self):
        """
        initialise the investment part of the backend
        sets up some required datatyes
        :return: void
        """
        self.investments:list[Investment] = []       #saves all investment objects
        self.investment_dict:dict[Investment, True] = {}     #saves all investment object in a hash map
        self.current_assets:list[Asset] = []    #saves all current assets hold by the user
        self.ticker_symbols:dict[str, True] = {}           #a list of tickers used by the user (we can import some tickers here)
        self.ticker_shares_dict:dict[str, float] = {}             #saves the current number of shares that the user is holding per asset
        self.sortCriteriaInv = [SortEnum.DATE, True]
        self.timeout_time = 1.0   #time in seconds the programm should wait for a api response before throwing

    def initAfterLoad(self):
        """
        this method gets called after the data is loaded from the file.
        Its a threaded method. Operations on the loaded data are performed
        :return: void
        """
        #create a hashmap with all investments
        for i in self.investments:
            if not i in self.investment_dict:
                self.investment_dict[i] = True

    def getTickerNames(self):
        """
        getter for ticker names
        :return: Iterable[str<ticker1>, ...]
        """
        return self.ticker_symbols
    
    def getAvailableShortNames(self):
        """
        getter for stock names
        :return: Iterable[str<stock name1>, ...]
        """
        return list(sorted(map(lambda x: x.short_name, self.current_assets)))

    def getInvestments(self):
        """
        getter for investment objects
        these are sorted like the sort criteria is specified
        :return: Iterable[Investment]
        """
        return self.investments

    def getTickerForName(self, name:str):
        """
        gets the ticker symbol from the given short name of the asset
        :param name: str<name of the asset>
        :return: str<ticker>
        """
        for asset in self.current_assets:
            if asset.short_name == name:
                return asset.ticker_symbol
        print("error finding the name in the current assets")
        raise ValueError

    def getSharesForAsset(self, ticker_symbol:str):
        """
        getter for the number of shares currently hold of the given asset
        :param ticker_symbol: str<ticker symbol of the asset from which the number of shares should be got>
        :return: void
        """
        if ticker_symbol in self.ticker_shares_dict:
            return self.ticker_shares_dict[ticker_symbol]
        else:
            #user dont hold this asset right now
            return 0
    @Dbenchmark
    def sortInvestments(self, sortElement:SortEnum, up:bool):
        """
        sorts the investments given the sort criteria. should also sort new adds too
        :param sortElement: object<SortEnum>
        :param up: bool<ascending?>
        :return: void
        """
        self.sortCriteriaTrans = [sortElement, up]
        if sortElement == SortEnum.NAME:
            self.investments.sort(key=lambda x: x.asset.short_name.lower(), reverse=not(up))
        elif sortElement == SortEnum.CASHFLOW:
            self.investments.sort(key=lambda x: x.price, reverse=up)
        elif sortElement == SortEnum.DATE:
            self.investments.sort(key=lambda x: x.date, reverse=up)
        else:
            assert(False), STRINGS.ERROR_SORTELEMENT_OUT_OF_RANGE+str(sortElement)
    
    def printInvestments(self): #DEBUGONLY
        """
        prints the current investment data for debug purposes
        :return: void
        """
        self.sortInvestments(SortEnum.DATE, False)
        print(list(map(lambda x: x.date.isoformat()+" "+x.trade_type+" "+x.asset.ticker_symbol+" "+str(x.number), self.investments)))
        print(self.investment_dict)
        print(list(map(lambda x: x.ticker_symbol+" "+x.short_name, self.current_assets)))
        print(self.ticker_symbols)
        print(self.ticker_shares_dict)

    @Dbenchmark
    @Dsave
    @DsortInv
    def addInvestment(self, data:list[str, str, float, float, float, float]):
        """
        takes in some data from the form 
        validates them first and adds the investment to the system if not error occurred
        :param data: list[datetime.date<date of the transaction>, str<trade_type>, str<ticker>, float<number>, float<ppa>, float<tradingfee>, float<tax>]
        :return: bool<success?>
        """
        assert(len(data) == 7), STRINGS.ERROR_WRONG_DATA_LENGTH+str(data)
        date, trade_type, ticker_symbol, number, ppa, tradingfee, tax = data
        ticker_symbol = ticker_symbol.lower()
        #some type and range checks
        assert(type(date) == datetime.date), STRINGS.getTypeErrorString(date, "date", datetime.date)
        assert(type(trade_type) == str), STRINGS.getTypeErrorString(trade_type, "trade_type", str)
        assert(type(ticker_symbol) == str), STRINGS.getTypeErrorString(ticker_symbol, "ticker", str)
        assert(type(number) == float), STRINGS.getTypeErrorString(number, "number", float)
        assert(type(ppa) == float), STRINGS.getTypeErrorString(ppa, "ppa", float)
        assert(type(tradingfee) == float), STRINGS.getTypeErrorString(tradingfee, "tradingfee", float)
        assert(type(tax) == float), STRINGS.getTypeErrorString(tax, "tax", float)
        self.printInvestments() #DEBUGONLY
        assert(trade_type in ["buy", "sell", "dividend"]), STRINGS.ERROR_TRADE_TYPE_NOT_VALID+trade_type
        if not datetime.date(1900, 1, 1) <= date <= datetime.date.today():
            #date out of range
            self.error_string = f"The provided date is out of range (between 1900-1-1 and today): {date.isoformat()}"
        if number <= 0 or ppa <= 0 or tradingfee < 0 or tax < 0:
            #data out of range
            self.error_string = "some of the following rules are broken:\nnumber of assets <= 0 \nprice per asset <= 0\n tradingfee < 0\ntax < 0"
            return False
        
        #gets the ticker object from the api
        #sets up a variable that should store the Ticker object
        self.ticker_obj = False
        #calling the loadTicker method on a new thread to avoid hanging program
        thread = Thread(target=self._loadTicker, args=[ticker_symbol])  
        thread.start()
        #if no ticker is got after a given timeout the program returns with a connection error
        thread.join(self.timeout_time)
        ticker_obj:yahooquery.Ticker = self.ticker_obj    
        if ticker_obj == False:
            #could not load the ticker object, because its still false
            self.error_string = f"ticker could not be loaded, because of network error or api errors.\nPlease try again later"
            return False
        try:
            ticker_obj.quote_type[ticker_symbol]
        except:
            #ticker was loaded but not valid (there are no information about this ticker)
            self.error_string = f"no data to the ticker with the symbol {ticker_symbol} could be found.\nCauses can be:\nThere was a network error\nThe api of yahoo finance has some errors or is not reachable at the moment\nThe provided ticker does not exist"
            return False
        try:
            short_name = ticker_obj.quote_type[ticker_symbol]["shortName"]
            cur = ticker_obj.price[ticker_symbol]["currency"]
        except:
            #there are still not enough informations to work with
            self.error_string = f"the ticker symbol exists but has no name and currency data"
            return False
        if cur != STRINGS.CURRENCY_STRING:
            #the ticker selected by the user has a different currency than the set currency of the program (that is invalid)
            self.error_string = f"the ticker you provided is not in your currency.\nYour currency: {STRINGS.CURRENCY_STRING}, asset currency: {cur}\nPlease provide the ticker with your currency"
            return False
        
        asset = Asset(ticker_symbol, short_name)    #creates the asset object
        inv_obj = Investment(trade_type, date, asset, number, ppa, tradingfee, tax) #create the investment object
        if inv_obj in self.investment_dict:
            #the user tries to add the same investment twice
            self.error_string = "This investment is already added"
            return False
        self.investments.append(inv_obj)    #adds the investment
        self.investment_dict[inv_obj] = True    #adds the investment to the map

        if self._update():
            #added transaction successfully
            return True
        else:
            #some error occured
            self.investments.remove(inv_obj)
            self.investment_dict.pop(inv_obj)
            self.error_string = "The investment was not added.\nFollowing error occured:\n"+self.error_string
            return False
    @Dbenchmark
    def _update(self):
        """
        this method should be called after a new investment is added
        the program iterates over all investments sorted by date and validates them
        if no error occured the class variables are overritten
        :return: bool<success?>
        """
        #creates the temp variables
        tcurrent_assets = []
        tticker_shares_dict = {}
        self.sortInvestments(SortEnum.DATE, False)  #sorts the investments (after that we should sort it back)
        for inv in self.investments:
            match inv.trade_type:
                case "buy":
                    if inv.asset.ticker_symbol in tticker_shares_dict:
                        #user buys an asset that is already in the portfolio
                        tticker_shares_dict[inv.asset.ticker_symbol] += inv.number
                    else:
                        #user buys an asset that is not in the portfolio
                        tticker_shares_dict[inv.asset.ticker_symbol] = inv.number
                case "sell":
                    if inv.asset.ticker_symbol in tticker_shares_dict:
                        #user sells a asset that is already in the portfolio (should check on negative shares)
                        tticker_shares_dict[inv.asset.ticker_symbol] -= inv.number
                    else:
                        #the user is trying to sell shares, but there are no currently hold
                        self.error_string = f"you have no shares of this asset.\nYou cannot sell shares"
                        return False
                case "dividend":
                    if inv.asset.ticker_symbol in tticker_shares_dict:
                        #user gets a dividend from an asset that is in the portfolio
                        if tticker_shares_dict[inv.asset.ticker_symbol] - inv.number < 0:
                            #the user is trying to get a dividend from more shares than currently hold
                            self.error_string = f"you only have {tticker_shares_dict[inv.asset.ticker_symbol]} shares of this asset.\nYou cannot get dividend from {inv.number} shares"
                            return False
                    else:
                        #the user is trying to get a dividend from this asset, but there is no share currently hold
                        self.error_string = f"you have no shares of this asset.\nYou cannot get dividend from this asset"
                        return False
            if tticker_shares_dict[inv.asset.ticker_symbol] < 0:
                #the user is trying to sell more shares than currently hold
                self.error_string = f"you only have {tticker_shares_dict[inv.asset.ticker_symbol] + inv.number} shares of this asset.\nYou cannot sell {inv.number} shares"
                return False
            elif tticker_shares_dict[inv.asset.ticker_symbol] > 0:
                #the user is now holding this asset
                if not hash(inv.asset) in map(lambda x: hash(x), tcurrent_assets):
                    #add it to the current assets if its not already added
                    tcurrent_assets.append(inv.asset)
            else:
                if hash(inv.asset) in map(lambda x: hash(x), tcurrent_assets):
                    #remove the asset from the current assets, because the user no longer holds this asset
                    tcurrent_assets.remove(inv.asset)
            #saves the ticker
            self.ticker_symbols[inv.asset.ticker_symbol] = True
        #update succeeded
        #load the data into the class
        self.current_assets = tcurrent_assets
        self.ticker_shares_dict = tticker_shares_dict
        return True    
    
    @Dsave
    def _reset(self):
        """
        resets the investment datatypes
        THIS WILL DELETE ALL INVESTMENT DATA
        :return: void
        """
        self.investments:list[Investment] = []       #saves all investment objects
        self.current_assets:list[Asset] = []    #saves all current assets hold by the user
        self.ticker_symbols:dict[str, True] = {}           #a list of tickers used by the user (we can import some tickers here)
        self.ticker_shares_dict:dict[str, float] = {}             #saves the current number of shares that the user is holding per asset
    @Dbenchmark
    def _loadTicker(self, ticker_symbol:str):
        """
        extern method for loading the ticker on an other thread
        :param ticker_symbol: str<symbol of the ticker you wanna load>
        :return: void
        """
        self.ticker_obj = yahooquery.Ticker(ticker_symbol)
        return
