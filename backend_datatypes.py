"""
this module is providing the datatypes that are used by the backend
"""
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
    
    def getLowerFtPersonNames(self, _sorted:bool=True):
        if _sorted:
            return sorted(map(lambda x: x.name.lower(), self.from_to_persons))
        else:
            return list(map(lambda x: x.name.lower(), self.from_to_persons))

    def getLowerWhyPersonNames(self, _sorted:bool=True):
        if _sorted:
            return sorted(map(lambda x: x.name.lower(), self.why_persons))
        else:
            return list(map(lambda x: x.name.lower(), self.why_persons))


class Asset:
    def __init__(self, ticker_symbol:str, short_name:str) -> None:
        self.ticker_symbol = ticker_symbol
        self.short_name = short_name


class Investment:
    def __init__(self, trade_type:str, date:datetime.date, asset:Asset, number:float, price_per_asset:float, tradingfee:float, tax:float):
        """
        
        """
        self.trade_type = trade_type
        self.date = date
        self.number = number
        self.asset = asset
        self.price_per_asset = price_per_asset
        self.price = price_per_asset * number
        self.tradingfee = tradingfee
        self.tax = tax