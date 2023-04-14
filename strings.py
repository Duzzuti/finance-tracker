"""
this module stores all strings that are used in the programm
you can add your own language and the programm can easily adapt to that language
"""
class ENG:
    """
    all strings in english are stored here
    """
    def getTypeErrorString(arg, arg_name,  _type):
        """
        gets the error string, if some argument has the wrong type
        :param arg: any<argument that has the wrong type>
        :param arg_name: str<the name of the argument>
        :param _type: type<the type the argument should have>
        :return: str<error message>
        """
        return f"The argument '{arg_name}' is not of type {_type}: {arg}"

    def getListTypeErrorString(arg, arg_name, inner_type):
        """
        gets the error string, if some list argument is either not a list or its contents are the wrong type
        :param arg: any<list argument that has the wrong type>
        :param arg_name: str<the name of the list argument>
        :param _type: type<the type the contents of the list should have>
        :return: str<error message>
        """
        return f"The list '{arg_name}' is not of type list or/and the contents are not of type {inner_type}: {arg}"


    #META Strings
    CURRENCY = "€"                  #currency sign
    CURRENCY_STRING = "EUR"         #currency abbreviation
    COMMA = "."                     #the comma that is used in the programm (all other commas are replaced with this)
    BIG_NUMBER_SEPARATER = ","
    COMMAS = [".", ","]             #all accepted commas
    ZERO_STRINGS = ["", " ", "."]   #strings that should evaluate to zero if we want a number as an input

    #Main Window Strings
    APP_TITLE = "Finance tracker"
    APP_ICON = "media/icon.png"

    APP_TAB1 = "Transactions"
    APP_TAB2 = "Investments"
    
    APP_LABEL_NEW_TRANSACTION = "Add new transaction"
    APP_LABEL_NEW_TRANSACTION_CF = "Enter the gain or loss of the transaction:"
    APP_LABEL_NEW_TRANSACTION_CF_PP = f"Per product (in {CURRENCY}):"
    APP_LABEL_NEW_TRANSACTION_CF_FULL = f"For the full transaction (in {CURRENCY}):"
    APP_LABEL_NEW_TRANSACTION_CF_SIGN = "Sign:"
    APP_LABEL_NEW_TRANSACTION_CF_SIGN_PLUS = "+ (Gain)"
    APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS = "- (Loss)"
    APP_LABEL_NEW_TRANSACTION_PRODUCT = "Enter the name of the product:"
    APP_LABEL_NEW_TRANSACTION_CAT = "Add a new category:"
    APP_LABEL_NEW_TRANSACTION_NUMBER = "Number of products:"
    APP_LABEL_NEW_TRANSACTION_PERSON = "Add a new person:"

    APP_LABEL_LAST_TRANSACTIONS = "Your transactions"

    APP_LABEL_EDIT = "Edit Products, Categories and Persons"

    APP_BUTTON_NEW_TRANSACTION_ADD_CAT = "Add"
    APP_BUTTON_NEW_TRANSACTION_RESET_CAT = "Reset Categories"
    APP_BUTTON_NEW_TRANSACTION_ADD_PERSON_WHYP = "Add why person"
    APP_BUTTON_NEW_TRANSACTION_ADD_PERSON_FTP = "Add from/to person"
    APP_BUTTON_NEW_TRANSACTION_RESET_PERSON = "Reset persons"
    APP_BUTTON_NEW_TRANSACTION_SUBMIT = "Add transaction"
    APP_BUTTON_FILTER_OFF = "Set a filter"
    APP_BUTTON_FILTER_ON = "Change filter"
    APP_BUTTON_FILTER_RESET = "Reset filter"

    APP_BUTTON_LAST_TRANSACTIONS_DATE = "Date "
    APP_BUTTON_LAST_TRANSACTIONS_CASHFLOW = "Cashflow "
    APP_BUTTON_LAST_TRANSACTIONS_PRODUCT = "Product "
    APP_BUTTON_LOAD = "Load from csv"
    APP_BUTTON_EXPORT = "Export to csv"

    APP_BUTTON_RENAMING_CATEGORY = "Rename category"
    APP_BUTTON_RENAMING_PERSON = "Rename person"
    APP_BUTTON_RENAMING_PRODUCT = "Rename product"
    APP_BUTTON_DELETING_CATEGORY = "Delete category"
    APP_BUTTON_DELETING_PERSON = "Delete person"
    APP_BUTTON_DELETING_PRODUCT = "Delete product"
    APP_BUTTON_MERGING_CATEGORY = "Merging categories"
    APP_BUTTON_MERGING_PERSON = "Merging persons"
    APP_BUTTON_MERGING_PRODUCT = "Merging products"


    APP_NEW_TRANSACTION_DEFAULT_CATEGORY = "Without category"
    APP_NEW_TRANSACTION_DEFAULT_FTPERSON = "No from/to person"
    APP_NEW_TRANSACTION_DEFAULT_WHYPERSON = "No why person"
    APP_NEW_TRANSACTION_DEFAULT_PERSON = "No person"

    APP_NEW_TRANSACTION_PRODUCT_INPUT = "product"
    APP_NEW_TRANSACTION_CASHFLOW_INPUT = "cashflow"

    APP_LABEL_TRANSACTION_COUNT = " Transactions"

    APP_LABEL_RENAMING = "Renaming"
    APP_LABEL_RENAMING_CATEGORY = "Old category name:"
    APP_LABEL_RENAMING_CATEGORY_EDIT = "New category name:"
    APP_LABEL_RENAMING_PERSON = "Old person name:"
    APP_LABEL_RENAMING_PERSON_EDIT = "New person name:"
    APP_LABEL_RENAMING_PRODUCT = "Old product name:"
    APP_LABEL_RENAMING_PRODUCT_EDIT = "New product name:"
    APP_LABEL_DELETING = "Deleting"
    APP_LABEL_DELETING_CATEGORY = "category name:"
    APP_LABEL_DELETING_PERSON = "person name:"
    APP_LABEL_DELETING_PRODUCT = "product name:"
    APP_LABEL_MERGING = "Merging"
    APP_LABEL_MERGING_CATEGORY1 = "First category name:"
    APP_LABEL_MERGING_CATEGORY2 = "Second category name:"
    APP_LABEL_MERGING_CATEGORY_EDIT = "New category name:"
    APP_LABEL_MERGING_PERSON1 = "First person name:"
    APP_LABEL_MERGING_PERSON2 = "Second person name:"
    APP_LABEL_MERGING_PERSON_EDIT = "New person name:"
    APP_LABEL_MERGING_PRODUCT1 = "First product name:"
    APP_LABEL_MERGING_PRODUCT2 = "Second product name:"
    APP_LABEL_MERGING_PRODUCT_EDIT = "New product name:"

    #edit mode
    APP_LABEL_EDIT_TRANSACTION = "Edit transaction"
    APP_BUTTON_EDIT_TRANSACTION_SUBMIT = "Save changes"
    APP_BUTTON_EDIT_TRANSACTION_DELETE = "Delete transaction"
    APP_BUTTON_EDIT_TRANSACTION_CANCEL = "Cancel"

    #FilterWindow Strings
    FWINDOW_TITLE = "Filter transactions"
    FWINDOW_ABSOLUTE = "Absolute cashflow"
    FWINDOW_RELATIVE = "Signed cashflow"
    FWINDOW_LABEL = "Filter settings"
    FWINDOW_LABEL_DATE = "Filter by date"
    FWINDOW_LABEL_MIN_DATE = "Minimum Date:"
    FWINDOW_LABEL_MAX_DATE = "Maximum Date:"
    FWINDOW_LABEL_PRODUCT = "Filter by product name"
    FWINDOW_LABEL_PRODUCT_CONTAINS = "Filter by substring:"
    FWINDOW_LABEL_PRODUCT_STARTS = "Filter by start string:"
    FWINDOW_LABEL_CASHFLOW = "Filter by cashflow"
    FWINDOW_LABEL_CASHFLOW_MIN = "Minimum cashflow:"
    FWINDOW_LABEL_CASHFLOW_MAX = "Maximum cashflow:"
    FWINDOW_LABEL_SET_FILTER = "Set filter"
    FWINDOW_LABEL_CATEGORY = "Filter by category"
    FWINDOW_LABEL_PERSON = "Filter by person"

    #CalendarWindow Strings
    CWINDOW_TITLE = "Choose a date"

    #invest tab strings
    INVFORM_LABEL_NEW_INV = "Add new investment"
    INVFORM_LABEL_TICKER = "Yahoo ticker:"
    INVFORM_LABEL_NUMBER = "Number of assets:"
    INVFORM_LABEL_PRICE = "Transaction price:"
    INVFORM_LABEL_PRICE_PER_ASSET = f"Per asset (in {CURRENCY}):"
    INVFORM_LABEL_PRICE_FULL = f"For all assets (in {CURRENCY}):"
    INVFORM_LABEL_FEES = "Other costs and fees:"
    INVFORM_LABEL_TRADINGFEE = f"Trading fees (in {CURRENCY}):"
    INVFORM_LABEL_TAX = f"Taxes (in {CURRENCY}):"
    INVFORM_LABEL_TRADE_TYPE = "Trade type:"
    INVFORM_LABEL_SELECT_STOCK = "Select asset:"
    INVFORM_LABEL_NUMBER_DIV_SHARES = "Number of dividend shares:"
    INVFORM_LABEL_DIVIDEND_RECEIVED = "Dividends received:"
    INVFORM_LABEL_DIVIDEND_PER_SHARE = f"Per share (in {CURRENCY}):"
    INVFORM_LABEL_DIVIDEND_FULL = f"For all shares (in {CURRENCY}):"

    INVFORM_BUTTON_SUBMIT = "Add investment"

    INVFORM_TYPE_BUY = "Buy"
    INVFORM_TYPE_DIVIDEND = "Dividend"
    INVFORM_TYPE_SELL = "Sell"
    

    #tooltips
    TOOLTIP_SUBMIT_BUTTON = "Fill out the form and submit with this button"
    TOOLTIP_TYPE_3_CHARS =  "Type at least 3 characters"
    TOOLTIP_CALENDAR = "Please select the date of the transaction"
    TOOLTIP_CASHFLOW = "Please provide information about the cashflow\nIf you lost money, set sign to minus, if you won choose plus\nYou can enter the cashflow per product or for the whole transaction"
    TOOLTIP_CATEGORY = "You can add some categories to your product\nChoose them on the left side\nIf you wanna add some new ones, use the input field and add button below\nNOTES:\nCategories are case insensitive\nYou can only have one combination of categories per product"
    TOOLTIP_PERSON = "You can add some persons related to that transaction\nChoose them above\nIf you wanna add some new ones, use the input field and add button below\nThere are TWO kinds of persons:\n1.From/To persons: A person who buys/sells the product from/to you\n2.Why persons: without this person, you would not made this transaction \nNOTES:\nPersons are case insensitive"

    FTOOLTIP_MAIN = "You can set the filters for the transactions here\nAll filters are combined using AND\nPress 'set Filter' to save your current filter"
    FTOOLTIP_DATE = "You can set the minimum and maximum dates for the transaction"
    FTOOLTIP_PRODUCT = "You can set filters for the product name of the transaction\nEnter a substring in the first input field that the product name HAS TO contain\nEnter a substring in the second input field that the product name HAS TO start with"
    FTOOLTIP_CASHFLOW = "You can set the lower and upper bound for the transaction's cash flows\nYou can set the bounds for full cashflow or cashflow per product\nIf you set the absolute/signed button to absolute, the filter looks for absolute cashflows\nNOTE:\nThe cashflows per product and full cashflows have to apply BOTH for the transaction"
    FTOOLTIP_CATEGORY = "You can set a category filter\nNOTE:\nAt least ONE category that is selected has to apply on the transaction"
    FTOOLTIP_PERSON = "You can set a person filter\nYou can choose a person that has to be in the from/to persons of the transaction\nYou can choose a why person\nOr a person that needs to show in the from/to OR why persons of the transaction\nNOTE:\nAt least one persons that is selected has to apply on the transaction"


    #questions
    QUESTION_OVERRIDE_OTHER_PRODUCT_CATEGORIES = "Do you wanna override the categories of ALL previous products?"
    QUESTION_TITLE = "Are you sure?"
    QUESTION_DELETING_CATEGORY = "The category will be deleted from the system.\nThis category is getting deleted from all transactions.\nContinue?"
    QUESTION_DELETING_PERSON = "The person will be deleted from the system.\nThis person is getting deleted from all transactions.\nContinue?"
    QUESTION_DELETING_PRODUCT = "The product will be deleted from the system.\nALL TRANSACTIONS with this product will be DELETED.\nContinue?"
    QUESTION_MERGING_CATEGORY = "The two categories will be merged into a new category with the given name.\nThe two categories are DELETED from all transactions and replaced with the new one.\nContinue?"
    QUESTION_MERGING_PERSON = "The two persons will be merged into a new person with the given name.\nThe two persons are DELETED from all transactions and replaced with the new one.\nTHE FIRST PERSON WILL TRANSMIT HIS ATTRIBUTES TO THE NEW PERSON\nContinue?"
    QUESTION_MERGING_PRODUCT = "The two products will be merged into a new product with the given name.\nThe two products are DELETED from all transactions and replaced with the new one.\nTHE CATEGORIES WILL BE TAKED OVER FROM THE FIRST PRODUCT\nContinue?"

    #warning
    WARNING_EXPORT_TRANSACTIONS_TITLE = "WARNING Export transactions"
    WARNING_EXPORT_TRANSACTIONS = "Please note that you only export the transactions.\nSettings, person categories, etc. are NOT saved\nIf you wanna save all data, please #WORK"
    WARNING_IMPORT_TRANSACTIONS_TITLE = "WARNING Import transactions"
    WARNING_IMPORT_TRANSACTIONS = "Please note that all data currently saved in the app could be lost\n All transactions currently stored in the app will be DELETED\nIf you wanna save your old transactions export them first\nYou should also consider to save all data before importing"

    #critical
    CRITICAL_IMPORT_TRANSACTIONS_TITLE = "Error importing transactions"
    CRITICAL_IMPORT_TRANSACTIONS = "Some errors are occured while importing the transactions.\nThe csv file was probably not in the right format\nYour data got lost due to this error, please load your backup (your full data backup) that you have made (hopefully :))"
    CRITICAL_ADD_INVESTMENT_TITLE = "Error while adding the investment"


    #info
    INFO_TRANSACTION_WAS_NOT_ADDED = "The transaction was not added"
    INFO_RENAMED_SUCCESSFUL = "Successful renaming"
    INFO_RENAMED_SUCCESSFUL_PART1 = "The renaming was successful.\n"
    INFO_RENAMED_SUCCESSFUL_CATEGORY_PART2 = "Category "
    INFO_RENAMED_SUCCESSFUL_PERSON_PART2 = "Person "
    INFO_RENAMED_SUCCESSFUL_PRODUCT_PART2 = "Product "
    INFO_RENAMED_SUCCESSFUL_PART3 = " was renamed to "
    INFO_DELETED_SUCCESSFUL = "Successful deletion"
    INFO_DELETED_SUCCESSFUL_PART1 = "The deletion was successful.\n"
    INFO_DELETED_SUCCESSFUL_CATEGORY_PART2 = "Following category was deleted: "
    INFO_DELETED_SUCCESSFUL_PERSON_PART2 = "Following person was deleted: "
    INFO_DELETED_SUCCESSFUL_PRODUCT_PART2 = "Following product was deleted: "
    INFO_MERGED_SUCCESSFUL = "Successful merge"
    INFO_MERGED_SUCCESSFUL_PART1 = "The merge was successful.\n"
    INFO_MERGED_SUCCESSFUL_CATEGORY_PART2 = "Following categories were merged: "
    INFO_MERGED_SUCCESSFUL_PERSON_PART2 = "Following persons were merged: "
    INFO_MERGED_SUCCESSFUL_PRODUCT_PART2 = "Following products were merged: "
    INFO_MERGED_SUCCESSFUL_PART3 = "\nThe new name is: "

    #errors
    ERROR_GRID_NOT_DEFINED = "The basic layout aka 'grid' is not defined. Please make sure to call InitWindow() first"

    ERROR_CONVERT_STRING_TO_INT =  "Could not convert str to int: "
    ERROR_NOT_TYPE_NUM = "The number is not of type int or float: "
    ERROR_CATEGORY_NOT_ACCEPTED = "Category is not accepted"
    ERROR_PERSON_NOT_ACCEPTED = "Person is not accepted"
    ERROR_NO_LAYOUT = "No layout set. Set a layout with setLayout() first"
    ERROR_TOO_MANY_COMBOS = "You tried to add a ComboBox, but the maximum was reached (current boxes, maximum): "
    ERROR_NO_BOXES = "No items to get, sort or reset, because there are no boxes. Please add a box first"
    ERROR_CHOOSED_TEXT_NOT_IN_ITEMS = "The choosed item in the ComboBox is not in the items list: "
    ERROR_INPUT_NOT_IN_INPUTDICT = "Input is not in input dict (input): "
    ERROR_DATE_OUT_OF_RANGE = "The provided date is in the future or too far in the past: "
    ERROR_PRODUCT_CONTAINS_NO_CHAR = "The product contains no visible characters: "
    ERROR_CATEGORY_CONTAINS_NOT_ENOUGH_CHAR = "The category contains less than 3 visible characters: "
    ERROR_PERSON_CONTAINS_NOT_ENOUGH_CHAR = "The person contains less than 3 visible characters: "
    ERROR_PRODUCT_CONTAINS_NOT_ENOUGH_CHAR = "The product contains less than 1 visible characters: "
    ERROR_NUMBER_ZERO_OR_LESS = "The number of products/assets is not greater than zero: "
    ERROR_PRICE_ZERO_OR_LESS = "The price of the asset is not greater than zero: "
    ERROR_TRADINGFEE_LESS_ZERO = "The tradingfee is below zero: "
    ERROR_TAX_LESS_ZERO = "The tax is below zero: "
    ERROR_CASHFLOW_ZERO = "The given Cashflow is zero: "
    ERROR_NOT_ALL_CATEGORIES_ARE_VALID = "There are some categories, which are not in the database: "
    ERROR_NOT_ALL_FTPERSONS_ARE_VALID = "There are some from/to persons, which are not in the database: "
    ERROR_NOT_ALL_WHYPERSONS_ARE_VALID = "There are some why persons, which are not in the database: "
    ERROR_GEOMETRY_LESS_ZERO = "Not all values in geometry are greater than zero: "
    ERROR_PRODUCT_CATEGORIES_DONT_MATCH = "product categories dont match with the previous products"
    ERROR_CATEGORY_NOT_UNIQUE = "There are two or more non unique categories choosen: "
    ERROR_FTPERSON_NOT_UNIQUE = "There are two or more non unique from/to persons choosen: "
    ERROR_WHYPERSON_NOT_UNIQUE = "There are two or more non unique why persons choosen: "
    ERROR_NOT_KNOWN_FTPERSON_CHOOSEN = "The user choosed a from/to person not known to the system: "
    ERROR_NOT_KNOWN_WHYPERSON_CHOOSEN = "The user choosedall qtwidgets a why person not known to the system: "
    ERROR_PRODUCT_ALREADY_KNOWN = "The product that should be added is already known to the system: "
    ERROR_NO_PRODUCT_FOUND = "No product found with name: "
    ERROR_BUTTON_NOT_FOUND = "The provided button is not found in the button list"
    ERROR_TRANSACTION_OUT_OF_RANGE = "the transaction index is out of range, should be as long as buttons"
    ERROR_NOT_IN_EDIT_MODE = "The action cannot be done because the window is not in edit mode"
    ERROR_IN_EDIT_MODE = "The action cannot be done because the window is in edit mode"
    ERROR_NO_TRANSACTION_BUTTON_SET = "There is no active transaction button set"
    ERROR_TRANSACTION_NOT_IN_LIST = "The given transaction is not found in the transaction list: "
    ERROR_SENDER_NOT_IN_SORT_BUTTONS = "The sender button is not part of the sort button list"
    ERROR_SORTELEMENT_OUT_OF_RANGE = "The sort element has some invalid data or is out of range: "
    ERROR_TOOLTIPS_ALREADY_SET = "The tooltips are already set"
    ERROR_NO_DATE_SELECTED = "No date has been selected"
    ERROR_CATEGORY_NOT_FOUND = "The provided category is not known to the system"
    ERROR_PERSON_NOT_FOUND = "The provided person is not known to the system"
    ERROR_PRODUCT_NOT_FOUND = "The provided product is not known to the system"
    ERROR_TRADE_TYPE_NOT_VALID = "The selected trade type is not valid: "

    ERROR_WRONG_CF_DATA = "Got wrong cashflow data: "
    ERROR_WRONG_FORMAT_GEOMETRY = "geometry is in a wrong format: "
    ERROR_WRONG_SENDER_TYPE = "The slot is connected to the wrong type (slot, type): "
    ERROR_WRONG_SENDER = "The slot is connected to the wrong sender (slot, sender): "
    ERROR_WRONG_SIGN_CONTENT = "The content of sign is not valid. Should be: "+APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS+" or "+APP_LABEL_NEW_TRANSACTION_CF_SIGN_PLUS+" but its: "
    ERROR_WRONG_PRODUCT_NAME_FORMAT = "The provided product name is not lowercase: "
    ERROR_WRONG_DATA_LENGTH = "The data given to the backend has the wrong length: "