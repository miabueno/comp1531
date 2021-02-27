"""

Implemented by Yue (Yuelanda) Dai (zid: z5310546)
24, Sep, 2020 - 03, Oct, 2020

"""

# libraies
import hashlib
import jwt
import string
import re
from random import choice

# libraies for emails
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import imaplib
import email

# src files
import error as err
from users_channels import users, SECRET


# ---------------------------------------------------------------------------------------- #
# ----------------------------------- helper functions ----------------------------------- #
# ---------------------------------------------------------------------------------------- #

def test_email(email):
    """ To test if a provided email is a valid email or not.
        Invalid emails are assumed to be string that do not contain the @ symbol
        Using similar method provided in the website:
        https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
        Note that slight changes are made to the regex.

    Parameters:
        email (str): the string of characters as the email of the user

    Returns:
        (bool): whether or not the email is a valid email
    """

    regex = r'^[a-zA-Z0-9]+([\._]?[a-zA-Z0-9]+)+[@](\w+[.])+\w{2,3}$'

    return re.search(regex, email) is not None


def handle_generate(name_first, name_last):
    """ Generates a handle from the user's first name and last name

    Parameters:
        name_first (str): first name of the user
        name_last (str): last name of the user

    Returns:
        handle (str): concatentation of a lowercase-only first name and last name
                      The last two characters in the handle is reserved for
                      numerical values to make each handle unique.
    """

    handle = name_first.lower() + name_last.lower()
    if len(handle) >= 19:
        handle = handle[:18]

    # handle = handle + '0'
    handle += '0'

    for u_id in users:
        if users[u_id].get('username') == handle:
            last = int(handle[-1]) + 1
            handle = handle[:-1] + str(last)

    return handle


def password_encryption(password):
    """ Encrypts user's password for security reasons in stroing data
        with hashing.

    Parameter:
        password (str): user's actual password before encryption

    Return: user's encrypted password
    """

    return hashlib.sha256(password.encode()).hexdigest()


def token_encryption(email):
    """ Encrypts user's token for authentication using jwt method.
        The token is generated from the user's email and SECRET stored
        as a global variable in users_channel.py

    Parameter:
        email (str): email of the user

    Return: authenticated token that is encrypted
    """

    byte_str = jwt.encode({'email': email}, SECRET, algorithm='HS256')
    return byte_str.decode()


def token_decryption(token):
    """ Decrypts user's token back to the email of the user using
        the jwt method with token and SECRET.
        Assumption is made that if the token is an empty string, then
        it is an invalid token

    Parameter:
        token: the token of the user

    Return: the email of the user
    """

    encoded = token.encode()
    decrypted = jwt.decode(encoded, SECRET, algorithms=['HS256'])
    return decrypted['email']


def generate_reset_code(email):
    """ Generate/ Create reset_code that is the same length as the user's password,
        with a combination of uppercase, lowercase letters and digits.

    Parameter:
        email (str): email of the user requesting the reset_code

    Return:
        reset_code (str): reset_code that is going to be sent as the content to the email.
    """

    length = int
    uid = str
    is_user_email = False
    for u_id, user in users.items():
        if user['email'] == email:
            is_user_email = True
            length = len(user['password'])
            uid = str(u_id)

    if not is_user_email:
        raise err.AccessError(f"Error, {email} is not a registered email.")

    # Assumption: secret_code is a fixed string 'RS' followed by the user's uid then '-', finally the
    # randomly generated stringt that is of the same length of the user's orginal encrypted password.
    choices = string.digits + string.ascii_letters
    random_str = ''.join((choice(choices) for i in range(length)))
    secret_code = 'RS' + uid + '-' + random_str
    return u_id, secret_code


def send_email(target_email, SECRET_CODE):
    """
    Send email using Python to the target_email with body message SECRET_CODE

    Parameters:
        target_email (str): target email address
        SECRET_CODE (str): randomly generated alphanumeric string

    Written by Yiyang Huang. Modified by Yue Dai.
    """

    # Header
    __ = "smtp.gmail.com"
    mail_pass = "Flockr-COMP1531"
    sent_from = target_email

    # Content
    subject = 'Flockr: Reset Password'
    mail_body = f'Security code: {SECRET_CODE}'
    mail_message = f'''
    From: {sent_from}
    To: {target_email}
    Subject: {subject}

    {mail_body}
    '''

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(sent_from, mail_pass)
    server.sendmail(sent_from, target_email, mail_message)
    server.close()


# ---------------------------------------------------------------------------------------- #
# ------------------------------------- auth functions ----------------------------------- #
# ---------------------------------------------------------------------------------------- #


def auth_login(email, password):
    """ Allows the users to login with valid email and valid password

    Parameters:
        email (str): email of the user requesting to login
        password (str): password provided by the user with the corresponding email

    Returns:
        u_id (int): the user id to the corresponding user logged in
        token (str): assumed to be the email of the user in iteration 1, an authentication tool
    """
    
    if not test_email(email): # Invalid email
        raise err.InputError(f"Error, invalid email: {email}")
    
    for u_id in users:
        if users[u_id].get('email') == email:
            encripted_pw = password_encryption(password)
            if users[u_id].get('password') != encripted_pw:
                # Password is not correct
                raise err.InputError("Incorrect password")
            users[u_id]['token'] = email
            # Correct email and password
            return {
                'u_id': u_id,
                'token': token_encryption(email),
            }

    # Email entered does not belong to a user
    raise err.InputError(f"Email: {email} does not belong to a user")


def auth_logout(token):
    """ Invalidates the token to sucessfully log the authenticated user out.

    Parameters:
        token (str): assumed to be the email of the user in iteration 1, an authentication tool

    Returns:
        (bool): return whether or not the authenticated user is successfully logged out.
    """

    decrypted_token = token_decryption(token)
    # In iteration_1 the token is the email of the logged in user.
    for u_id in users:
        if users[u_id].get('token') == decrypted_token: # token is valid
            # Invalidate the token as an empty string to log the user out
            users[u_id]['token'] = ''
            return {'is_success': True}
    return {'is_success': False}


def auth_register(email, password, name_first, name_last):
    """ Given a new/unregistered email, check all execptions, and store the
        new user details in the data structure (user dictionary)
        and generate a handle as the username of the user.

    Parameters:
        email (str): email of the user requesting to login
        password (str): password provided by the user with the corresponding email
        name_first (str): first name of the user
        name_last (str): last name of the user

    Returns:
        u_id (int): the user id to the corresponding user logged in
        token (str): assumed to be the email of the user in iteration 1, an authentication tool
                     the token returned is the same token as returned from auth_login function
    """
    
    if not test_email(email): # Invalid email
        raise err.InputError(f"Invalid email: {email}")
    
    # Email address is already being used by another user
    u_id = 0
    for u_id in users:
        if users[u_id].get('email') == email:
            raise err.InputError(f"Error, {email} already used by another user")
    # u_id += 1
    u_id = len(users)
    
    # Password entered is less than 6 characters long
    if len(password) < 6:
        raise err.InputError("Password entered is less than 6 characters long")
    
    # name_first not is between 1 and 50 characters in length
    if len(name_first) < 1 or len(name_first) > 50:
        raise err.InputError("name_first not is between 1 and 50 characters in length")

    # name_last not is between 1 and 50 characters in length
    if len(name_last) < 1 or len(name_last) > 50:
        raise err.InputError("name_last not is between 1 and 50 characters in length")

    # Set permission_id for each member
    # 1 for the first user register (owner), and 2 for the rest (member)
    if u_id == 0:
        permission_id = 1
    else:
        permission_id = 2

    # New user
    users[u_id] = {
        'username': handle_generate(name_first, name_last),
        'token': email,
        'name_first': name_first,
        'name_last': name_last,
        'email': email,
        'password': password_encryption(password),
        'reset_code': '',
        'permission_id': permission_id,
        'in_channels': [],
        'msg_sent': [],
        'profile_img_url': '',
    }

    # Assume automatic login after registration.
    # The token returned for auth_register is the same token returned from auth_login
    dictionary = auth_login(email, password)
    return {
        'u_id': u_id,
        'token': dictionary['token'],
    }


def auth_passwordreset_request(email):
    """ To ensure that the user who intend to reset the pasword is the user
        of the registered email.
        Wrapper around passwordreset_request_return_secret_code, discarding the
        return value.

    Parameter:
        email (str): email linked to the account of the user who intend to reset the password.

    Return: {}
    """

    u_id, secret_code = generate_reset_code(email)
    # store the reset_code (secret_code) into the users database.

    users[u_id]['reset_code'] = secret_code

    send_email(email, secret_code)
    return {}


def auth_passwordreset_reset(reset_code, newpassword):
    """ Given the valid reset_code, reset to a new password to the user account

    Parameter:
        reset_code (str): the secret code that is sent to the user email
        newpassword: the password that is going to replace the old password

    Return: {}
    """

    # newpassword entered is less than 6 characters long
    if len(newpassword) < 6:
        raise err.InputError("Invalid password: password entered is less than 6 characters long")

    # store new password into the users dictionary
    reseted = False
    for u_id in users:
        if users[u_id].get('reset_code') == reset_code:
            users[u_id]['password'] = password_encryption(newpassword)
            reseted = True

    if not reseted:
        raise err.InputError("Incorrect reset code")

    return {}
