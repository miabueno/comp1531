'''
Created by Yue (Yuelanda) Dai (z5310546)

Tests for the function search in other.py

Reviewed by Yiyang Huang
'''

# Libraries
import pytest

# src files
import channel as ch
import channels as chs
import auth as au
import user as u
import other as o
import message as msg
import error


# pylint: disable=redefined-outer-name

@pytest.fixture
def pre_test_setup():
    """ Fixture for clearing the data from previous tests,
        and creates: 3 users (user_1, user_2, user_3) 3 channels (channel_1, channel_2, channel_3)

        :return
        (dict): u_id and token of user_1
        (dict): u_id and token of user_2
        (dict): u_id and token of user_3
    """

    o.clear()

    # Register User, return token and uid
    user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "passWord", "First-Name", "Last-Name")
    user_2 = au.auth_register("z2222222@ad.unsw.edu.au", "passWord", "First-Name2", "Last-Name2")
    user_3 = au.auth_register("z3333333@ad.unsw.edu.au", "passWord", "First-Name3", "Last-Name3")

    return user_1, user_2, user_3


@pytest.fixture
def search_pre_test_setup():
    """ Fixture for clearing the data from previous tests, and
        creates:
            - 3 users:
                - user_1 (dict): owner of channel_1, channel_3 and channel_5
                - user_2 (dict): owner of channel_2, channel_4 and channel_5
                - user_3 (dict): member of channel_1, channel_2 and channel_5
            -  5 channels (channel_1, channel_2, channel_3, channel_4, channel_5)

    Returns:
        user_1 (dict): a key in the user dictionary
        user_2 (dict): a key in the user dictionary
        user_3 (dict): a key in the user dictionary
    """

    o.clear()

    # first user is the owner of the flockr
    owner = au.auth_register("z0000000@ad.unsw.edu.au", "passWord", "Owner_flockr", "Owner_flockr")

    # Register User, return token and u_id
    user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "passWord", "First-Name", "Last-Name")
    user_2 = au.auth_register("z2222222@ad.unsw.edu.au", "passWord", "First-Name2", "Last-Name2")
    user_3 = au.auth_register("z3333333@ad.unsw.edu.au", "passWord", "First-Name3", "Last-Name3")

    token_1, token_2, token_3 = user_1['token'], user_2['token'], user_3['token']

    # user_1 create 3 channels, return channel id
    # user_2 create 2 channels, return channel id
    channel_1 = chs.channels_create(token_1, "Channel_1", True)['channel_id']
    channel_2 = chs.channels_create(token_2, "Channel_2", True)['channel_id']
    channel_3 = chs.channels_create(token_1, "Channel_3", True)['channel_id']
    channel_4 = chs.channels_create(token_2, "Channel_4", True)['channel_id']
    channel_5 = chs.channels_create(token_1, "Channel_5", True)['channel_id']

    # add user_3 as a member of channel_1, channel_2 and channel_5
    ch.channel_join(owner['token'], channel_1)
    ch.channel_join(owner['token'], channel_2)
    ch.channel_join(owner['token'], channel_3)
    ch.channel_join(owner['token'], channel_4)
    ch.channel_join(owner['token'], channel_5)
    ch.channel_join(token_3, channel_1)
    ch.channel_join(token_3, channel_2)
    ch.channel_join(token_3, channel_5)

    # add user_2 as an owner of channel_5
    ch.channel_addowner(token_1, channel_5, user_2['u_id'])

    # add messages into the channels from each user
    msg.message_send(token_1, channel_1, "user_1 msg_1 in channel_1: Hi")
    msg.message_send(token_3, channel_1, "user_3 msg_1 in channel_1: Hey")
    msg.message_send(token_1, channel_3, "user_1 msg_2 in channel_3: Hi")
    msg.message_send(token_1, channel_3, "user_1 msg_3 in channel_3: Hey!")
    msg.message_send(token_1, channel_3, "user_1 msg_4 in channel_3: Hi")
    msg.message_send(token_2, channel_4, "user_2 msg_1 in channel_4: HEY")
    msg.message_send(token_1, channel_5, "user_1 msg_5 in channel_5: Hi")
    msg.message_send(token_2, channel_5, "user_2 msg_2 in channel_5: Hello")
    msg.message_send(token_2, channel_5, "user_2 msg_3 in channel_5: Hi")
    msg.message_send(token_3, channel_5, "user_3 msg_2 in channel_5: Hey")
    msg.message_send(token_3, channel_5, "user_3 msg_3 in channel_5: Hi!")
    msg.message_send(token_3, channel_5, "TEST CAPITALIZATION")
    msg.message_send(token_3, channel_5, "test capitalization")
    msg.message_send(token_1, channel_3, "   ")

    return owner, user_1, user_2, user_3


#----------------------------------------------------------------------------------#
#--------------------------- Tests for user_all -----------------------------------#
#----------------------------------------------------------------------------------#

def test_users_all_success(pre_test_setup):
    """
    Test if the function is working successful and the list
    with correct length and details is returned

    Note: we use 'username' instead of 'handle_str'
    will there be problem when we use our test with other groups?
    """

    user_1 = pre_test_setup[0]
    token_1 = user_1['token']

    users_list = o.users_all(token_1)

    # Check the overall length of the list -> 3 users
    assert len(users_list['users']) == 3

    # Check the users' details
    for i in range(len(users_list['users'])):
        u_detail = u.user_profile(token_1, i)['user']
        assert users_list['users'][i]['u_id'] == u_detail['u_id']
        assert users_list['users'][i]['email'] == u_detail['email']
        assert users_list['users'][i]['name_first'] == u_detail['name_first']
        assert users_list['users'][i]['name_last'] == u_detail['name_last']
        assert users_list['users'][i]['handle_str'] == u_detail['handle_str']


def test_users_all_invalid_token():
    """
    The token input in this function does not exist -> AccessError is raised
    """
    o.clear()
    invalid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'

    # Check AccessError when token is incorrect
    with pytest.raises(error.AccessError): # Failing behaviour
        o.users_all(invalid_token)


#----------------------------------------------------------------------------------#
#------------------ Tests for admin_userpermission_change -------------------------#
#----------------------------------------------------------------------------------#

def test_admin_upermchange_change_success_to_admin(pre_test_setup):
    """
    Test if the function is working for changing
    the global permission for the selected user from member to admin
    """

    user_1, user_2, user_3 = pre_test_setup
    token_1 = user_1['token']
    u_id2 = user_2['u_id']
    token_2 = user_2['token']
    u_id3 = user_3['u_id']
    token_3 = user_3['token']
    permission_id = 1

    channel_1 = chs.channels_create(token_3, "Channel_1", True)['channel_id']
    assert o.admin_userpermission_change(token_1, u_id2, permission_id) == {}

    # Check permission_id of user_2 if user_2 has permission_id of 1,
    # it will become owner of the channel automatically
    ch.channel_join(token_2, channel_1)
    #if the person becomes owner able to remove another owner. if no error means was able to
    ch.channel_removeowner(token_2, channel_1, u_id3)


def test_admin_upermchange_change_success_to_user(pre_test_setup):
    """
    Test if the function is working for changing
    the global permission for the selected user from admin to member
    """

    user_1, user_2, user_3 = pre_test_setup
    token_1 = user_1['token']
    u_id2 = user_2['u_id']
    token_2 = user_2['token']
    u_id3 = user_3['u_id']
    token_3 = user_3['token']

    channel_1 = chs.channels_create(token_3, "Channel_1", True)['channel_id']
    o.admin_userpermission_change(token_1, u_id2, 1)
    o.admin_userpermission_change(token_1, u_id2, 2)

    # Check permission_id of user_2 if user_2 has permission_id of 2,
    # it will become member of the channel
    ch.channel_join(token_2, channel_1)
    # then, it cannot remove owner and function should raise AccessError
    with pytest.raises(error.AccessError):
        ch.channel_removeowner(token_2, channel_1, u_id3)


def test_admin_upermchange_invalid_token(pre_test_setup):
    """
    The token input in this function does not exist -> AccessError is raised
    """

    user_1 = pre_test_setup[0]
    u_id = user_1['u_id']
    permission_id = 1
    invalid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'

    # Check AccessError when token is incorrect
    with pytest.raises(error.AccessError): # Failing behaviour
        o.admin_userpermission_change(invalid_token, u_id, permission_id)


def test_admin_upermchange_not_authorised_token(pre_test_setup):
    """
    The user is not an owner/admin (Not authorised) -> AccessError is raised
    """

    user_3 = pre_test_setup[2]
    token = user_3['token']
    u_id = user_3['u_id']
    permission_id = 1

    # Check AccessError when token is not authorised
    with pytest.raises(error.AccessError): # Failing behaviour
        o.admin_userpermission_change(token, u_id, permission_id)


def test_admin_upermchange_invalid_u_id(pre_test_setup):
    """
    The user ID input does not exist -> InpputError is raised
    """

    user_1 = pre_test_setup[0]
    token = user_1['token']
    u_id = "Invalid ID"
    permission_id = 1


    # Check InputError when u_id is invalid
    with pytest.raises(error.InputError): # Failing behaviour
        o.admin_userpermission_change(token, u_id, permission_id)


def test_admin_upermchange_invalid_perm_value(pre_test_setup):
    """
    The permission ID input is invalid (Not 1 or 2) -> InpputError is raised
    """

    user_1 = pre_test_setup[0]
    token = user_1['token']
    u_id = user_1['u_id']
    permission_id = 4 # Not a valid permission_id, can only be 1 or 2

    # Check InputError when permission_id is invalid
    with pytest.raises(error.InputError): # Failing behaviour
        o.admin_userpermission_change(token, u_id, permission_id)


#----------------------------------------------------------------------------------#
#----------------------------- Tests for search -----------------------------------#
#----------------------------------------------------------------------------------#

def test_search_flockr_owner_msg(search_pre_test_setup):
    ''' Test when the owner of the entire flockr trying to search for a query.
        Should return all messages in all channels that includes the query.
    '''

    owner, __, __, __ = search_pre_test_setup
    token = owner['token']


    msgs = o.search(token, 'msg')

    # sort messages by each message_id
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    # Brief test
    assert len(msg_list) == 11
    # Test the user who sent the message in the mesages list are correct.
    assert msg_list[0]['message'] == "user_1 msg_1 in channel_1: Hi"
    assert msg_list[1]['message'] == "user_3 msg_1 in channel_1: Hey"
    assert msg_list[2]['message'] == "user_1 msg_2 in channel_3: Hi"
    assert msg_list[3]['message'] == "user_1 msg_3 in channel_3: Hey!"
    assert msg_list[4]['message'] == "user_1 msg_4 in channel_3: Hi"
    assert msg_list[5]['message'] == "user_2 msg_1 in channel_4: HEY"
    assert msg_list[6]['message'] == "user_1 msg_5 in channel_5: Hi"
    assert msg_list[7]['message'] == "user_2 msg_2 in channel_5: Hello"
    assert msg_list[8]['message'] == "user_2 msg_3 in channel_5: Hi"
    assert msg_list[9]['message'] == "user_3 msg_2 in channel_5: Hey"
    assert msg_list[10]['message'] == "user_3 msg_3 in channel_5: Hi!"


def test_search_none(search_pre_test_setup):
    ''' Searching for a query string that does not exist in messages.
    '''

    __, user_1, __, __ = search_pre_test_setup

    msgs = o.search(user_1['token'], 'Hello World')

    # sort messages by each message_id
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    assert not msg_list


def test_search_user_1_msg_hi(search_pre_test_setup):
    ''' Search message that contains 'Hi' as a query for messages that
        user_1 is part of.
    '''

    __, user_1, user_2, user_3 = search_pre_test_setup
    token_1, uid_1 = user_1['token'], user_1['u_id']
    uid_2, uid_3 = user_2['u_id'], user_3['u_id']

    msgs = o.search(token_1, 'Hi')

    # sort messages by each message_id
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    # Brief test
    assert len(msg_list) == 6
    # Test the user who sent the message in the mesages list are correct.
    assert msg_list[0]['u_id'] == uid_1
    assert msg_list[1]['u_id'] == uid_1
    assert msg_list[2]['u_id'] == uid_1
    assert msg_list[3]['u_id'] == uid_1
    assert msg_list[4]['u_id'] == uid_2
    assert msg_list[5]['u_id'] == uid_3
    # Test message details
    assert msg_list[0]['message'] == "user_1 msg_1 in channel_1: Hi"
    assert msg_list[1]['message'] == "user_1 msg_2 in channel_3: Hi"
    assert msg_list[2]['message'] == "user_1 msg_4 in channel_3: Hi"
    assert msg_list[3]['message'] == "user_1 msg_5 in channel_5: Hi"
    assert msg_list[4]['message'] == "user_2 msg_3 in channel_5: Hi"
    assert msg_list[5]['message'] == "user_3 msg_3 in channel_5: Hi!"


def test_search_user_1_msg_hello(search_pre_test_setup):
    ''' Search meseages that contains 'Hello' as a query for messages that
        user_1 is part of.
    '''

    __, user_1, __, __ = search_pre_test_setup
    token_1 = user_1['token']

    msgs = o.search(token_1, 'Hello')

    # sort messages by each message_id
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    # Brief test
    assert len(msg_list) == 1
    # Test message details
    assert msg_list[0]['message'] == "user_2 msg_2 in channel_5: Hello"


def test_search_user_2_msg_hi(search_pre_test_setup):
    ''' Search meseages that contains 'Hi' as a query for messages that
        user_2 is part of.
    '''

    __, user_1, user_2, user_3 = search_pre_test_setup
    token_2, uid_2 = user_2['token'], user_2['u_id']
    uid_1, uid_3 = user_1['u_id'], user_3['u_id']

    msgs = o.search(token_2, 'Hi')

    # sort messages by each message_id
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    # Brief test
    assert len(msg_list) == 3
    # Test the user who sent the message in the mesages list are correct.
    assert msg_list[0]['u_id'] == uid_1
    assert msg_list[1]['u_id'] == uid_2
    assert msg_list[2]['u_id'] == uid_3
    # Test message details
    assert msg_list[0]['message'] == "user_1 msg_5 in channel_5: Hi"
    assert msg_list[1]['message'] == "user_2 msg_3 in channel_5: Hi"
    assert msg_list[2]['message'] == "user_3 msg_3 in channel_5: Hi!"


def test_search_user_2_msg_hey(search_pre_test_setup):
    ''' Search meseages that contains 'Hey' as a query for messages that
        user_2 is part of.
    '''

    __, __, user_2, __ = search_pre_test_setup
    token_2 = user_2['token']

    msgs = o.search(token_2, 'Hey')

    # sort messages by each message_id
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    # Brief test
    assert len(msg_list) == 1
    # Test message details
    assert msg_list[0]['message'] == "user_3 msg_2 in channel_5: Hey"


def test_search_user_3_msg_hey(search_pre_test_setup):
    ''' Search meseages that contains 'Hey' as a query for messages that
        user_3 is a member of.
    '''

    __, __, __, user_3 = search_pre_test_setup
    token_3 = user_3['token']

    msgs = o.search(token_3, 'Hey')

    # sort messages by each message_id
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    # Brief test
    assert len(msg_list) == 2
    # Test message details
    assert msg_list[0]['message'] == "user_3 msg_1 in channel_1: Hey"
    assert msg_list[1]['message'] == "user_3 msg_2 in channel_5: Hey"



def test_search_msg_user(search_pre_test_setup):
    ''' Search meseages that contains 'user' as a query for messages that
        user_2 is a member or owner of.
        This should return all messages in channels that user_2 is part of
    '''

    __, __, user_2, __ = search_pre_test_setup

    msgs = o.search(user_2['token'], 'user')

    # sort messages by each message_id
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    # Brief test
    assert len(msg_list) == 6
    # Test message details
    assert msg_list[0]['message'] == "user_2 msg_1 in channel_4: HEY"
    assert msg_list[1]['message'] == "user_1 msg_5 in channel_5: Hi"
    assert msg_list[2]['message'] == "user_2 msg_2 in channel_5: Hello"
    assert msg_list[3]['message'] == "user_2 msg_3 in channel_5: Hi"
    assert msg_list[4]['message'] == "user_3 msg_2 in channel_5: Hey"
    assert msg_list[5]['message'] == "user_3 msg_3 in channel_5: Hi!"


def test_search_msg_lowercase(search_pre_test_setup):
    ''' Search meseages that contains 'hi' (all lowercase letters) as a query
        Assumption: upper and lowercase letters are treated differently.
    '''

    __, user_1, __, __ = search_pre_test_setup

    msgs = o.search(user_1['token'], 'hi')
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    assert not msg_list


def test_search_msg_uppercase(search_pre_test_setup):
    ''' Search meseages that contains 'HI' (all uppercase letters) as a query
        Assumption: upper and lowercase letters are treated differently.
    '''

    __, user_1, __, __ = search_pre_test_setup

    msgs = o.search(user_1['token'], 'HI')
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    assert not msg_list


def test_search_unique_msg(search_pre_test_setup):
    ''' Search meseages that contains 'channel_6' as a query.
        This should return an empty dict since 'channel_6' is not a
        valid substring in any messages
    '''

    __, user_1, __, __ = search_pre_test_setup

    msgs = o.search(user_1['token'], 'channel_6')
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    assert not msg_list


def test_search_msg_symbol(search_pre_test_setup):
    ''' Search message that contains '_' (symbol) as a query for messages that
        user_1 is an owner of.
        This should return all messages that user_1 is part of.
    '''

    __, user_1, __, __ = search_pre_test_setup
    token_1 = user_1['token']

    msgs = o.search(token_1, '_')

    # sort messages by each message_id
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    # Brief test
    assert len(msg_list) == 10
    # Test message details
    assert msg_list[0]['message'] == "user_1 msg_1 in channel_1: Hi"
    assert msg_list[1]['message'] == "user_3 msg_1 in channel_1: Hey"
    assert msg_list[2]['message'] == "user_1 msg_2 in channel_3: Hi"
    assert msg_list[3]['message'] == "user_1 msg_3 in channel_3: Hey!"
    assert msg_list[4]['message'] == "user_1 msg_4 in channel_3: Hi"
    assert msg_list[5]['message'] == "user_1 msg_5 in channel_5: Hi"
    assert msg_list[6]['message'] == "user_2 msg_2 in channel_5: Hello"
    assert msg_list[7]['message'] == "user_2 msg_3 in channel_5: Hi"
    assert msg_list[8]['message'] == "user_3 msg_2 in channel_5: Hey"
    assert msg_list[9]['message'] == "user_3 msg_3 in channel_5: Hi!"


def test_search_uppercase(search_pre_test_setup):
    ''' Search message that contains 'TEST CAPITALIZATION'
        (all uppercase letters) as a query for messages
    '''

    __, user_1, __, __ = search_pre_test_setup
    token_1 = user_1['token']

    msgs = o.search(token_1, 'TEST CAPITALIZATION')

    # sort messages by each message_id
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    # Brief test
    assert len(msg_list) == 1
    # Test message details
    assert msg_list[0]['message'] == "TEST CAPITALIZATION"


def test_search_lowercase(search_pre_test_setup):
    ''' Search message that contains 'test capitalization'
        (all lowercase letters) as a query for messages
    '''

    __, __, user_2, __ = search_pre_test_setup
    token_2 = user_2['token']

    msgs = o.search(token_2, 'test capitalization')

    # sort messages by each message_id
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    # Brief test
    assert len(msg_list) == 1
    # Test message details
    assert msg_list[0]['message'] == "test capitalization"


def test_search_mixed_cases(search_pre_test_setup):
    ''' Search meseages that contains 'TeSt cApitaLISatIon'
        (mix of upper- and lower-cases) as a query for messages
    '''

    __, user_1, __, __ = search_pre_test_setup

    msgs = o.search(user_1['token'], 'TeSt cApitaLISatIon')
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    assert not msg_list


def test_search_punctuation(search_pre_test_setup):
    ''' Search message that contains '!' (punctuation) as a query
    '''

    __, user_1, __, __ = search_pre_test_setup
    token_1 = user_1['token']

    msgs = o.search(token_1, '!')

    # sort messages by each message_id
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    # Brief test
    assert len(msg_list) == 2
    # Test message details
    assert msg_list[0]['message'] == "user_1 msg_3 in channel_3: Hey!"
    assert msg_list[1]['message'] == "user_3 msg_3 in channel_5: Hi!"


def test_search_whitespace(search_pre_test_setup):
    ''' Search message that contains '  ' (two whitespaces) as a query
    '''

    __, user_1, __, __ = search_pre_test_setup
    token_1 = user_1['token']

    msgs = o.search(token_1, '  ')

    # sort messages by each message_id
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    # Brief test
    assert len(msg_list) == 1
    # Test message details
    assert msg_list[0]['message'] == "   "


def test_search_empty_string(search_pre_test_setup):
    ''' Search message that contains '' (empty string) as a query
        Should return all messages in channels that the user is part of.
    '''

    __, __, user_2, __ = search_pre_test_setup

    msgs = o.search(user_2['token'], '')
    msg_list = sorted(msgs['messages'], key=lambda item: item['message_id'])

    # Brief test
    assert len(msg_list) == 8
    # Test message details
    assert msg_list[0]['message'] == "user_2 msg_1 in channel_4: HEY"
    assert msg_list[1]['message'] == "user_1 msg_5 in channel_5: Hi"
    assert msg_list[2]['message'] == "user_2 msg_2 in channel_5: Hello"
    assert msg_list[3]['message'] == "user_2 msg_3 in channel_5: Hi"
    assert msg_list[4]['message'] == "user_3 msg_2 in channel_5: Hey"
    assert msg_list[5]['message'] == "user_3 msg_3 in channel_5: Hi!"
    assert msg_list[6]['message'] == "TEST CAPITALIZATION"
    assert msg_list[7]['message'] == "test capitalization"
