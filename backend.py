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