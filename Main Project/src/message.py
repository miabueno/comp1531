"""
Created by:

Yiyang Huang (z5313425) [message_send, message_remove, message_react, message_unreact]
Yue Dai (z5310546) [message_edit]
Nont Fakungkun (z5317972) [message_pin, message_unpin]
Mia Bueno (z5210209) [message_send_later]

Reviewed by:

Yue Dai (z5310546) [message_send, message_remove, message_react, message_unreact]
Yiyang Huang (z5313425) [message_edit, message_pin, message_unpin]

"""


# Libraries
# from datetime import datetime, timezone
# import time

# Files
import users_channels as uc
import error
from channel import token_to_uid, is_global_owner, \
                    generate_timestamp, is_channel_id_valid, \
                    is_uid_valid, is_user_owner, is_user_member


# Helper functions

def search_all_msg(msg_id):
    """ Search for the specific message with id msg_id in the whole channel database.
    :param msg_id: the message_id of the message for searching
    :return:
        (tuple) Consists of 2 elements:
            - (int) channel_id that the msg located.
            - (int) index of the message in 'messages' list.
    :exception:
        InputError: msg_id does not exist
    """
    for channel_id, channel_info in uc.channel.items():
        for index, msg_list in enumerate(channel_info['messages']):
            if msg_list['message_id'] == msg_id:
                return int(channel_id), int(index)
    raise error.InputError("message ID doesn't exist.")


def search_own_msg(uid, msg_id):
    """ Determine if the message is sent by the user.
    :param uid: uid of the user
    :param msg_id: msg_id that the user want to locate
    :return: (boolean) True or False
    """
    return msg_id in uc.users[uid]['msg_sent']


def is_message_too_long(message):
    """ To determine if the message is too long

    Args:
        message (str)

    Raises:
        error.InputError: when message is > 1000 char in length
    """
    if len(message) > 1000:
        raise error.InputError("Message is too long.")


# Main Functions


def message_send(token, channel_id, message):
    """ Send a message from authorised_user to the channel specified by channel_id
    :param token: token of the authorized user
    :param channel_id: channel_id that the user want to send message to
    :param message: the message that user want to send.
    :return:
        (dict) {'message_id': 1,}
    :exception:
        InputError: any Message is more than 1000 characters or Message is an empty string ""
        AccessError: the authorised user has not joined the channel they are trying to post to
    """

    is_message_too_long(message)
    if message == "":
        raise error.InputError("Message can't be empty.")
    uid = token_to_uid(token)

    if not is_user_member(uid, channel_id) and \
        not is_user_owner(uid, channel_id):
        raise error.AccessError("You are not a member of the channel.")

    # Update in database
    msg_id = uc.TOTAL_MSG
    new_msg = {
        'message_id': msg_id,
        'u_id': uid,
        'message': message,
        'time_created': generate_timestamp(),
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
            }
        ],
        'is_pinned': False,
    }
    uc.channel[channel_id]['messages'].insert(0, new_msg)
    uc.users[uid]['msg_sent'].append(msg_id)
    uc.TOTAL_MSG += 1

    return {
        'message_id': msg_id,
    }


def message_remove(token, message_id):
    """ Given a message_id for a message, this message is removed from the channel.
    :param token: token of the authorized user
    :param message_id: message that want to be removed
    :return: (dict) {}
    :exception:
        InputError: message (based on ID) no longer exists
        AccessError:
            The authorized user is not an owner of the channel
            and not an owner of the flockr,
            and s/he is trying to remove the message is not sent by him/herself.
    """

    if message_id > uc.TOTAL_MSG or message_id < 0:
        raise error.InputError("Invalid message ID")

    uid = token_to_uid(token)
    channel_id, index = search_all_msg(message_id)

    msg_sender_uid = uc.channel[channel_id]['messages'][index]['u_id']

    if not search_own_msg(uid, message_id) and \
        not is_user_owner(uid, channel_id) and \
            not is_global_owner(uid):
        raise error.AccessError("Don't have the right to remove this message.")

    del uc.channel[channel_id]['messages'][index]
    uc.users[msg_sender_uid]['msg_sent'].remove(message_id)

    return {}


def message_edit(token, message_id, message):
    """ [Direct reference to specification]
        Given a message, update it's text with new text.
        If the new message is an empty string, the message is deleted.

    Parameters:
        token (str): token of the authenticated user editing the message
        message_id (int): the id of the message in the list that is to be edited
        message (str): the new text message that is replacing the old message at index message_id

    Returns:
        AccessError: (Direct refernce to the specification)
            - Message with message_id was sent by the authorised user making this request
            - The authorised user is an owner of this channel or the flockr
    """
    is_message_too_long(message)
    msg_id, new_msg = int(message_id), str(message)

    if new_msg == '': return message_remove(token, msg_id)

    uid = token_to_uid(token)
    channel_id, msg_index = search_all_msg(msg_id)

    if not search_own_msg(uid, message_id) and \
        not is_user_owner(uid, channel_id) and \
            not is_global_owner(uid):
        raise error.AccessError("Don't have the right to edit this message.")

    uc.channel[channel_id]['messages'][msg_index]['message'] = new_msg

    return {}


def reaction_logics(token, message_id, react_id, action_type):
    """ Helper function that contains the main logic
        of message_react and message_unreact

    Args:
        token (str): token of the authorized user
        message_id (int): message_id that user wants to action upon
        react_id (int): types of reaction
        type (int): 0 is unreact, 1 is react.

    Return:
        uid_list (list): list of uids in 'react'
        uid (int): uid of the current user

    Raises:
        error.InputError: [Invalid React ID]
        error.InputError: [User already reacted to the message]
        error.InputError: [User unreacts an unreacted message]
    """
    uid = token_to_uid(token)
    message_id, react_id = int(message_id), int(react_id)

    if react_id not in uc.REACTIONS:
        raise error.InputError("Invalid React ID")

    channel_id, msg_index = search_all_msg(message_id)
    uid_list = uc.channel[channel_id]['messages'][msg_index]['reacts'] \
                         [react_id - 1]['u_ids']

    if uid in uid_list and action_type == 1:
        raise error.InputError("User already reacted with same React ID.")

    if uid not in uid_list and action_type == 0:
        raise error.InputError("User not reacted to this message with" \
                               "this React ID.")
    return uid_list, uid


def message_react(token, message_id, react_id):
    """ Given a message within a channel the authorised user is part of,
        add a "react" to that particular message. (from spec)

    Assumption: If implementing new React ID, it will be added to the end of
                valid_react_ids' list.

    Return: {}

    Args:
        token (str): token of the authorized user.
        message_id (int): message_id of the message that user wants to react.
        react_id (int): id of a type of reactions provided by Flockr.

    Exceptions:
        InputError: when any one of them is True,
            1.  message_id is not a valid message within a channel
                that the authorised user has joined.
            2.  react_id is not a valid React ID. The only valid react
                ID the frontend has is 1. (currently)
            3.  Message with ID message_id already contains an active
                React with ID react_id from the authorised user.

    """
    uid_list, uid = reaction_logics(token, message_id, react_id, 1)
    uid_list.append(uid)
    return {}


def message_unreact(token, message_id, react_id):
    """ Given a message within a channel the authorised user
        is part of, remove a "react" to that particular message.
        (from spec)

    Return: {}

    Args:
        token (str): token of the authorized user.
        message_id (int): message ID of the message that user wants to unreact.
        react_id (int): ID of a type of reaction.

    Exceptions:
        InputError: when any one of them is True,
        1.  message_id is not a valid message within a channel that the
            authorised user has joined.
        2.  react_id is not a valid React ID.
        3.  Message with ID message_id does not contain an active React with
            ID react_id.

    """
    uid_list, uid = reaction_logics(token, message_id, react_id, 0)
    uid_list.remove(uid)
    return {}


def message_pin(token, message_id):
    """ [Direct reference to specification]
        Given a message within a channel, mark it as "pinned"
        to be given special display treatment by the frontend

    Parameters:
        token (str): token of the authenticated user pinning the message
        message_id (int): the id of the message in the list that is to be pinned

    Returns:
        {} if success
        InputError: (Direct refernce to the specification)
            - message_id is not a valid message
            - Message with ID message_id is already pinned
        AccessError: (Direct refernce to the specification)
            - Invalid token
            - The authorised user is not a member of the channel that the message
              is within
            - The authorised user is not an owner
    """

    msg_id = int(message_id)
    uid = token_to_uid(token)
    channel_id, msg_index = search_all_msg(msg_id)

    if uc.channel[channel_id]['messages'][msg_index]['is_pinned']:
        raise error.InputError(f"Message with ID {msg_id} is already pinned")

    if not is_user_member(uid, channel_id):
        raise error.AccessError("The authorised user is not a member of the "\
                                "channel that the message is within")
    if not is_user_owner(uid, channel_id):
        raise error.AccessError("The authorised user is not an owner")

    uc.channel[channel_id]['messages'][msg_index]['is_pinned'] = True

    return {}


def message_unpin(token, message_id):
    """ [Direct reference to specification]
        Given a message within a channel, remove it's mark as unpinned

    Parameters:
        token (str): token of the authenticated user unpinning the message
        message_id (int): the id of the message in the list that is to be unpinned

    Returns:
        {} if success
        InputError: (Direct refernce to the specification)
            - message_id is not a valid message
            - Message with ID message_id is already unpinned
        AccessError: (Direct refernce to the specification)
            - Invalid token
            - The authorised user is not a member of the channel that the message is within
            - The authorised user is not an owner
    """

    msg_id = int(message_id)
    uid = token_to_uid(token)
    channel_id, msg_index = search_all_msg(msg_id)

    if uc.channel[channel_id]['messages'][msg_index]['is_pinned'] is False:
        raise error.InputError(f"Message with ID {msg_id} is already unpinned")

    if not is_user_member(uid, channel_id):
        raise error.AccessError("The authorised user is not a member of the "\
                                "channel that the message is within")
    if not is_user_owner(uid, channel_id):
        raise error.AccessError("The authorised user is not an owner")

    uc.channel[channel_id]['messages'][msg_index]['is_pinned'] = False

    return {}


def message_send_later(token, channel_id, message, time_sent):
    """ Given time_sent, send a message at given time

    Parameters:
        token (str): token of the authenticated user unpinning the message,
        channel_id(int): channel id of channel message is being sent to,
        message(str): message that will be scheduled,
        time_sent(int): the timestamp of when the message is to be sent

    Returns:
        {message_id} if success
        InputError: (Direct refernce to the specification)
            - message_id is not a valid message
            - Message with ID message_id is already unpinned
        AccessError: (Direct refernce to the specification)
            - Invalid token
            - The authorised user is not a member of the channel that the message is within
            - The authorised user is not an owner
    """
    is_message_too_long(message)
    is_channel_id_valid(channel_id)
    u_id = token_to_uid(token)

    # time_sent is in the past --> raise InputError
    if time_sent < generate_timestamp():
        raise error.InputError("cannot send a message in past time")

    # the authorised user not member of channel_id --> AccessError
    if not is_user_member(u_id, channel_id) and \
        not is_user_owner(u_id, channel_id):
        raise error.AccessError("You are not a member of the channel.")

    # Update in database
    # taken from message_send --> modified time_created
    msg_id = uc.TOTAL_MSG
    new_msg = {
        'message_id': msg_id,
        'u_id': u_id,
        'message': message,
        'time_created': time_sent,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
            }
        ],
        'is_pinned': False,
    }
    uc.channel[channel_id]['messages'].insert(0, new_msg)
    uc.users[u_id]['msg_sent'].append(msg_id)
    uc.TOTAL_MSG += 1

    return {
        'message_id': msg_id,
    }

def message_broadcast(token, message):
    """ Allow owner of the flockr to send a message over all channels
    :param token: token of the authorized user
    :param message: the message that user want to send.
    Return: List of dictionaries, where each dictionary contains types { message_id }
    Exception:
        InputError when message is longer than 1000 characters
        AccessError when:
            - Token input is invalid
            - the authorised user is not owner of Flockr
    """

    uid = token_to_uid(token)
    message = str(message)
    msg_list = []

    if uc.users[uid]['permission_id'] == 2:
        raise error.AccessError("The authorised user is not owner of Flockr")
    if len(message) > 1000 or len(message) < 1:
        raise error.InputError("Message is more than 1000 characters")
    for channel_id in uc.channel:
        # Update in database
        msg_id = uc.TOTAL_MSG
        new_msg = {
            'message_id': msg_id,
            'u_id': uid,
            'message': message,
            'time_created': generate_timestamp(),
            'reacts': [
                {
                    'react_id': 1,
                    'u_ids': [],
                }
            ],
            'is_pinned': False,
        }
        uc.channel[channel_id]['messages'].insert(0, new_msg)
        uc.users[uid]['msg_sent'].append(msg_id)
        msg_list.append({
            'message_id': msg_id,
        })
        uc.TOTAL_MSG += 1

    return {
        'messages': msg_list
    }
