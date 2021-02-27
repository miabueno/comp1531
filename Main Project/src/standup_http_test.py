'''
standup http tests
Compiled on 8 November 2020
standup_start, standup_active - Miriam Tuvel, z5257404
standup_send - Mia Bueno z5210209
'''

import json
import time
from datetime import datetime, timezone
from time import sleep

import pytest
import requests


@pytest.fixture
def _pre_setup_(urls, data_setup):
    '''
    fixture of registering two users
    '''
    requests.get(urls['other_clear'])

    # User Registration
    a_reg = requests.post(urls['auth_register'], json=data_setup[0]).json()
    b_reg = requests.post(urls['auth_register'], json=data_setup[1]).json()

    # Channel Creation
    ch_create_data = {"token": a_reg['token'], "name": "A", "is_public": True}
    a_channel_id = requests.post(urls['channels_create'], json=ch_create_data).json()
    ch_create_data['name'] = 'B'
    b_channel_id = requests.post(urls['channels_create'], json=ch_create_data).json()
    return a_reg, b_reg, a_channel_id, b_channel_id


#-----tests for standup_start
def test_startstandup_invalidtoken(url, _pre_setup_):
    '''raise an access error because it is an invalid token'''
    __, __, a_channel_id, __ = _pre_setup_
    data = {
        "token": 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                 'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        "channel_id": a_channel_id['channel_id'],
        "length": 120
    }
    response = requests.post(url + "standup/start", json=data)
    assert response.status_code == 400


def test_startstandup_invalidchannel(url, _pre_setup_):
    '''raise an input error because it is an invalid channel'''
    a_reg, __, __, __ = _pre_setup_
    data = {
        "token": a_reg['token'],
        "channel_id": 99999,
        "length": 120
    }
    response = requests.post(url + "standup/start", json=data)
    assert response.status_code == 400


def test_startstandup_alreadyactive(url, _pre_setup_):
    '''raise an input error because there is already an active standup'''
    a_reg, __, a_channel_id, __ = _pre_setup_
    data = {
        "token": a_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "length": 300
    }
    requests.post(url + "standup/start", json=data)
    #since already started this should raise error
    response = requests.post(url + "standup/start", json=data)
    assert response.status_code == 400


def test_startstandup(url, _pre_setup_):
    '''starts a standup in the channel'''
    a_reg, __, a_channel_id, __ = _pre_setup_
    data = {
        "token": a_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "length": 1
    }
    response = requests.post(url + "standup/start", json=data)
    beginning_time = int(time.time())
    assert json.loads(response.text) == {
        "time_finish": beginning_time + 1
    }


#------tests for standup_active-------


def test_standupactive_invalidtoken(url, _pre_setup_):
    '''raise an access error because it is an invalid token'''
    __, __, a_channel_id, __ = _pre_setup_
    data = {
        "token": 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                 'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        "channel_id": a_channel_id['channel_id']
    }
    response = requests.get(url + "standup/active", params=data)
    assert response.status_code == 400


def test_standupactive_invalidchannel(url, _pre_setup_):
    '''raise an input error if not valid channel'''
    a_reg, __, __, __ = _pre_setup_
    data = {
        "token": a_reg['token'],
        "channel_id": 999999
    }
    response = requests.get(url + "standup/active", params=data)
    assert response.status_code == 400


def test_standupactive_nonactive(url, _pre_setup_):
    '''function should return False if no active standup'''
    a_reg, __, a_channel_id, __ = _pre_setup_
    data = {
        "token": a_reg['token'],
        "channel_id": a_channel_id['channel_id']
    }
    response = requests.get(url + "standup/active", params=data)
    response = json.loads(response.text)
    assert response == {
        "is_active": False,
        "time_finish": None
    }


def test_standupactive_active(url, _pre_setup_):
    '''
    function should return True if active standup and other standup should
    be inactive
    '''
    a_reg, b_reg, a_channel_id, b_channel_id = _pre_setup_
    data0 = {
        "token": a_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "length": 180
    }
    data1 = {
        "token": a_reg['token'],
        "channel_id": a_channel_id['channel_id']
    }
    start_response = requests.post(url + "standup/start", json=data0)
    start_response = json.loads(start_response.text)
    active_response = requests.get(url + "standup/active", params=data1)
    assert json.loads(active_response.text) == {
        "is_active": True,
        "time_finish": start_response['time_finish']
    }
    data0 = {
        "token": b_reg['token'],
        "channel_id": b_channel_id['channel_id'],
        "length": 180
    }
    data1 = {
        "token": b_reg['token'],
        "channel_id": b_channel_id['channel_id']
    }
    active_response = requests.get(url + "standup/active", params=data1)
    assert json.loads(active_response.text) == {
        "is_active": False,
        "time_finish": None
    }


def test_standupactive_after(url, _pre_setup_):
    '''function should return False if active standup no longer'''
    a_reg, __, a_channel_id, __ = _pre_setup_
    data0 = {
        "token": a_reg['token'],
        "channel_id": a_channel_id['channel_id'],
        "length": 1
    }
    data1 = {
        "token": a_reg['token'],
        "channel_id": a_channel_id['channel_id']
    }
    requests.post(url + "standup/start", json=data0)
    sleep(3)
    active_response = requests.get(url + "standup/active", params=data1)
    assert json.loads(active_response.text) == {
        "is_active": False,
        "time_finish": None
    }


#------tests for standup_sendmessage----


@pytest.fixture
def _pre_setup(url):
    '''
    fixture of registering two users and two channels
    '''
    requests.get(url + 'other/clear')

    data_user_1 = {
        'email': "mia@gmail.com",
        'password': "miaiscool101",
        'name_first': "Mia",
        'name_last': "Bueno"

    }

    data_user_2 = {
        'email': "hayden@gmail.com",
        'password': "kittykat1269",
        'name_first': "Hayden",
        'name_last': "Smith"
    }

    user_1 = requests.post(url + "auth/register", json=data_user_1)
    user_1 = json.loads(user_1.text)

    user_2 = requests.post(url + "auth/register", json=data_user_2)
    user_2 = json.loads(user_2.text)

    data_ch_1 = {
        'token': user_1['token'],
        'name': "Channel 1",
        'is_public': True
    }

    data_ch_2 = {
        'token': user_2['token'],
        'name': "Channel 2",
        'is_public': False
    }

    channel_1 = requests.post(url + "channels/create", json=data_ch_1)
    channel_1 = json.loads(channel_1.text)['channel_id']

    channel_2 = requests.post(url + "channels/create", json=data_ch_2)
    channel_2 = json.loads(channel_2.text)['channel_id']

    standup_start_data = {
        'token': user_1['token'],
        'channel_id': channel_1,
        'length': 2
    }

    time_finish = requests.post(url + "standup/start", json=standup_start_data)
    time_finish = json.loads(time_finish.text)

    return user_1, user_2, channel_1, channel_2, time_finish['time_finish']


def test_standup_send_invalid_channel (url, _pre_setup):
    """
    standup_send - channel id invalid
    :params: token, channel_id, message
    :raise: InputError
    """

    token = _pre_setup[0]['token']

    standup_send_data = {
        'token': token,
        'channel_id': 99999,
        'message': "message"
    }

    response = requests.post(url + "standup/send", json=standup_send_data)
    assert response.status_code == 400


def test_standup_send_long_message(url, _pre_setup):
    """
    standup_send - message is too long (> 1000 char)
    :params: token, channel_id, message
    :raise: InputError
    """

    token, channel_id = _pre_setup[0]['token'], _pre_setup[2]

    standup_active_data = {
        'token': token,
        'channel_id': channel_id
    }

    active_response = requests.get(url + "standup/active", params=standup_active_data)
    assert json.loads(active_response.text)['is_active'] == True

    message_1000 = 'a' * 1002

    standup_send_data = {
        'token': token,
        'channel_id': channel_id,
        'message': message_1000
    }

    response = requests.post(url + "standup/send", json=standup_send_data)
    assert response.status_code == 400


def test_standup_send_inactive(url, _pre_setup):
    """
    standup_send - standup is not currently running
    :params: token, channel_id, message
    :raise: InputError
    """

    token, channel_id, time_finish = _pre_setup[0]['token'], _pre_setup[2], _pre_setup[4]

    standup_active_data = {
        'token': token,
        'channel_id': channel_id,
    }

    # check standup is currently active
    active_response = requests.get(url + "standup/active", params=standup_active_data)
    assert json.loads(active_response.text)['is_active'] == True

    time_now = int(time.time())
    time_diff = time_finish - time_now

    # delay for duration of time remaining
    sleep(time_diff + 1)

    # standup should now be finished, check no longer active
    active_response = requests.get(url + "standup/active", params=standup_active_data)
    assert json.loads(active_response.text)['is_active'] == False

    standup_send_data = {
        'token': token,
        'channel_id': channel_id,
        'message': "message"
    }

    response = requests.post(url + "standup/send", json=standup_send_data)
    assert response.status_code == 400


def test_standup_send_non_member(url, _pre_setup):
    """
    standup_send - token refers to uid not member of channel
    :params: token, channel_id, message
    :raise: AccessError
    """

    token_1, channel_2 = _pre_setup[0]['token'], _pre_setup[3]

    standup_send_data = {
        'token': token_1,
        'channel_id': channel_2,
        'message': "message"
    }

    response = requests.post(url + "standup/send", json=standup_send_data)
    assert response.status_code == 400


def test_standup_send_token_invalid(url, _pre_setup):
    """
    standup_send - token is an invalid token
    :params: token, channel_id, message
    :raise: AccessError
    """

    invalid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                    'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'

    standup_send_data = {
        'token': invalid_token,
        'channel_id': _pre_setup[2],
        'message': "message"
    }

    response = requests.post(url + "standup/send", json=standup_send_data)
    assert response.status_code == 400


def test_standup_send(url, _pre_setup):
    """
    standup_send - test successful implementation
    :params: token, channel_id, message
    :add to data storage: append to messages in standup dict
    :return: nothing
    """
    user_1, channel_id, time_finish = _pre_setup[0], _pre_setup[2], _pre_setup[4]

    standup_active_data = {
        'token': user_1['token'],
        'channel_id': channel_id,
    }

    # check standup is currently active
    active_response = requests.get(url + "standup/active", params=standup_active_data)
    assert json.loads(active_response.text)['is_active'] == True

    channel_messages_data = {
        'token': user_1['token'],
        'channel_id': channel_id,
        'start': 0
    }

    # check the messages in the current channel
    ch_msg_response = requests.get(url + "channel/messages", params=channel_messages_data)

    # ensure channel messages empty
    assert not json.loads(ch_msg_response.text)['messages']

    # remaining time of standup
    time_now = int(time.time())
    #time_now = round(datetime.now().replace(tzinfo=timezone.utc).timestamp())
    time_diff = time_finish - time_now

    # wait for half time
    sleep(time_diff/2)

    # parameters for standup/send
    message = "hello world!"

    standup_send_data = {
        'token': user_1['token'],
        'channel_id': channel_id,
        'message': message
    }

    # send a message during standup
    requests.post(url + "standup/send", json=standup_send_data)

    # wait for remaining time
    sleep((time_diff/2) + 2)

    # check standup is no longer active
    active_response = requests.get(url + "standup/active", params=standup_active_data)
    assert json.loads(active_response.text)['is_active'] == False

    # collect detail about user
    user_profile_data = {
    	'token': user_1['token'],
        'u_id': user_1['u_id']
    }

    # using user profile data, collect first name
    user_profile = requests.get(url + "user/profile", params=user_profile_data)
    user_1_name = json.loads(user_profile.text)['user']['handle_str']

    # what the expected collated message is
    expected_data = f"{user_1_name}: {message}"

    # collect channel's most recent messages
    ch_msg_response = requests.get(url + "channel/messages", params=channel_messages_data)
    assert json.loads(ch_msg_response.text)['messages'][0]['message'] == expected_data
