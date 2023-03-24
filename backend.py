import datetime
from strings import ENG as STRINGS

class Backend:
    def __init__(self):
        pass

    def getProductNames(self):
        return ["product"]

    def getCategories(self):
        return ["cat"+str(i) for i in range(20)] + ["z1"]

    def addCategory(self, category):
        return True

    def getError(self):
        return "An error occured"

    def getPersons(self):
        return ["per"+str(i) for i in range(20)] + ["z1"]

    def addPerson(self, person_text):
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
        assert(all(map(lambda x: x in self.getPersons(), ftpersons))), STRINGS.ERROR_NOT_ALL_FTPERSONS_ARE_VALID+str(ftpersons)
        assert(type(whypersons) == list and all(map(lambda x: type(x) == str, whypersons))), STRINGS.getListTypeErrorString(whypersons, "whypersons", str)
        assert(all(map(lambda x: x in self.getPersons(), whypersons))), STRINGS.ERROR_NOT_ALL_WHYPERSONS_ARE_VALID+str(whypersons)
        print(f"DATE: {date}")
        print(f"PRODUCT: {product}")
        print(f"NUMBER: {number}")
        print(f"FULL CASHFLOW: {full_cf}")
        print(f"CATEGORIES: {categories}")
        print(f"FTPERSONS: {ftpersons}")
        print(f"WHYPERSONS: {whypersons}")