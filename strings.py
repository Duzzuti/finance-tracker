class ENG:
    APP_TITLE = "Finance tracker"
    APP_ICON = "media/icon.png"
    
    APP_LABEL_NEW_TRANSACTION = "Add new transaction"
    APP_LABEL_NEW_TRANSACTION_CF = "Enter the gain or loss of the transaction:"
    APP_LABEL_NEW_TRANSACTION_CF_PP = "Per product (in €):"
    APP_LABEL_NEW_TRANSACTION_CF_FULL = "For the full transaction (in €):"
    APP_LABEL_NEW_TRANSACTION_CF_SIGN = "Sign:"
    APP_LABEL_NEW_TRANSACTION_CF_SIGN_PLUS = "+ (Gain)"
    APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS = "- (Loss)"
    APP_LABEL_NEW_TRANSACTION_PRODUCT = "Enter the name of the product:"
    APP_LABEL_NEW_TRANSACTION_CAT = "Add a new category:"
    APP_LABEL_NEW_TRANSACTION_NUMBER = "Number of products:"
    APP_LABEL_NEW_TRANSACTION_PERSON = "Add a new person:"
    
    APP_BUTTON_NEW_TRANSACTION_ADD_CAT = "Add"
    APP_BUTTON_NEW_TRANSACTION_RESET_CAT = "Reset Categories"
    APP_BUTTON_NEW_TRANSACTION_ADD_PERSON_WHYP = "Add why person"
    APP_BUTTON_NEW_TRANSACTION_ADD_PERSON_FTP = "Add from/to person"
    APP_BUTTON_NEW_TRANSACTION_RESET_PERSON = "Reset persons"
    APP_BUTTON_NEW_TRANSACTION_SUBMIT = "Add transaction"

    APP_NEW_TRANSACTION_DEFAULT_CATEGORY = "Without category"
    APP_NEW_TRANSACTION_DEFAULT_FTPERSON = "No from/to person"
    APP_NEW_TRANSACTION_DEFAULT_WHYPERSON = "No why person"

    APP_NEW_TRANSACTION_PRODUCT_INPUT = "product"
    APP_NEW_TRANSACTION_CASHFLOW_INPUT = "cashflow"

    COMMA = "."
    COMMAS = [".", ","]
    ZERO_STRINGS = ["", " ", "."]

    #tooltips
    TOOLTIP_SUBMIT_BUTTON = "Fill out the form and submit with this button"
    TOOLTIP_TYPE_3_CHARS =  "Type at least 3 characters"

    #errors
    ERROR_CONVERT_STRING_TO_INT =  "Could not convert str to int: "
    ERROR_NOT_TYPE_NUM = "The number is not of type int or float: "
    ERROR_CATEGORY_NOT_ACCEPTED = "Category is not accepted"
    ERROR_PERSON_NOT_ACCEPTED = "Person is not accepted"
    ERROR_NO_LAYOUT = "No layout set. Set a layout with setLayout() first"
    ERROR_TOO_MANY_COMBOS = "You tried to add a ComboBox, but the maximum was reached (current boxxes, maximum): "
    ERROR_NO_BOXES = "No items to get, sort or reset, because there are no boxes. Please add a box first"
    ERROR_CHOOSED_TEXT_NOT_IN_ITEMS = "The choosed item in the ComboBox is not in the items list: "
    ERROR_INPUT_NOT_IN_INPUTDICT = "Input is not in input dict (input): "

    ERROR_WRONG_CF_DATA = "Got wrong cashflow data: "
    ERROR_WRONG_FORMAT_GEOMETRY = "geometry is in a wrong format: "
    ERROR_WRONG_SENDER_TYPE = "The slot is connected to the wrong type (slot, type): "
    ERROR_WRONG_SENDER = "The slot is connected to the wrong sender (slot, sender): "
    ERROR_WRONG_SIGN_CONTENT = "The content of sign is not valid. Should be: "+APP_LABEL_NEW_TRANSACTION_CF_SIGN_MINUS+" or "+APP_LABEL_NEW_TRANSACTION_CF_SIGN_PLUS+" but its: "
    ERROR_WRONG_DEFAULT_ITEM_TYPE = "The default item is not of type str: "
    ERROR_WRONG_ITEM_TYPE = "The item is not of type str: "
    ERROR_WRONG_SET_ITEM_TYPE = "The 'set_item' argument is not of type bool: "
    ERROR_WRONG_EVENT_FUNC_TYPE = "The event function is not of type function: "
    ERROR_WRONG_GET_ITEMS_FUNC_TYPE = "The item getter function is not of type function: "
    ERROR_WRONG_TRUE_FUNC_TYPE = "The argument 'true_func' is not of type function: "
    ERROR_WRONG_FALSE_FUNC_TYPE = "The argument 'false_func' is not of type function: "
    ERROR_WRONG_INPUT_ARG_TYPE = "The argument 'input' is not of type str: "
    ERROR_WRONG_INPUT_ARG_TYPE = "The argument 'status' is not of type bool: "
    ERROR_WRONG_LAYOUT_TYPE = "The layout is not of type QLayout: "
    ERROR_WRONG_DEFAULT_ARG_TYPE = "The argument 'default' is not of type bool: "
    ERROR_WRONG_RETURN_ITEMS_TYPE = "The list 'items' is not of type list or/and the contents are not of type str: "
    ERROR_WRONG_RETURN_RES_TYPE = "The list 'res' is not of type list or/and the contents are not of type str: "
    ERROR_WRONG_INPUT_LIST_TYPE = "The list 'input_list' is not of type list or/and the contents are not of type str: "
    ERROR_WRONG_ARG_SORT_TYPE = "The argument 'sort' is not of type bool: "