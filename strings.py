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
    APP_NEW_TRANSACTION_CASHFLOW_INPUT = "product"

    COMMA = "."
    COMMAS = [".", ","]
    ZERO_STRINGS = ["", " ", "."]

    #tooltips
    TOOLTIP_SUBMIT_BUTTON = "Fill out the form and submit with this button"
    TOOLTIP_TYPE_3_CHARS =  "Type at least 3 characters"

    #errors
    ERROR_CONVERT_STRING_TO_INT =  "Could not convert str to int: "
    ERROR_CATEGORY_NOT_ACCEPTED = "Category is not accepted"
    ERROR_PERSON_NOT_ACCEPTED = "Person is not accepted"
    ERROR_WRONG_CF_DATA = "got wrong cashflow data: "
