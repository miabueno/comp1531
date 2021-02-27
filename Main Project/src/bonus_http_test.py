
""" This is the http test of bonus functions in bonus.py

@author Yiyang Huang (z5313425)
@date 2020/11/15

message_broadcast

@author Nont Fakungkun z5317972
@date 2020/11/13
Reviewed by Yiyang Huang z5313425
"""
import requests

# pylint: disable=redefined-outer-name


def test_message_broadcast_success_http(msg_setup, urls):
    ''' testing case for successfully broadcast message to all channel '''
    owner = msg_setup[0]

    bc_msg_data = {
        "token": owner['token'],
        "message": "Message to all channels",
    }
    msg_bc_list = requests.post(urls['message_broadcast'], json=bc_msg_data).json()['messages']
    search_msg_data = {
        "token": owner['token'],
        "query_str": "Message to all channels",
    }
    msg_list = requests.get(urls['other_search'], params=search_msg_data).json()['messages']

    assert msg_list[0]['message_id'] == msg_bc_list[0]['message_id']
    assert msg_list[0]['u_id'] == owner['u_id']
    assert msg_list[0]['message'] == "Message to all channels"

    assert msg_list[1]['message_id'] == msg_bc_list[1]['message_id']
    assert msg_list[1]['u_id'] == owner['u_id']
    assert msg_list[1]['message'] == "Message to all channels"


def test_message_broadcast_invalid_token_http(urls):
    '''
    testing case for invalid token
    Return: AccessError
    '''
    bc_msg_data = {
        "token": 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                 'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        "message": "message",
    }
    assert requests.post(urls['message_broadcast'], json=bc_msg_data).status_code == 400


def test_message_broadcast_not_owner_http(msg_setup, urls):
    '''
    testing case for the authorised user is not owner of flockr
    Return: AccessError
    '''
    user_2 = msg_setup[1]
    bc_msg_data = {
        "token": user_2['token'],
        "message": "message",
    }
    assert requests.post(urls['message_broadcast'], json=bc_msg_data).status_code == 400


def test_message_broadcast_message_too_long_http(msg_setup, urls):
    '''
    testing case for message longer than 1000 characters
    Return: InputError
    '''
    owner = msg_setup[0]
    bc_msg_data = {
        "token": owner['token'],
        "message": "l" * 1005,
    }
    assert requests.post(urls['message_broadcast'], json=bc_msg_data).status_code == 400
