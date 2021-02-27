""" Tests for channels.py

20 / 9 / 2020
by Nont Fakungkun z5317972

Reviewed tests
by Yiyang Huang z5313425
30 / 9 / 2020

"""

import pytest
import channel as ch
import channels as chs
import auth as au
import users_channels as uc
import other
import error

# pylint: disable=redefined-outer-name


# -------------------------- Tests for channels_list -------------------------- #


# Correct Behaviour
def test_channels_list():
    """
    Test that channels_listall is working correctly
    The list length should be 3 since there are 3 channels that user_1 is member of
    """
    # Provide a list of all channels (and details) that the authorised user is part of
    # user_id = 1
    other.clear()
    user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "Password123", "First", "Subject")
    token_1 = user_1['token']

    user_2 = au.auth_register("z2222222@ad.unsw.edu.au", "Password222", "Second", "Subject")
    token_2 = user_2['token']

    # assert the channel with the user as member is listed
    __ = chs.channels_create(token_1, 'Channel_1', True)['channel_id']
    __ = chs.channels_create(token_1, 'Channel_2', True)['channel_id']
    __ = chs.channels_create(token_2, 'Channel_3', True)['channel_id']
    __ = chs.channels_create(token_2, 'Channel_4', True)['channel_id']

    channel_list = chs.channels_list(token_2)
    expected = {'channels': [
        {
            'channel_id': 2,
            'name': 'Channel_3',
        },
        {
            'channel_id': 3,
            'name': 'Channel_4',
        }
    ]}
    # Check for channels' detail
    assert channel_list == expected


def test_channels_list_error():
    """
    Test for error if invalid token is put
    """
    other.clear()
    # Check AccessError when token is incorrect
    with pytest.raises(error.AccessError):  # Failing behaviour
        chs.channels_list('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                          'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU')


# -------------------------- Tests for channels_listall --------------------------


def test_channels_listall():  # Correct Behaviour
    """
    Test that channels_listall is working correctly
    The list length should be 3 since there are 3 channels overall
    """
    other.clear()
    user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "Password123", "Testing", "Subject")
    token_1 = user_1['token']

    user_2 = au.auth_register("z2222222@ad.unsw.edu.au", "Password222", "Second", "Subject")
    token_2 = user_2['token']

    # assert all channel is listed
    __ = chs.channels_create(token_1, 'Channel_1', True)['channel_id']
    __ = chs.channels_create(token_1, 'Channel_2', True)['channel_id']
    __ = chs.channels_create(token_2, 'Channel_3', True)['channel_id']

    channel_list = chs.channels_listall(token_2)
    expected = {'channels': [
        {
            'channel_id': 0,
            'name': 'Channel_1',
        },
        {
            'channel_id': 1,
            'name': 'Channel_2',
        },
        {
            'channel_id': 2,
            'name': 'Channel_3',
        }
    ]}
    # Check for channels' detail
    assert channel_list == expected


def test_channels_listall_error():
    """
    Test for error if invalid token is put
    """
    other.clear()
    # Check AccessError when token is incorrect
    with pytest.raises(error.AccessError):  # Failing Behaviour
        chs.channels_listall('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                             'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU')


# -------------------------- Tests for channels_create -------------------------- #


@pytest.fixture
def channels_create_action():  # Correct Behaviours
    """
    Fixture function that creates a new user and create a new channel
    Return: new user, the created channel's details, the given channel name
    """
    other.clear()
    name = 'new_channel'
    is_public = True

    user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "Password123", "Testing", "Subject")
    token_1 = user_1['token']
    user_2 = au.auth_register("z2222222@ad.unsw.edu.au", "Password222", "Testing-2", "Subject-2")
    token_2 = user_2['token']

    new_channel_id = chs.channels_create(token_1, name, is_public)['channel_id']
    ch.channel_join(token_2, new_channel_id)
    # assertion that new channel has created with correct details
    channel_details = ch.channel_details(token_1, new_channel_id)
    return user_1, channel_details, name, user_2


def test_channels_create_name(channels_create_action):
    """
    Test that the created channel has an identical name as given
    """
    other.clear()
    channel_details = channels_create_action[1]
    name = channels_create_action[2]
    assert channel_details['name'] == name


def test_channels_create_owner(channels_create_action):
    """
    Test that the creator is in owner list
    """
    other.clear()
    user_1 = channels_create_action[0]
    channel_details = channels_create_action[1]

    # as creator of the channel
    assert user_1['u_id'] in [each['u_id'] for each in channel_details['owner_members']]


def test_channels_create_member(channels_create_action):
    """
    Test that the creator is in member list
    """
    other.clear()
    user_2 = channels_create_action[3]
    channel_details = channels_create_action[1]
    # as creator of the channel
    assert user_2['u_id'] in [each['u_id'] for each in channel_details['all_members']]


def test_channels_create_token_error():
    """
    Test for AccessError if invalid token is put
    """
    other.clear()
    name = "Channel1"
    is_public = True

    # Check AccessError when token is incorrect
    with pytest.raises(error.AccessError):
        chs.channels_create('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                            'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU', name, is_public)


def test_channels_create_name_length_error():
    """
    Test for InputError if the given name is > 20 Characters long
    """
    other.clear()
    name = "abcdefghijklmnopqrstuv"
    is_public = True

    user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "Password123", "Testing", "Subject")
    token = user_1['token']

    with pytest.raises(error.InputError):
        chs.channels_create(token, name, is_public)


# def test_channels_create_name_unique_error():
#     """
#     Test for InputError if the name is already used
#     """
#     other.clear()
#     name = "The Channel"
#     is_public = True

#     user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "Password123", "Testing", "Subject")
#     token = user_1['token']

#     __ = chs.channels_create(token, name, is_public)

#     with pytest.raises(error.InputError):
#         chs.channels_create(token, name, is_public)


def test_channels_create_is_public_error():
    """
    Test for AccessError if invalid token is put
    """
    other.clear()
    name = "Channel1"
    is_public = "Somthing else"

    user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "Password123", "Testing", "Subject")
    token = user_1['token']

    # Check AccessError when is_public is incorrect
    with pytest.raises(error.InputError):
        chs.channels_create(token, name, is_public)
