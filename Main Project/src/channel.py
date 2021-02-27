"""
@author

Yiyang Huang (z5313425): channel_leave, channel_join

Mia Bueno (z5210209): channel_details, channel_messages

Miriam Tuvel (z5257404): channel_invite, channel_addowner, channel_removeowner

30 / 09 / 2020
"""

import time
from copy import deepcopy
from datetime import datetime, timezone

import jwt

import error
import users_channels as uc


# Helper functions
def token_to_uid(token):
    """ Return the corresponding uid of the token

    Args:
        token (string): token of a user

    Raises:
        error.AccessError: If token is not found in the database

    Returns:
        uid (int): corresponding uid of of the token
    """

    encoded = token.encode()
    decrypted = jwt.decode(encoded, uc.SECRET, algorithms=['HS256'])
    token = decrypted['email']

    for uid, user_info in uc.users.items():
        if user_info['token'] == token:
            return uid
    raise error.AccessError("Invalid token")


def generate_timestamp():
    """ Generate unix timestamp, accurate to minutes.
    :return: (int) timestamp
    """
    return round(time.time())


def is_global_owner(uid):
    """ Determine if the user of this uid is a global owner:

    Args:
        uid (int): uid of the user

    Returns:
        (boolean): the user is or isn't a global owner
    """
    return uc.users[uid]['permission_id'] == 1


def is_user_reacted(uid, msg):
    """ Update msg's dictionary key of 'is_this_user_reacted'
        Only applies to the react_id 0 for now.

    Args:
        uid (int): uid of the authorized user
        msg (dictionary): a message's info dictionary that contains
                          timestamp, message_id, reacts etc.
    """
    for react in msg['reacts']:
        reacted = uid in react['u_ids']
        react['is_this_user_reacted'] = reacted
    return msg


def update_messages_with_react(uid, msg_returned):
    """ Return the updated list of message dictionaries.

    Args:
        uid (int): uid of the authorized user that calls the function
        msg_returned (list): the message dictionaries without 'is_this_user_reacted'

    Returns:
        (list): list of updated message dictionaries
    """
    return list(map(is_user_reacted, [uid] * len(msg_returned),
                    msg_returned))


def is_user_member(uid, channel_id):
    """ Return if user is a member of the channel

    Args:
        uid (int): user to be determined
        channel_id (int): channel for determining if the user is in

    Returns:
        (booleam): True if user is in the channel, else False
    """
    return uid in uc.channel[channel_id]['members']


def is_user_owner(uid, channel_id):
    """ Return if user is an owner of the channel

    Args:
        uid (int): user to be determined
        channel_id (int): channel for determining if the user is in

    Returns:
        (booleam): True if user is owner of the channel, else False
    """
    return uid in uc.channel[channel_id]['owners']


def is_uid_valid(uid):
    """ To determine if the uid exists in the database.

    Args:
        uid (int): uid to be determined

    Raises:
        error.InputError: When uid does not exist.
    """
    if uid not in uc.users.keys():
        raise error.InputError("The uid does not exist")


def is_channel_id_valid(channel_id):
    """ To determine if the channel_id exists in the database.

    Args:
        channel_id (int): channel_id to be determined

    Raises:
        error.InputError: When channel_id does not exist.
    """
    if channel_id not in uc.channel.keys():
        raise error.InputError("The channel_id is invalid")


def channel_invite(token, channel_id, u_id):
    """ Invite user to the channel
    :param token:
    :param channel_id:
    :param u_id:
    :return:
    """
    inviter = token_to_uid(token)
    is_channel_id_valid(channel_id)
    is_uid_valid(u_id)

    if is_user_member(u_id, channel_id):
        raise error.InputError("User you want to invite is already a member.")

    if not is_user_member(inviter, channel_id) \
        and not is_user_owner(inviter, channel_id):
        raise error.AccessError("You are not inside the channel yet.")

    uc.channel[channel_id]['members'].append(u_id)

    uc.users[u_id]['in_channels'].append(channel_id)


def channel_details(token, channel_id):
    """ Show details of the channel
    :param token: token of the active user
    :param channel_id: channel ID of the channel that the user has asks for
    :return: (dict)
    """

    user = token_to_uid(token)
    is_channel_id_valid(channel_id)

    if not is_user_member(user, channel_id) and \
        not is_user_owner(user, channel_id):
        raise error.AccessError("You are not inside the channel yet.")

    owners = uc.channel[channel_id]['owners']
    members = uc.channel[channel_id]['members']

    owner_members = []
    all_members = []

    for index, u_id in enumerate(owners + members):
        tmp = {'u_id': u_id,
             'name_first': uc.users[u_id]['name_first'],
             'name_last': uc.users[u_id]['name_last'],
             'profile_img_url': uc.users[u_id]['profile_img_url']
             }
        if index < len(owners): owner_members.append(tmp)
        else: all_members.append(tmp)

    return {
        'name': uc.channel[channel_id]['name'],
        'owner_members': owner_members,
        'all_members': all_members
    }


def channel_messages(token, channel_id, start):
    """ View messages in the channel, return a padding of at most 50

    :param token: token of the active user
    :param channel_id: channel_id that the user want to check message in
    :param start: the messasge that user wants to start checking
    :return: (dict) contains a list of message's dictionary,
             and start and end of the padding
    """
    padding = 50
    active_user = token_to_uid(token)
    is_channel_id_valid(channel_id)

    if not is_user_member(active_user, channel_id) and \
       not is_user_owner(active_user, channel_id):
        raise error.AccessError("You are not inside the channel.")

    all_msgs = uc.channel[channel_id]['messages']

    if start > len(all_msgs):
        raise error.InputError("The message start over boundaries.")

    exceed = len(all_msgs) < start + padding
    end = -1 if exceed else start + padding
    msgs_returned = deepcopy(all_msgs[start::]) \
                    if exceed else deepcopy(all_msgs[start:end])

    # don't show the message if it's timestamp > current time
    msgs_returned = [msg for msg in msgs_returned \
                    if msg['time_created'] <= generate_timestamp()]

    # sort reversed according to timestamp
    msgs_returned = sorted(msgs_returned,
                           key=lambda x:x['time_created'], reverse=True)

    return {
        'messages': update_messages_with_react(active_user, msgs_returned),
        'start': start,
        'end': end,
    }


def channel_leave(token, channel_id):
    """ Given a channel ID, the user removed as a member of this channel

    :param token: token of user that sends the invite
    :param channel_id: the id of channel that token's user is in
    :return:
        AccessError if token is invalid
        AccessError if user(token) is not part of the channel
        InputError if the channel_id is not the id of a existing channel
    """

    uid = token_to_uid(token)
    is_channel_id_valid(channel_id)

    if not is_user_member(uid, channel_id):
        raise error.AccessError("You are not in the channel yet.")

    uc.users[uid]['in_channels'].remove(channel_id)
    uc.channel[channel_id]['members'].remove(uid)

    if uid in uc.channel[channel_id]['owners']:
        uc.channel[channel_id]['owners'].remove(uid)
    return {}


def channel_join(token, channel_id):
    """ Given a channel_id of a channel that the authorised user can join,
        and adds them to that channel.

        If an user's global permission = 1, then the user is an owner of the flockr.
        Owner of the flockr can join channel disregarding the channel is private/public
        and also automatically becomes owner of the channel once user joined the channel.

    :param token: token of the authorized user
    :param channel_id: the channel's id that the user want to join
    :return:
        InputError if the channel_id is not an id of existing channel
        AccessError:
            if the token is invalid
            if the channel is private and user is not an owner
            if the user is not owner of the flockr (i.e. permission id = 2)
    """

    uid = token_to_uid(token)
    is_channel_id_valid(channel_id)

    if not uc.channel[channel_id]['is_public'] and not is_global_owner(uid):
        raise error.AccessError("You don't have permission to join this channel.")

    # Avoid joining multiple times
    if channel_id not in uc.users[uid]['in_channels']:
        uc.users[uid]['in_channels'].append(channel_id)
    if not is_user_member(uid, channel_id):
        uc.channel[channel_id]['members'].append(uid)
    if not is_user_owner(uid, channel_id) and is_global_owner(uid):
        uc.channel[channel_id]['owners'].append(uid)
    return {}


def channel_addowner(token, channel_id, u_id):
    """ Function that adds owner
    :param token: token of the user
    :param channel_id: channel_id that the authorized user is an owner of
    :param u_id: the user that the authorized user want to add as an owner
    :return: {}
    """

    # make sure that the token is valid
    owner_uid = token_to_uid(token)
    is_channel_id_valid(channel_id)

    if not is_user_owner(owner_uid, channel_id) and \
       not is_global_owner(owner_uid):
        raise error.AccessError("You are not an owner of the channel '\
                                ' or owner of the Flockr")

    if is_user_owner(u_id, channel_id):
        raise error.InputError("You are already an owner of the channel.")

    # add u_id to the owner of the channel
    uc.channel[channel_id]['owners'].append(u_id)

    # add uid into members if s/he is not already a member
    if u_id not in uc.channel[channel_id]['members']:
        uc.channel[channel_id]['members'].append(u_id)
        uc.users[u_id]['in_channels'].append(channel_id)
    return {}


def channel_removeowner(token, channel_id, u_id):
    """ Function that removes owner
    :param token: token of the active user
    :param channel_id: channel ID of the channel that user want to remove owner from
    :param u_id: uid of the user that is going to be removed from owner of the channel
    :return: {}
    """

    owner_uid = token_to_uid(token)
    is_channel_id_valid(channel_id)

    if is_global_owner(u_id):
        raise error.InputError("Owner of flockr can't be removed '\
                               'from owner of the channel.")

    if not is_user_owner(owner_uid, channel_id) and \
        not is_global_owner(owner_uid):
        raise error.AccessError("You are not an owner of the channel '\
                                ' or owner of the Flockr")

    # make sure that the u_id is an owner of the channel
    if not is_user_owner(u_id, channel_id):
        raise error.InputError("The user you want to removed owner is '\
                               'not an owner of the channel")

    # remove the u_id from being owner of channel.
    uc.channel[channel_id]['owners'].remove(u_id)
    return {}
