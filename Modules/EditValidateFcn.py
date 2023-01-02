def edit_str_to_value(messagePart, editStr):
    """Function for converting the edit text to value
       Error codes: 0 - no error, 1 - not a number, 2 - negative, 3 - zero"""
    value = None
    errorText = None
    editStr = editStr.replace(',', '.')  # Symbol ',' is also available
    errorCode = 0
    try:
        value = float(editStr)
    except:
        errorCode = 1
    # Check the different situations
    if errorCode == 1:
        errorText = '{0} should be a number!'.format(messagePart)
        return value, errorCode, errorText
    if value < 0:
        errorCode = 2
        errorText = '{0} should be a positive number!'.format(messagePart)
    if value == 0:
        errorCode = 3
        errorText = '{0} can not be a zero!'.format(messagePart)
    return value, errorCode, errorText
