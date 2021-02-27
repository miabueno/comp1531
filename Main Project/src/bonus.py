""" This is the **bonus** function of channel_todos

    1.  channel_todo_show
    2.  channel_todo_add
    3.  channel_todo_update
    4.  channel_todo_remove
    5.  channel_todo_create

@author Yiyang Huang (z5313425)
@date 2020/11/15
"""

from datetime import datetime, timezone
from channel import token_to_uid, is_channel_id_valid, is_user_member, is_user_owner
import users_channels as uc
import error


def find_todo(channel_id, todo_id): # pragma: no cover
    """ Find the todo list item and return its index in the list 'todos'

    Args:
        channel_id (int): the ID of the channel that user want to modify
                          for item with id todo_id in
        todo_id (int): the ID of the todo list item that user want to modify

    Raises:
        error.InputError: When the todo list item is not found

    Returns:
        index (int): the index of the todo list item in the list 'todos'
    """
    for index, todo in enumerate(uc.channel[channel_id]['todos']):
        if todo['todo_id'] == todo_id:
            return index
    raise error.InputError("The todo list item doesn't exist.")


def channel_todo_create(token, channel_id):
    """ Create a todo list in that channel

    Args:
        token (str): the token of the authroized user
        channel_id (int): ID of the channel that user want to crate todo list in

    Exceptions:
        AccessError: If user is not an authorized user
        AccessError: If user is not an member of the channel
        InputError: If there is already a todo list in the channel
    """
    uid = token_to_uid(token)
    if not is_user_member(uid, channel_id):
        raise error.AccessError("You are not an member of the channel.")

    try:
        __ = uc.channel[channel_id]['todos']
        raise error.InputError("There is already a todo list in this channel.")
    except KeyError:
        uc.channel[channel_id]['todos'] = []

    return {}


def channel_todo_show(token, channel_id, sort=False):
    """ Show all of the todo items in the channel's todo list

    Args:
        token (str): the token of the authorized user
        channel_id (int): the channel ID of the todo list's channel
                          that the user want to check
        sort (boolean): determine if the return list should be sorted by significance

    Returns:
        todos (list): list of all todo items in the channel. Dictionary contains
                      related information of each todo item.

    Exceptions:
        AccessError: If user is not an authorized user
        AccessError: If user is not an member of the channel
    """
    uid = token_to_uid(token)

    if not is_user_member(uid, channel_id):
        raise error.AccessError("You are not an member of the channel.")

    try:
        todos = uc.channel[channel_id]['todos']
    except KeyError:
        raise error.InputError("There is no todo list in this channel.")

    return {'todos': todos} if not sort else {'todos': sorted(todos,
                                                       key=lambda x:x['level'],
                                                       reverse=True),}


def channel_todo_add(token, channel_id, message, level):
    """ Add an item to the channel's todo list

    Args:
        token (str): the token of the authorized user
        channel_id (int): the ID of the channel that user want to add todo list item in
        message (str): the message (topic) of the todo list item
        level (int): 1 (not significant), 2, 3, 4 (Extremely urgent)

    Exceptions:
        InputError: If level is > 4 or level is < 0
        InputError: If message length is > 50 characters
        AccessError: If user is not an authorized user
        AccessError: If there is no todo list in the channel
        AccessError: If user is not an member of the channel
    """
    if level > 4 or level < 0:
        raise error.InputError("level invalid.")
    if len(message) > 50:
        raise error.InputError("Message too long as a todo item.")

    uid = token_to_uid(token)
    if not is_user_member(uid, channel_id):
        raise error.AccessError("You are not an member of the channel.")

    try:
        todo_id = len(uc.channel[channel_id]['todos'])
        uc.channel[channel_id]['todos'].append({
            'todo_id': todo_id,
            'message': message,
            'level': level,
            'status': False,
        })
    except KeyError:
        raise error.AccessError("Todo list not created in this channel.")

    return {
        'todo_id': todo_id,
    }


# ======== message_broadcast ========

def generate_timestamp():
    """ Generate unix timestamp, accurate to seconds.
    :return: (int) timestamp
    """
    timestamp = round(datetime.now().replace(tzinfo=timezone.utc).timestamp())
    return timestamp


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

# def channel_todo_update(token, channel_id, todo_id, status=True): # pragma: no cover
#     """ Update the status of a todo list item

#     Args:
#         token (str): token of the authorized user
#         channel_id (int): ID of the channel that user want to update todo list item in
#         statu (boolean): status of the todo list item, completed or incomplete
#         todo_id (int): the id of the todo item

#     Excetpion:
#         InputError: the todo_id doesn't exist
#         AccessError: if user is not an authorized user
#         AccessError: If user is not an member of the channel
#     """
#     uid = token_to_uid(token)
#     if not is_user_member(uid):
#         raise error.AccessError("You are not an member of the channel.")

#     index = find_todo(channel_id, todo_id)
#     uc.channel[channel_id]['todos'][index]['status'] = status
#     return {}


# def channel_todo_remove(token, channel_id, todo_id): # pragma: no cover
#     """ Remove a todo list item from the channel's todo list

#     Args:
#         token (str): the token of the authroized user
#         channel_id (int): the ID of the channel
#         todo_id (int): the id of the todo list item

#     Exceptions:
#         AccessError: if user is not an authorized user
#         AccessError: If user is not an member of the channel
#     """
#     uid = token_to_uid(token)
#     if not is_user_member(uid):
#         raise error.AccessError("You are not an member of the channel.")

#     index = find_todo(channel_id, todo_id)
#     del uc.channel[channel_id]['todos'][index]
#     return {}

