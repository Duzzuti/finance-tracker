class ENG:
    def getTypeErrorString(arg, arg_name,  _type):
        return f"The argument '{arg_name}' is not of type {_type}: {arg}"

    def getListTypeErrorString(arg, arg_name, inner_type):
        return f"The list '{arg_name}' is not of type list or/and the contents are not of type {inner_type}: {arg}"


    #META Strings
    CURRENCY = "€"
    COMMA = "."
    COMMAS = [".", ","]
    ZERO_STRINGS = ["", " ", "."]

    #Main Window Strings
    APP_TITLE = "Finance tracker"
    APP_ICON = "media/icon.png"
    
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

    APP_LABEL_LAST_TRANSACTIONS = "Your last transactions"

    APP_BUTTON_NEW_TRANSACTION_ADD_CAT = "Add"
    APP_BUTTON_NEW_TRANSACTION_RESET_CAT = "Reset Categories"
    APP_BUTTON_NEW_TRANSACTION_ADD_PERSON_WHYP = "Add why person"
    APP_BUTTON_NEW_TRANSACTION_ADD_PERSON_FTP = "Add from/to person"
    APP_BUTTON_NEW_TRANSACTION_RESET_PERSON = "Reset persons"
    APP_BUTTON_NEW_TRANSACTION_SUBMIT = "Add transaction"

    APP_BUTTON_LAST_TRANSACTIONS_DATE = "Date "
    APP_BUTTON_LAST_TRANSACTIONS_CASHFLOW = "Cashflow "
    APP_BUTTON_LAST_TRANSACTIONS_PRODUCT = "Product "

    APP_NEW_TRANSACTION_DEFAULT_CATEGORY = "Without category"
    APP_NEW_TRANSACTION_DEFAULT_FTPERSON = "No from/to person"
    APP_NEW_TRANSACTION_DEFAULT_WHYPERSON = "No why person"
    APP_NEW_TRANSACTION_DEFAULT_PERSON = "No person"

    APP_NEW_TRANSACTION_PRODUCT_INPUT = "product"
    APP_NEW_TRANSACTION_CASHFLOW_INPUT = "cashflow"

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

    #CalendarWindow Strings
    CWINDOW_TITLE = "Choose a date"

    #tooltips
    TOOLTIP_SUBMIT_BUTTON = "Fill out the form and submit with this button"
    TOOLTIP_TYPE_3_CHARS =  "Type at least 3 characters"
    TOOLTIP_CALENDAR = "Please select the date of the transaction"
    TOOLTIP_CASHFLOW = "Please provide information about the cashflow\nIf you lost money, set sign to minus, if you won choose plus\nYou can enter the cashflow per product or for the whole transaction"
    TOOLTIP_CATEGORY = "You can add some categories to your product\nChoose them on the left side\nIf you wanna add some new ones, use the input field and add button below\nNOTES:\nCategories are case insensitive\nYou can only have one combination of categories per product"
    TOOLTIP_PERSON = "You can add some persons related to that transaction\nChoose them above\nIf you wanna add some new ones, use the input field and add button below\nThere are TWO kinds of persons:\n1.From/To persons: A person who buys/sells the product from/to you\n2.Why persons: without this person, you would not made this transaction \nNOTES:\nPersons are case insensitive"

    #questions
    QUESTION_OVERRIDE_OTHER_PRODUCT_CATEGORIES = "Do you wanna override the categories of ALL previous products?"

    #info
    INFO_TRANSACTION_WAS_NOT_ADDED = "The transaction was not added"

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
    ERROR_NUMBER_ZERO_OR_LESS = "The number of products is not greater than zero: "
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

    ERROR_WRONG_CF_DATA = "Got wrong cashflow data: "
    ERROR_WRONG_FORMAT_GEOMETRY = "geometry is in a wrong format: "
    ERROR_WRONG_SENDER_TYPE = "The slot is connected to the wrong type (slot, type): "
    ERROR_WRONG_SENDER = "The slot is connected to the wrong sender (slot, sender): "
    ERROR_WRONG_SIGN_CONTENT = "The content of sign is not valid. Should be: "+APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS+" or "+APP_LABEL_NEW_TRANSACTION_CF_SIGN_PLUS+" but its: "
    ERROR_WRONG_PRODUCT_NAME_FORMAT = "The provided product name is not lowercase: "