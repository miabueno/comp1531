""" HTTP Tests for channels.py

21 / 10 / 2020
by Nont Fakungkun z5317972

"""
import json
import requests
import pytest

# pylint: disable=redefined-outer-name

@pytest.fixture
def pre_test_setup(urls):
    """ Pytest fixture that register users and create channels
        through http methods for testing.

        :params url: basic url of the server
        :return
        (dict): u_id and token of owner
        (dict): u_id and token of user_1
        (dict): return of channel_details for Channel_3
        (str):  given name of Channel_3
    """

    requests.get(urls['other_clear'])
    owner_data = {
        "email": "FLOCKR@gmail.com",
        "password": "Password",
        "name_first": "flock",
        "name_last": "owner"
    }
    u_data1 = {
        "email": "z1111111@ad.unsw.edu.au",
        "password": "password",
        "name_first": "Nont",
        "name_last": "Fakungkun"

    }
    # Register User, return token and uid
    owner = requests.post(urls['auth_register'], json=owner_data).json()
    user_1 = requests.post(urls['auth_register'], json=u_data1).json()

    ch_data1 = {
        "token": owner['token'],
        "name": "Channel_1",
        "is_public": True
    }
    ch_data2 = {
        "token": user_1['token'],
        "name": "Channel_2",
        "is_public": True
    }
    ch_data3 = {
        "token": owner['token'],
        "name": "Channel_3",
        "is_public": True
    }

    # Create channels
    __ = requests.post(urls['channels_create'], json=ch_data1)
    __ = requests.post(urls['channels_create'], json=ch_data2)
    channel_3 = requests.post(urls['channels_create'], json=ch_data3).json()

    ch_join_data = {
        'token': user_1['token'],
        'channel_id': channel_3['channel_id'],
    }
    requests.post(urls['channel_join'], json=ch_join_data)

    channel_details = requests.get(urls['channel_details'], params={
        "token": owner['token'],
        "channel_id": channel_3['channel_id']
    })
    channel_details = json.loads(channel_details.text)

    ch_3_name = ch_data3['name']
    return owner, user_1, channel_details, ch_3_name

# -------------------------- Tests for channels_list -------------------------- #


# Correct Behaviour
def test_channels_list(urls, pre_test_setup):
    """
    Test that channels_listall is working correctly
    The list length should be 3 since there are 2 channels that user_1 is member of
    """
    owner = pre_test_setup[0]

    channel_list = requests.get(urls['channels_list'], params={'token': owner['token'],})
    channel_list = json.loads(channel_list.text)

    expected = {'channels': [
        {
            'channel_id': 0,
            'name': 'Channel_1',
        },
        {
            'channel_id': 2,
            'name': 'Channel_3',
        }
    ]}
    # Check for channels' detail
    assert channel_list == expected


def test_channels_list_error(urls):
    """
    Test for error if invalid token is put
    """
    # Check AccessError when token is incorrect
    assert requests.get(urls['channels_list'], params={'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',}).status_code == 400

# -------------------------- Tests for channels_listall --------------------------


def test_channels_listall(urls, pre_test_setup):  # Correct Behaviour
    """
    Test that channels_listall is working correctly
    The list length should be 3 since there are 3 channels overall
    """
    user_1 = pre_test_setup[1]

    channel_list = requests.get(urls['channels_listall'], params={'token': user_1['token'],})
    channel_list = json.loads(channel_list.text)

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

def test_channels_listall_error(urls):
    """
    Test for error if invalid token is put
    """

    # Check AccessError when token is incorrect
    assert requests.get(urls['channels_listall'], params={'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',}).status_code == 400


# -------------------------- Tests for channels_create -------------------------- #

def test_channels_create_name(pre_test_setup):
    """
    Test that the created channel has a correct information
    """
    owner, user_1, channel_details, name = pre_test_setup

    assert channel_details['name'] == name
    assert owner['u_id'] in [each['u_id'] for each in channel_details['owner_members']]
    assert user_1['u_id'] in [each['u_id'] for each in channel_details['all_members']]


def test_channels_create_token_error(urls):
    """
    Test for AccessError if invalid token is put
    """
    data = {
        "token": 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                 'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        "name": "Channel_5",
        "is_public": True
    }
    # Check AccessError when token is incorrect
    assert requests.post(urls['channels_create'], json=data).status_code == 400



def test_channels_create_name_length_error(urls, pre_test_setup):
    """
    Test for InputError if the given name is > 20 Characters long
    """
    user_1 = pre_test_setup[1]
    data = {
        "token": user_1['token'],
        "name": "a_longggggggggggggggggg_name",
        "is_public": True
    }

    assert requests.post(urls['channels_create'], json=data).status_code == 400


def test_channels_create_is_public_error(urls, pre_test_setup):
    """
    Test for InputError if the name is already used
    """
    user_1 = pre_test_setup[1]
    data = {
        "token": user_1['token'],
        "name": "Channel_5",
        "is_public": "Somthing else"
    }
    # Check AccessError when is_public is incorrect
    assert requests.post(urls['channels_create'], json=data).status_code == 400
