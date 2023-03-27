import datetime

class PersonCategory:
    def __init__(self, category_name:str):
        self.name = category_name


class Person:
    def __init__(self, name:str, person_categories:list[PersonCategory]=[]):
        self.name = name
        self.person_categories = person_categories
    
    def addCategory(self, person_category):
        self.person_categories.append(person_category)


class Product:
    def __init__(self, product_name:str, categories:list[str]=[]):
        self.name = product_name
        self.categories = categories


class Transaction:
    def __init__(self, date:datetime.date, product:Product, number:int, cashflow:float, from_to_persons:list[Person], why_persons:list[Person]):
        """
        
        """
        self.date = date
        self.number = number
        self.product = product
        self.cashflow = round(cashflow, 2)
        self.cashflow_per_product = round(self.cashflow / self.number, 2)
        self.from_to_persons = from_to_persons
        self.why_persons = why_persons
    
    def getFtPersonNames(self):
        return sorted(map(lambda x: x.name, self.from_to_persons))

    def getWhyPersonNames(self):
        return sorted(map(lambda x: x.name, self.why_persons))