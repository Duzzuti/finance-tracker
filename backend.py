"""
this module is handling the backend of the application
it is providing some api methods, that are used by the frontend
"""
import datetime
import pandas
import math
import pickle
from strings import ENG as STRINGS
from PyQt5.QtWidgets import QMessageBox
from backend_datatypes import Product, Person, Transaction
from fullstack_utils import SortEnum, Filter


def Dsave(func):
    """
    decorator, which runs the function and executes a save afterwards
    """
    def wrapper(self, *args):
        ret = func(self, *args)
        self._save()
        return ret
    return wrapper

def Dsort(func):
    """
    decorator, which runs the function and executes a sort afterwards
    """
    def wrapper(self, *args):
        ret = func(self, *args)
        self.sortTransactions(self.sortCriteria[0], self.sortCriteria[1])
        return ret
    return wrapper


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

        self.sortCriteria = [SortEnum.DATE.value, True]

        if load:
            self._load()
        self.clean(full=True)

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
    @Dsort
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
    @Dsort
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
    @Dsort
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
    @Dsort
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
    @Dsort
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

    def sortTransactions(self, sortElement:SortEnum, up:bool):
        """
        sorts the transactions given the sort criteria. should also sort new adds too
        :param sortElement: object<SortEnum>
        :param up: bool<ascending?>
        :return: void
        """
        self.sortCriteria = [sortElement, up]
        if sortElement == SortEnum.PRODUCT:
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

    @Dsave
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
    
    def _save(self):
        """
        saves, the backend object in a file
        :return: void
        """
        pickle.dump([self.products, self.categories, self.persons, self.transactions], open("data.pkl", "wb"))

    def _load(self):
        """
        loads, the backend object from a file
        :return: void
        """
        try:
            saved = pickle.load(open("data.pkl", "rb"))
            self.products = saved[0]
            self.categories = saved[1]
            self.persons =  saved[2]
            self.transactions = saved[3]
        except:
            print("no file to load from found")
            self.__init__(self.ui, load=False)

