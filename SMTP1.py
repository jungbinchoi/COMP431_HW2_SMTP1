# Jungbin Choi
# I pledge to the COMP 431 Honor Code


import sys
import os


# Globals
string: str = ''
value: str = ''
index: int = 0
error: str = ''
forward: str = []
reverse: str = ''
data: str = []


# Constants
ZERO_ASCII = 48
NINE_ASCII = 57
UPPER_A_ASCII = 65
UPPER_Z_ASCII = 90
LOWER_A_ASCII = 97
LOWER_Z_ASCII = 122
ERROR500 = "500 Syntax error: command unrecognized"
ERROR501 = "501 Syntax error in parameters or arguments"
ERROR503 = "503 Bad sequence of commands"
DATA354 = "354 Start mail input; end with <CRLF>.<CRLF>"
OK250 = "250 OK"


def main():
    global string, value, index, error, reverse, forward, data
    data_fail: bool = False
    try:
        while True:
            error = ''
            index = 0

            string = sys.stdin.readline()
            sys.stdout.write(string)
            data_fail = False

            value = string[index]

            reverse = ''
            forward.clear()
            data.clear()

            if mail_from_cmd():
                print(OK250)

                at_least_one: bool = False
                while True:
                    index = 0

                    string = sys.stdin.readline()
                    sys.stdout.write(string)

                    value = string[index]

                    if rcpt_to_cmd():
                        at_least_one = True
                        print(OK250)
                    else:
                        index = 0
                        value = string[index]
                        error = ''
                        if mail_from_cmd() or error == ERROR501:
                            error = ERROR503
                            break
                        else:
                            index = 0
                            value = string[index]
                            error = ''
                            if at_least_one and data_cmd():
                                print(DATA354)

                                data.append("From: <" + reverse + ">\n")

                                for path in forward:
                                    data.append("To: <" + path + ">\n")

                                while True:
                                    message: str = sys.stdin.readline()
                                    if message == '':
                                        data_fail = True
                                        raise EOFError
                                    sys.stdout.write(message)
                                    if message != '.\n':
                                        data.append(message)
                                    else:
                                        break

                                for path in forward:
                                    full_path: str = "./forward/" + path
                                    if os.path.exists(full_path):
                                        with open(full_path, 'at') as message:
                                            message.writelines(data)
                                    else:
                                        with open(full_path, 'xt') as message:
                                            message.writelines(data)

                                print(OK250)
                                break
                            else:
                                index = 0
                                value = string[index]
                                error = ''
                                if ((not at_least_one) and data_cmd()) or error == ERROR501:
                                    error = ERROR503
                                    break
                                else:
                                    index = 0
                                    value = string[index]
                                    error = ''
                                    rcpt_to_cmd()
                                    break

                if error != '':
                    print(error)
            else:
                index = 0
                value = string[index]
                error = ''
                if rcpt_to_cmd() or error == ERROR501:
                    error = ERROR503
                else:
                    index = 0
                    value = string[index]
                    error = ''
                    if data_cmd() or error == ERROR501:
                        error = ERROR503
                    else:
                        index = 0
                        value = string[index]
                        error = ''
                        mail_from_cmd()

                print(error)

    except (EOFError, IndexError):
        if data_fail:
            print(ERROR501)
        return


"""
    Checks the MAIL FROM Command

    * Generates 500/501 Error
"""
def mail_from_cmd():
    global value, string, index, error, reverse
    for char in "MAIL":
        if char != value:
            error = "500 Syntax error: command unrecognized"
            return False
        index += 1
        value = string[index]

    if not whitespace():
        error = "500 Syntax error: command unrecognized"
        return False

    for char in "FROM:":
        if char != value:
            error = "500 Syntax error: command unrecognized"
            return False
        index += 1
        value = string[index]

    if not nullspace():
        return False

    if not reverse_path():
        return False
    index += 1
    value = string[index]

    if not nullspace():
        return False

    if not CRLF():
        return False

    # Saving reverse path
    begin_index: int = 0
    end_index: int = 0
    temp_index: int = 0
    for char in string:
        if char == '<':
            begin_index = temp_index + 1
        elif char == '>':
            end_index = temp_index
        temp_index += 1
    reverse = string[begin_index:end_index]

    return True


"""
    Checks the RCPT TO Command

    * Generates 500/501 Error
"""
def rcpt_to_cmd():
    global value, string, index, error, forward
    for char in "RCPT":
        if char != value:
            error = "500 Syntax error: command unrecognized"
            return False
        index += 1
        value = string[index]

    if not whitespace():
        error = "500 Syntax error: command unrecognized"
        return False

    for char in "TO:":
        if char != value:
            error = "500 Syntax error: command unrecognized"
            return False
        index += 1
        value = string[index]

    if not nullspace():
        return False

    if not forward_path():
        return False
    index += 1
    value = string[index]

    if not nullspace():
        return False

    if not CRLF():
        return False

    begin_index: int = 0
    end_index: int = 0
    temp_index: int = 0
    for char in string:
        if char == '<':
            begin_index = temp_index + 1
        elif char == '>':
            end_index = temp_index
        temp_index += 1
    forward.append(string[begin_index:end_index])

    return True


"""
    Checks the DATA Command

    * Generates 500/501 Error
"""
def data_cmd():
    global value, string, index, error
    for char in "DATA":
        if char != value:
            error = "500 Syntax error: command unrecognized"
            return False
        index += 1
        value = string[index]

    if not nullspace():
        return False

    if not CRLF():
        return False

    return True


"""
    Checks if the value is a whitespace or is a part of a whitespace

    * Generates 501 Error
"""
def whitespace():
    global value, error, index, string
    if not space():
        if error == '':
            error = "501 Syntax error in parameters or arguments"
        return False
    index += 1
    value = string[index]

    if not whitespace():
        error = ''

    return True


"""
    Checks if the character is a space or a tab
"""
def space():
    global value
    return ((value == ' ') or (value == '\t'))


"""
    Checks if the value is a null or is a whitespace
"""
def nullspace():
    global value, error
    if not whitespace():
        if not null():
            error = ''
            return True
        return False

    return True


"""
    Checks if the value is null
"""
def null():
    global value
    return value == ''


"""
    Checks if the reverse path is a valid path
"""
def reverse_path():
    return path()


"""
    Checks if the foward path is a valid path
"""
def forward_path():
    return path()


"""
    Checks the path

    * Generates 501 Error
"""
def path():
    global string, index, value, error
    if value != '<':
        if error == '':
            error = "501 Syntax error in parameters or arguments"
        return False
    index += 1
    value = string[index]

    if not mailbox():
        return False

    if value != '>':
        if error == '':
            error = "501 Syntax error in parameters or arguments"
        return False

    return True


"""
    Checks the mailbox

    * Generates 501 Error
"""
def mailbox():
    global string, index, value, error
    if not local_part():
        if error == '':
            error = "501 Syntax error in parameters or arguments"
        return False

    if value != '@':
        if error == '':
            error = "501 Syntax error in parameters or arguments"
        return False
    index += 1
    value = string[index]

    if not domain():
        if error == '':
            error = "501 Syntax error in parameters or arguments"
        return False

    return True


"""
    Checks if the local part is a string
"""
def local_part():
    return string_func()


"""
    Checks if it's a string

    * Generates 501 Error
"""
def string_func():
    global value, string, index, error
    if not char():
        if error == '':
            error = "501 Syntax error in parameters or arguments"
        return False
    index += 1
    value = string[index]

    if not string_func():
        error = ''

    return True


"""
    Checks if the current value is a regular character i.e. not a spaceial char or space/tab
"""
def char():
    return not (space() or special())


"""
    Checks for the domain name
"""
def domain():
    global string, index, value
    if not element():
        return False

    if value == '.':
        index += 1
        value = string[index]
        return domain()

    return True


"""
    Checks if the element is a single character of is a name

    * Generates 501 Error
"""
def element():
    global value, string, index, error
    if not name():
        if error == '':
            error = "501 Syntax error in parameters or arguments"
        return False

    return True


"""
    Checks if the name is a series of letters
"""
def name():
    global value, string, index
    if not letter():
        return False
    index += 1
    value = string[index]

    let_dig_str()

    return True


"""
    Checks if the character is a letter using the character's ASCII
"""
def letter():
    global value
    ascii_value = ord(value)

    return (((ascii_value >= UPPER_A_ASCII) and (ascii_value <= UPPER_Z_ASCII)) or ((ascii_value >= LOWER_A_ASCII) and (ascii_value <= LOWER_Z_ASCII)))


"""
    Checks if the given string is a letter, digit or a string
"""
def let_dig_str():
    global value, string, index
    if not let_dig():
        return False
    index += 1
    value = string[index]

    let_dig_str()

    return True


"""
    Checks if the character is a letter or a digit
"""
def let_dig():
    return (letter() or digit())


"""
    Checks if the character is decimal digit
"""
def digit():
    global value
    ascii_value = ord(value)

    return ((ascii_value >= ZERO_ASCII) and (ascii_value <= NINE_ASCII))


"""
    Checks if the character is a newline

    * Generates 501 Error
"""
def CRLF():
    global value, error
    if value != '\n':
        if error == '':
            error = "501 Syntax error in parameters or arguments"
        return False

    return True


"""
    Checks if the character is a special character
"""
def special():
    global value
    spec_char: str = ['<', '>', '(', ')', '[', ']', '\\', '.', ',', ';', ':', '@', '\"']

    return value in spec_char


main()