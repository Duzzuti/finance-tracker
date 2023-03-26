class PersonCategory:
    def __init__(self, category_name):
        self.name = category_name


class Person:
    def __init__(self, name, person_categories=[]):
        self.name = name
        self.person_categories = person_categories
    
    def addCategory(self, person_category):
        self.person_categories.append(person_category)


class Product:
    def __init__(self, product_name, categories=[]):
        self.name = product_name
        self.categories = categories


class Transaction:
    def __init__(self, date, product, number, cashflow, from_to_persons, why_persons):
        """
        
        """
        self.date = date
        self.number = number
        self.product = product
        self.cashflow = round(cashflow, 2)
        self.cashflow_per_product = round(self.cashflow / self.number, 2)
        self.from_to_persons = from_to_persons
        self.why_persons = why_persons