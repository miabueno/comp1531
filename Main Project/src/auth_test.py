"""

Created by Yue (Yuelanda) Dai (zid: z5310546)
21, September, 2020

Tests for auth.py

Reviewed by Yiyang (Sophia) Huang (zid: z5313425)
04, November, 2020
(tests for auth/password/request, auth/password/reset)
"""


import pytest
import auth as au
import error as err
import other

# libraies for emails
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import imaplib
import email


# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name

@pytest.fixture(name='reset_dict')
def reset():
    """ Using the clear function in other.py to initalise the data dictionaries after each test"""

    other.clear()


@pytest.fixture
def registration(reset_dict):
    """ A standard registered used for tests use"""

    return au.auth_register('comp1531.20t3.flockr@gmail.com', 'password', 'name_first', 'name_last')


# ------------------------------------------------------------------------------------------------- #
# ----------------------------------- Tests for auth_login ---------------------------------------- #
# ------------------------------------------------------------------------------------------------- #


def test_invalid_email():
    """ Expects to fail since invalid email is given"""

    with pytest.raises(err.InputError):
        au.auth_login('invalidemail.com', 'password')


def test_not_user_email(registration):
    """ Expects to fail since the email given does not belong to a user."""

    with pytest.raises(err.InputError):
        au.auth_login('notuseremail@testdata.com', 'password')


def test_incorrect_password(registration):
    """ Expects to fail since the password is incorrect"""

    with pytest.raises(err.InputError):
        au.auth_login('comp1531.20t3.flockr@gmail.com', 'incorrect_password')


def test_succesfull_login(registration):
    """ Expects to pass since correct email and password that
        matches the database is entered"""

    d_test = au.auth_login('comp1531.20t3.flockr@gmail.com', 'password')
    assert isinstance(d_test['u_id'], int) and d_test['token'] is not None


# ------------------------------------------------------------------------------------------------- #
# ----------------------------------- Tests for auth_logout --------------------------------------- #
# ------------------------------------------------------------------------------------------------- #


def test_unsuccessful_auth_logout_invalid_token(registration):
    """ The given token is invalid -> unsuccessful logout
        as a result of invalidation of the token during the user's active session"""

    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'
    d_logout = au.auth_logout(token)
    assert not d_logout['is_success']


def test_successful_auth_logout():
    """ The given token is valid and user is logged out"""

    other.clear()
    d_test = au.auth_register('comp1531.20t3.flockr@gmail.com', 'password', 'name_first', 'name_last')
    assert au.auth_logout(d_test['token'])


def test_auth_login_after_logout(registration):
    """ Test logging in and generating a valid token again after logged out"""

    assert au.auth_logout(registration['token'])
    login = au.auth_login('comp1531.20t3.flockr@gmail.com', 'password')

    assert isinstance(login['u_id'], int) and login['token'] is not None


# ------------------------------------------------------------------------------------------------- #
# ---------------------------------- Tests for auth_register -------------------------------------- #
# ------------------------------------------------------------------------------------------------- #


def test_successful_auth_register(reset_dict):
    """ Assume token is the email of the current user in iteration-1
        au.auth_login is called in au.auth_register, in other words,
        assumption is made that the user is logged in automatically after they are
        successfully registered."""

    d_reg = au.auth_register('comp1531.20t3.flockr@gmail.com', 'password', 'name_first', 'name_last')
    d_login = au.auth_login('comp1531.20t3.flockr@gmail.com', 'password')
    assert isinstance(d_reg['u_id'], int) and d_reg['token'] == d_login['token']


def test_successful_auth_register_two_users(reset_dict):
    """
    Assume token is the email of the current user in iteration-1
    au.auth_login is called in au.auth_register, in other words,
    assumption is made that the user is logged in automatically after they are
    successfully registered.
    """

    d_reg1 = au.auth_register('validemail1@testdata.com', '1password', 'name1_first', 'name1_last')
    d_reg2 = au.auth_register('validemail2@testdata.com', '2password', 'name2_first', 'name2_last')
    d_login1 = au.auth_login('validemail1@testdata.com', '1password')
    d_login2 = au.auth_login('validemail2@testdata.com', '2password')
    assert isinstance(d_reg1['u_id'], int) and d_reg1['token'] == d_login1['token']
    assert isinstance(d_reg2['u_id'], int) and d_reg2['token'] == d_login2['token']


def test_auth_register_invalid_email1(reset_dict):
    """ Expects to fail since email entered does not contain @"""

    with pytest.raises(err.InputError):
        au.auth_register('invalidemail.com', 'password', 'name_first', 'name_last')


def test_auth_register_invalid_email2(reset_dict):
    """ Expects to fail since email is entered has - before @"""

    with pytest.raises(err.InputError):
        au.auth_register('invalidemail-@email.com', 'password', 'name_first', 'name_last')


def test_auth_register_email_registered(registration):
    """ Email address is already being used by another user"""

    with pytest.raises(err.InputError):
        au.auth_register('comp1531.20t3.flockr@gmail.com', 'password', 'name_first', 'name_last')


def test_auth_register_password(reset_dict):
    """ Password entered is less than 6 characters long"""

    with pytest.raises(err.InputError):
        au.auth_register('comp1531.20t3.flockr@gmail.com', '123', 'name_first', 'name_last')


def test_auth_register_short_name_first(reset_dict):
    """ name_first less than 1 character in length"""

    with pytest.raises(err.InputError):
        au.auth_register('comp1531.20t3.flockr@gmail.com', 'password', '', 'name_last')


def test_auth_register_long_name_first(reset_dict):
    """ name_first greater than 50 characters in length"""

    with pytest.raises(err.InputError):
        au.auth_register('comp1531.20t3.flockr@gmail.com', 'password',
                      'qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm', 'name_last')


def test_auth_register_short_name_last(reset_dict):
    """ name_last is less than 1 character in length"""

    with pytest.raises(err.InputError):
        au.auth_register('comp1531.20t3.flockr@gmail.com', 'password', 'name_first', '')


def test_auth_register_long_name_last(reset_dict):
    """ name_last greater than 50 characters in length"""

    with pytest.raises(err.InputError):
        au.auth_register('comp1531.20t3.flockr@gmail.com', 'password',
                      'name_first', 'qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm')


def test_auth_register_handle_generation(registration):
    """ Test handle generation when name_first and name_last are the same.
        Cannot be directly tested since method to approach duplicate handles are
        different for each group. Only added to check it does not have unexpected
        and illegal behaviours (no errors raised).
    """

    d_reg = au.auth_register('validemail1@testdata.com', 'password', 'name_first', 'name_last')
    d_login = au.auth_login('validemail1@testdata.com', 'password')
    assert isinstance(d_reg['u_id'], int) and d_reg['token'] == d_login['token']


def test_auth_register_long_handle_generation(registration):
    """ Test handle generation when name_first and name_last are long in length.
        Cannot be directly tested since method to to handle long handles are
        different for each group. Only added to check it does not have unexpected
        and illegal behaviours (no errors raised).
    """

    d_reg = au.auth_register('validemail1@testdata.com', 'password', 'longFisrtNameLongFisrtName', 'longLastNameLongLast')
    d_login = au.auth_login('validemail1@testdata.com', 'password')
    assert isinstance(d_reg['u_id'], int) and d_reg['token'] == d_login['token']


# ------------------------------------------------------------------------------------------------- #
# --------------------------- Tests for auth_passwordreset_resquest ------------------------------- #
# ------------------------------------------------------------------------------------------------- #


def test_auth_passwordreset_request(registration):
    """ Test the user receiving the tempary password is the user
        who entered an alternate email address. Normal behaviour for
        auth_passwordreset_request.
        White-box testing to ensure behaviour and functionality.
    """

    u_id = registration['u_id']

    au.auth_passwordreset_request('comp1531.20t3.flockr@gmail.com')

    # Recieve email.
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('comp1531.20t3.flockr@gmail.com', 'Flockr-COMP1531')
    mail.select(readonly=True)
    __, message_ids = mail.search(None, 'ALL')
    # Get the latest email received.
    msg_ids = message_ids[0].split()
    latest_msg = msg_ids[-1]
    __, message_data = mail.fetch(latest_msg, '(RFC822)')
    # Get the message content needed from the latest email.
    msg = email.message_from_bytes(message_data[0][1]).get_payload()
    reset_code = msg.partition("Security code: ")[2].rstrip()

    assert reset_code[0:4] == 'RS' + str(u_id) + '-'


def test_auth_passwordreset_request_unregistered_email(registration):
    """ Testing that the email given is not an actual email and
        you cannot send an email to the account.
    """

    au.auth_logout(registration['token'])

    with pytest.raises(err.AccessError):
        au.auth_passwordreset_request('z0000000@ad.unsw.edu.au')


# ------------------------------------------------------------------------------------------------- #
# --------------------------- Tests for auth_passwordreset_reset ---------------------------------- #
# ------------------------------------------------------------------------------------------------- #


def test_auth_passwordreset_reset(registration):
    """ Test normal behaviour of auth_passwordreset_reset,
        The user should succeed calling auth_login after resetting the password.
    """

    au.auth_logout(registration['token'])

    au.auth_passwordreset_request('comp1531.20t3.flockr@gmail.com')

    # Recieve email.
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('comp1531.20t3.flockr@gmail.com', 'Flockr-COMP1531')
    mail.select(readonly=True)
    __, message_ids = mail.search(None, 'ALL')
    # Get the latest email received.
    msg_ids = message_ids[0].split()
    latest_msg = msg_ids[-1]
    __, message_data = mail.fetch(latest_msg, '(RFC822)')
    # Get the message content needed from the latest email.
    msg = email.message_from_bytes(message_data[0][1]).get_payload()
    reset_code = msg.partition("Security code: ")[2].rstrip()

    au.auth_passwordreset_reset(reset_code, 'newPassword')
    login = au.auth_login('comp1531.20t3.flockr@gmail.com', 'newPassword')

    # Test successful login after resetting to the new password
    assert login['token'] == registration['token'] and login['u_id'] == registration['u_id']


def test_auth_passwordreset_reset_invalid_reset_code(registration):
    """ Test when the reset_code entered is not valid """

    au.auth_passwordreset_request('comp1531.20t3.flockr@gmail.com')

    # assert au.get_reset_code('comp1531.20t3.flockr@gmail.com') == receive_email

    with pytest.raises(err.InputError):
        au.auth_passwordreset_reset('', 'newPassword')


def test_auth_passwordreset_reset_invalid_password(registration):
    """ Test when the new password entered is not valid """

    au.auth_logout(registration['token'])
    au.auth_passwordreset_request('comp1531.20t3.flockr@gmail.com')

    # Recieve email.
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('comp1531.20t3.flockr@gmail.com', 'Flockr-COMP1531')
    mail.select(readonly=True)
    __, message_ids = mail.search(None, 'ALL')
    # Get the latest email received.
    msg_ids = message_ids[0].split()
    latest_msg = msg_ids[-1]
    __, message_data = mail.fetch(latest_msg, '(RFC822)')
    # Get the message content needed from the latest email.
    msg = email.message_from_bytes(message_data[0][1]).get_payload()
    reset_code = msg.partition("Security code: ")[2].rstrip()

    with pytest.raises(err.InputError):
        au.auth_passwordreset_reset(reset_code, 'pw')
