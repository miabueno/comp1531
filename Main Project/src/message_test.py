"""
Created by:

Yiyang (Sophia) Huang (z5313425)
Yue (Yuelanda) Dai (z5310546)
Nont Fakungkun (z5317972)

Tests for message.py

message_remove, message_sent: Reviewed by Yue Dai. (13/10/2020)
message_edit: Reviewed by Yiyang Huang. (14/10/2020)
message_react, message_unreact: Reviewed by Yue Dai. (05/11/2020)
message_pin, message_unpin: Reviewed by Yiyang Huang (2020/11/05)
"""


# Libraries
from datetime import datetime, timezone
import time
from random import choice
import pytest

# Src files
import channel as ch
import channels as chs
import auth as au
import other as o
import message as msg
import error

# pylint: disable=redefined-outer-name
@pytest.fixture
def pre_test_setup():
    """ Fixture for clearing the data from previous tests, and creates:
            1. owner of the Flockr,
            2. normal users (user_1, user_2),
            3. two channels (channel_public, channel_private).
        :return (tuple):
            (dict) owner
            (dict) user_1
            (dict) user_2
            (int) channel_public's channel_id
            (int) channel_private's channel_id
    """

    o.clear()

    owner = au.auth_register("z0000000@ad.unsw.edu.au", "passWord", "Owner_flockr", "Owner_flockr")
    user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "passWord", "First-Name", "Last-Name")
    user_2 = au.auth_register("z2222222@ad.unsw.edu.au", "passWord", "First-Name2", "Last-Name2")
    channel_public = chs.channels_create(user_1['token'], "Channel_1", True)['channel_id']
    channel_private = chs.channels_create(user_1['token'], "Channel_2", False)['channel_id']

    return owner, user_1, user_2, channel_public, channel_private


@pytest.fixture
def empty_msg_list():
    """ Return empty msg_list from calling channel_message with start = 0.
    :return: (dict)
    """
    return {'end': -1, 'messages': [], 'start': 0}


@pytest.fixture
def all_react_ids(pre_test_setup):
    """ Return all the valid react_id(s) that Flockr have. Ensure that
        future changes to react_ids can be implemented without refactoring
        the tests.

        Assumption: Every message in every channel all have the same types of
        reactions avaible.

    Args:
        pre_test_setup (pytest.fixture):
            Let user_1 acquire the list of messages and its 'reacts' dictionary
            that contains react_id(s)

    Returns:
        react_ids (list): All the valid react_id(s)
    """

    token_1, channel_id = pre_test_setup[1]['token'], pre_test_setup[3]
    msg_id = msg.message_send(token_1, channel_id, "hello")['message_id']
    reacts_list = ch.channel_messages(token_1, channel_id, 0)['messages'][0]['reacts']
    msg.message_remove(token_1, msg_id)
    return [react['react_id'] for react in reacts_list]


@pytest.fixture
def msg_edit_pre_test_setup():
    """ Fixture for clearing the data from previous tests, and initialisation of data structures.
        Creates:
         - 4 users (owner, user_1, user_2, user_3)
         - 1 channel (channel_1)

    Returns:
        owner (dictionary): first key in the sub dictionary of the user dictionary
                            (personalised data structure for users)
                            The owner of the entire flockr
        user_1 (dictionary): one key in the sub dictionary of the user dictionary
                             owner of channel_1
        user_2 (dictionary): one key in the sub dictionary of the user dictionary
                             member of channel_1
        user_3 (dictionary): one key in the sub dictionary of the user dictionary
                             Not a member of channel_1
        channel_1 (int): the channel id of a unique channel
                         where user_1 is the owner and user_2 is a member of this channel
    """

    # Clear the data strucutre for both user and channels dictionary before each test
    o.clear()

    # first user is the owner of the flockr
    owner = au.auth_register("z0000000@ad.unsw.edu.au", "passWord", "Owner_flockr", "Owner_flockr")

    # Register User, return token and uid
    user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "passWord", "First-Name", "Last-Name")
    user_2 = au.auth_register("z2222222@ad.unsw.edu.au", "passWord", "First-Name2", "Last-Name2")
    user_3 = au.auth_register("z3333333@ad.unsw.edu.au", "passWord", "First-Name3", "Last-Name3")

    # User1 create 3 channels, return channel id
    channel_1 = chs.channels_create(user_1['token'], "Channel_1", True)['channel_id']

    # add user_2 as a member of channel_1
    ch.channel_join(user_2['token'], channel_1)

    return owner, user_1, user_2, user_3, channel_1


# --------------------------------------------------------------------------------------- #
# ----------------------------- Tests for message_send ---------------------------------- #
# --------------------------------------------------------------------------------------- #


def test_msg_send(pre_test_setup, generate_timestamp):
    """ Test the normal functioning of message_send
    """

    __, user_1, __, channel_public, __ = pre_test_setup
    token, uid = user_1['token'], user_1['u_id']
    timestamp = generate_timestamp

    msg_1 = msg.message_send(token, channel_public, "Hello world")['message_id']
    msg_2 = msg.message_send(token, channel_public, "Hello world twice")['message_id']
    msg_list = ch.channel_messages(token, channel_public, 0)

    assert len(msg_list['messages']) == 2
    assert msg_list['messages'][1]['message_id'] == msg_1
    assert msg_list['messages'][1]['u_id'] == uid
    assert msg_list['messages'][1]['message'] == 'Hello world'
    assert msg_list['messages'][1]['time_created'] == timestamp
    assert msg_list['messages'][0]['message_id'] == msg_2
    assert msg_list['messages'][0]['u_id'] == uid
    assert msg_list['messages'][0]['message'] == 'Hello world twice'
    assert abs(msg_list['messages'][0]['time_created'] - timestamp) < 5


def test_msg_empty(pre_test_setup):
    """ Test when user send an empty message

    Exception:
        InputError
    """
    __, user_1, __, channel_public, __ = pre_test_setup

    with pytest.raises(error.InputError):
        msg.message_send(user_1['token'], channel_public, "")


def test_msg_send_input_error(pre_test_setup):
    """ When message is longer than 1000 characters
    :return: InputError
    """

    __, user_1, __, channel_public, __ = pre_test_setup

    with pytest.raises(error.InputError):
        __ = msg.message_send(user_1['token'], channel_public, "l" * 1005)


def test_msg_send_access_error(pre_test_setup):
    """ when the user haven't joined the channel and
        try to send a message to the channel.
    :return: AccessError
    """

    __, __, user_2, channel_public, __ = pre_test_setup

    # user2 not in channel_public (channel was created by user_1)
    with pytest.raises(error.AccessError):
        __ = msg.message_send(user_2['token'], channel_public, "Hello World!")


def test_msg_send_owner_send_to_private(pre_test_setup, generate_timestamp):
    """ Test if owner of the Flockr can send message to a private channel.
    """

    owner, __, __, __, channel_private = pre_test_setup
    owner_token, owner_uid = owner['token'], owner['u_id']
    timestamp = generate_timestamp

    ch.channel_join(owner_token, channel_private)
    msg_1 = msg.message_send(owner_token, channel_private, "Hello world")['message_id']
    msg_list = ch.channel_messages(owner_token, channel_private, 0)

    assert len(msg_list['messages']) == 1
    assert msg_list['messages'][0]['message_id'] == msg_1
    assert msg_list['messages'][0]['u_id'] == owner_uid
    assert msg_list['messages'][0]['message'] == 'Hello world'
    assert abs(msg_list['messages'][0]['time_created'] - timestamp) < 5


# --------------------------------------------------------------------------------------- #
# ----------------------------- Tests for message_remove -------------------------------- #
# --------------------------------------------------------------------------------------- #


def test_msg_remove(pre_test_setup, generate_timestamp):
    """ Given a message_id for a message,
        this message is removed from the channel
    """

    __, user_1, __, channel_public, __ = pre_test_setup
    token, uid = user_1['token'], user_1['u_id']
    timestamp = generate_timestamp

    msg_1 = msg.message_send(token, channel_public, "Hello world")['message_id']
    msg_2 = msg.message_send(token, channel_public, "Hello world twice")['message_id']
    msg.message_remove(token, msg_1)
    msg_list = ch.channel_messages(token, channel_public, 0)

    assert len(msg_list['messages']) == 1
    assert msg_list['messages'][0]['message_id'] == msg_2
    assert msg_list['messages'][0]['u_id'] == uid
    assert msg_list['messages'][0]['message'] == 'Hello world twice'
    assert abs(msg_list['messages'][0]['time_created'] - timestamp) < 5


def test_msg_remove_middle_message(pre_test_setup, generate_timestamp):
    """ Test if it can correctly remove the message sent in between other messages.
    """

    __, user_1, user_2, channel_public, __ = pre_test_setup
    token_1, uid_1 = user_1['token'], user_1['u_id']
    token_2 = user_2['token']
    ch.channel_join(token_2, channel_public)
    timestamp = generate_timestamp

    msg_1 = msg.message_send(token_1, channel_public, "Hello world")['message_id']
    __ = msg.message_send(token_1, channel_public, "Hello world two")['message_id']
    msg_3 = msg.message_send(token_2, channel_public, "Hello world three")['message_id']
    __ = msg.message_send(token_2, channel_public, "Hello world four")['message_id']
    __ = msg.message_send(token_2, channel_public, "Hello world five")['message_id']

    msg.message_remove(token_2, msg_3)
    msg_list = ch.channel_messages(token_2, channel_public, 0)

    assert len(msg_list['messages']) == 4
    assert msg_3 not in [each['message_id'] for each in msg_list['messages']]
    assert msg_list['messages'][3]['message_id'] == msg_1
    assert msg_list['messages'][3]['u_id'] == uid_1
    assert msg_list['messages'][3]['message'] == 'Hello world'
    assert abs(msg_list['messages'][3]['time_created'] - timestamp) < 5


def test_msg_remove_last_message(pre_test_setup, empty_msg_list):
    """ Normal user remove the last message in the channelm, sent by user itself.
    """
    __, user_1, __, channel_public, __ = pre_test_setup
    token_1 = user_1['token']

    msg_1 = msg.message_send(token_1, channel_public, "Hello world")['message_id']
    msg_2 = msg.message_send(token_1, channel_public, "Hello world two")['message_id']
    msg.message_remove(token_1, msg_1)
    msg.message_remove(token_1, msg_2)

    assert empty_msg_list == ch.channel_messages(token_1, channel_public, 0)


def test_msg_remove_is_channel_owner(pre_test_setup, empty_msg_list):
    """ The user (owner of the channel)  is trying to remove the message
    """

    __, user_1, user_2, channel_public, __ = pre_test_setup
    token_1, token_2, uid_2 = user_1['token'], user_2['token'], user_2['u_id']

    # user 1 send the message. user 1 is owner of the channel with id channel_public
    msg_1 = msg.message_send(token_1, channel_public, "Hello world")['message_id']

    # add user 2 as the owner of channel_public, user 2 remove the message sent by user 1
    ch.channel_addowner(token_1, channel_public, uid_2)
    msg.message_remove(token_2, msg_1)

    assert empty_msg_list == ch.channel_messages(token_1, channel_public, 0)


def test_msg_remove_is_flockr_owner(pre_test_setup, empty_msg_list):
    """ Owner of flockr is trying to remove the message.
    """

    owner, user_1, __, channel_public, __ = pre_test_setup
    token_1, token_f = user_1['token'], owner['token']

    msg_1 = msg.message_send(token_1, channel_public, "Hello world")['message_id']
    msg.message_remove(token_f, msg_1)

    assert empty_msg_list == ch.channel_messages(token_1, channel_public, 0)


def test_msg_remove_input_error_negative(pre_test_setup):
    """ When the msg_id exceeds lower bound.
    :return: InputError
    """

    token_1 = pre_test_setup[1]['token']

    with pytest.raises(error.InputError):
        msg.message_remove(token_1, -1)


def test_msg_remove_input_error_over(pre_test_setup):
    """ When the msg_id exceeds upper bound.
    :return: InputError
    """

    token_1 = pre_test_setup[1]['token']

    with pytest.raises(error.InputError):
        msg.message_remove(token_1, 1231234151235125)


def test_msg_remove_input_error_double(pre_test_setup):
    """ When the msg_id is trying to be removed twice.
    :return: InputError
    """
    __, user_1, __, channel_public, __ = pre_test_setup
    token_1 = user_1['token']

    msg_1 = msg.message_send(token_1, channel_public, "Double remove this.")['message_id']
    msg.message_remove(token_1, msg_1)

    with pytest.raises(error.InputError):
        msg.message_remove(token_1, msg_1)


def test_msg_remove_access_error(pre_test_setup):
    """ User is trying to remove the message not sent by owner
        and the authorised user is not owner of the channel/flockr.
    :return: AccessError
    """

    __, user_1, user_2, channel_public, __ = pre_test_setup
    token_1, token_2 = user_1['token'], user_2['token']

    ch.channel_join(token_2, channel_public)
    msg_1 = msg.message_send(token_1, channel_public, "Hello world")['message_id']

    # user2 is not an owner of channel_public and not an owner of flockr
    with pytest.raises(error.AccessError):
        msg.message_remove(token_2, msg_1)


# --------------------------------------------------------------------------------------- #
# ------------------------------- Tests for message_edit -------------------------------- #
# --------------------------------------------------------------------------------------- #


def test_msg_edit_input_error(msg_edit_pre_test_setup):
    """ When the new message is longer than 1000 characters
    Return:
        InputError
    """

    __, user_1, __, __, channel_1 = msg_edit_pre_test_setup

    with pytest.raises(error.InputError):
        __ = msg.message_edit(user_1['token'], channel_1, "l" * 1005)


def test_msg_edit_owner_self_msg(msg_edit_pre_test_setup):
    """ Test when the owner of the channel edited message sent by themselves,
        where the given message is only edited but not deleted.
    """

    __, user_1, __, __, channel_1 = msg_edit_pre_test_setup
    token_1, uid_1 = user_1['token'], user_1['u_id']

    msg_id_1 = msg.message_send(token_1, channel_1, "message content 1")['message_id']
    msg_id_2 = msg.message_send(token_1, channel_1, "message content 2")['message_id']
    msg.message_edit(token_1, msg_id_1, "EDITED message content 1 by owner themselves")
    msg_list = ch.channel_messages(token_1, channel_1, 0)

    # Brief check, two messages sent in total in channel_1
    assert len(msg_list['messages']) == 2

    # msg_id_2 content latest message, remain unchanged
    assert msg_list['messages'][0]['message_id'] == msg_id_2
    assert msg_list['messages'][0]['u_id'] == uid_1
    assert msg_list['messages'][0]['message'] == 'message content 2'
    # msg_id_1 (older msg) content is updated
    assert msg_list['messages'][1]['message_id'] == msg_id_1
    assert msg_list['messages'][1]['u_id'] == uid_1
    assert msg_list['messages'][1]['message'] == 'EDITED message content 1 by owner themselves'


def test_msg_edit_mem_self_msg(msg_edit_pre_test_setup):
    """ Test when a member of the channel edited message sent by themselves,
        where the given message is only edited but not deleted.
        Message with message_id was sent by the authorised user making this request.
    """

    __, __, user_2, __, channel_1 = msg_edit_pre_test_setup
    token_2 = user_2['token']
    uid_2 = user_2['u_id']

    msg_id_1 = msg.message_send(token_2, channel_1, "message content 1")['message_id']
    msg.message_edit(token_2, msg_id_1, "EDITED message content 1 by original user")
    msg_list = ch.channel_messages(token_2, channel_1, 0)

    # msg_id_1 content is updated by authorised user (member of channel editing their own message)
    assert len(msg_list['messages']) == 1
    assert msg_list['messages'][0]['message_id'] == msg_id_1
    assert msg_list['messages'][0]['u_id'] == uid_2
    assert msg_list['messages'][0]['message'] == 'EDITED message content 1 by original user'


def test_msg_edit_owner_edit_mem(msg_edit_pre_test_setup):
    """ Test when an owner of the channel edited message sent by a member of the channel,
        where the given message is only edited but not deleted.
        The authorised user is an owner of this channel.
    """

    __, user_1, user_2, __, channel_1 = msg_edit_pre_test_setup
    token_1 = user_1['token']
    token_2, uid_2 = user_2['token'], user_2['u_id']

    # message 1 (msg_id_1) sent by user_2, who is a valid member of channel_1
    msg_id_1 = msg.message_send(token_2, channel_1, "message content 1")['message_id']

    # message 1 (msg_id_1) edited by user_1, who is an owner of channel_1
    msg.message_edit(token_1, msg_id_1, "EDITED message content 1 by owner of channel_1")

    # assumption made that the message (msg_id_1) is still considered to be sent by user_2
    msg_list = ch.channel_messages(token_2, channel_1, 0)

    # msg_id_1 content is updated by authorised user (owner of this channel, user_1)
    assert len(msg_list['messages']) == 1
    assert msg_list['messages'][0]['message_id'] == msg_id_1
    assert msg_list['messages'][0]['u_id'] == uid_2
    assert msg_list['messages'][0]['message'] == 'EDITED message content 1 by owner of channel_1'


def test_msg_edit_owner_edit_owner(msg_edit_pre_test_setup):
    """ Test when owner trying to edit message from another owner of the channel
        where the given message is only edited but not deleted.
        The authorised user is the owner of channel_1.
    """

    __, user_1, user_2, __, channel_1 = msg_edit_pre_test_setup
    token_1, uid_1 = user_1['token'], user_1['u_id']
    token_2, uid_2 = user_2['token'], user_2['u_id']

    # user_1 (owner of channel_1) making user_2 an owner of channel_1
    ch.channel_addowner(token_1, channel_1, uid_2)
    # message 1 (msg_id_1) sent by user_1, who is an authenticated owner of channel_1
    msg_id_1 = msg.message_send(token_1, channel_1, "message by user_1 (owner)")['message_id']
    # message 1 (msg_id_1) edited by user_2, another owner of channel_1
    msg.message_edit(token_2, msg_id_1, "message edited by another owner of channel_1")

    msg_list = ch.channel_messages(token_1, channel_1, 0)

    # msg_id_1 content should be updated.
    assert len(msg_list['messages']) == 1
    assert msg_list['messages'][0]['message_id'] == msg_id_1
    assert msg_list['messages'][0]['u_id'] == uid_1
    assert msg_list['messages'][0]['message'] == 'message edited by another owner of channel_1'


def test_msg_edit_mem_edit_owner(msg_edit_pre_test_setup):
    """ Test when a authorised member of the channel edited message sent by an owner.
        This will raise an AccessError.

    Returns:
        AccessError: A type of error defined in error.py
    """

    __, user_1, user_2, __, channel_1 = msg_edit_pre_test_setup
    token_1 = user_1['token']
    token_2 = user_2['token']

    # user_1 (owner of this channel) sent the message with msg_id msg_1
    msg_1 = msg.message_send(token_1, channel_1, "message content 1")['message_id']

    # user_2 tries to edit message with id msg_id_1
    # user_2 (authorised member of channel_1) has no permissions
    # to edit messages by owners of channel_1 (user_1)
    with pytest.raises(error.AccessError):
        msg.message_edit(token_2, msg_1, "EDITED message content is invalid")


def test_msg_edit_mem_edit_mem(msg_edit_pre_test_setup):
    """ Test when a authorised member of the channel edited message sent by another member.
        This will raise an AccessError.

    Returns:
        AccessError: A type of error defined in error.py
    """

    __, __, user_2, user_3, channel_1 = msg_edit_pre_test_setup
    token_3 = user_3['token']
    # make user_3 a member of channel_1
    ch.channel_join(token_3, channel_1)

    # user_2 (member of this channel) sent the message with msg_id msg_1
    msg_1 = msg.message_send(user_2['token'], channel_1, "message sent by member")['message_id']

    # user_3 tries to edit message with id msg_id_1
    # user_3 (authorised member of channel_1), has no permissions
    # to edit messages sent by another member (uesr_2) of the channel
    with pytest.raises(error.AccessError):
        msg.message_edit(token_3, msg_1, "invalid edit of message by user_3")


def test_msg_edit_flockr_owner_edit_owner(msg_edit_pre_test_setup):
    """ Test when an owner of the entire flockr edited message sent by an owner of the channel,
        where the given message is only edited but not deleted.
        The authorised user is the owner of the entire flockr.
    """

    owner, user_1, __, __, channel_1 = msg_edit_pre_test_setup
    token_1, uid_1 = user_1['token'], user_1['u_id']
    # token of the owner of the flockr
    token_f = owner['token']

    # message 1 (msg_id_1) sent by user_1, who is an authenticated owner of channel_1
    msg_id_1 = msg.message_send(token_1, channel_1, "message content 1")['message_id']
    # message 1 (msg_id_1) edited by owner of flockr (token_f)
    msg.message_edit(token_f, msg_id_1, "EDITED message content 1 by owner of the flockr")
    msg_list = ch.channel_messages(token_1, channel_1, 0)

    # msg_id_1 content is updated by the owner of the entire flockr
    assert len(msg_list['messages']) == 1
    assert msg_list['messages'][0]['message_id'] == msg_id_1
    assert msg_list['messages'][0]['u_id'] == uid_1
    assert msg_list['messages'][0]['message'] == 'EDITED message content 1 by owner of the flockr'


def test_msg_edit_flockr_owner_edit_mem(msg_edit_pre_test_setup):
    """ Test when an owner of the entire flockr edited message sent by a member of the channel,
        where the given message is only edited but not deleted.
        The authorised user is the owner of the entire flockr.
    """

    owner, __, user_2, __, channel_1 = msg_edit_pre_test_setup
    token_2, uid_2 = user_2['token'], user_2['u_id']
    # token of the owner of the flockr
    token_f = owner['token']

    # message 1 (msg_id_1) sent by user_2, who is an authenticated member of channel_1
    msg_id_1 = msg.message_send(token_2, channel_1, "message content 1")['message_id']
    # message 1 (msg_id_1) edited by owner of flockr (token_f)
    msg.message_edit(token_f, msg_id_1, "EDITED message content 1 by owner of the flockr")
    msg_list = ch.channel_messages(token_2, channel_1, 0)

    # msg_id_1 content is updated by the owner of the entire flockr
    assert len(msg_list['messages']) == 1
    assert msg_list['messages'][0]['message_id'] == msg_id_1
    assert msg_list['messages'][0]['u_id'] == uid_2
    assert msg_list['messages'][0]['message'] == 'EDITED message content 1 by owner of the flockr'


def test_msg_edit_delete_msg1(msg_edit_pre_test_setup):
    """ Test when the new message is an empty string, the message will be deleted.
        There is only one message in the list of messages dictionary.
        The authorised user is the owner of the entire flockr.
    """

    __, user_1, __, __, channel_1 = msg_edit_pre_test_setup
    token_1 = user_1['token']

    # message 1 (msg_id_1) sent by user_1, who is an authenticated owner of channel_1
    msg_id_1 = msg.message_send(token_1, channel_1, "message content 1")['message_id']
    # message 1 (msg_id_1) edited by user_1 himslef, which is an empty string
    msg.message_edit(token_1, msg_id_1, "")
    msg_list = ch.channel_messages(token_1, channel_1, 0)

    # The message should be deleted entirely.
    assert len(msg_list['messages']) == 0


def test_msg_edit_delete_msg2(msg_edit_pre_test_setup):
    """ Test when the new message is an empty string, the message will be deleted.
        There are more than one message in the list of messages dictionaries.
        The authorised user is the owner of the entire flockr.
    """

    __, user_1, __, __, channel_1 = msg_edit_pre_test_setup
    token_1, uid_1 = user_1['token'], user_1['u_id']

    # message 1 (msg_id_1) sent by user_1, who is an authenticated owner of channel_1
    msg_id_1 = msg.message_send(token_1, channel_1, "message content 1")['message_id']
    msg_id_2 = msg.message_send(token_1, channel_1, "message content 2")['message_id']
    # message 1 (msg_id_1) edited by user_1 himslef, which is an empty string
    msg.message_edit(token_1, msg_id_1, "")
    msg_list = ch.channel_messages(token_1, channel_1, 0)

    # The message should be deleted entirely.
    # The first message will then become the message with id msg_id_2
    assert len(msg_list['messages']) == 1
    assert msg_list['messages'][0]['message_id'] == msg_id_2
    assert msg_list['messages'][0]['u_id'] == uid_1
    assert msg_list['messages'][0]['message'] == 'message content 2'


def test_msg_edit_not_mem(msg_edit_pre_test_setup):
    """ when the user is not an authorised member of the channel and
        tries to edit a message in the channel

    Return:
        AccessError: A type of error defined in error.py
    """

    __, user_1, __, user_3, channel_1 = msg_edit_pre_test_setup

    # message 1 (msg_id_1) sent by user_1, who is an authenticated owner of channel_1
    msg_id_1 = msg.message_send(user_1['token'], channel_1, "message content 1")['message_id']

    # user_3 is not a member of channel_1
    with pytest.raises(error.AccessError):
        __ = msg.message_edit(user_3['token'], msg_id_1, "Invalid edit of message")


# --------------------------------------------------------------------------------------- #
# ------------------------------- Tests for message_react ------------------------------- #
# --------------------------------------------------------------------------------------- #


def test_message_react(pre_test_setup, all_react_ids):
    """ Testing normal functionality of messasge_react()

        Owner send a message in channel with channel ID channel_1
        user_1 reacts to this message.
    """

    owner, user_1, __, channel_1, __ = pre_test_setup
    token_0, token_1, uid_1 = owner['token'], user_1['token'], user_1['u_id']

    ch.channel_join(token_0, channel_1)
    msg_id = msg.message_send(token_0, channel_1, "Hi")['message_id']

    # user_1 react in all kinds of reactions
    for react_id in all_react_ids:
        msg.message_react(token_1, msg_id, react_id)

    reacts_list_0 = ch.channel_messages(token_0, channel_1, 0)['messages'][0]['reacts']
    reacts_list_1 = ch.channel_messages(token_1, channel_1, 0)['messages'][0]['reacts']

    # Loop through channel_messages invoke by owner and user_1
    # and see if all reacts are recorded with correct information.
    for react_pair in zip(reacts_list_0, reacts_list_1):
        # user_1 reacted, thus in both lists
        assert uid_1 in react_pair[0]['u_ids'] and uid_1 in react_pair[1]['u_ids']
        # owner invoked reacts_list_0, owner not reacted, thus False.
        assert react_pair[0]['is_this_user_reacted'] is False
        # user_1 invoked reacts_list_1, user_1 reacted, thus True
        assert react_pair[1]['is_this_user_reacted'] is True


def test_message_react_no_reactions(pre_test_setup):
    """ Testing normal functionality of messasge_react() when the
        message has no reactions at all.

        'situation_1' and 'situation_2' used for future changes in
        deciding what is a valid return of message with no reactions.

        There might be 2 situations:
            1.  Initialize all the reactions' dictionaries inside 'react' list,
                but with no values in 'reacts'['u_ids'] at all.
                (What we used in our implementation of Flockr's message_react().)
            2.  'reacts' is an empty list.

        Test will pass if one situation returns True or both returns True.
    """

    __, user_1, __, channel_1, __ = pre_test_setup
    token_1 = user_1['token']

    msg.message_send(token_1, channel_1, "Hi")
    reacts_list = ch.channel_messages(token_1, channel_1, 0)['messages'][0]['reacts']

    # Situation 1: 'reacts' is an empty list
    situation_1 = situation_2 = len(reacts_list) == 0

    # Situation 2: 'reacts' is initialized with dict,
    # but 'reacts'['u_ids'] is an empty list
    if not situation_1:
        uid_list = [len(react['u_ids']) for react in reacts_list]
        situation_2 = sum(uid_list) == 0

    assert situation_1 or situation_2


def test_message_react_invalid_msg_id(pre_test_setup, all_react_ids):
    """ Test when message_id is not a valid message within a
    channel that the authorised user has joined.

    Raise:
        InputError
    """

    __, user_1, __, channel_1, __ = pre_test_setup
    token_1 = user_1['token']

    msg_id = msg.message_send(token_1, channel_1, "Hi")['message_id']
    msg.message_remove(token_1, msg_id)

    with pytest.raises(error.InputError):
        msg.message_react(token_1, msg_id, choice(all_react_ids))


def test_message_react_invalid_react_id(pre_test_setup, all_react_ids):
    """ React_id is not a valid React ID. The only valid react ID
        the frontend has is 1.

        Find the largest react_id in the list made of reacts' id,
        just in case if new react_id added.
        Thus the largest react_id + 1 must be invalid.

    Raise:
        InputError
    """

    __, user_1, __, channel_1, __ = pre_test_setup
    token_1 = user_1['token']

    msg_id = msg.message_send(token_1, channel_1, "Hi")['message_id']

    with pytest.raises(error.InputError):
        msg.message_react(token_1, msg_id, max(all_react_ids) + 1)


def test_message_react_same_reacts(pre_test_setup, all_react_ids):
    """ Message with ID message_id already contains an
        active React with ID react_id from the authorised user.

    Raise:
        InputError
    """

    __, user_1, __, __, channel_2 = pre_test_setup
    token_1 = user_1['token']

    msg_id = msg.message_send(token_1, channel_2, "Hi")['message_id']
    msg.message_react(token_1, msg_id, choice(all_react_ids))

    with pytest.raises(error.InputError):
        msg.message_react(token_1, msg_id, choice(all_react_ids))


# --------------------------------------------------------------------------------------- #
# ----------------------------- Tests for message_unreact ------------------------------- #
# --------------------------------------------------------------------------------------- #


def test_message_unreact(pre_test_setup, all_react_ids):
    """ Testing normal functionality of unreacting reacted message.
        Assume message_react is functioning.

        Currently passed because message_react() not implemented.

    Raise:
        InputError
    """

    owner, user_1, __, channel_1, __ = pre_test_setup
    token_0, token_1, uid_1 = owner['token'], user_1['token'], user_1['u_id']

    ch.channel_join(token_0, channel_1)
    msg_id = msg.message_send(token_0, channel_1, "Hi")['message_id']

    # user_1 reacts to the message sent by owner
    for react_id in all_react_ids:
        msg.message_react(token_1, msg_id, react_id)
        msg.message_unreact(token_1, msg_id, react_id)

    reacts_list_0 = ch.channel_messages(token_0, channel_1, 0)['messages'][0]['reacts']
    reacts_list_1 = ch.channel_messages(token_1, channel_1, 0)['messages'][0]['reacts']

    for react_pair in zip(reacts_list_0, reacts_list_1):
        # user_1 unreacted
        assert uid_1 not in react_pair[0]['u_ids'] and uid_1 not in react_pair[1]['u_ids']
        # owner and user_1 both not reacted, thus False.
        assert react_pair[0]['is_this_user_reacted'] is False
        assert react_pair[1]['is_this_user_reacted'] is False


def test_message_unreact_invalid_react_id(pre_test_setup, all_react_ids):
    """ Test when react_id is not a valid React ID.

    Raise:
        InputError
    """

    __, user_1, __, channel_1, __ = pre_test_setup
    token_1 = user_1['token']

    msg_id = msg.message_send(token_1, channel_1, "Hi")['message_id']
    msg.message_react(token_1, msg_id, choice(all_react_ids))

    with pytest.raises(error.InputError):
        msg.message_unreact(token_1, msg_id, max(all_react_ids) + 1)


def test_message_unreact_invalid_msg_id(pre_test_setup, all_react_ids):
    """ Testing when message_id is not a valid message within a channel
        that the authorised user has joined.

    Raise:
        InputError
    """

    __, user_1, __, channel_1, __ = pre_test_setup
    token_1 = user_1['token']

    msg_id = msg.message_send(token_1, channel_1, "Hi")['message_id']
    msg.message_react(token_1, msg_id, choice(all_react_ids))
    msg.message_remove(token_1, msg_id)

    with pytest.raises(error.InputError):
        msg.message_unreact(token_1, msg_id, choice(all_react_ids))


def test_message_unreact_unreacted_msg(pre_test_setup, all_react_ids):
    """ Test when message with ID message_id does not contain
        an active React with ID react_id.

    Raise:
        InputError
    """
    __, user_1, __, __, channel_2 = pre_test_setup
    token_1 = user_1['token']

    msg_id = msg.message_send(token_1, channel_2, "Hi")['message_id']

    with pytest.raises(error.InputError):
        msg.message_unreact(token_1, msg_id, choice(all_react_ids))


# --------------------------------------------------------------------------------------- #
# --------------------- Tests for message_pin and message_unpin ------------------------- #
# --------------------------------------------------------------------------------------- #


@pytest.fixture
def pre_test_setup_pin_unpin():
    """ Fixture for clearing the data from previous tests, and creates:
            1. owner of the Flockr,
            2. normal users (user_1, user_2), user_1 joins the channel
            3. one channel
            4. two messages 1. Pinned 2. Unpinned
        :return (tuple):
            (dict) owner
            (dict) user_1
            (dict) user_2
            (int) Channel_1's channel_id
    """
    o.clear()

    owner = au.auth_register("z0000000@ad.unsw.edu.au", "passWord", "Owner_flockr", "Owner_flockr")
    user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "passWord", "First-Name", "Last-Name")
    user_2 = au.auth_register("z2222222@ad.unsw.edu.au", "passWord", "First-Name2", "Last-Name2")
    channel_id = chs.channels_create(owner['token'], "Channel_1", True)['channel_id']
    ch.channel_join(user_1['token'], channel_id)

    msg_1 = msg.message_send(user_1['token'], channel_id, "pinned")['message_id']
    msg.message_pin(owner['token'], msg_1)
    msg_2 = msg.message_send(user_1['token'], channel_id, "unpinned")['message_id']

    return owner, user_1, user_2, channel_id, msg_1, msg_2


def test_message_pin_success(pre_test_setup_pin_unpin):
    """
    test for message is successfully pinned
    """
    owner, __, __, channel_id, __, msg_2 = pre_test_setup_pin_unpin

    msg.message_pin(owner['token'], msg_2)
    messages = ch.channel_messages(owner['token'], channel_id, 0)['messages']
    assert messages[0]['is_pinned'] is True


def test_message_pin_invalid_message(pre_test_setup_pin_unpin):
    """
    Test for invalid input message_id
    """
    owner, __, __, __, __, msg_2 = pre_test_setup_pin_unpin

    msg.message_remove(owner['token'], msg_2)
    with pytest.raises(error.InputError):  # Failing behaviour
        msg.message_pin(owner['token'], msg_2)


def test_message_pin_message_pinned(pre_test_setup_pin_unpin):
    """
    Test for the message is already pinned
    """
    owner, __, __, __, msg_1, __ = pre_test_setup_pin_unpin

    with pytest.raises(error.InputError):  # Failing behaviour
        msg.message_pin(owner['token'], msg_1)


def test_message_pin_invalid_token(pre_test_setup_pin_unpin):
    """
    Test for invalid token input
    """
    msg_2 = pre_test_setup_pin_unpin[5]

    with pytest.raises(error.AccessError):
        msg.message_pin('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                        'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU', msg_2)


def test_message_pin_not_in_channel(pre_test_setup_pin_unpin):
    """
    Test for the authorised user is not a member of the channel that
    the message is in.
    """
    __, __, user_2, __, __, msg_2 = pre_test_setup_pin_unpin

    with pytest.raises(error.AccessError):
        msg.message_pin(user_2['token'], msg_2)


def test_message_pin_not_owner(pre_test_setup_pin_unpin):
    """
    Test for the authorised user is not an owner of the channel that
    the message is in.
    """
    __, user_1, __, __, __, msg_2 = pre_test_setup_pin_unpin

    with pytest.raises(error.AccessError):
        msg.message_pin(user_1['token'], msg_2)


def test_message_unpin_success(pre_test_setup_pin_unpin):
    """
    test for message is successfully unpinned
    """
    owner, __, __, channel_id, msg_1, __ = pre_test_setup_pin_unpin

    msg.message_unpin(owner['token'], msg_1)
    messages = ch.channel_messages(owner['token'], channel_id, 0)['messages']
    assert messages[1]['is_pinned'] is False


def test_message_unpin_invalid_message(pre_test_setup_pin_unpin):
    """
    Test for invalid input message_id
    """
    owner, __, __, __, msg_1, __ = pre_test_setup_pin_unpin

    msg.message_remove(owner['token'], msg_1)
    with pytest.raises(error.InputError):
        msg.message_unpin(owner['token'], msg_1)


def test_message_unpin_message_unpinned(pre_test_setup_pin_unpin):
    """
    Test for the message is already unpinned
    """
    owner, __, __, __, __, msg_2 = pre_test_setup_pin_unpin

    with pytest.raises(error.InputError):
        msg.message_unpin(owner['token'], msg_2)


def test_message_unpin_invalid_token(pre_test_setup_pin_unpin):
    """
    Test for invalid token input
    """
    msg_1 = pre_test_setup_pin_unpin[4]

    with pytest.raises(error.AccessError):
        msg.message_unpin('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                          'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU', msg_1)


def test_message_unpin_not_in_channel(pre_test_setup_pin_unpin):
    """
    Test for the authorised user is not a member of the channel that the message is in
    """
    __, __, user_2, __, msg_1, __ = pre_test_setup_pin_unpin

    with pytest.raises(error.AccessError):
        msg.message_unpin(user_2['token'], msg_1)


def test_message_unpin_not_owner(pre_test_setup_pin_unpin):
    """
    Test for the authorised user is not an owner of the channel that the message is in
    """
    __, user_1, __, __, msg_1, __ = pre_test_setup_pin_unpin

    with pytest.raises(error.AccessError):
        msg.message_unpin(user_1['token'], msg_1)


# --------------------------------------------------------------------------------------- #
# ---------------------------- Tests for message_send_later------------------------------ #
# --------------------------------------------------------------------------------------- #


def test_msg_send_later(pre_test_setup):
    """
    message_send_later - test successful implementation
    :params: token, channel_id, message, time_sent
    :add to data storage: message (at certain time)
    :return: message_id
    """
    token, channel_id = pre_test_setup[1]['token'], pre_test_setup[3]

    time_sent = ch.generate_timestamp() + 5
    message = "this message to be sent later"

    msg.message_send_later(token, channel_id, message, time_sent)
    assert not ch.channel_messages(token, channel_id, 0)['messages']

    time.sleep(5)

    assert ch.channel_messages(token, channel_id, 0)['messages'][0]['message'] == message


# message_send_later (msl)
def test_msg_send_later_complex(pre_test_setup):
    """
    message_send_later - test messages sent before scheduled time
    :params: token, channel_id, message, time_sent
    :add to data storage: message (at certain time)
    :return: message_id
    """
    token, channel_id = pre_test_setup[1]['token'], pre_test_setup[3]

    # current time + 5 sec
    time_sent = ch.generate_timestamp() + 5

    message_1 = "this message to be sent later"
    message_2 = "this will be the first message"
    message_3 = "this should be in the middle"

    # schedule message
    msg.message_send_later(token, channel_id, message_1, time_sent)

    # check messages in channel empty because none have been sent
    assert not ch.channel_messages(token, channel_id, 0)['messages']

    # the most recent message is now message_2
    msg.message_send(token, channel_id, message_2)
    assert ch.channel_messages(token, channel_id, 0)['messages'][0]\
            ['message'] == message_2

    time.sleep(1)

    # the most recent message is now message_3
    msg.message_send(token, channel_id, message_3)
    assert ch.channel_messages(token, channel_id, 0)['messages'][0]\
            ['message'] == message_3

    # wait for scheduled time
    time.sleep(5)

    # the most recent message is now message_2
    assert ch.channel_messages(token, channel_id, 0)['messages'][0]\
            ['message'] == message_1


def test_msl_invalid_channel(pre_test_setup):
    """
    message_send_later - channel id does not exist (invalid)
    :params: token, channel_id, message, time_sent
    :raises: InputError
    """
    token = pre_test_setup[0]['token']
    time_sent = ch.generate_timestamp() + 5

    with pytest.raises(error.InputError):
        msg.message_send_later(token, 999999, \
                            "this message to be sent later", time_sent)


def test_msl_invalid_length(pre_test_setup):
    """
    message_send_later - message length too long (> 1000 char)
    :params: token, channel_id, message, time_sent
    :raises: InputError
    """
    token, channel_id = pre_test_setup[1]['token'], pre_test_setup[3]
    time_sent = ch.generate_timestamp() + 5

    with pytest.raises(error.InputError):
        msg.message_send_later(token, channel_id, 'a' * 1002, time_sent)


def test_msl_invalid_time(pre_test_setup):
    """
    message_send_later - time_sent is in the past
    :params: token, channel_id, message, time_sent
    :raises: InputError
    """
    token, channel_id = pre_test_setup[1]['token'], pre_test_setup[3]

    # current time - 5 sec
    time_sent = ch.generate_timestamp() - 5

    with pytest.raises(error.InputError):
        msg.message_send_later(token, channel_id, \
                                "this message to be sent later", time_sent)


def test_msl_unauthorised_user(pre_test_setup):
    """
    message_send_later - user is non member of channel
    :params: token, channel_id, message, time_sent
    :raises: AccessError
    """

    token, channel_id = pre_test_setup[2]['token'], pre_test_setup[3]

    # current time + 5 sec
    time_sent = ch.generate_timestamp() + 5

    # this channel was created by user 1 but using user 2 token
    with pytest.raises(error.AccessError):
        msg.message_send_later(token, channel_id, \
                                "this message to be sent later", time_sent)


def test_msl_token_invalid(pre_test_setup):
    """
    message_send_later - token is invalid
    :params: token, channel_id, message, time_sent
    :raises: AccessError
    """
    invalid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'\
                    'eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'

    channel_id = pre_test_setup[3]

    # current time + 5 sec
    time_sent = ch.generate_timestamp() + 5

    message = "this message to be sent later"

    with pytest.raises(error.AccessError):
        msg.message_send_later(invalid_token, channel_id, message, time_sent)


# ======= bonus feature message_broadcast =======

@pytest.fixture
def pre_test_setup_bc():
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


def test_message_broadcast_success(pre_test_setup_bc):
    ''' testing case for successfully broadcast message to all channel '''
    owner = pre_test_setup_bc[0]

    msg_broadcast_list = msg.message_broadcast(owner['token'], "Message to all channels")
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
        __ = msg.message_broadcast(invalid_token, "Message")

def test_message_broadcast_not_owner(pre_test_setup_bc):
    '''
    testing case for the authorised user is not owner of flockr
    Return: AccessError
    '''
    user_1 = pre_test_setup_bc[1]

    with pytest.raises(error.AccessError):
        __ = msg.message_broadcast(user_1['token'], "Message")

def test_message_broadcast_message_too_long(pre_test_setup_bc):
    '''
    testing case for message longer than 1000 characters
    Return: InputError
    '''
    owner = pre_test_setup_bc[0]

    with pytest.raises(error.InputError):
        __ = msg.message_broadcast(owner['token'], "l" * 1005)
