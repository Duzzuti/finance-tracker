class PersonCategory:
    def __init__(self, category_name):
        self.name = category_name


class Person:
    def __init__(self, name, person_categories):
        self.name = name
        self.person_categories = person_categories
    
    def addCategory(self, person_category):
        self.person_categories.append(person_category)


class Category:
    def __init__(self, category_name, under_categories=False):
        self.name = category_name
        self.under_categories = under_categories


class Product:
    def __init__(self, product_name, category):
        self.name = product_name
        self.category = category


class Transaction:
    def __init__(self, date, product, number, price_per_product, from_to_person, why_person):
        """
        
        """
        self.date = date
        self.number = number
        self.product = product
        self.price_per_product = price_per_product
        self.full_price = self.price_per_product * self.number
        self.from_to_person = from_to_person
        self.why_person = why_person