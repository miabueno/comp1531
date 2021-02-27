"""
Created by Yiyang Huang (z5313425)

V.1.2: The data structure prototype. 22/9/2020
# test changes.

# 11/10/2020:
    1.  Add field 'in_channels' and 'msg_sent'
        to user with uid 0 (i.e. owner of the Flockr).

# 12/10/2020:
    1.  Add field 'msg_sent' to user's dictionary.
        Stores a list of tuple (msg_id, channel_id)
    2.  Add global variable 'TOTAL_MSG'.
        Stores the total amount of msg in the server.

# 13/10/2020:
    1.  Default owner of the flockr removed.
        The first user registered on Flockr will be the owner of the flockr.
    2.  'msg_sent' is just a list that stores the msg_id.

# 20/10/2020:
    1.  Add permission_id into users data structure

# 31/10/2020:
    1.  Add key 'reactions' to message's dictionary.
    2.  Add key 'is_pinned' to message's dictionary.

# 09/11/2020:
    1.  Add global variable 'REACTIONS', a list of implemented reaction in current
        iteration.

"""

# A dictionary of users_info_dictionaries
users = {
    # Format of normal user's info dictionary
    # 0: {                            # users[1] == user info with uid 1
    #     'username': '',             # str
    #     'token': '',                # str
    #     'name_first': '',           # str
    #     'name_last': '',            # str
    #     'email': '',                # str
    #     'password': '',             # str
    #     'permission_id': 1 or 2,    # int
    #     'in_channels': [],          # id of channels
    #     'msg_sent': [],             # list of msg_id
    #     'profile_img_url': '',      # str
    # },
}

# stores the # of msg on the server, gives the newest msg_id
TOTAL_MSG = 0
# stores list of valid reactions currently implemented
REACTIONS = [1]

# s constant string for jwt encryption of the token as the secret
global SECRET
SECRET = "Thur13Grape05"

# A dictionary that stores the information of each channel
channel = {
    # Format only, not actual data
    # 0: {
    #     'name': 'name',
    #     'members': [1, 2, 3],
    #     'owners': [1],
    #     'is_public': True,
    #     'messages': [
    #         {
    #          'message_id': 1,
    #          'u_id': 1,
    #          'message': 'Hello world',
    #          'time_created': 1582426789,
    #          'reacts': [],             # list of dictionaries
    #          'is_pinned': True,       # boolean
    #         },
    #     ],
    #     'standup': {
    #         'is_active': False,
    #         'token': '',
    #         'time_finish': None,
    #         'messages': []
    #     },
    # },
}

