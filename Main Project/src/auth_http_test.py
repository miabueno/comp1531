"""
Created by Yue (Yuelanda) Dai (z5310546)
22/10/2020 - 25/10/2020

Integration tests for testing http routes for auth.py
Tests only handles normal http behaviours and error checkings.
Functionality tests and edge case handlings for each targeted
feature is done in auth_test.py.

Reviewed by Yiyang (Sophia) Huang (z5313425)
05/11/2020

"""


# import json
import requests
import pytest

# emails
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import imaplib
import email

# ------------------------------------------------------------------------------------------------- #
# --------------------------------- http tests for auth/login ------------------------------------- #
# ------------------------------------------------------------------------------------------------- #

def test_auth_login_normal_behaviour(urls, data_setup, auth_register_setup):
    """ Test normal http behaviour of auth_login method.
        Regsiter the first user (owner of entire flockr) and test if
        the returned string matches with the return by directly caling
        auth_login.
    """

    # call pytest fixture login to register and log in new users.
    user_http = auth_register_setup[1]
    # call pytest fixture exptected values for expected output for
    # auth_login function.
    data = {
        "email": data_setup[1]['email'],
        "password": data_setup[1]['password']
    }
    user_login = requests.post(urls['auth_login'], json=data).json()

    assert user_http == user_login


def test_auth_login_input_error(urls, auth_register_setup, data_setup):
    """ Test raising InputError for http.
        There are more than one way to raise InputErrors in auth_login.
        See detailed test cases in unit testings in auth_test.py.
        This test uses incorrect password to raise InputError. Other InputErrors include:
            - Email entered does not belong to an user.
            - Entered invalid email.

        Return: InputError
    """

    user_data = data_setup[1]

    data = {
        "email": user_data['email'],
        "password": "invalidPassword"
    }

    response = requests.post(urls['auth_login'], json=data)
    assert response.status_code == 400


# ------------------------------------------------------------------------------------------------- #
# --------------------------------- http tests for auth/logout ------------------------------------ #
# ------------------------------------------------------------------------------------------------- #

def test_auth_logout_success(urls, auth_register_setup):
    """ Test normal http behaviour of auth_logout method when
        authenticated token is passed in.
        Regsiter the first user (owner of entire flockr) and test if
        the returned string matches with the return by directly caling
        auth_logout.
    """

    owner = auth_register_setup[0]
    data = {
        "token": owner['token']
    }

    response = requests.post(urls['auth_logout'], json=data).json()

    assert response == {"is_success": True}


def test_auth_logout_failed(urls, auth_register_setup):
    """ Test normal http behaviour of auth_logout method when
        invalid token is passed in.
        Regsiter the first user (owner of entire flockr) and test if
        the returned string matches with the return by directly caling
        auth_logout.
    """

    # jwt form of {email: ''}, where the token is an empty string.
    # Asuumption are made that token are invalidated with empty string.
    data = {
        "token": 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                 'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'
    }

    response = requests.post(urls['auth_logout'], json=data).json()

    assert response == {'is_success': False}


# ------------------------------------------------------------------------------------------------- #
# ------------------------ http tests for auth/passwordreset/request ------------------------------ #
# ------------------------------------------------------------------------------------------------- #


def test_auth_passwordreset_request_normal_behaviour(urls, auth_register_setup, data_setup, auth_passwordreset_setup):
    """ Given a email, sends a secret code to the email that user can enter in the
        front-end, to ensure that the user who is resetting the password is the
        user with that email.
        Not completely black-box testing as the definition of secret_code in groups vary, also
        receive_email helper function is not completely black-box.
    """

    reset_code, u_id = auth_passwordreset_setup

    assert reset_code[0:4] == 'RS' + str(u_id) + '-'


# ------------------------------------------------------------------------------------------------- #
# -------------------------- http tests for auth/passwordreset/reset ------------------------------ #
# ------------------------------------------------------------------------------------------------- #


def test_auth_passwordreset_reset_inputerror(urls, auth_passwordreset_setup):
    """ Test raising InputError for /auth/passwordreset/reset
        There are more than one way to raise InputErrors for /auth/passwordreset/reset
        See detailed test cases in unit testings in auth_test.py.
        This test uses invalid reset_code to raise inputerror.
    """

    data = {
        "reset_code": '-1',
        "new_password": "newPassword"
    }

    response = requests.post(urls['auth_reset'], json=data)
    assert response.status_code == 400


def test_auth_passwordreset_reset_normal_behaviour(urls):
    """ Test normal http behaviour for auth/passwordreset_reset request
        in the front-end. Reset the password to the new password entered.
        If new password is setted correctly, then user should be able to
        login with the new password successfully.
    """

    requests.get(urls['other_clear'])

    owner = {
        "email": "comp1531.20t3.flockr@gmail.com",
        "password": "Password0",
        "name_first": "firstName0",
        "name_last": "lastName0"
    }

    # Registering the owner of the entire flockr
    owner = requests.post(urls['auth_register'], json=owner).json()

    # Log the user out before requesting password reset
    token = {
        "token": owner['token']
    }
    response1 = requests.post(urls['auth_logout'], json=token)
    assert response1.status_code == 200

    data = {
        "email": "comp1531.20t3.flockr@gmail.com"
    }
    response2 = requests.post(urls['auth_request'], json=data)
    assert response2.status_code == 200

    # Recieve email.
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login("comp1531.20t3.flockr@gmail.com", 'Flockr-COMP1531')
    mail.select(readonly=True)
    __, message_ids = mail.search(None, 'ALL')
    # Get the latest email received.
    msg_ids = message_ids[0].split()
    latest_msg = msg_ids[-1]
    __, message_data = mail.fetch(latest_msg, '(RFC822)')
    # Get the message content needed from the latest email.
    msg = email.message_from_bytes(message_data[0][1]).get_payload()
    reset_code = msg.partition("Security code: ")[2].rstrip()

    data1 = {
        "reset_code": reset_code,
        "new_password": "newPassword"
    }
    response3 = requests.post(urls['auth_reset'], json=data1)
    assert response3.status_code == 200

    data2 = {
        "email": "comp1531.20t3.flockr@gmail.com",
        "password": "newPassword"
    }
    response = requests.post(urls['auth_login'], json=data2)
    response = response.json()

    assert int(response['u_id']) == 0
