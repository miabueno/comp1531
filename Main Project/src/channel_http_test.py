""" This module is for testing http routes of channel.py
    Only test for normal behavior and errors. Edge cases
    should be tested in separate functionality tests in
    channel_test.py

@author Yiyang Huang
@date 2020/10/20

"""

# Libraries
import json
import requests
import pytest

# pylint: disable=redefined-outer-name

@pytest.fixture
def pre_test_setup(urls, data_setup):
    """ Pytest fixture that register users and create channels
        through http methods for testing.

        :params url: basic url of the server
        :Returns:
            1.  (dict) Dictionary contains token and u_id of the owner of the Flockr
            2.  (dict) Dictionary that contains token and u_id of registered user
            3.  (dict) Dictionary that contains token and u_id of registered user
            4.  (int)  channel ID of the public channel named channel_1
            5.  (int)  channel ID of the private channel named channel_2
    """

    requests.get(urls['other_clear'])

    # create 3 users: 1 owner of the Flockr, 2 normal users
    registration = []
    for user_info in data_setup:
        success_data = requests.post(urls['auth_register'], json=user_info).json()
        registration.append(success_data)

    # Create 2 channels: 1 public, 1 private
    creation = []
    for j in range(2):
        create_ch_data = {
            'token': registration[1]['token'],
            'name': 'channel_' + str(j),
            'is_public': j == 0,
        }
        channel = requests.post(urls['channels_create'], json=create_ch_data).json()
        creation.append(int(channel['channel_id']))

    return registration + creation


def test_channel_leave(urls, pre_test_setup):
    """ Test the basic functionality of channel/leave
    """

    __, __, user_2, channel_public, __ = pre_test_setup

    data = {
        'token': user_2['token'],
        'channel_id': channel_public,
    }
    lst_data = {'token': user_2['token']}

    # user_2 joins channel_public
    requests.post(urls['channel_join'], json=data)
    ch_list = requests.get(urls['channels_list'], params=lst_data).json()
    assert channel_public in [int(each['channel_id']) for each in ch_list['channels']]

    # user_2 leaves channel_public
    requests.post(urls['channel_leave'], json=data)
    ch_list = requests.get(urls['channels_list'], params=lst_data).json()
    assert channel_public not in [int(each['channel_id']) for each in ch_list['channels']]


def test_channel_leave_access_error(urls, pre_test_setup):
    """ User_2 is not in the private channel created by user_1,
        thus causing an AccessError.

        :Exception: AccessError
    """
    __, __, user_2, __, channel_private = pre_test_setup
    leave_data = {
        'token': user_2['token'],
        'channel_id': channel_private,
    }

    assert requests.post(urls['channel_leave'], json=leave_data).status_code == 400


def test_channel_leave_input_error(urls, pre_test_setup):
    """ Input an invalid channel_id that causes an InputError.

        :Exception: InputError
    """
    user_1 = pre_test_setup[1]
    leave_data = {
        'token': user_1['token'],
        'channel_id': -99999,
    }

    assert requests.post(urls['channel_leave'], json=leave_data).status_code == 400


def test_channel_join(urls, pre_test_setup):
    """ Test the normal functionality of channel/join.

        Owner joins channel_public successfully.
    """

    owner, user_1, __, channel_public, __ = pre_test_setup

    # User 1 join the channel with ID channel_3
    join_ch = {
        'token': owner['token'],
        'channel_id': channel_public,
    }
    requests.post(urls['channel_join'], json=join_ch)
    ch_list = requests.get(urls['channels_list'], params={'token': user_1['token']}).json()

    assert channel_public in [int(each['channel_id']) for each in ch_list['channels']]


def test_channel_join_input_error(urls, pre_test_setup):
    """ Tryint to join a channel with invalid channe_id.

        :Exception: InputError
    """

    user_1 = pre_test_setup[1]
    join_data = {
        'token': user_1['token'],
        'channel_id': -99999,
    }

    assert requests.post(urls['channel_join'], json=join_data).status_code == 400


def test_channel_join_access_error(urls, pre_test_setup):
    """ Tryint to join a channel when channel is private. And the
        authorized user is not owner of the flockr (i.e. global owner)

        :Exception: AccessError
    """

    __, __, user_2, __, channel_private = pre_test_setup
    join_data = {
        'token': user_2['token'],
        'channel_id': channel_private,
    }

    assert requests.post(urls['channel_join'], json=join_data).status_code == 400


def test_channel_invite(urls, pre_test_setup):
    """
        > User 1 has created a channel
        > User 1 invites User 2 to channel
        New channel should appear in User 2's channel list
    """

    __, user_1, user_2, __, channel_private = pre_test_setup

    ch_list_2 = requests.get(urls['channels_list'],
                                  params={"token": user_2['token']}
                                  ).json()['channels']

    assert channel_private not in [channel_info['channel_id'] for channel_info in ch_list_2]

    ch_invite_data = {
        "token": user_1['token'],
        "channel_id": channel_private,
        "u_id": user_2['u_id']
    }
    requests.post(urls['channel_invite'], json=ch_invite_data)

    # User_1 invites user_2 into channel_2 with ID channel_private
    ch_list_2 = requests.get(urls['channels_list'],
                                  params={"token": user_2['token']}
                                  ).json()['channels']

    assert channel_private in [channel_info['channel_id'] for channel_info in ch_list_2]


def test_channel_invite_input_error_user(urls, pre_test_setup):
    """
        Input Error:
        uid does not refer to a valid user
    """
    __, user_1, __, channel_public, __ = pre_test_setup

    channel_invite_data = {
        "token": user_1['token'],
        "channel_id": channel_public,
        "u_id": user_1['u_id'] + 999
    }

    response = requests.post(urls['channel_invite'], json=channel_invite_data)
    assert response.status_code == 400


def test_channel_invite_input_error_channel(urls, pre_test_setup):
    """
        Input Error:
        channel_id does not refer to a valid channel
    """

    user_1 = pre_test_setup[1]
    channel_invite_data = {
        "token": user_1['token'],
        "channel_id": -99999,
        "u_id": user_1['u_id']
    }

    # should return InputError since channel_id doesn't exist
    response = requests.post(urls['channel_invite'], json=channel_invite_data)
    assert response.status_code == 400


def test_channel_invite_access_error(urls, pre_test_setup):
    """
        Access Error: User_2 is not a member of the channel but
        trying to invite someone to that channel.
    """
    owner, __, user_2, channel_public, __ = pre_test_setup

    channel_invite_data = {
        "token": user_2['token'],
        "channel_id": channel_public,
        "u_id": owner['u_id'],
    }

    # should return AccessError since token is not valid
    response = requests.post(urls['channel_invite'], json=channel_invite_data)
    assert response.status_code == 400


def test_channel_details(urls, pre_test_setup):
    """ Tests if channel_details returns the correct value.
    """
    __, user_1, user_2, channel_public, __ = pre_test_setup

    # params for channel_details
    ch_details_data_1 = {
        "token": user_1['token'],
        "channel_id": channel_public,
    }
    ch_details_data_2 = {
        "token": user_2['token'],
        "channel_id": channel_public,
    }

    requests.post(urls['channel_join'], json=ch_details_data_2)
    details_1 = requests.get(urls['channel_details'], params=ch_details_data_1).json()
    details_2 = requests.get(urls['channel_details'], params=ch_details_data_2).json()

    assert details_1 == details_2
    assert user_1['u_id'] in [user['u_id'] for user in details_1['owner_members']]
    assert user_1['u_id'] in [user['u_id'] for user in details_1['all_members']]
    assert user_2['u_id'] not in [user['u_id'] for user in details_2['owner_members']]
    assert user_2['u_id'] in [user['u_id'] for user in details_2['all_members']]


def test_channel_details_input_error_channel(urls, pre_test_setup):
    """
        Input Error:
        channel_id does not refer to a valid channel
    """

    user_1 = pre_test_setup[1]

    # params for channel_details
    ch_details_data = {
        'token': user_1['token'],
        'channel_id': 99999999
    }

    # input error
    ch_details = requests.get(urls['channel_details'], params=ch_details_data)
    assert ch_details.status_code == 400


def test_channel_details_access_error(urls, pre_test_setup):
    """
        Access Error:
        user (id by token) is not already a member of the channel
    """

    # params for channel_details
    ch_details_data = {
        'token': pre_test_setup[2]['token'],
        'channel_id': pre_test_setup[-1]
    }

    # access error
    channel_details = requests.get(urls['channel_details'], params=ch_details_data)
    assert channel_details.status_code == 400


def test_channel_messages_less_50(urls, pre_test_setup):
    """
        check that channel_messages matches expected output
        case: there are less than 50 messages in channel
    """
    __, user_1, __, channel_public, __ = pre_test_setup

    msg_send_data = {
        'token': user_1['token'],
        'channel_id': channel_public,
        'message': "Hello World!",
    }

    msg_ids = []
    for __ in range(10):
        msg_id = requests.post(urls['message_send'], \
                               json=msg_send_data).json()['message_id']
        msg_ids.append(msg_id)

    # params for channel_messages
    ch_msg_data = {
        'token': user_1['token'],
        'channel_id': channel_public,
        'start': 0,
    }

    # collect messages in channel
    channel_messages = requests.get(urls['channel_messages'], params=ch_msg_data).json()

    assert channel_messages['start'] == 0 and channel_messages['end'] == -1
    assert channel_messages['messages'][0]['message_id'] == msg_ids[-1]
    assert channel_messages['messages'][-1]['message_id'] == msg_ids[0]


def test_channel_messages_more_50(urls, pre_test_setup):
    """
        check that channel_messages matches expected output
        case: there are more than 50 messages in channel
    """
    __, user_1, __, channel_public, __ = pre_test_setup

    for i in range(1, 51):
        msg_send_data = {
            'token': user_1['token'],
            'channel_id': channel_public,
            'message': "Hello " + str(i),
        }
        requests.post(urls['message_send'], json=msg_send_data).json()['message_id']

    ch_msg_data = {
        'token': user_1['token'],
        'channel_id': channel_public,
        'start': 0,
    }

    # collect messages in channel
    channel_messages = requests.get(urls['channel_messages'], params=ch_msg_data).json()
    assert channel_messages['start'] == 0 and channel_messages['end'] == 50
    assert channel_messages['messages'][0]['message'] == 'Hello 50'
    assert channel_messages['messages'][-1]['message'] == 'Hello 1'


def test_channel_messages_access_error(urls, pre_test_setup):
    """
        Access Error:
        user (id by token) is not valid
    """

    # params for channel_messages
    ch_msg_data = {
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9'
                 '.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        'channel_id': pre_test_setup[-2],
        'start': 0
    }

    # access error
    channel_messages = requests.get(urls['channel_messages'], params=ch_msg_data)
    assert channel_messages.status_code == 400


def test_channel_messages_input_error_ch_invalid(urls, pre_test_setup):
    """
        Input Error:
        channel_id does not exist

    """

    # params for channel_messages
    ch_msg_data = {
        'token': pre_test_setup[1]['token'],
        'channel_id': 999999,
        'start': 0
    }

    # input error
    channel_messages = requests.get(urls['channel_messages'], params=ch_msg_data)
    assert channel_messages.status_code == 400


def test_channel_messages_input_error_total_messages(urls, pre_test_setup):
    """
        Input Error:
        starting number is more than the amount of total messages

    """
    __, user_1, __, channel_public, __ = pre_test_setup

    for i in range(0, 10):
        msg_send_data = {
            'token': user_1['token'],
            'channel_id': channel_public,
            'message': "Hello " + str(i),
        }
        requests.post(urls['message_send'], json=msg_send_data).json()['message_id']

    ch_msg_data = {
        'token': user_1['token'],
        'channel_id': channel_public,
        'start': 12
    }

    # input error
    channel_messages = requests.get(urls['channel_messages'], params=ch_msg_data)
    assert channel_messages.status_code == 400


@pytest.fixture
def _pre_setup_(urls):
    '''
    fixture of registering two users
    '''
    requests.get(urls['other_clear'])
    data0 = {
        "email": "FLOCKR@gmail.com",
        "password": "Password",
        "name_first": "flock",
        "name_last": "owner"
    }
    data1 = {
        "email": "233333@gmail.com",
        "password": "Nopassword",
        "name_first": "Miriam",
        "name_last": "Tuvel"

    }
    data2 = {
        "email": "433333@gmail.com",
        "password": "password?",
        "name_first": "Hayden",
        "name_last": "Smith"
    }
    data3 = {
        "email": "533333@gmail.com",
        "password": "password?",
        "name_first": "James",
        "name_last": "New"
    }
    owner_reg = requests.post(urls['auth_register'], json=data0)
    owner_reg = json.loads(owner_reg.text)
    a_reg = requests.post(urls['auth_register'], json=data1).json()
    b_reg = requests.post(urls['auth_register'], json=data2).json()
    c_reg = requests.post(urls['auth_register'], json=data3).json()

    channel_link = urls['channels_create']
    a_channel_id = requests.post(channel_link, json={"token": a_reg['token'], "name": "A", "is_public": True})
    a_channel_id = json.loads(a_channel_id.text)
    b_channel_id = requests.post(channel_link, json={"token": a_reg['token'], "name": "B", "is_public": True})
    b_channel_id = json.loads(b_channel_id.text)
    c_channel_id = requests.post(channel_link, json={"token": c_reg['token'], "name": "C", "is_public": True})
    c_channel_id = json.loads(c_channel_id.text)
    return owner_reg, a_reg, b_reg, c_reg, a_channel_id, b_channel_id, c_channel_id


def test_channel_add_owner(urls, _pre_setup_):
    '''
    add a valid user to a valid channel
    '''
    __, a_reg, b_reg, __, a_channel_id, __, __ = _pre_setup_
    data = {
        "token": a_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "u_id": b_reg['u_id']
    }
    response = requests.post(urls['channel_addowner'], json=data)
    assert json.loads(response.text) == {}
    #if the person becomes owner able to remove another owner. if no error means was able to
    data2 = {
        "token": b_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "u_id": a_reg['u_id']
    }
    response = requests.post(urls['channel_removeowner'], json=data2)
    assert response.status_code == 200


def test_invalid_channel_add_owner(urls, _pre_setup_):
    '''
    try to add a valid user to a non-valid channel so raises error input
    '''
    __, a_reg, b_reg, __, __, __, __ = _pre_setup_
    data = {
        "token": a_reg['token'],
        "channel_id": 4,
        "u_id": b_reg['u_id']
    }
    response = requests.post(urls['channel_addowner'], json=data)
    assert response.status_code == 400


def test_channel_add_already_owner(urls, _pre_setup_):
    ''' try to add someone who is already an owner so raise error input '''
    __, a_reg, b_reg, __, a_channel_id, __, __ = _pre_setup_
    data = {
        "token": a_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "u_id": b_reg['u_id']
    }

    requests.post(urls['channel_addowner'], json=data)
    response = requests.post(urls['channel_addowner'], json=data)
    assert response.status_code == 400


def test_channel_add_by_wrong_owner(urls, _pre_setup_):
    ''' an unauthorised owner trying to add an owner so raise access error '''

    __, __, __, c_reg, a_channel_id, __, __ = _pre_setup_
    data = {
        "token": c_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "u_id": c_reg['u_id']
    }

    response = requests.post(urls['channel_addowner'], json=data)
    assert response.status_code == 400


def test_channel_add_by_none_owner(urls, _pre_setup_):
    ''' not an owner of flock trying to add owner so raises access error'''
    __, __, __, c_reg, a_channel_id, __, __ = _pre_setup_
    data = {
        "token": 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9'
                 '.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        "channel_id": a_channel_id['channel_id'],
        "u_id": c_reg['u_id']
    }
    response = requests.post(urls['channel_addowner'], json=data)
    assert response.status_code == 400


def test_add_by_main_owner(urls, _pre_setup_):
    ''' the owner of flock can add owner '''
    owner_reg, a_reg, __, c_reg, a_channel_id, __, __ = _pre_setup_
    data1 = {
        "token": owner_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "u_id": c_reg['u_id']
    }
    data2 = {
        "token": c_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "u_id": a_reg['u_id']
    }
    requests.post(urls['channel_addowner'], json=data1)
    #if the person becomes owner able to remove another owner. if no error means was able to
    response = requests.post(urls['channel_removeowner'], json=data2)
    assert response.status_code == 200


def test_fail_add_by_main_owner(urls, _pre_setup_):

    '''main owner trying to add to invalid channel raises input error'''
    owner_reg, __, __, c_reg, __, __, __ = _pre_setup_
    data = {
        "token": owner_reg['token'],
        "channel_id": 4,
        "u_id": c_reg['u_id']
    }
    response = requests.post(urls['channel_addowner'], json=data)
    assert response.status_code == 400


def test_cant_add_by_main_owner(urls, _pre_setup_):
    '''owner of flock trying to add someone already an owner raises input error'''

    owner_reg, a_reg, __, __, a_channel_id, __, __ = _pre_setup_
    data = {
        "token": owner_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "u_id": a_reg['u_id']
    }
    response = requests.post(urls['channel_addowner'], json=data)
    assert response.status_code == 400


def test_channel_remove_owner(urls, _pre_setup_):

    '''valid owner removes another owner'''
    __, a_reg, b_reg, __, a_channel_id, __, __ = _pre_setup_
    data = {
        "token": a_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "u_id": b_reg['u_id']
    }
    data1 = {
        "token": a_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "u_id": a_reg['u_id']
    }
    data2 = {
        "token": a_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "u_id": b_reg['u_id']
    }
    requests.post(urls['channel_addowner'], json=data)
    requests.post(urls['channel_removeowner'], json=data1)
    #if owner removed properly wont be able to add anyone else to channel
    response = requests.post(urls['channel_addowner'], json=data2)
    assert response.status_code == 400


def test_invalid_channel_remove_owner(urls, _pre_setup_):
    '''try to add to invalid channel so raises input error'''
    __, a_reg, b_reg, __, __, __, __ = _pre_setup_
    data = {
        "token": a_reg['token'],
        "channel_id": 4,
        "u_id": b_reg['u_id']
    }
    response = requests.post(urls['channel_removeowner'], json=data)
    assert response.status_code == 400


def test_channel_remove_invalid_owner(urls, _pre_setup_):
    '''the person being removed is not an owner so raises input error'''
    __, a_reg, b_reg, __, __, b_channel_id, __ = _pre_setup_
    data = {
        "token": a_reg['token'],
        "channel_id": b_channel_id['channel_id'],
        "u_id": b_reg['u_id']
    }

    response = requests.post(urls['channel_removeowner'], json=data)
    assert response.status_code == 400


def test_channel_remove_by_wrong_owner(urls, _pre_setup_):
    '''a non-owner trying to remove owner so raises access owner'''
    __, a_reg, __, c_reg, __, __, c_channel_id = _pre_setup_
    data = {
        "token": a_reg['token'],
        "channel_id": c_channel_id['channel_id'],
        "u_id": c_reg['u_id']
    }
    response = requests.post(urls['channel_removeowner'], json=data)
    assert response.status_code == 400


def test_channel_remove_by_none_owner(urls, _pre_setup_):
    '''trying to remove an unauthorised owner'''
    __, __, __, c_reg, __, __, c_channel_id = _pre_setup_
    data = {
        "token": 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        "channel_id": c_channel_id['channel_id'],
        "u_id": c_reg['u_id']
    }
    response = requests.post(urls['channel_removeowner'], json=data)
    assert response.status_code == 400


def test_remove_by_main_owner(urls, _pre_setup_):
    '''main owner of flock can remove owner'''
    owner_reg, a_reg, __, c_reg, a_channel_id, __, __ = _pre_setup_
    data1 = {
        "token": owner_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "u_id": a_reg['u_id']
    }
    data2 = {
        "token": a_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "u_id": c_reg['u_id']
    }
    join_data = {
        "token": owner_reg['token'],
        "channel_id": a_channel_id['channel_id']
    }
    requests.post(urls['channel_join'], json=join_data)
    requests.post(urls['channel_removeowner'], json=data1)
    # if the person is removed wont be able to add
    response = requests.post(urls['channel_addowner'], json=data2)
    assert response.status_code == 400


def test_fail_remove_by_main_owner(urls, _pre_setup_):
    '''main owner try to remove from invalid channel so raises input error'''
    owner_reg, a_reg, __, __, __, __, __ = _pre_setup_
    data = {
        "token": owner_reg['token'],
        "channel_id": 4,
        "u_id": a_reg['u_id']
    }
    response = requests.post(urls['channel_removeowner'], json=data)
    assert response.status_code == 400


def test_cant_remove_by_main_owner(urls, _pre_setup_):
    '''the main owner tries to remove someone who isnt owner so raises input error'''
    owner_reg, __, __, c_reg, a_channel_id, __, __ = _pre_setup_
    data = {
        "token": owner_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "u_id": c_reg['u_id']
    }
    response = requests.post(urls['channel_removeowner'], json=data)
    assert response.status_code == 400


def test_removing_mainowner(urls, _pre_setup_):
    '''can't remove the main flockr owner'''
    owner_reg, __, __, c_reg, __, __, c_channel_id = _pre_setup_
    data = {
        "token": c_reg['token'],
        "channel_id": c_channel_id['channel_id'],
        "u_id": owner_reg['u_id']
    }
    response = requests.post(urls['channel_removeowner'], json=data)
    assert response.status_code == 400

