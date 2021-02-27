""" This is the test of bonus functions in bonus.py

@author Yiyang Huang (z5313425)
@date 2020/11/15

message_broadcast

@author Nont Fakungkun (z5317972)
@date 2020/11/13
Reviewed by Yiyang Huang (z5313425)
"""

# Library
import pytest

# Files
import channel as ch
import channels as chs
import auth as au
import other as o
import message as msg
import error

import bonus as bn


@pytest.fixture
def bonus_setup():
    """ Fixture for clearing the data from previous tests,
        and creates: 2 users (user_1, user_2) 1 channel (channel_1)

        :return
        (int): token of user_1
        (int): token of user_2
        (int): channel id of channel_1
    """

    o.clear()
    # Register User, return token and uid
    owner = au.auth_register("z0000000@ad.unsw.edu.au", "passWord2",
                             "Owner", "Owner")
    owner_token = owner['token']
    user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "passWord",
                              "First-Name", "Last-Name")
    token_1 = user_1['token']
    user_2 = au.auth_register("z2222222@ad.unsw.edu.au", "passWord",
                              "First-Name2", "Last-Name2")
    token_2 = user_2['token']

    # Create Channel, return channel id
    channel_1 = chs.channels_create(token_1, "Channel_1", True)['channel_id']
    return owner_token, token_1, token_2, channel_1


@pytest.fixture
def create_todo_list(bonus_setup):
    token_1, channel_1 = bonus_setup[1], bonus_setup[-1]
    bn.channel_todo_create(token_1, channel_1)
    return {}


def test_channel_todo_create_normal(bonus_setup):
    """ If successfully create a todo list in the channel,
        it will return {}
    """

    token_1, channel_1 = bonus_setup[1], bonus_setup[-1]
    resp = bn.channel_todo_create(token_1, channel_1)
    assert resp == {}

    with pytest.raises(error.InputError):
        bn.channel_todo_create(token_1, channel_1)


def test_channel_todo_create_input_error(create_todo_list, bonus_setup):
    """ If successfully create a todo list in the channel,
        it will return {}
    """

    token_1, channel_1 = bonus_setup[1], bonus_setup[-1]

    with pytest.raises(error.InputError):
        bn.channel_todo_create(token_1, channel_1)


def test_channel_todo_create_unauthorized(bonus_setup):
    """ If successfully create a todo list in the channel,
        it will return {}
    """

    channel_1 = bonus_setup[-1]
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.' \
            'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'

    with pytest.raises(error.AccessError):
        bn.channel_todo_create(token, channel_1)


def test_channel_todo_create_not_member(bonus_setup):
    """ If successfully create a todo list in the channel,
        it will return {}
    """

    token_2, channel_1 = bonus_setup[2], bonus_setup[-1]

    with pytest.raises(error.AccessError):
        bn.channel_todo_create(token_2, channel_1)


def test_channel_todo_show_normal(create_todo_list, bonus_setup):
    """
    """

    token_1, channel_1 = bonus_setup[1], bonus_setup[-1]
    bn.channel_todo_add(token_1, channel_1, "todo1", 0)
    todos = bn.channel_todo_show(token_1, channel_1, sort=False)
    assert len(todos['todos']) == 1
    assert todos['todos'][0]['message'] == 'todo1'


def test_channel_todo_show_sorted(create_todo_list, bonus_setup):
    """
    """

    token_1, channel_1 = bonus_setup[1], bonus_setup[-1]
    bn.channel_todo_add(token_1, channel_1, "todo1", 0)
    bn.channel_todo_add(token_1, channel_1, "todo2", 4)
    todos = bn.channel_todo_show(token_1, channel_1, sort=True)
    assert len(todos['todos']) == 2
    assert todos['todos'][0]['message'] == 'todo2'
    assert todos['todos'][-1]['message'] == 'todo1'


def test_channel_todo_show_empty(create_todo_list, bonus_setup):
    """
    """

    token_1, channel_1 = bonus_setup[1], bonus_setup[-1]
    todos = bn.channel_todo_show(token_1, channel_1, sort=True)
    assert len(todos['todos']) == 0
    assert not todos['todos']


def test_channel_todo_show_unauthorized(create_todo_list, bonus_setup):
    """
    """

    channel_1 = bonus_setup[-1]
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.' \
            'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'

    with pytest.raises(error.AccessError):
        bn.channel_todo_show(token, channel_1)


def test_channel_todo_show_not_member(create_todo_list, bonus_setup):
    """
    """

    token_2, channel_1 = bonus_setup[2], bonus_setup[-1]

    with pytest.raises(error.AccessError):
        bn.channel_todo_show(token_2, channel_1)


def test_channel_todo_show_no_list(bonus_setup):
    """
    """

    token_1, channel_1 = bonus_setup[1], bonus_setup[-1]

    with pytest.raises(error.InputError):
        bn.channel_todo_show(token_1, channel_1, False)


def test_channel_todo_add_normal(create_todo_list, bonus_setup):
    """
    """

    token_1, channel_1 = bonus_setup[1], bonus_setup[-1]
    todo_id = bn.channel_todo_add(token_1, channel_1, "todo1", 0)
    todos = bn.channel_todo_show(token_1, channel_1, sort=False)
    assert len(todos['todos']) == 1
    assert todos['todos'][0]['message'] == 'todo1'
    assert todos['todos'][0]['todo_id'] == todo_id['todo_id']
    assert todos['todos'][0]['status'] is False
    assert todos['todos'][0]['level'] == 0


def test_channel_todo_add_multiple(create_todo_list, bonus_setup):
    """
    """

    token_1, channel_1 = bonus_setup[1], bonus_setup[-1]

    for i in range(20):
        bn.channel_todo_add(token_1, channel_1, f"todo{i}", 0)

    todos = bn.channel_todo_show(token_1, channel_1, sort=False)
    assert len(todos['todos']) == 20

    for i in range(20):
        assert todos['todos'][i]['message'] == f'todo{i}'


def test_channel_todo_add_exceed_length(create_todo_list, bonus_setup):
    """
    """

    token_1, channel_1 = bonus_setup[1], bonus_setup[-1]
    with pytest.raises(error.InputError):
        bn.channel_todo_add(token_1, channel_1, "a" * 51, 0)


def test_channel_todo_add_invalid_level(create_todo_list, bonus_setup):
    """
    """

    token_1, channel_1 = bonus_setup[1], bonus_setup[-1]
    with pytest.raises(error.InputError):
        bn.channel_todo_add(token_1, channel_1, "ab", 8)

    with pytest.raises(error.InputError):
        bn.channel_todo_add(token_1, channel_1, "a", -2)


def test_channel_todo_add_unauthorized(create_todo_list, bonus_setup):
    """
    """

    channel_1 = bonus_setup[-1]
    token_1 = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.' \
            'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'

    with pytest.raises(error.AccessError):
        bn.channel_todo_add(token_1, channel_1, "hi", 0)


def test_channel_todo_add_no_list(bonus_setup):
    """
    """

    token_1, channel_1 = bonus_setup[1], bonus_setup[-1]

    with pytest.raises(error.AccessError):
        bn.channel_todo_add(token_1, channel_1, "hi", 1)


def test_channel_todo_add_not_member(create_todo_list, bonus_setup):
    """
    """

    token_2, channel_1 = bonus_setup[2], bonus_setup[-1]

    with pytest.raises(error.AccessError):
        bn.channel_todo_add(token_2, channel_1, "hi", 0)

# ======== message_broadcast ========
# pylint: disable=redefined-outer-name

@pytest.fixture
def pre_test_setup_msg_bc():
    """ Fixture for clearing the data from previous tests, and creates:
            1. owner of the Flockr,
            2. normal user (user_1), user_1 joins the channel_1
            3. three channels
        :return (tuple):
            (dict) owner
            (dict) user_1
    """
    o.clear()

    owner = au.auth_register("z0000000@ad.unsw.edu.au", "passWord", "Owner_flockr", "Owner_flockr")
    user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "passWord", "First-Name", "Last-Name")
    channel_1 = chs.channels_create(owner['token'], "Channel_1", True)['channel_id']
    ch.channel_join(user_1['token'], channel_1)
    __ = chs.channels_create(owner['token'], "Channel_2", True)['channel_id']
    __ = chs.channels_create(owner['token'], "Channel_3", False)['channel_id']

    return owner, user_1


def test_message_broadcast_success(pre_test_setup_msg_bc):
    ''' testing case for successfully broadcast message to all channel '''
    owner = pre_test_setup_msg_bc[0]

    msg_broadcast_list = bn.message_broadcast(owner['token'], "Message to all channels")
    msg_broadcast_list = msg_broadcast_list['messages']
    msg_list = o.search(owner['token'], "Message to all channels")['messages']

    assert msg_list[0]['message_id'] == msg_broadcast_list[0]['message_id']
    assert msg_list[0]['u_id'] == owner['u_id']
    assert msg_list[0]['message'] == 'Message to all channels'

    assert msg_list[1]['message_id'] == msg_broadcast_list[1]['message_id']
    assert msg_list[1]['u_id'] == owner['u_id']
    assert msg_list[1]['message'] == 'Message to all channels'

    assert msg_list[2]['message_id'] == msg_broadcast_list[2]['message_id']
    assert msg_list[2]['u_id'] == owner['u_id']
    assert msg_list[2]['message'] == 'Message to all channels'


def test_message_broadcast_invalid_token():
    '''
    testing case for invalid token
    Return: AccessError
    '''
    invalid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.' \
                    'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'
    with pytest.raises(error.AccessError):
        __ = bn.message_broadcast(invalid_token, "Message")

def test_message_broadcast_not_owner(pre_test_setup_msg_bc):
    '''
    testing case for the authorised user is not owner of flockr
    Return: AccessError
    '''
    user_1 = pre_test_setup_msg_bc[1]

    with pytest.raises(error.AccessError):
        __ = bn.message_broadcast(user_1['token'], "Message")

def test_message_broadcast_message_too_long(pre_test_setup_msg_bc):
    '''
    testing case for message longer than 1000 characters
    Return: InputError
    '''
    owner = pre_test_setup_msg_bc[0]

    with pytest.raises(error.InputError):
        __ = bn.message_broadcast(owner['token'], "l" * 1005)
