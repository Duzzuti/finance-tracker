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
        print(f"DATE: {date}")
        print(f"PRODUCT: {product}")
        print(f"NUMBER: {number}")
        print(f"FULL CASHFLOW: {full_cf}")
        print(f"CATEGORIES: {categories}")
        print(f"FTPERSONS: {ftpersons}")
        print(f"WHYPERSONS: {whypersons}")