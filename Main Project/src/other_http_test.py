"""
Created by Yue (Yuelanda) Dai (z5310546)
24/10/2020 - 25/10/2020

Integration tests for testing http routes for other.py
Tests only handles normal http behaviours and error checkings.
Functionality tests and edge case handlings for each targeted
feature is done in other_test.py.

"""

import json
import requests
import pytest


# pylint: disable=redefined-outer-name


@pytest.fixture
def setup(url, data_setup):
    """ Pytest fixture for testing http route of message_edit, which:
        - Register three valid users (auth/register): owner, user_1, user_2
        - Login (auth/login) user_1 and user_2
        - user_1 creates reate a channel, channel_1 (owner: user_1, no members)
        - user_1 sents a message in channel_1

    Parameter:
        url: returned from pytest fixture url()
        register: pytest fixture that registers two valid users

    Returns:
        - base_url (str): the url port in which the http tests are running on.
        - user_1 (dict): u_id and valid token after logged in.
        - user_2 (dict): u_id and valid token after logged in.
        - channel_id (int): id of channel_1 (owner: user_1).
        - message_id (int): id of a message sent by user_1 in channel_1.
    """

    base_url = url
    requests.get(base_url + 'other.clear')

    owner_data, user1_data, user2_data = data_setup

    # Registering the owner of the entire flockr
    requests.post(base_url + '/auth/register', json=owner_data)
    # Registering valid users
    requests.post(base_url + '/auth/register', json=user1_data)
    requests.post(base_url + '/auth/register', json=user2_data)

    data = {
        "email": user1_data['email'],
        "password": user1_data['password']
    }
    user_1 = requests.post(base_url + '/auth/login', json=data)

    data = {
        "email": user2_data['email'],
        "password": user2_data['password']
    }
    user_2 = requests.post(base_url + '/auth/login', json=data)

    user_1, user_2 = user_1.json(), user_2.json()

    # user_1 creates channel_1
    create_ch_data = {
        "token": user_1['token'],
        "name": "channel_1",
        "is_public": True
    }
    channel = requests.post(base_url + '/channels/create', json=create_ch_data)
    channel = channel.json()
    channel_id = int(channel['channel_id'])

    return base_url, user_1, user_2, channel_id


@pytest.fixture
def msgs_data(setup):
    """ messages dictionaries to be passed into message/send.

    Parameter:
        setup (pytest fixture): initilisation of users and channels

    Returns: (dict) msg_data_1, msg_data_2, msg_data_3
    """

    base_url, user_1, __, channel_id = setup

    # user_1 sends messages in channel_1
    msg_data_1 = {
        "token": user_1['token'],
        "channel_id": channel_id,
        "message": "Hello World"
    }
    msg_data_2 = {
        "token": user_1['token'],
        "channel_id": channel_id,
        "message": "hello"
    }
    msg_data_3 = {
        "token": user_1['token'],
        "channel_id": channel_id,
        "message": "Hello"
    }
    ch_msgs_data = {
        "token": str(user_1['token']),
        "channel_id": str(channel_id),
        "start": "0"
    }
    # send messages using http route message/send
    requests.post(base_url + '/message/send', json=msg_data_1)
    requests.post(base_url + '/message/send', json=msg_data_2)
    requests.post(base_url + '/message/send', json=msg_data_3)

    return msg_data_1, msg_data_2, msg_data_3, ch_msgs_data


@pytest.fixture
def channel_msgs(msgs_data, setup):
    """ using http route channel/messages to return all
        messages in channel_1

    Parameter: (pytest fixture) setup

    Returns: (dict) msg_1, msg_2, msg_3
    """

    base_url, __, __, __ = setup
    __, __, __, ch_msgs_data = msgs_data

    msgs = requests.get(base_url + '/channel/messages', params=ch_msgs_data)
    msg_list = msgs.json()
    msg_1, msg_2, msg_3 = msg_list['messages'][0], msg_list['messages'][1], msg_list['messages'][2]

    return msg_1, msg_2, msg_3


def test_search_normal_behavior(setup, channel_msgs):
    """ Testing the normal behavior of search function in http route.

    Parameters:
        - setup (pytest fixture): used for testing
        - channel_msgs (pytest fixture): used to show the expcted outputs
    """

    base_url, user_1, __, __ = setup
    msg_1, __, msg_3 = channel_msgs
    exp = [msg_1, msg_3]

    search_data = {
        "token": user_1['token'],
        "query_str": "Hello"
    }

    msgs = requests.get(base_url + '/search', params=search_data)
    msgs = msgs.json()['messages']

    assert msgs == exp


def test_search_empty_messages(setup):
    """ Testing when no messsage contains the query_string in http route.

    Parameters:
        - setup (pytest fixture): used for testing
        - channel_msgs (pytest fixture): used to show the expcted outputs
    """

    base_url, user_1, __, __ = setup

    search_data = {
        "token": user_1['token'],
        "query_str": "Hi"
    }

    msgs = requests.get(base_url + '/search', params=search_data)
    msgs = msgs.json()['messages']

    assert msgs == []

# ================= users_all and admin_permission_change functions =================

@pytest.fixture
def generate_url(url):
    """ Generate url for specific functionality.
        :params url: basic url of the server
        :Return:
            1.  (str) url for users/all
            2.  (str) url for admin/userpermission/change
    """
    url_usersall = url + '/users/all'
    url_permissionchange = url + '/admin/userpermission/change'

    return url_usersall, url_permissionchange


@pytest.fixture
def pre_test_setup(url):
    """ Pytest fixture that register users and create channels
        through http methods for testing.

        :params url: basic url of the server
        :return
        (dict): u_id and token of user_1
        (dict): u_id and token of user_2
        (dict): u_id and token of user_3
    """

    requests.get(url + '/other/clear')
    data0 = {
        "email": "FLOCKR@gmail.com",
        "password": "Password",
        "name_first": "flock",
        "name_last": "owner"
    }
    data1 = {
        "email": "z1111111@ad.unsw.edu.au",
        "password": "password",
        "name_first": "Nont",
        "name_last": "Fakungkun"

    }
    data2 = {
        "email": "z2222222@ad.unsw.edu.au",
        "password": "password123",
        "name_first": "Dummy",
        "name_last": "Dummy"
    }
    # Register User, return token and uid
    owner = requests.post(url + "/auth/register", json=data0).json()
    user_1 = requests.post(url + "/auth/register", json=data1).json()
    user_2 = requests.post(url + "/auth/register", json=data2).json()

    return owner, user_1, user_2


def test_users_all_success(url, generate_url, pre_test_setup):
    """
    Test if the function is working successful and the list
    with correct length and details is returned

    Note: we use 'username' instead of 'handle_str'
    will there be problem when we use our test with other groups?
    """

    owner = pre_test_setup[0]
    url_usersall = generate_url[0]

    users_list = requests.get(url_usersall, params={'token': owner['token'],}).json()

    # Check the overall length of the list -> 3 users
    assert len(users_list['users']) == 3

    # Check the users' details
    for i in range(len(users_list['users'])):
        data = {
            "token": owner['token'],
            "u_id": i
        }
        u_detail = requests.get(url + 'user/profile', params=data)
        u_detail = json.loads(u_detail.text)['user']
        assert users_list['users'][i]['u_id'] == u_detail['u_id']
        assert users_list['users'][i]['email'] == u_detail['email']
        assert users_list['users'][i]['name_first'] == u_detail['name_first']
        assert users_list['users'][i]['name_last'] == u_detail['name_last']
        assert users_list['users'][i]['handle_str'] == u_detail['handle_str']


def test_users_all_invalid_token(generate_url):
    """
    The token input in this function does not exist -> AccessError is raised
    """
    url_usersall = generate_url[0]

    # Check AccessError when token is incorrect
    assert requests.get(url_usersall, params= {'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.' \
                                                        'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'}) \
                        .status_code == 400


def test_admin_upermchange_change_success_to_admin(url, generate_url, pre_test_setup):
    """
    Test if the function is working for changing
    the global permission for the selected user from member to admin
    """

    owner, user_1, user_2 = pre_test_setup
    url_permissionchange = generate_url[1]

    data_0 = {
        "token": user_2['token'],
        "name": "Channel_1",
        "is_public": True
    }
    channel = requests.post(url + '/channels/create', json=data_0).json()
    channel_1 = int(channel['channel_id'])
    data_1 = {
        "token": owner['token'],
        "u_id": user_1['u_id'],
        "permission_id": 1
    }
    response = requests.post(url_permissionchange, json=data_1)
    # status code 200 is NULL means that the function working correctly
    assert response.status_code == 200

    # Check permission_id of user_2 if user_2 has permission_id of 1,
    # it will become owner of the channel automatically
    data_2 = {
        "token": user_1['token'],
        "channel_id": channel_1
    }
    requests.post(url + '/channel/join', json=data_2)
    #if the person becomes owner able to remove another owner. if no error means was able to
    data_3 = {
        "token": user_1['token'],
        "channel_id": channel_1,
        "u_id": user_2['u_id']
    }
    response = requests.post(url + "/channel/removeowner", json=data_3)
    # status code 200 is NULL means that the function working correctly
    assert response.status_code == 200


def test_admin_upermchange_change_success_to_user(url, generate_url, pre_test_setup):
    """
    Test if the function is working for changing
    the global permission for the selected user from admin to member
    """

    owner, user_1, user_2 = pre_test_setup
    url_permissionchange = generate_url[1]

    data_0 = {
        "token": user_2['token'],
        "name": "Channel_1",
        "is_public": True
    }
    channel = requests.post(url + '/channels/create', json=data_0).json()
    channel_1 = int(channel['channel_id'])
    data_1 = {
        "token": owner['token'],
        "u_id": user_1['u_id'],
        "permission_id": 1
    }
    response = requests.post(url_permissionchange, json=data_1)
    # status code 200 is NULL means that the function working correctly
    assert response.status_code == 200

    data_2 = {
        "token": owner['token'],
        "u_id": user_1['u_id'],
        "permission_id": 2
    }
    response = requests.post(url_permissionchange, json=data_2)
    # status code 200 is NULL means that the function working correctly
    assert response.status_code == 200

    # Check permission_id of user_2 if user_2 has permission_id of 1,
    # it will become owner of the channel automatically
    data_3 = {
        "token": user_1['token'],
        "channel_id": channel_1
    }
    requests.post(url + '/channel/join', json=data_3)
    #if the person becomes owner able to remove another owner. if no error means was able to
    data_4 = {
        "token": user_1['token'],
        "channel_id": channel_1,
        "u_id": user_2['u_id']
    }
    response = requests.post(url + "/channel/removeowner", json=data_4)
    assert response.status_code == 400


def test_admin_upermchange_invalid_token(generate_url, pre_test_setup):
    """
    The token input in this function does not exist -> AccessError is raised
    """

    owner = pre_test_setup[0]
    url_permissionchange = generate_url[1]
    data = {
        "token": 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        "u_id": owner['u_id'],
        "permission_id": 1
    }
    # Check AccessError when token is incorrect
    assert requests.post(url_permissionchange, json=data).status_code == 400

def test_admin_upermchange_not_authorised_token(generate_url, pre_test_setup):
    """
    The user is not an owner/admin (Not authorised) -> AccessError is raised
    """

    user_2 = pre_test_setup[2]
    url_permissionchange = generate_url[1]
    data = {
        "token": user_2['token'],
        "u_id": user_2['u_id'],
        "permission_id": 1
    }
    # Check AccessError when token is not authorised
    assert requests.post(url_permissionchange, json=data).status_code == 400


def test_admin_upermchange_invalid_u_id(generate_url, pre_test_setup):
    """
    The user ID input does not exist -> InpputError is raised
    """

    owner = pre_test_setup[0]
    url_permissionchange = generate_url[1]
    data = {
        "token": owner['token'],
        "u_id": -999,
        "permission_id": 1
    }

    # Check InputError when u_id is invalid
    assert requests.post(url_permissionchange, json=data).status_code == 400


def test_admin_upermchange_invalid_perm_value(generate_url, pre_test_setup):
    """
    The permission ID input is invalid (Not 1 or 2) -> InpputError is raised
    """

    owner = pre_test_setup[0]
    url_permissionchange = generate_url[1]
    data = {
        "token": owner['token'],
        "u_id": owner['u_id'],
        "permission_id": 4  # Not a valid permission_id, can only be 1 or 2
    }
    # Check InputError when permission_id is invalid
    assert requests.post(url_permissionchange, json=data).status_code == 400
