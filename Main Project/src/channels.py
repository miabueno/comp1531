'''
Written by: Nont Fakungkun z5317972

Reviewed by: Yiyang Huang z5313425, 29/09/2020

'''

# Import files
import users_channels as data
from channel import token_to_uid
import error


def channels_list(token):
    """ Provide a list of all channels
        (and their associated details) that the authorised user is part of
    :param token: token of a user
    :return:
        channels (List of dictionaries, where each dictionary
        is the channels the user is member of contains types { channel_id, name })

        AccessError if token is invalid
    """

    # Check token is valid
    u_id = token_to_uid(token)

    channel_list = []
    # Create a list of channel (extract the list that the user is member of)
    for channel_id in data.users[u_id]['in_channels']:
        channel_tmp = {
            'channel_id': channel_id,
            'name': data.channel[channel_id]['name'],
        }
        # Add the copy of dictionary instead of adding directly to avoid making reference
        channel_copy = channel_tmp.copy()
        channel_list.append(channel_copy)

    return {'channels': channel_list}


def channels_listall(token):
    """ Provide a list of all channels (and their associated details)
    :param token: token of a user
    :return:
        channels (List of dictionaries, where each dictionary contains types { channel_id, name })

        AccessError if token is invalid
    """
    # Check token is valid
    __ = token_to_uid(token)

    channel_list = []
    # Create a list of all channel (extract the list from data.channel)
    for channel_id in data.channel:
        channel_tmp = {
            'channel_id': channel_id,
            'name': data.channel[channel_id]['name'],
        }
        # Add the copy of dictionary instead of adding directly to avoid making reference
        channel_copy = channel_tmp.copy()
        channel_list.append(channel_copy)

    return {'channels': channel_list}


def channels_create(token, name, is_public):
    """ Creates a new channel with that name that is either a public or private channel

    :param token: token of the authorized user
    :param name: the channel's given name
    :param is_public: channel status for public/private
    :return:
        ID of the channel created

        InputError:
            if name contain more than 20 characters
            if name is taken
            if is_public is not either True or False
        AccessError if the token is invalid
    """
    # Check token is valid
    creator_id = token_to_uid(token)

    # Check the length of name
    if len(name) > 20:
        raise error.InputError(f"Name {name} is more than 20 characters")

    if type(is_public) != bool:
        raise error.InputError("is_public value is not valid can only be True or False")

    # # Creating channel ID while checking for uniqueness of the chosen channel name
    # # assume that channel name has to be unique
    # for channel_id in data.channel:
    #     if data.channel[channel_id].get('name') == name:
    #         raise error.InputError(f"Name '{name}' is already taken")

    # create channel id in numerical order
    channel_id = int(len(data.channel))

    # add users information
    data.channel[channel_id] = dict({
        'name': name,
        'members': [creator_id],
        'owners': [creator_id],
        'is_public': is_public,
        'messages': [],
        'standup': {
            'is_active': False,
            'token': '',
            'time_finish': None,
            'messages': []
        }
    })
    data.users[creator_id]['in_channels'].append(channel_id)

    return {
        'channel_id': channel_id,
    }
