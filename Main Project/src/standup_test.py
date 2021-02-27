'''
Standup tests
Compiled on 8 Novemeber 2020
standup_start, standup_active - Miriam Tuvel, z5257404
standup_send - Mia Bueno z5210209
'''

# Files
import channel as ch
import channels as chs
import auth as au
import error
import other as o
import user as u
import standup as su

# Library
import pytest
import time
import other as o
from datetime import datetime, timezone
import error


@pytest.fixture
def _pre_setup_():
    """ pytest fixture for registering and creating channels
        for functions: channel_addowner, channel_removeowner
    :return:
    """

    o.clear()
    a_reg = au.auth_register("mt@gmail.com", "nopassword", "Miriam", "Tuvel")
    b_reg = au.auth_register("hs@gmail.com", "Nopassword", "Hayden", "Smith")
    a_channel_id = chs.channels_create(a_reg['token'], "A", True)
    b_channel_id = chs.channels_create(a_reg['token'], "B", True)
    return a_reg, b_reg, a_channel_id, b_channel_id

#--------tests for standup_start-----------

def test_startstandup_invalidtoken(_pre_setup_):
    '''raise an access error because it is an invalid token'''
    __, __, a_channel_id, __ = _pre_setup_
    with pytest.raises(error.AccessError):
        su.standup_start('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU', a_channel_id['channel_id'], 10)


def test_startstandup_invalidchannel(_pre_setup_):
    '''raise an input error because it is an invalid channel'''
    a_reg, __, __, __ = _pre_setup_
    with pytest.raises(error.InputError):
        su.standup_start(a_reg['token'], 99999, 10)


def test_startstandup_alreadyactive(_pre_setup_):
    '''raise an input error because there is already an active standup'''
    a_reg, __, a_channel_id, __ = _pre_setup_
    su.standup_start(a_reg['token'], a_channel_id['channel_id'], 5)
    #since already started this should raise error
    with pytest.raises(error.InputError):
        su.standup_start(a_reg['token'], a_channel_id['channel_id'], 5)

def test_startstandup(_pre_setup_):
    '''starts a standup in the channel'''
    a_reg, __, a_channel_id, __ = _pre_setup_
    response = su.standup_start(a_reg['token'], a_channel_id['channel_id'], 1)
    beginning_time = int(time.time())
    #beginning_time = round(datetime.now().replace(tzinfo=timezone.utc).timestamp())
    assert response == {
        'time_finish': beginning_time + 1
    }
    time.sleep(1)

#------tests for standup_active-------

def test_standupactive_invalidtoken(_pre_setup_):
    '''raise an access error because it is an invalid token'''
    __, __, a_channel_id, __ = _pre_setup_
    with pytest.raises(error.AccessError):
        su.standup_active('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU', a_channel_id['channel_id'])


def test_standupactive_invalidchannel(_pre_setup_):
    '''raise an input error if not valid channel'''
    a_reg, __, __, __ = _pre_setup_
    with pytest.raises(error.InputError):
        su.standup_active(a_reg['token'], 99999)

def test_standupactive_nonactive(_pre_setup_):
    '''function should return False if no active standup'''
    a_reg, __, a_channel_id, __ = _pre_setup_
    response = su.standup_active(a_reg['token'], a_channel_id['channel_id'])
    assert response == {
        "is_active": False,
        "time_finish": None
    }

def test_standupactive_active(_pre_setup_):
    '''
    function should return True if active standup and other channel should have
    no standup
    '''
    a_reg, b_reg, a_channel_id, b_channel_id = _pre_setup_
    start_response = su.standup_start(a_reg['token'], a_channel_id['channel_id'], 6)
    active_response = su.standup_active(a_reg['token'], a_channel_id['channel_id'])
    assert active_response == {
        "is_active": True,
        "time_finish": start_response['time_finish']
    }
    active_response = su.standup_active(b_reg['token'], b_channel_id['channel_id'])
    assert active_response == {
        "is_active": False,
        "time_finish": None
    }
    time.sleep(6)
    
def test_standupactive_after(_pre_setup_):
    '''function should return False if active standup no longer'''
    a_reg, __, a_channel_id, __ = _pre_setup_
    start_response = su.standup_start(a_reg['token'], a_channel_id['channel_id'], 1)
    time.sleep(2)
    active_response = su.standup_active(a_reg['token'], a_channel_id['channel_id'])
    assert active_response == {
        "is_active": False,
        "time_finish": None
    }
    start_response = su.standup_start(a_reg['token'], a_channel_id['channel_id'], 3)
    active_response = su.standup_active(a_reg['token'], a_channel_id['channel_id'])
    assert active_response == {
        "is_active": True,
        "time_finish": start_response['time_finish']
    }
    time.sleep(5)
    active_response = su.standup_active(a_reg['token'], a_channel_id['channel_id'])
    assert active_response == {
        "is_active": False,
        "time_finish": None
    }
 
 
#-------tests for standup_send-----    
    
@pytest.fixture
def _pre_setup():
    """ 
    pytest fixture for registering users and creating channels
    for function: su.standup_send
    :return:
    """

    o.clear()

    user_1 = au.auth_register("mia@gmail.com", "miaiscool101", "Mia", "Bueno")
    user_2 = au.auth_register("hayden@gmail.com", "kittykat1269", "Hayden", "Smith")

    channel_a = chs.channels_create(user_1['token'], "Channel A", True)
    channel_a = channel_a['channel_id']

    channel_b = chs.channels_create(user_2['token'], "Channel B", False)
    channel_b = channel_b['channel_id']

    time_finish = su.standup_start(user_1['token'], channel_a, 5)['time_finish']

    return user_1, user_2, channel_a, channel_b, time_finish

def test_standup_send_invalid_channel (_pre_setup):
    """
    standup_send - channel id invalid
    :params: token, channel_id, message
    :raise: InputError
    """
    token = _pre_setup[0]['token']

    with pytest.raises(error.InputError):
        su.standup_send(token, 99999, "message")

def test_standup_send_long_message(_pre_setup):
    """
    standup_send - message is too long
    :params: token, channel_id, message
    :raise: InputError
    """
    token, channel_id = _pre_setup[0]['token'], _pre_setup[2]
    message_1000 = "Bacon ipsum dolor amet bresaola andouille frankfurter capicola pork loin buffalo. Ham meatloaf beef ribs shank strip steak pancetta jerky tri-tip picanha turkey ribeye tongue rump kevin brisket. Meatloaf capicola landjaeger ground round, drumstick leberkas cow pork salami sausage bresaola ham hock swine ball tip pig. Andouille pancetta ball tip ribeye, capicola cupim strip steak prosciutto swine boudin. Bresaola boudin shoulder, shankle sausage spare ribs burgdoggen ground round pig ham hock rump brisket shank jerky fatback. Boudin drumstick picanha prosciutto salami shank porchetta t-bone kevin capicola flank swine frankfurter landjaeger. Brisket kielbasa pork belly strip steak, meatloaf ham burgdoggen venison chislic buffalo tail.Ham shankle ribeye prosciutto cupim biltong turkey hamburger pork belly bresaola shank filet mignon beef. Cupim bacon doner, fatback sausage pancetta ribeye frankfurter corned beef rump filet mignon. Chicken frankfurter strip steak shankle, capicola fatback tail boudin flank rump drumstick turducken sausage. "

    # check standup is active
    assert su.standup_active(token, channel_id)['is_active'] == True

    with pytest.raises(error.InputError):
        su.standup_send(token, channel_id, message_1000)

def test_standup_send_inactive(_pre_setup):
    """
    su.standup_send - standup is not currently running
    :params: token, channel_id, message
    :raise: InputError
    """
    token, channel_id, time_finish = _pre_setup[0]['token'], _pre_setup[2], _pre_setup[4]

    # check standup is active
    assert su.standup_active(token, channel_id)['is_active'] == True
    
    time_now = int(time.time())
    #time_now = round(datetime.now().replace(tzinfo=timezone.utc).timestamp())
    time_diff = time_finish - time_now

    # delay for duration of time remaining
    time.sleep(time_diff)

    # standup should now be inactive (exceeded time limit of standup)
    assert su.standup_active(token, channel_id)['is_active'] == False

    with pytest.raises(error.InputError):
        su.standup_send(token, channel_id, "message")

def test_standup_send_non_member(_pre_setup):
    """
    standup_send - token refers to uid not member of channel
    :params: token, channel_id, message
    :raise: AccessError
    """
    token_1, channel_2 = _pre_setup[0]['token'], _pre_setup[3]
    with pytest.raises(error.AccessError):
        su.standup_send(token_1, channel_2, "message")

def test_standup_send_token_invalid(_pre_setup):
    """
    standup_send - token is an invalid token
    :params: token, channel_id, message
    :raise: AccessError
    """
    invalid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'
    channel = _pre_setup[2]
    with pytest.raises(error.AccessError):
        su.standup_send(invalid_token, channel, "message")

def test_standup_send(_pre_setup):
    """
    standup_send - test successful implementation
    :params: token, channel_id, message
    :add to data storage: append to messages in standup dict
    :return: nothing
    """
    user_1, __, channel_id, __, time_finish = _pre_setup

    # check if standup is active
    assert su.standup_active(user_1['token'], channel_id)['is_active'] == True

    # user 1 to send message
    message = "hello world!"

    su.standup_send(user_1['token'], channel_id, message)

    # remaining time of standup
    time_now = int(time.time())
    #time_now = round(datetime.now().replace(tzinfo=timezone.utc).timestamp())
    time_diff = time_finish - time_now

    # ensure empty
    assert not ch.channel_messages(user_1['token'], channel_id, 0)['messages']

    # wait for remaining time
    time.sleep(time_diff + 2)
    assert su.standup_active(user_1['token'], channel_id)['is_active'] == False

    # collect user details (first name)
    user_1_name = u.user_profile(user_1['token'], user_1['u_id'])['user']['handle_str']

    # what the expected collated message is 
    expected_data = f"{user_1_name}: {message}"

    # check that the messages sent were collated into the a single message in channel
    output = ch.channel_messages(user_1['token'], channel_id, 0)['messages'][0]['message']
    assert output == expected_data
    
