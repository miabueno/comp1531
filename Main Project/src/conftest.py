""" This file stores the pytest fixture that is used
    across all the existing pytests.

@author Yiyang Huang (z5313425)
@date 2020/11/04
"""

import json
import re
import signal
from subprocess import PIPE, Popen
from time import sleep, time

import pytest
import requests

# emails
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import imaplib
import email

# # ------------------------ pytest fixtures for server url ------------------------ #


# pylint: disable=redefined-outer-name
@pytest.fixture
def url():
    """ Imported from echo_http_test.py.
        Use this fixture to get the URL of the server.
        It starts the server for you, so you don't need to.

        :Return: (str) url for the server
    """
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")


# # ------------------------ pytest fixtures for all urls ------------------------ #


@pytest.fixture
def urls(url):
    """ Returns all the involving urls for the tests.

    Args:
        url (pytest.fixture): url of server generated from local machine.

    Returns:
        (list): All the possible urls of functions.
    """
    urls = {
        'other_clear': url + 'other/clear',
        'other_search': url + 'search',
        'auth_register': url + 'auth/register',
        'auth_login': url + 'auth/login',
        'auth_logout': url + 'auth/logout',
        'auth_request': url + 'auth/passwordreset/request',
        'auth_reset': url + 'auth/passwordreset/reset',
        'channels_list': url + 'channels/list',
        'channels_listall': url + 'channels/listall',
        'channels_create': url + 'channels/create',
        'channel_join': url + 'channel/join',
        'channel_leave': url + 'channel/leave',
        'channel_invite': url + 'channel/invite',
        'channel_messages': url + 'channel/messages',
        'channel_addowner': url + 'channel/addowner',
        'channel_removeowner': url + 'channel/removeowner',
        'channel_details': url + 'channel/details',
        'admin_permissionchange': url + 'admin/userpermission/change',
        'message_send': url + 'message/send',
        'message_remove': url + 'message/remove',
        'message_edit': url + 'message/edit',
        'message_react': url + 'message/react',
        'message_unreact': url + 'message/unreact',
        'message_sendlater': url + 'message/sendlater',
        'message_pin': url + 'message/pin',
        'message_unpin': url + 'message/unpin',
        'message_broadcast': url + 'message/broadcast',
        'users_all': url + 'users/all',
        'user_permission_change': url + 'admin/userpermission/change'
    }
    return urls


# # ------------------------ pytest fixtures for registration data ------------------------ #


@pytest.fixture
def data_setup():   # pragma: no cover
    """ Four dictioanries that can be passed into http routes.

        Returns:
            - owner (dict)
            - user_1 (dict)
            - user_2 (dict)
            - create_ch_data (json dict)
    """

    # First user regitered is the owner of the entire flockr
    owner = {
        "email": "comp1531.20t3.flockr@gmail.com",
        "password": "Password0",
        "name_first": "firstName0",
        "name_last": "lastName0"
    }

    # Registering valid users
    user_1 = {
        "email": "z1111111@ad.unsw.edu.au",
        "password": "Password1",
        "name_first": "firstName1",
        "name_last": "lastName1"
    }

    user_2 = {
        "email": "z2222222@ad.unsw.edu.au",
        "password": "Password2",
        "name_first": "firstName2",
        "name_last": "lastName2"
    }

    return owner, user_1, user_2


# ---------------------------- pytest fixtures for message.py -------------------------- #


@pytest.fixture
def msg_setup(urls, data_setup):    # pragma: no cover
    """ Pytest fixture that register users and create channels
        through http methods for testing.

        :params url: basic url of the server
        :Returns:
            1.  (dict) Dictionary of registered user_1
            2.  (dict) Dictionary of registered user_2
            3.  (int)  channel ID of a public channel named channel_1
            4.  (int)  channel ID of a private channel named channel_2
    """
    requests.get(urls['other_clear'])

    # create three users: 1 owner of the Flockr, 2 normal user
    registration = []
    for data in data_setup:
        user = requests.post(urls['auth_register'], json=data).json()
        registration.append(user)

    # create two channels: 1 public and 1 private
    creation = []
    for j in range(1, 3):
        create_ch_data = {
            'token': registration[1]['token'],
            'name': 'channel_' + str(j),
            'is_public': j == 1,
        }
        channel = requests.post(urls['channels_create'], json=create_ch_data)
        creation.append(int(channel.json()['channel_id']))

    # user_2 join the public channel named channel_1
    ch_join_data = {
        'token': registration[2]['token'],
        'channel_id': creation[0],
    }
    requests.post(urls['channel_join'], json=ch_join_data)

    pmc_data = {
        'token': registration[0]['token'],
        'u_id': registration[1]['u_id'],
        'permission_id': 1,
    }
    requests.post(urls['user_permission_change'], json=pmc_data)

    return registration[1::] + creation


@pytest.fixture
def send_one_msg(urls, msg_setup):  # pragma: no cover
    """ Pytest fixture that send 1 message using http methods.
        All parameters are valid and should not raise any error.

        :Return: (int) msg_id
    """
    user_1, __, channel_public, __ = msg_setup
    data = {
        'token': user_1['token'],
        'channel_id': channel_public,
        'message': "Hello World!",
    }
    msg_id = requests.post(urls['message_send'], json=data).json()['message_id']
    return msg_id


@pytest.fixture
def send_msg_pin_unpin(urls, msg_setup):    # pragma: no cover
    """ Pytest fixture that send 2 messages using http methods.
        pecified for message_pin and message_unpin functions.
        All parameters are valid and should not raise any error.

        :Return: (int) msg_id
    """
    user_1, user_2, channel_public, __ = msg_setup

    msg_1_data = {
        "token": user_2['token'],
        "channel_id": channel_public,
        "message": "pinned"
    }
    msg_1 = requests.post(urls['message_send'], json=msg_1_data).json()['message_id']

    pinning_msg_data = {
        "token": user_1['token'],
        "message_id": msg_1,
    }
    requests.post(urls['message_pin'], json=pinning_msg_data)

    msg_2_data = {
        "token": user_2['token'],
        "channel_id": channel_public,
        "message": "unpinned"
    }
    msg_2 = requests.post(urls['message_send'], json=msg_2_data).json()['message_id']

    return msg_1, msg_2


@pytest.fixture
def generate_timestamp():
    """ Generate timestamp for testing. Round to seconds.
    :return: (unix timestamp) timestamp
    """
    return round(time())


@pytest.fixture
def msg_data(msg_setup, send_one_msg):  # pragma: no cover
    """ Data dictionaries for all message related functions.

    Returns:
    1 dictinary that contains key and value pair respectively as follows:
        - msg_edit_data (dict): valid data for message_edit
        - msg_send_data (dict): valid data for message_send
        - msg_edit_invalid (dict): invalid data for message_edit
        - msg_react_data (dict): valid data for message_react
        - msg_remove_data (dict): valid data for message_remove
        - ch_msgs_data (dict): valid data for channel_messages
    """
    user_1, user_2, channel_id, channel_private = msg_setup

    msg_edit_data = {
        "token": user_1['token'],
        "message_id": channel_id,
        "message": "Updated message"
    }
    msg_send_data = {
        'token': user_1['token'],
        'channel_id': channel_id,
        'message': "Hello World!",
    }
    msg_edit_invalid = {
        "token": user_2['token'],
        "message_id": channel_private,
        "message": "Invalid Update"
    }
    msg_react_data = {
        'token': user_1['token'],
        'message_id': send_one_msg,
        'react_id': 1,
    }
    ch_msgs_data = {
        "token": user_1['token'],
        "channel_id": channel_id,
        "start": 0,
    }
    msg_remove_data = {
        'token': user_1['token'],
        'message_id': send_one_msg,
    }

    msg_send_later_data = {
        'token': user_1['token'],
        'channel_id': channel_id,
        'message': "this message to be sent later",
        'time_sent': 5,
    }

    data = {
        'msg_edit': msg_edit_data,
        'msg_send': msg_send_data,
        'msg_edit_invalid': msg_edit_invalid,
        'ch_msgs': ch_msgs_data,
        'msg_react': msg_react_data,
        'msg_remove': msg_remove_data,
        'msg_send_later': msg_send_later_data,
    }

    return data


# --------------------------- pytest fixtures for auth.py -------------------------- #


@pytest.fixture
def auth_register_setup(urls, data_setup):  # pragma: no cover
    """ pytest fixture that log valid users in with http methods.

    Parameter:
        urls: returned from pytest fixture urls()
        data_setup: pytest fixture with all initialise data

    Return:
        owner (dict): a dictionary that contains the u_id and valid token of owner.
        user (dict): a dictionary that contains the u_id and valid token of user.
    """

    requests.get(urls['other_clear'])

    # Registering the owner of the entire flockr
    owner = requests.post(urls['auth_register'], json=data_setup[0]).json()
    # Registering a valid user
    user = requests.post(urls['auth_register'], json=data_setup[1]).json()

    return owner, user


@pytest.fixture
def auth_passwordreset_setup(urls, auth_register_setup, data_setup):    # pragma: no cover
    """ pytest fixture that sends a reset_code to a user email.

    Parameter:
        login: pytest fixture that returns information after user is logged in.

    Returns:
        - base_url: url used for all the http features to take place
    """

    u_id, token_data = auth_register_setup[0]['u_id'], auth_register_setup[0]['token']

    # Log the user out before requesting password reset
    token = {
        "token": token_data
    }
    requests.post(urls['auth_logout'], json=token)

    data = {
        "email": data_setup[0]['email']
    }
    requests.post(urls['auth_request'], json=data)

    # Recieve email.
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(data_setup[0]['email'], 'Flockr-COMP1531')
    mail.select(readonly=True)
    __, message_ids = mail.search(None, 'ALL')
    # Get the latest email received.
    msg_ids = message_ids[0].split()
    latest_msg = msg_ids[-1]
    __, message_data = mail.fetch(latest_msg, '(RFC822)')
    # Get the message content needed from the latest email.
    msg = email.message_from_bytes(message_data[0][1]).get_payload()
    reset_code = msg.partition("Security code: ")[2].rstrip()

    return reset_code, u_id
