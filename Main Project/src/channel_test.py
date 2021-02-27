'''

Created by:

Yiyang Huang (z5313425)
[channel_leave, channel_join]

Mia Bueno (z5210209)
[channel_invite, channel_details, channel_messages]


Miriam Tuvel (z5257404)
[channel_addowner, channel_removeowner]

20 / 09 / 2020



'''

# Library
import pytest

# Files
import channel as ch
import channels as chs
import auth as au
import other as o
import message as msg
import error


# disable error W0621
# pylint: disable=redefined-outer-name
@pytest.fixture
def pre_test_setup():
    """ Fixture for clearing the data from previous tests,
        and creates: 2 users (user_1, user_2) 1 channel (channel_1)

        :return
        (int): token of user_1
        (int): token of user_2
        (int): channel id of channel_1
    """

    o.clear()
    # Register User, return token and uid
    owner = au.auth_register("z0000000@ad.unsw.edu.au", "passWord2",
                             "Owner", "Owner")
    owner_token = owner['token']
    user_1 = au.auth_register("z1111111@ad.unsw.edu.au", "passWord",
                              "First-Name", "Last-Name")
    token_1 = user_1['token']
    user_2 = au.auth_register("z2222222@ad.unsw.edu.au", "passWord",
                              "First-Name2", "Last-Name2")
    token_2 = user_2['token']

    # Create Channel, return channel id
    channel_1 = chs.channels_create(token_1, "Channel_1", True)['channel_id']
    return owner_token, token_1, token_2, channel_1


def test_channel_leave(pre_test_setup):
    """ User1 (owner) leave the channel that
        user is an owner and a member of.
    :param pre_test_setup: the fixture
    """

    __, token, __, channel_1 = pre_test_setup

    # User1 created and channel, and leave the channel_1
    ch.channel_leave(token, channel_1)
    channel_lists = chs.channels_list(token)['channels']

    # Assert user1 not in channel_1 anymore
    assert channel_1 not in [each['channel_id'] for each in channel_lists]


def test_channel_leave_member(pre_test_setup):
    """ User2 (member) leave channel that the user is a member of.
    :param pre_test_setup: the fixture
    """

    __, __, token, channel_1 = pre_test_setup

    ch.channel_join(token, channel_1)
    ch.channel_leave(token, channel_1)
    channel_lists = chs.channels_list(token)['channels']
    assert channel_1 not in [each['channel_id'] for each in channel_lists]


def test_channel_leave_input_error(pre_test_setup):
    """ Should return InputError since channel_id 100 doesn't exist.
    :param pre_test_setup: the fixture
    """

    __, token, __, __ = pre_test_setup

    # should return InputError since channel_id doesn't exist
    with pytest.raises(error.InputError):
        ch.channel_leave(token, 999999)


def test_channel_leave_access_error(pre_test_setup):
    """ Should return AccessError since user 1 is not a
        member of channel_3.

    :param pre_test_setup: the fixture
    """

    __, __, token_2, channel_1 = pre_test_setup

    # user2 trying to leave channel_1 that he is not in, should return AccessError
    with pytest.raises(error.AccessError):
        ch.channel_leave(token_2, channel_1)


def test_channel_join(pre_test_setup):
    """ Join user1 to channel3, should be normal behavior
    :param pre_test_setup: the fixture
    """

    __, token, __, channel_id = pre_test_setup

    ch.channel_join(token, channel_id)

    # channel_1 should be in the list of channels that user1 is in
    channel_lists = chs.channels_list(token)['channels']

    assert channel_id in [each['channel_id'] for each in channel_lists]


def test_channel_join_twice(pre_test_setup):
    """ Join twice, second try should be ignored
    :param pre_test_setup: the fixture
    """

    __, __, token_2, channel_id = pre_test_setup

    ch.channel_join(token_2, channel_id)
    ch.channel_join(token_2, channel_id)

    # channel_1 should be in the list of channels that user1 is in
    channel_lists = chs.channels_list(token_2)['channels']

    # channel_3 should only appear once
    # assert 0
    assert [each['channel_id'] for each in channel_lists].count(channel_id) == 1


def test_channel_join_input_error(pre_test_setup):
    """ Should return InputError since channel_id 100 doesn't exist.
    :param pre_test_setup: the fixture
    """

    token = pre_test_setup[1]

    # should return InputError since channel_id doesn't exist
    with pytest.raises(error.InputError):
        ch.channel_join(token, 999999)


def test_channel_join_access_error(pre_test_setup):
    """ Should return AccessError since channel_1 is private
        and user2 is not an owner of the channel or the FLOCKR
    :param pre_test_setup: the fixture
    """

    __, token_1, token_2, __ = pre_test_setup

    # create private Channel_1
    channel_2 = chs.channels_create(token_1, "Channel_2", False)['channel_id']

    with pytest.raises(error.AccessError):
        ch.channel_join(token_2, channel_2)


def test_channel_join_private_flockrowner(pre_test_setup):
    """ Let owner of the flockr join a private channel.
    :param pre_test_setup: pytest fixture
    """
    owner_token, token_1, __, __ = pre_test_setup

    # create private Channel_1
    channel_2 = chs.channels_create(token_1, "Channel_2", False)['channel_id']

    ch.channel_join(owner_token, channel_2)

    # channel_1 should be in the list of channels that user1 is in
    channel_lists = chs.channels_list(owner_token)['channels']

    assert channel_2 in [each['channel_id'] for each in channel_lists]


def test_channel_join_multiple_flockrowner(pre_test_setup):
    """ Let owner of the flockr add user_3 as another owner of the flockr.
        User_3 may then join the channel and become owner and member
        of that channel

    :param pre_test_setup: pytest fixture
    """

    owner_token, __, __, channel_public = pre_test_setup

    user_3 = au.auth_register("a545345@ad.unsw.edu.au", "passWord", "First-Name2", "Last-Name2")
    token_3, uid_3 = user_3['token'], user_3['u_id']
    o.admin_userpermission_change(owner_token, uid_3, 1)

    ch.channel_join(owner_token, channel_public)
    ch.channel_join(token_3, channel_public)

    ch_details = ch.channel_details(token_3, channel_public)
    ch_owners = [each['u_id'] for each in ch_details['owner_members']]
    assert uid_3 in ch_owners


@pytest.fixture
def pre_test_owners():
    """ pytest fixture for registering and creating channels
        for functions: channel_addowner, channel_removeowner
    :return:
    """

    o.clear()
    owner_reg = au.auth_register("FLOCKR@gmail.com", "password", "flock", "owner")
    a_reg = au.auth_register("233333@gmail.com", "nopassword", "Sophia", "Huang")
    b_reg = au.auth_register("533333@gmail.com", "Nopassword", "Z", "D")
    c_reg = au.auth_register("633333@gmail.com", "password?", "S", "A")
    a_channel_id = chs.channels_create(a_reg['token'], "A", True)
    b_channel_id = chs.channels_create(a_reg['token'], "B", True)
    c_channel_id = chs.channels_create(c_reg['token'], "C", True)

    return (owner_reg, a_reg, b_reg, c_reg,
            a_channel_id, b_channel_id, c_channel_id)


def test_channel_add_owner(pre_test_owners):
    '''
    add a valid user to a valid channel
    '''
    __, a_reg, b_reg, __, a_channel_id, __, __ = pre_test_owners
    ch.channel_addowner(a_reg['token'], a_channel_id['channel_id'], b_reg['u_id'])
    #if the person becomes owner able to remove another owner. if no error means was able to
    ch.channel_removeowner(b_reg['token'], a_channel_id['channel_id'], a_reg['u_id'])


def test_channel_add_member_as_owner(pre_test_owners):
    ''' Add a member of the channel as an owner.
    '''
    __, a_reg, b_reg, __, a_channel_id, __, __ = pre_test_owners

    ch.channel_join(b_reg['token'], a_channel_id['channel_id'])
    ch.channel_addowner(a_reg['token'], a_channel_id['channel_id'], b_reg['u_id'])
    #if the person becomes owner able to remove another owner. if no error means was able to
    ch.channel_removeowner(b_reg['token'], a_channel_id['channel_id'], a_reg['u_id'])


def test_invalid_channel_add_owner(pre_test_owners):
    '''
    try to add a valid user to a non-valid channel so raises error input
    '''

    __, a_reg, b_reg, __, __, __, __ = pre_test_owners

    with pytest.raises(error.InputError):
        ch.channel_addowner(a_reg['token'], 4, b_reg['u_id'])


def test_channel_add_already_owner(pre_test_owners):
    ''' try to add someone who is already an owner so raise error input '''

    __, a_reg, b_reg, __, a_channel_id, __, __ = pre_test_owners

    ch.channel_addowner(a_reg['token'], a_channel_id['channel_id'], \
                        b_reg['u_id'])
    with pytest.raises(error.InputError):
        ch.channel_addowner(a_reg['token'], a_channel_id['channel_id'], \
                            b_reg['u_id'])


def test_channel_add_by_wrong_owner(pre_test_owners):
    ''' an unauthorised owner trying to add an owner so raise access error '''

    __, __, __, c_reg, a_channel_id, __, __ = pre_test_owners

    with pytest.raises(error.AccessError):
        ch.channel_addowner(c_reg['token'], a_channel_id['channel_id'], \
                            c_reg['u_id'])


def test_channel_add_by_none_owner(pre_test_owners):
    ''' not an owner of flock trying to add owner so raises access error'''

    __, __, __, c_reg, a_channel_id, __, __ = pre_test_owners
    invalid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.' \
                    'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'
    with pytest.raises(error.AccessError):
        ch.channel_addowner(invalid_token, a_channel_id['channel_id'], \
                            c_reg['u_id'])


def test_add_by_main_owner(pre_test_owners):
    ''' the owner of flock can add owner '''
    owner_reg, a_reg, __, c_reg, a_channel_id, __, __ = pre_test_owners

    ch.channel_addowner(owner_reg['token'], a_channel_id['channel_id'], \
                        c_reg['u_id'])
    # if the person becomes owner able to remove another owner.
    # if no error means was able to
    ch.channel_removeowner(c_reg['token'], a_channel_id['channel_id'], \
                           a_reg['u_id'])


def test_fail_add_by_main_owner(pre_test_owners):

    '''main owner trying to add to invalid channel raises input error'''
    owner_reg, __, __, c_reg, __, __, __ = pre_test_owners

    with pytest.raises(error.InputError):
        ch.channel_addowner(owner_reg['token'], 4, c_reg['u_id'])


def test_cant_add_by_main_owner(pre_test_owners):
    ''' owner of flock trying to add someone already an owner
        raises input error
    '''

    owner_reg, a_reg, __, __, a_channel_id, __, __ = pre_test_owners

    with pytest.raises(error.InputError):
        ch.channel_addowner(owner_reg['token'], a_channel_id['channel_id'], \
                            a_reg['u_id'])


def test_channel_remove_owner(pre_test_owners):
    '''valid owner removes another owner'''
    __, a_reg, b_reg, __, a_channel_id, __, __ = pre_test_owners

    ch.channel_removeowner(a_reg['token'], a_channel_id['channel_id'], \
                           a_reg['u_id'])
    #if owner removed properly wont be able to remove anyone else from channel
    with pytest.raises(error.AccessError):
        ch.channel_addowner(a_reg['token'], a_channel_id['channel_id'], b_reg['u_id'])


def test_invalid_channel_remove_owner(pre_test_owners):
    '''try to add to invalid channel so raises input error'''
    __, a_reg, b_reg, __, __, __, __ = pre_test_owners

    with pytest.raises(error.InputError):
        ch.channel_removeowner(a_reg['token'], 4, b_reg['u_id'])


def test_channel_remove_invalid_owner(pre_test_owners):
    '''the person being removed is not an owner so raises input error'''
    __, a_reg, b_reg, __, __, b_channel_id, __ = pre_test_owners

    with pytest.raises(error.InputError):
        ch.channel_removeowner(a_reg['token'], b_channel_id['channel_id'], \
                               b_reg['u_id'])


def test_channel_remove_by_wrong_owner(pre_test_owners):
    '''a non-owner trying to remove owner so raises access owner'''
    __, __, __, c_reg, __, __, c_channel_id = pre_test_owners
    d_reg = au.auth_register("433333@gmail.com", "Password?", "H", "T")

    with pytest.raises(error.AccessError):
        ch.channel_removeowner(d_reg['token'], \
        c_channel_id['channel_id'], c_reg['u_id'])


def test_channel_remove_by_none_owner(pre_test_owners):
    '''trying to remove an unauthorised owner'''
    __, __, __, c_reg, __, __, c_channel_id = pre_test_owners
    invalid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.' \
                    'eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_' \
                    'GW39f1IT3kECz_AhckQGVU'
    with pytest.raises(error.AccessError):
        ch.channel_removeowner(invalid_token, \
        c_channel_id['channel_id'], c_reg['u_id'])


def test_remove_by_main_owner(pre_test_owners):
    '''main owner of flock can remove owner'''
    owner_reg, a_reg, b_reg, c_reg, a_channel_id, __, __ = pre_test_owners
    ch.channel_addowner(a_reg['token'], a_channel_id['channel_id'], \
                        b_reg['u_id'])
    ch.channel_removeowner(owner_reg['token'], a_channel_id['channel_id'], \
                           a_reg['u_id'])

    #if the person is removed wont be able to add
    with pytest.raises(error.AccessError):
        ch.channel_addowner(a_reg['token'], a_channel_id['channel_id'], \
                            c_reg['u_id'])


def test_fail_remove_by_main_owner(pre_test_owners):
    ''' main owner try to remove from invalid channel
        so raises input error
    '''
    owner_reg, a_reg, __, __, __, __, __ = pre_test_owners

    with pytest.raises(error.InputError):
        ch.channel_removeowner(owner_reg['token'], 4, a_reg['u_id'])


def test_cant_remove_by_main_owner(pre_test_owners):
    ''' the main owner tries to remove someone
        who isnt owner so raises input error
    '''
    owner_reg, __, __, c_reg, a_channel_id, __, __ = pre_test_owners

    with pytest.raises(error.InputError):
        ch.channel_removeowner(owner_reg['token'], \
                               a_channel_id['channel_id'], c_reg['u_id'])

def test_removing_mainowner(pre_test_owners):
    '''can't remove the main flockr owner'''
    owner_reg, __, __, c_reg, __, __, c_channel_id = pre_test_owners

    with pytest.raises(error.InputError):
        ch.channel_removeowner(c_reg['token'], c_channel_id['channel_id'], \
                               owner_reg['u_id'])


def test_channel_invite():
    """
        Register two users, User 1 creates a channel
        User 1 to invite User 2 to new channel
        New channel should appear in channel lists of user 2
    """

    o.clear()

    # the one who will create channel + invite people
    user_1 = au.auth_register("z1234567@ad.unsw.edu.au", "kittykat", "First-Name1", "Last-Name1")
    token_1 = user_1['token']

    # the one who will be invited
    user_2 = au.auth_register("z1234568@ad.unsw.edu.au", "iloveyou", "First-Name2", "Last-Name2")
    u_id_2 = user_2['u_id']
    token_2 = user_2['token']

    channel_name = "Channel 69"

    # create channel to retrieve channel_id
    channel_id = chs.channels_create(token_1, channel_name, True)['channel_id']

    # check the user_1 is in the list of users in the channel they created
    channel_lists = chs.channels_list(token_1)['channels']
    assert channel_id in [each['channel_id'] for each in channel_lists]

    # only invite user_2 into channel if the channel is not already listed in its channels_list
    channel_lists = chs.channels_list(token_2)['channels']
    if channel_id not in [each['channel_id'] for each in channel_lists]:
        # user_1 invite user_2
        ch.channel_invite(token_1, channel_id, u_id_2)

    # check the new user (user_2) is in the list of users in the channel
    channel_lists = chs.channels_list(token_2)['channels']

    assert channel_id in [each['channel_id'] for each in channel_lists]


def test_channel_invite_input_error_channel():
    """
        Input Error:
        channel_id does not refer to a valid channel
    """

    o.clear()

    # the one who will create channel + invite people
    user_1 = au.auth_register("z1234567@ad.unsw.edu.au", "kittykat", "First-Name1", "Last-Name1")
    token_1 = user_1['token']

    # the one who will be invited
    user_2 = au.auth_register("z1234568@ad.unsw.edu.au", "iloveyou", "First-Name2", "Last-Name2")
    u_id_2 = user_2['u_id']

    # create 2 x channels
    channel_id_1 = chs.channels_create(token_1, "channel_1", True)['channel_id']

    channel_id_2 = channel_id_1 + 1

    # check channel_id_2 does not already exist
    all_channels = chs.channels_listall(token_1)['channels']
    assert channel_id_2 not in [each['channel_id'] for each in all_channels]

    # should return InputError since channel_id_3 doesn't exist
    with pytest.raises(error.InputError):
        ch.channel_invite(token_1, channel_id_2, u_id_2)


def test_channel_invite_input_error_user():
    """
        Input Error:
        ud_id does not refer to a valid user
    """

    o.clear()

    # the one who will create channel + invite people
    user_1 = au.auth_register("z1234567@ad.unsw.edu.au", "kittykat", "First-Name1", "Last-Name1")
    u_id_1 = user_1['u_id']
    token_1 = user_1['token']

    channel_name = "Channel Test"

    # user_1 creates a channel
    channel_id = chs.channels_create(token_1, channel_name, True)['channel_id']

    # user_1 to retrieve details
    name, owners, members = ch.channel_details(token_1, channel_id).values()

    assert name == channel_name

    assert u_id_1 in [each['u_id'] for each in owners]  # created the channel

    u_id_2 = u_id_1 + 1

    # check user_2 is not in list of channel members
    assert u_id_2 not in [each['u_id'] for each in members]

    # should return InputError since u_id doesn't exist
    with pytest.raises(error.InputError):
        ch.channel_invite(token_1, channel_id, u_id_2)


def test_channel_invite_access_error():
    """
        Access Error:
        user (id by token) is not already a member of the channel
    """

    o.clear()

    # the one who will create channel
    user_1 = au.auth_register("z1234567@ad.unsw.edu.au", "kittykat", "First-Name1", "Last-Name1")
    u_id_1 = user_1['u_id']
    token_1 = user_1['token']

    # the one who will attempt to invite from a channel they don't have access to
    user_2 = au.auth_register("z1234568@ad.unsw.edu.au", "iloveyou", "First-Name2", "Last-Name2")
    u_id_2 = user_2['u_id']
    token_2 = user_2['token']

    # the one who will be invited
    user_3 = au.auth_register("z1234569@ad.unsw.edu.au", "iloveyou", "First-Name2", "Last-Name2")
    u_id_3 = user_3['u_id']

    channel_name = "Channel3000"

    # Channel created by user_1 and is currently only user with access
    channel_id = chs.channels_create(token_1, channel_name, True)['channel_id']

    # user_1 to retrive details
    (name, owners, members) = ch.channel_details(token_1, channel_id).values()

    assert name == channel_name

    # check user_1 in channel
    assert u_id_1 in [each['u_id'] for each in owners]  # created the channel
    assert u_id_1 in [each['u_id'] for each in members]

    # check user_2 is not a member of channel
    assert u_id_2 not in [each['u_id'] for each in members]

    # check user_3 is not a member of channel
    assert u_id_3 not in [each['u_id'] for each in members]

    # user_2 attempts to invite user_3 to existing channel but user_2 has no access
    with pytest.raises(error.AccessError):
        ch.channel_invite(token_2, channel_id, u_id_3)


def test_channel_invite_input_error_already():
    """
        Input Error:
        user being added is  already a member of the channel
    """

    o.clear()

    # the one who will create channel
    user_1 = au.auth_register("z1234567@ad.unsw.edu.au", "kittykat", "First-Name1", "Last-Name1")
    token_1 = user_1['token']

    # the one who will be invited twice
    user_2 = au.auth_register("z1234568@ad.unsw.edu.au", "iloveyou", "First-Name2", "Last-Name2")
    u_id_2 = user_2['u_id']

    channel_name = "Channel3000"

    # Channel created by user_1 and is currently only user with access
    channel_id = chs.channels_create(token_1, channel_name, True)['channel_id']

    # user_1 to retrive details
    __, __, members = ch.channel_details(token_1, channel_id).values()

    # check user_2 is not a member of channel
    assert u_id_2 not in [each['u_id'] for each in members]

    # first occurence of inviting user 2 into channel
    ch.channel_invite(token_1, channel_id, u_id_2)

    # user_1 to retrive details
    __, __, members = ch.channel_details(token_1, channel_id).values()

    # check user_2 is not a member of channel
    assert u_id_2 in [each['u_id'] for each in members]

    # user_1 attempts to invite user_2 again but is already a member of the channel
    with pytest.raises(error.InputError):
        # second occurence of inviting user 2 into channel
        ch.channel_invite(token_1, channel_id, u_id_2)


# ------------------- Tests of channel_details() ---------------------


def test_channel_details():
    """
        channel_details should reflect:
        the correct name
        the members
        the owners

    """

    o.clear()

    # the one who will create channel + invite people
    user_1 = au.auth_register("z1234567@ad.unsw.edu.au", "kittykat", "First-Name1", "Last-Name1")
    u_id_1 = user_1['u_id']
    token_1 = user_1['token']

    # the one who will be invited
    user_2 = au.auth_register("z1234568@ad.unsw.edu.au", "iloveyou", "First-Name2", "Last-Name2")
    u_id_2 = user_2['u_id']
    token_2 = user_2['token']

    channel_name = "channel1269"

    # create channel to retrieve channel_id
    channel_id = chs.channels_create(token_1, channel_name, True)['channel_id']

    # check the user_1 is in the list of users in the channel they created
    channel_lists = chs.channels_list(token_1)['channels']
    assert channel_id in [each['channel_id'] for each in channel_lists]

    # only invite user_2 into channel if the channel is not already listed in its channels_list
    channel_lists = chs.channels_list(token_2)['channels']
    if channel_id not in [each['channel_id'] for each in channel_lists]:
        # user_1 invite user_2
        ch.channel_invite(token_1, channel_id, u_id_2)

    # check the new user (user_2) is in the list of users in the channel
    channel_lists = chs.channels_list(token_2)['channels']
    assert channel_id in [each['channel_id'] for each in channel_lists]

    # user_1 to retrive details
    name, owners, members = ch.channel_details(token_1, channel_id).values()
    # string, list of dic, list of dic

    assert name == channel_name

    assert u_id_1 in [each['u_id'] for each in owners]  # created the channel
    assert u_id_2 not in [each['u_id'] for each in owners]  # not an owner

    assert u_id_1 in [each['u_id'] for each in members]
    assert u_id_2 in [each['u_id'] for each in members]


def test_channel_details_input_error_channel():
    """
        Input Error:
        channel_id does not refer to a valid channel
    """

    o.clear()

    # the one who will attempt to find the details of a non-existent channel
    user_1 = au.auth_register("z1234567@ad.unsw.edu.au", "kittykat", "First-Name1", "Last-Name1")
    token_1 = user_1['token']

    # A single channel created by user_1 and therefore the only channel
    channel_id = chs.channels_create(token_1, "Channel3000", True)['channel_id']

    # should not exist
    channel_id_2 = channel_id + 1

    # check channel_id_2 does not already exist
    all_channels = chs.channels_listall(token_1)['channels']
    assert channel_id_2 not in [each['channel_id'] for each in all_channels]

    # should return InputError since channel_id doesn't exist
    with pytest.raises(error.InputError):
        ch.channel_details(token_1, channel_id_2)


def test_channel_details_access_error():
    """
        Access Error:
        user (id by token) is not already a member of the channel
    """

    o.clear()

    # the one who will create channel
    user_1 = au.auth_register("z1234567@ad.unsw.edu.au", "kittykat", "First-Name1", "Last-Name1")
    token_1 = user_1['token']

    # the one who will attempt to invite from a channel they don't have access to
    user_2 = au.auth_register("z1234568@ad.unsw.edu.au", "iloveyou", "First-Name2", "Last-Name2")
    token_2 = user_2['token']

    # channel created by user_1 and therefore is currently the only member of the channel
    channel_id = chs.channels_create(token_1, "Channel3000", True)['channel_id']

    # # check the user_1 is in the list of users in the channel they created
    # channel_lists = chs.channels_list(token_1)['channels']
    # assert channel_id in [each['channel_id'] for each in channel_lists]

    # channel_lists = chs.channels_list(token_2)['channels']
    # # check user_2 is not a member of the channel therefore has no access
    # assert channel_id not in [each['channel_id'] for each in channel_lists]

    # user_2 (token_2) has no access to the channel
    with pytest.raises(error.AccessError):
        ch.channel_details(token_2, channel_id)


def test_channel_messages_no_msg():
    """
        Currently only testing an empty case in interation 1
        since less than 50 messages sent, should return:
        start == 0, end == -1
    """

    o.clear()

    # the one who will create channel
    user_1 = au.auth_register("z1234567@ad.unsw.edu.au", "kittykat", "First-Name1", "Last-Name1")
    token_1 = user_1['token']

    # channel created by user_1 and therefore is currently the only member of the channel
    channel_id = chs.channels_create(token_1, "Channel3000", True)['channel_id']

    # test functionality of returning start + end indices
    msg_list = ch.channel_messages(token_1, channel_id, 0)
    assert (msg_list['start'] == 0 and
            msg_list['end'] == -1 and
            len(msg_list['messages']) == 0)


def test_channel_messages_with_msgs(pre_test_setup):
    """ Tests of normal cases, few messages in the channel.
        See if the content, msg_id, reactions are correct.
    """

    __, token_1, __, channel_1 = pre_test_setup
    __ = msg.message_send(token_1, channel_1, "Hello")['message_id']
    msg_id_2 = msg.message_send(token_1, channel_1, "Hello2")['message_id']
    msg_list = ch.channel_messages(token_1, channel_1, 0)
    latest_msg = msg_list['messages'][0]

    assert len(msg_list['messages']) == 2
    assert msg_list['start'] == 0 and msg_list['end'] == -1

    # msg information
    assert latest_msg['message_id'] == msg_id_2
    assert latest_msg['message'] == "Hello2"

    # user_1 invoked channel_messages, user_1 didn't react to any message
    assert latest_msg['reacts'][0]['react_id'] == 1
    assert len(latest_msg['reacts'][0]['u_ids']) == 0
    assert not latest_msg['reacts'][0]['is_this_user_reacted']


def test_channel_messages_input_error_channel():
    """ Input Error
        channel_id does not refer to a valid channel
    """

    o.clear()

    # the one who will attempt to find the details of a non-existent channel
    user_1 = au.auth_register("z1234567@ad.unsw.edu.au", "kittykat", "First-Name1", "Last-Name1")
    token_1 = user_1['token']

    # should return InputError since channel_id doesn't exist
    with pytest.raises(error.InputError):
        ch.channel_messages(token_1, 999999, 1)


def test_channel_messages_input_error_total_messages():
    """
        Input Error:
        starting number is more than the amount of total messages

    """

    o.clear()

    # the one who will create channel
    user_1 = au.auth_register("z1234567@ad.unsw.edu.au", "kittykat", "First-Name1", "Last-Name1")
    token_1 = user_1['token']

    # channel created by user_1 and therefore is currently the only member of the channel
    channel_id = chs.channels_create(token_1, "Channel3000", True)['channel_id']

    with pytest.raises(error.InputError):
        ch.channel_messages(token_1, channel_id, 1)


def test_channel_messages_access_error():

    """
        Access Error:
        user (id by token) is not already a member of the channel
    """

    o.clear()

    # the one who will create channel
    user_1 = au.auth_register("z1234567@ad.unsw.edu.au", "kittykat", "First-Name1", "Last-Name1")
    token_1 = user_1['token']

    # the one who will attempt to see messages from a channel they don't have access to
    user_2 = au.auth_register("z1234568@ad.unsw.edu.au", "iloveyou", "First-Name2", "Last-Name2")
    token_2 = user_2['token']
    u_id_2 = user_2['u_id']

    # channel created by user_1 and therefore is currently the only member of the channel
    channel_id = chs.channels_create(token_1, "Channel3000", True)['channel_id']

    # user_1 to retrive details
    members = ch.channel_details(token_1, channel_id)['all_members']

    # check user_2 is not a member of channel
    assert u_id_2 not in [each['u_id'] for each in members]

    # user_2 (token_2) has no access to the existing channel
    with pytest.raises(error.AccessError):
        ch.channel_messages(token_2, channel_id, 0)


def test_channel_messages_over_50_msg(pre_test_setup):
    """ Test if the returned values are correct if there
        is more than 50 messages in the channel.
    """

    __, token_1, __, channel_1 = pre_test_setup

    for i in range(1, 51):
        msg_str = "Hello " + str(i)
        msg.message_send(token_1, channel_1, msg_str)

    msg_info = ch.channel_messages(token_1, channel_1, 0)
    start, end = msg_info['start'], msg_info['end']
    msg_list = [each['message'] for each in msg_info['messages']]

    assert end == 50 and start == 0
    assert msg_list[0] == "Hello 50" and msg_list[-1] == "Hello 1"
