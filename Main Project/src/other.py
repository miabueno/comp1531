'''
@author Yiyang Huang z5313425 01/10/2020
users_all and admin_userpermission_change coded by Nont Fakungkun z5317972

'''

import users_channels as uc
from channel import token_to_uid, update_messages_with_react
import error

def clear():
    """ Clear tests data in the database.
    Insert owner of the FLOCKR's detail as default with uid 0.
    :return:
    """
    uc.users.clear()
    uc.channel.clear()
    uc.TOTAL_MSG = 0


def users_all(token):
    """ Returns a list of all users and their associated details
    :param token: token of a user
    :return:
        user (List of dictionaries, where each dictionary
        contains types u_id, email, name_first, name_last, handle_str)

        AccessError if token is invalid
    """
    # Check token is valid
    __ = token_to_uid(token)

    user_list = []
    # Create a list of all users (extract the list from uc.users)
    for u_id in uc.users:
        user_tmp = {
            'u_id': u_id,
            'email': uc.users[u_id]['email'],
            'name_first': uc.users[u_id]['name_first'],
            'name_last': uc.users[u_id]['name_last'],
            'handle_str': uc.users[u_id]['username'],
            'profile_img_url': uc.users[u_id]['profile_img_url'],
        }
        # Add the copy of dictionary instead of adding directly to avoid making reference
        user_list.append(user_tmp.copy())

    return {
        'users': user_list,
    }


def admin_userpermission_change(token, u_id, permission_id):
    """ Given a User by their user ID,
        set their permissions to new permissions described by permission_id

    :param token: token of the authorized user
    :param u_id: the user's ID to have its permission set
    :param permission_id (int): user status either owner or member given to the user (u_id)
    :return:
        {} if success

        InputError:
            if u_id is invalid
            if permission_id is not either 1 or 2
        AccessError:
            if the token is invalid
            if the authorised user is not owner
    """

    # Check token is valid
    accessing_u_id = token_to_uid(token)

    if uc.users[accessing_u_id]['permission_id'] == 2:
        raise error.AccessError(f"The authorised user {accessing_u_id} is not an owner of Flockr")

    if u_id not in uc.users.keys():
        raise error.InputError(f"{u_id} does not refer to a valid user")

    if permission_id not in [1, 2]:
        raise error.InputError(f"{permission_id} does not refer to a value permission")

    uc.users[u_id]['permission_id'] = permission_id

    return {}

def search(token, query_str):
    ''' [Direct reference to specification] Given a query string,
        return a collection of messages in all of the channels that
        the user has joined that match the query

    Parameters:
        token (str): token of the user requesting this function
        query_str (str): test whether or not a mssage contains this query_str

    Returns:
        messages:
            A list of messages that contains the query string provided.
            [Direct reference to specification]:
            List of dictionaries, where each dictionary contains types
            {message_id, u_id, message, time_created}

    '''

    uid = token_to_uid(token)
    msg_list = []

    for channel_id in uc.users[uid]['in_channels']:
        for msg in uc.channel[channel_id]['messages']:
            if query_str in msg['message']:
                msg_list.append(msg)

    return {
        'messages': update_messages_with_react(uid, msg_list)
    }
