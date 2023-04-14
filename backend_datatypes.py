"""
this module is providing the datatypes that are used by the backend
"""
import datetime
from strings import ENG as STRINGS


class Person:
    """
    person class holds a name and a person category that you can set
    """
    def __init__(self, name:str, person_categories:list[str]=[]):
        """
        basic constructor
        saves the arguments in the object
        :param name: str<name of the person>
        :param person_categories: list<str<person category1>, ...>
        :return: void
        """
        assert(type(name) == str), STRINGS.getTypeErrorString(name, "name", str)
        assert(type(person_categories) == list and all(map(lambda x: type(x) == str, person_categories))), STRINGS.getListTypeErrorString(person_categories, "person_categories", str)
        self.name = name
        self.person_categories = person_categories
    
    def addCategory(self, person_category:str):
        """
        adds a given person category to that person
        :param person_category: str<person category>
        :return: void
        """
        assert(type(person_category) == str), STRINGS.getTypeErrorString(person_category, "person_category", str)
        self.person_categories.append(person_category)


class Product:
    """
    a product contains a product name and a list of categories.
    categories are used to filter the products and for statistics
    """
    def __init__(self, product_name:str, categories:list[str]=[]):
        """
        basic constructor
        saves the arguments to that object
        :param product_name: str<name of the product>
        :param categories: list<str<product category1>, ... >
        :return: void
        """
        assert(type(product_name) == str), STRINGS.getTypeErrorString(product_name, "product_name", str)
        assert(type(categories) == list and all(map(lambda x: type(x) == str, categories))), STRINGS.getListTypeErrorString(categories, "categories", str)
        self.name = product_name
        self.categories = categories


class Transaction:
    """
    a transaction contains a date, product, number of products, the cashflow of the transaction and 
    two lists with persons that are involved into the transaction
    the from/to persons are the persons who made the transaction with you and the why persons are the persons who are the reason for this transaction
    """
    def __init__(self, date:datetime.date, product:Product, number:int, cashflow:float, from_to_persons:list[Person], why_persons:list[Person]):
        """
        basic constructor
        saves the given arguments in the object
        :param date: datetime.date<date of the transaction>
        :param product: object<Product that are bought/sold
        :param number: int<number of products>
        :param cashflow: float<cashflow of the transaction from your sight (negative if you lost money)>
        :param from_to_persons: list<object<from/to person1>, ...>
        :param why_persons: list<object<why person1>, ...>
        :return: void
        """
        assert(type(date) == datetime.date), STRINGS.getTypeErrorString(date, "date", datetime.date)
        assert(type(product) == Product), STRINGS.getTypeErrorString(product, "product", Product)
        assert(type(number) == int), STRINGS.getTypeErrorString(number, "number", int)
        assert(type(cashflow) == float), STRINGS.getTypeErrorString(cashflow, "cashflow", float)
        assert(type(from_to_persons) == list and all(map(lambda x: type(x) == Person, from_to_persons))), STRINGS.getListTypeErrorString(from_to_persons, "from_to_persons", Person)
        assert(type(why_persons) == list and all(map(lambda x: type(x) == Person, why_persons))), STRINGS.getListTypeErrorString(why_persons, "why_persons", Person)
        self.date = date
        self.number = number
        self.product = product
        self.cashflow = round(cashflow, 2)
        self.cashflow_per_product = round(self.cashflow / self.number, 2)
        self.from_to_persons = from_to_persons
        self.why_persons = why_persons
    
    def getFtPersonNames(self):
        """
        returns a sorted list of all from/to persons names
        :return: list<str<from/to person name1>, ...>
        """
        return sorted(map(lambda x: x.name, self.from_to_persons))

    def getWhyPersonNames(self):
        """
        returns a sorted list of all why persons names
        :return: list<str<why person name1>, ...>
        """
        return sorted(map(lambda x: x.name, self.why_persons))
    
    def getLowerFtPersonNames(self, _sorted:bool=True):
        """
        returns a list of all from/to persons names, but lowercase
        :param _sorted: bool<should the returned list be sorted?>
        :return: list<str<from/to person name lowercase1>, ...>
        """
        assert(type(_sorted) == bool), STRINGS.getTypeErrorString(_sorted, "_sorted", bool)
        if _sorted:
            return sorted(map(lambda x: x.name.lower(), self.from_to_persons))
        else:
            return list(map(lambda x: x.name.lower(), self.from_to_persons))

    def getLowerWhyPersonNames(self, _sorted:bool=True):
        """
        returns a list of all why persons names, but lowercase
        :param _sorted: bool<should the returned list be sorted?>
        :return: list<str<why person name lowercase1>, ...>
        """
        assert(type(_sorted) == bool), STRINGS.getTypeErrorString(_sorted, "_sorted", bool)
        if _sorted:
            return sorted(map(lambda x: x.name.lower(), self.why_persons))
        else:
            return list(map(lambda x: x.name.lower(), self.why_persons))


class Asset:
    """
    an asset contains a ticker_symbol and a short name that are gotten from the yahoo finance api
    """
    def __init__(self, ticker_symbol:str, short_name:str) -> None:
        """
        basic constructor
        saves the arguments into the object
        :param ticker_symbol: str<symbol of the yahoo ticker>
        :param short_name: str<short name of the asset according to yahoo.ticker.info["shortName"]>
        :return: void
        """
        assert(type(ticker_symbol) == str), STRINGS.getTypeErrorString(ticker_symbol, "ticker_symbol", str)
        assert(type(short_name) == str), STRINGS.getTypeErrorString(short_name, "short_name", str)
        self.ticker_symbol = ticker_symbol
        self.short_name = short_name


class Investment:
    """
    an investment contains a trade_type which is "buy", "sell" or "dividend", date, asset object, number of assets,
    price per asset, tradingfee and tax
    """
    def __init__(self, trade_type:str, date:datetime.date, asset:Asset, number:float, price_per_asset:float, tradingfee:float, tax:float):
        """
        basic constructor
        saves the arguments into the object
        :param trade_type: str<"buy", "sell" or "dividend">
        :param date: datetime.date<date of the investment>
        :param asset: object<Asset that is traded>
        :param number: float<number of shares that are traded>
        :param price_per_asset: float<price per share/dividend per share>
        :param tradingfee: float<tradingfee (not in dividend mode)>
        :param tax: float<taxes (not in buy mode)>
        :return: void
        """
        assert(type(trade_type) == str), STRINGS.getTypeErrorString(trade_type, "trade_type", str)
        assert(type(date) == datetime.date), STRINGS.getTypeErrorString(date, "date", datetime.date)
        assert(type(asset) == Asset), STRINGS.getTypeErrorString(asset, "asset", Asset)
        assert(type(number) == float), STRINGS.getTypeErrorString(number, "number", float)
        assert(type(price_per_asset) == float), STRINGS.getTypeErrorString(price_per_asset, "price_per_asset", float)
        assert(type(tradingfee) == float), STRINGS.getTypeErrorString(tradingfee, "tradingfee", float)
        assert(type(tax) == float), STRINGS.getTypeErrorString(tax, "tax", float)

        assert(trade_type in ["buy", "sell", "dividend"]), STRINGS.ERROR_TRADE_TYPE_NOT_VALID+trade_type
        assert(number > 0), STRINGS.ERROR_NUMBER_ZERO_OR_LESS+str(number)
        assert(price_per_asset > 0), STRINGS.ERROR_PRICE_ZERO_OR_LESS+str(price_per_asset)
        assert(tradingfee >= 0), STRINGS.ERROR_TRADINGFEE_LESS_ZERO+str(tradingfee)
        assert(tax >= 0), STRINGS.ERROR_TAX_LESS_ZERO+str(tax)
        self.trade_type = trade_type
        self.date = date
        self.number = number
        self.asset = asset
        self.price_per_asset = price_per_asset
        self.price = price_per_asset * number
        self.tradingfee = tradingfee
        self.tax = tax
