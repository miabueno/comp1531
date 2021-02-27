""" This module is for testing http routes of message.py

    ONLY test for normal behavior and errors.

    Edge cases should be tested in separate functionality tests in
    message_test.py

    Fixtures in conftest.py, no import needed.
    msg_data calls msg_setup already.

@author:
Yiyang Huang (message/send, message/remove, message/react, message/unreact)
Yue Dai (message/edit)
Nont Fakungkun (message_pin / message_unpin)

@date 2020/10/17 (iteration_2)
@date 2020/11/04 (iteration_3)
"""


# Libraries
import json
import requests
import time
import pytest


def test_msg_send(msg_setup, urls, send_one_msg, msg_data):
    """ Test the normal behavior of message/send.
        Only 1 message sent in send_one_msg, thus channel/messages's returned
        list should have index 0 to be the message 'Changed in send_one_msg'.
    """

    user_1 = msg_setup[0]
    ch_msg_data = msg_data['ch_msgs']
    msg_list = requests.get(urls['channel_messages'], params=ch_msg_data).json()

    assert msg_list['messages'][0]['message'] == "Hello World!"
    assert int(msg_list['messages'][0]['u_id']) == int(user_1['u_id'])
    assert int(msg_list['messages'][0]['message_id']) == send_one_msg


def test_msg_send_input_error(urls, msg_data):
    """ Test if message/send returns InputError
        The message is more than 1000 char.

        :Exception: InputError
    """

    requests.get(urls['other_clear'])
    error_data = msg_data['msg_send']
    error_data['message'] = 'a' * 1005

    assert requests.post(urls['message_send'], json=error_data).status_code == 400


def test_msg_send_access_error(urls, msg_data):
    """ Test if message/send returns AcessError
        The authorized user is not in the channel

        :Exception: AccessError
    """

    requests.get(urls['other_clear'])
    error_data = msg_data['msg_edit_invalid']

    return requests.post(urls['message_send'], json=error_data).status_code == 400


# ---------------------------------------------------------------------------------------------- #
# ------------------------------- http tests for message/remove -------------------------------- #
# ---------------------------------------------------------------------------------------------- #


def test_msg_remove(msg_setup, urls, send_one_msg, msg_data):
    """ Test the normal behavior of message/remove.
        Remove the only message sent by send_one_msg fixture.
        Basic sanity check only.
    """

    # Remove the only message in the channel_public
    requests.delete(urls['message_remove'], json=msg_data['msg_remove'])

    # Assert there is no message returned from channel/messages
    msg_list = requests.get(urls['channel_messages'], params=msg_data['ch_msgs']).json()
    assert len(msg_list['messages']) == 0


def test_msg_remove_input_error(msg_setup, urls, msg_data):
    """ Test if message/remove returns InputError when msg_id does not exist

        :Exception: InputError
    """

    msg_rm_data = msg_data['msg_remove']
    msg_rm_data['message_id'] = -99999

    return requests.delete(urls['message_remove'], json=msg_rm_data).status_code == 400


def test_msg_remove_access_error(msg_setup, urls, send_one_msg, msg_data):
    """ Test if message/remove returns AccessError:
            - user_2 didn't send any message in the channel AND
              user_2 is not an owner of the channel nor owner of the Flockr

        :Exception: AccessError
    """

    msg_rm_data = msg_data['msg_remove']
    msg_rm_data['token'] = msg_setup[1]['token']

    return requests.delete(urls['message_remove'], json=msg_rm_data).status_code == 400


# ---------------------------------------------------------------------------------------------- #
# -------------------------------- http tests for message/edit --------------------------------- #
# ---------------------------------------------------------------------------------------------- #


def test_message_edit_normal_behavior(msg_setup, send_one_msg, urls, msg_data):
    """ Test normal http behaviour of message_edit.
        Use channel/messages method to test if the message is being updated.
    """

    user_1, message_id = msg_setup[0], send_one_msg

    requests.put(urls['message_edit'], json=msg_data['msg_edit'])

    # Get a list of message from channel/messages method
    msgs = requests.get(urls['channel_messages'], params=msg_data['ch_msgs']).json()
    msg = msgs['messages'][0]

    assert int(msg['message_id']) == int(message_id)
    assert int(msg['u_id']) == int(user_1['u_id'])
    assert msg['message'] == "Updated message"


def test_message_edit_delete_msg(urls, msg_data):
    """ Test deleting the message if an emtpy string is passed inot message_edit.
        Use channel/messages method to test if the message is being updated.
    """

    msg_edit_data = msg_data['msg_edit']
    msg_edit_data['message'] = ""
    requests.put(urls['message_edit'], json=msg_edit_data)

    # Get a list of message from channel/messages method
    msgs = requests.get(urls['channel_messages'], params=msg_data['ch_msgs'])
    msg_list = msgs.json()

    assert msg_list['messages'] == []


def test_message_edit_access_error(urls, msg_data):
    """ Test raising Access Error with the http method.
        There are two ways to raise access error, see detailed
        test cases in unit testings in message_test.py.
        This test uses the case when the user (user_2) is not a member
        of the channel.
    """

    resp = requests.put(urls['message_edit'], json=msg_data['msg_edit_invalid'])
    assert resp.status_code == 400


# ---------------------------------------------------------------------------------------------- #
# ------------------------------- http tests for message/react --------------------------------- #
# ---------------------------------------------------------------------------------------------- #


def test_msg_react(msg_setup, urls, send_one_msg, msg_data):
    """ Testing for normal functioning of message/react.

        Only test the react_id == 1 cases, does not consider future
        implementation since this is a http sanity test.
    """

    user_1 = msg_setup[0]

    # user_1 reacts to the message that user_1 sent
    requests.post(urls['message_react'], json=msg_data['msg_react'])

    # user_1 calls channel_messages
    msg_list = requests.get(urls['channel_messages'], params=msg_data['ch_msgs']).json()
    reacts_list = msg_list['messages'][0]['reacts']

    tested = False
    for react in reacts_list:
        if react['react_id'] == 1:
            assert user_1['u_id'] in react['u_ids']
            assert react['is_this_user_reacted'] is True
            tested = True

    assert tested


def test_msg_react_invalid_msg_id(msg_setup, urls, msg_data):
    """ Testing for raising InputError if the message ID of the message
        that the authorized user want to react to is invalid.

        Raise:
            InputError
    """

    react_data = msg_data['msg_react']
    react_data['message_id'] = -9999

    assert requests.post(urls['message_react'], json=react_data).status_code == 400


def test_msg_react_invalid_react_id(msg_setup, urls, send_one_msg, msg_data):
    """ Testing for raising InputError if the react ID of the reactions
        is invalid. i.e. doesn't exists.

        Raise:
            InputError
    """

    react_data = msg_data['msg_react']
    react_data['react_id'] = -1

    assert requests.post(urls['message_react'], json=react_data).status_code == 400


def test_msg_react_double_react(msg_setup, urls, send_one_msg, msg_data):
    """ Testing for raising InputError if user reacts to the same message
        twice with the same reaction.

        Raise:
            InputError
    """

    react_data = msg_data['msg_react']
    requests.post(urls['message_react'], json=react_data)

    assert requests.post(urls['message_react'], json=react_data).status_code == 400


# ---------------------------------------------------------------------------------------------- #
# ------------------------------ http tests for message/unreact -------------------------------- #
# ---------------------------------------------------------------------------------------------- #


def test_msg_unreact(msg_setup, urls, send_one_msg, msg_data):
    """ Testing for normal functioning of message/unreact.

        Assume message/react is working.

        Only testing for basic sanity of msg/unreact, thus assume the only reaction
        available is react with React ID = 1.
    """

    user_1 = msg_setup[0]

    # user_1 reacted and unreacted to message with message ID 'msg_id'
    requests.post(urls['message_react'], json=msg_data['msg_react'])
    requests.post(urls['message_unreact'], json=msg_data['msg_react'])

    # user_1 calls channel_messages
    msg_list = requests.get(urls['channel_messages'], params=msg_data['ch_msgs']).json()
    reacts_list = msg_list['messages'][0]['reacts']

    tested = False
    for react in reacts_list:
        if react['react_id'] == 1:
            assert user_1['u_id'] not in react['u_ids']
            assert react['is_this_user_reacted'] is False
            tested = True

    assert tested


def test_msg_unreact_invalid_msg_id(msg_setup, urls, send_one_msg, msg_data):
    """ Testing for raising InputError message_id is not a valid
        message within a channel that the authorised user has joined.

        Raise:
            InputError
    """

    react_data = msg_data['msg_react']
    requests.post(urls['message_react'], json=react_data)
    react_data['message_id'] = -9999

    assert requests.post(urls['message_unreact'], json=react_data).status_code == 400


def test_msg_unreact_invalid_react_id(msg_setup, urls, send_one_msg, msg_data):
    """ Testing for raising InputError when react_id
        is not a valid React ID.

        Raise:
            InputError
    """

    react_data = msg_data['msg_react']
    requests.post(urls['message_react'], json=react_data)
    react_data['react_id'] = -9999

    assert requests.post(urls['message_unreact'], json=react_data).status_code == 400


def test_msg_unreact_unreacted(msg_setup, urls, send_one_msg, msg_data):
    """ Testing for raising InputError if user unreacts to an
        unreacted message.

        Raise:
            InputError
    """

    react_data = msg_data['msg_react']

    assert requests.post(urls['message_unreact'], json=react_data).status_code == 400


def test_message_pin_success(urls, msg_setup, send_msg_pin_unpin):
    """
    test for message is successfully pinned
    """

    user_1, __, channel_id, __ = msg_setup
    __, msg_2 = send_msg_pin_unpin

    pinning_msg_data = {
        "token": user_1['token'],
        "message_id": msg_2,
    }
    requests.post(urls['message_pin'], json=pinning_msg_data)
    messages_data = {
        "token": user_1['token'],
        "channel_id": channel_id,
        "start": 0
    }
    messages = requests.get(urls['channel_messages'], params=messages_data)
    messages = json.loads(messages.text)['messages']

    assert messages[0]['is_pinned'] is True


def test_message_pin_invalid_message(urls, msg_setup, send_msg_pin_unpin):
    """
    Test for invalid input message_id
    """
    user_1, __, __, __ = msg_setup
    __, msg_2 = send_msg_pin_unpin

    remove_msg_data = {
        "token": user_1['token'],
        "message_id": msg_2,
    }
    requests.delete(urls['message_remove'], json=remove_msg_data)

    pinning_msg_data = {
        "token": user_1['token'],
        "message_id": msg_2,
    }
    assert requests.post(urls['message_pin'], json=pinning_msg_data).status_code == 400


def test_message_pin_message_pinned(urls, msg_setup, send_msg_pin_unpin):
    """
    Test for the message is already pinned
    """
    user_1, __, __, __ = msg_setup
    msg_1, __ = send_msg_pin_unpin

    pinning_msg_data = {
        "token": user_1['token'],
        "message_id": msg_1,
    }
    assert requests.post(urls['message_pin'], json=pinning_msg_data).status_code == 400


def test_message_pin_invalid_token(urls, send_msg_pin_unpin):
    """
    Test for invalid token input
    """
    msg_2 = send_msg_pin_unpin[1]

    pinning_msg_data = {
        "token": 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                 'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        "message_id": msg_2,
    }
    assert requests.post(urls['message_pin'], json=pinning_msg_data).status_code == 400


def test_message_pin_not_in_channel(urls, send_msg_pin_unpin):
    """
    Test for the authorised user is not a member of the channel that the message is in
    """
    msg_2 = send_msg_pin_unpin[1]

    user_3_data = {
        "email": "z3333333@ad.unsw.edu.au",
        "password": "Password3",
        "name_first": "firstName3",
        "name_last": "lastName3"
    }
    user_3 = requests.post(urls['auth_register'], json=user_3_data).json()

    pinning_msg_data = {
        "token": user_3['token'],
        "message_id": msg_2,
    }
    assert requests.post(urls['message_pin'], json=pinning_msg_data).status_code == 400


def test_message_pin_not_owner(urls, msg_setup, send_msg_pin_unpin):
    """
    Test for the authorised user is not an owner of the channel that the message is in
    """
    __, user_2, __, __ = msg_setup
    __, msg_2 = send_msg_pin_unpin

    pinning_msg_data = {
        "token": user_2['token'],
        "message_id": msg_2,
    }
    assert requests.post(urls['message_pin'], json=pinning_msg_data).status_code == 400


def test_message_unpin_success(urls, msg_setup, send_msg_pin_unpin):
    """
    test for message is successfully unpinned
    """
    user_1, __, channel_id, __ = msg_setup
    msg_1, __ = send_msg_pin_unpin

    unpinning_msg_data = {
        "token": user_1['token'],
        "message_id": msg_1,
    }
    requests.post(urls['message_unpin'], json=unpinning_msg_data)
    messages_data = {
        "token": user_1['token'],
        "channel_id": channel_id,
        "start": 0
    }
    messages = requests.get(urls['channel_messages'], params=messages_data)
    messages = json.loads(messages.text)['messages']
    assert messages[1]['is_pinned'] is False


def test_message_unpin_invalid_message(urls, msg_setup, send_msg_pin_unpin):
    """
    Test for invalid input message_id
    """
    user_1, __, __, __ = msg_setup
    msg_1, __ = send_msg_pin_unpin

    remove_msg_data = {
        "token": user_1['token'],
        "message_id": msg_1,
    }
    requests.delete(urls['message_remove'], json=remove_msg_data)

    unpinning_msg_data = {
        "token": user_1['token'],
        "message_id": msg_1,
    }
    assert requests.post(urls['message_unpin'], json=unpinning_msg_data).status_code == 400


def test_message_unpin_message_unpinned(urls, msg_setup, send_msg_pin_unpin):
    """
    Test for the message is already unpinned
    """
    user_1, __, __, __ = msg_setup
    __, msg_2 = send_msg_pin_unpin

    unpinning_msg_data = {
        "token": user_1['token'],
        "message_id": msg_2,
    }
    assert requests.post(urls['message_unpin'], json=unpinning_msg_data).status_code == 400


def test_message_unpin_invalid_token(urls, send_msg_pin_unpin):
    """
    Test for invalid token input
    """
    msg_1 = send_msg_pin_unpin[0]

    unpinning_msg_data = {
        "token": 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                 'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        "message_id": msg_1,
    }
    assert requests.post(urls['message_unpin'], json=unpinning_msg_data).status_code == 400


def test_message_unpin_not_in_channel(urls, send_msg_pin_unpin):
    """
    Test for the authorised user is not a member of the channel that the message is in
    """
    msg_1 = send_msg_pin_unpin[0]

    user_3_data = {
        "email": "z3333333@ad.unsw.edu.au",
        "password": "Password3",
        "name_first": "firstName3",
        "name_last": "lastName3"
    }
    user_3 = requests.post(urls['auth_register'], json=user_3_data).json()
    unpinning_msg_data = {
        "token": user_3['token'],
        "message_id": msg_1,
    }
    assert requests.post(urls['message_unpin'], json=unpinning_msg_data).status_code == 400


def test_message_unpin_not_owner(urls, msg_setup, send_msg_pin_unpin):
    """
    Test for the authorised user is not an owner of the channel that the message is in
    """
    __, user_2, __, __ = msg_setup
    msg_1, __ = send_msg_pin_unpin
    unpinning_msg_data = {
        "token": user_2['token'],
        "message_id": msg_1,
    }
    assert requests.post(urls['message_unpin'], json=unpinning_msg_data).status_code == 400

# --------------------------------------------------------------------------------------- #
# ---------------------------- Tests for message_send_later------------------------------ #
# --------------------------------------------------------------------------------------- #

def test_msg_send_later(msg_setup, urls, generate_timestamp, msg_data):
    """ Message_send_later - test successful implementation
    """

    msg_data['msg_send_later']['time_sent'] += generate_timestamp # + 5
    requests.post(urls['message_sendlater'], json=msg_data['msg_send_later'])

    channel_msg_data = msg_data['ch_msgs']
    resp = requests.get(urls['channel_messages'],
                            params=channel_msg_data).json()

    # Default message send by msg_data's parameter fixture: send_one_msg
    assert len(resp['messages']) == 1

    msg_send_now_data = msg_data['msg_send']
    requests.post(urls['message_send'], json=msg_send_now_data)

    # check channel messages
    resp = requests.get(urls['channel_messages'],
                            params=channel_msg_data).json()

    # Now 2 messages in the channel
    assert len(resp['messages']) == 2
    assert resp['messages'][0]['message'] == "Hello World!"

    # wait for 5 seconds so that message should be sent then
    time.sleep(5)

    # check channel messages
    resp = requests.get(urls['channel_messages'],
                            params=channel_msg_data).json()

    # Check now 3 messages in that chanenl
    assert len(resp['messages']) == 3
    assert resp['messages'][0]['message'] == "this message to be sent later"


def test_msl_invalid_channel(msg_setup, urls, generate_timestamp, msg_data):
    """ Message_send_later - channel id does not exist (invalid)
    :raises: InputError
    """

    msg_data['msg_send_later']['channel_id'] = 99999
    msg_data['msg_send_later']['time_sent'] += generate_timestamp

    resp = requests.post(urls['message_sendlater'], json=msg_data['msg_send_later'])
    assert resp.status_code == 400


def test_msl_invalid_length(msg_setup, urls, generate_timestamp, msg_data):
    """ message_send_later - message length too long (> 1000 char)
    :raises: InputError
    """

    msg_data['msg_send_later']['time_sent'] += generate_timestamp
    msg_data['msg_send_later']['message'] = "a" * 1002

    resp = requests.post(urls['message_sendlater'], json=msg_data['msg_send_later'])
    assert resp.status_code == 400


def test_msl_invalid_time(msg_setup, urls, generate_timestamp, msg_data):
    """ message_send_later - time_sent is in the past
    :raises: InputError
    """

    msg_data['msg_send_later']['time_sent'] = generate_timestamp - 5

    resp = requests.post(urls['message_sendlater'], json=msg_data['msg_send_later'])
    assert resp.status_code == 400


def test_msl_unauthorised_user(msg_setup, urls, generate_timestamp, msg_data):
    """ message_send_later - user is non member of channel
    :raises: AccessError
    """

    token, __ = msg_setup[1]['token'], msg_setup[3]
    msg_data['msg_send_later']['token'] = token

    resp = requests.post(urls['message_sendlater'], json=msg_data['msg_send_later'])
    assert resp.status_code == 400


def test_msl_token_invalid(msg_setup, urls, generate_timestamp, msg_data):
    """ message_send_later - token is invalid
    :raises: AccessError
    """

    msg_data['msg_send_later']['token'] = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'\
                                          'eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_'\
                                          'GW39f1IT3kECz_AhckQGVU'

    resp = requests.post(urls['message_sendlater'], json=msg_data['msg_send_later'])
    assert resp.status_code == 400


# ======== bonus feature message_broadcast ========


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
