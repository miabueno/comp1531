'''
User functions tests
user_profile tests, user_profile_sethandle tests done by Mia Bueno z5210209
user_profile_setemail tests, user_profile_setname tests done by Mia Bueno z5257404
Compiled October 21.

user_profile_uploadphoto tests done by Yiyang Huang z5313425
*Lower coverage of user.py due to black box testing,
 directory to save image is unknown*
Reviewed by Yue Dai (10/11/2020) 
2020/11/05
'''

# Libraries
import pytest
from PIL import Image, ImageChops
import os
import urllib
import requests

# Files
import channel as ch
import channels as chs
import auth as au
import user as u
import other as o
import error


@pytest.fixture
def _pre_setup():
    '''
    fixture of registering two users
    '''
    o.clear()
    user1 = au.auth_register("z55555@gmail.com", "PassWord", "Miriam", "Tuvel")
    user2 = au.auth_register("z66666@gmail.com", "PASSword", "Hayden", "Smith")
    return user1, user2


# ----tests for user_profile_setname------


def test_invalidtoken(_pre_setup):
    '''
    invalid token raises access error
    '''
    __, __ = _pre_setup
    invalid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                    'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'
    with pytest.raises(error.AccessError):
        u.user_profile_setname(invalid_token, "First", "Last")


def test_short_firstname(_pre_setup):
    '''
    if first name is less than one character raises input error
    '''
    user1, __ = _pre_setup
    with pytest.raises(error.InputError):
        u.user_profile_setname(user1['token'], '', 'Last')


def test_long_firstname(_pre_setup):
    '''
    if first name is longer than 50 letters raises input error
    '''
    user1, __ = _pre_setup
    with pytest.raises(error.InputError):
        u.user_profile_setname(user1['token'], 'asseocarnisanguineovisce'\
                                'ricartilaginonervomedullary', 'Last')


def test_short_lastname(_pre_setup):
    '''
    if the last name is shorter than one letter raises input error
    '''
    user1, __ = _pre_setup
    with pytest.raises(error.InputError):
        u.user_profile_setname(user1['token'], "First", '')


def test_long_lastname(_pre_setup):
    '''
    if the last name is longer than 50 letters raises input error
    '''
    user1, __ = _pre_setup
    with pytest.raises(error.InputError):
        u.user_profile_setname(user1['token'], "First",
                               "asseocarnisanguineoviscericartilaginonervomedullary")


def test_valid_names(_pre_setup):
    '''
    if the function works it will update the first and last name
    '''
    user1, __ = _pre_setup
    u.user_profile_setname(user1['token'], "First", "Last")
    #if it works it should update first and last name
    test = u.user_profile(user1['token'], user1['u_id'])
    assert test['user']['name_first'] == "First" and test['user']['name_last'] == "Last"


#----tests for user_profile_setemail-----


def test_invalid_token(_pre_setup):
    '''
    if the token is invalid raises access error
    '''
    __, __ = _pre_setup
    invalid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                    'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'
    with pytest.raises(error.AccessError):
        u.user_profile_setemail(invalid_token, "z43678@gmail.com")

def test_invalid_email(_pre_setup):
    '''
    if the email is invalid raise input error
    '''
    user1, __ = _pre_setup
    with pytest.raises(error.InputError):
        u.user_profile_setemail(user1['token'], "z4268gmail.com")


def test_alreadyused_email(_pre_setup):
    '''
    if the email is already used raises input error
    '''
    user1, user2 = _pre_setup
    user2_profile = u.user_profile(user2['token'], user2['u_id'])
    with pytest.raises(error.InputError):
        u.user_profile_setemail(user1['token'], user2_profile['user']['email'])


def test_valid_email(_pre_setup):
    '''
    if the function works properly it will update to the new email
    '''
    user1, __ = _pre_setup
    u.user_profile_setemail(user1['token'], "newemail@gmail.com")
    #if correctly changes than the new email should update
    test = u.user_profile(user1['token'], user1['u_id'])
    assert test['user']['email'] == "newemail@gmail.com"


@pytest.fixture
def _pre_setup():
    '''
    fixture of registering two users
    '''
    o.clear()
    user1 = au.auth_register("miabueno@gmail.com", "Password123", "Mia", "Bueno")
    user2 = au.auth_register("miabueno69@gmail.com", "adm1n@", "Mia", "Bueno")
    return user1, user2


# ------ tests for user_profile ------


def test_user_profile(_pre_setup):
    '''
    amend user details of existing user using other user_profile functions,
    check that user_profile reflects changes
    '''

    u_id1 = _pre_setup[0]['u_id']
    token1 = _pre_setup[0]['token']

    # collect info user_profile
    user1_profile = u.user_profile(token1, u_id1)['user']

    # collect a list of all users to cross check details
    all_users = o.users_all(token1)['users']

    # using this instead to cross check so I'm not hard coding first & last name + email etc
    for user in all_users:
        if user['u_id'] == u_id1:
            assert user['email'] == user1_profile['email']
            assert user['name_first'] == user1_profile['name_first']
            assert user['name_last'] == user1_profile['name_last']
            assert user['handle_str'] == user1_profile['handle_str']
            break

    new_first_name = "NewMia"
    new_last_name = "NewBueno"
    new_email = "miab999@yahoo.com"
    new_handle = "fergaliciousmia"

    # update user's details
    u.user_profile_setname(token1, new_first_name, new_last_name)
    u.user_profile_setemail(token1, new_email)
    u.user_profile_sethandle(token1, new_handle)

    # collect updated info user_profile
    user1_profile = u.user_profile(token1, u_id1)['user']

    # check the new output of user_profile matches new variables
    assert user1_profile['email'] == new_email
    assert user1_profile['name_first'] == new_first_name
    assert user1_profile['name_last'] == new_last_name
    assert user1_profile['handle_str'] == new_handle


def test_user_profile_invalid_token(_pre_setup):
    '''
    invalid token raises access error
    '''
    user1 = _pre_setup[0]['u_id']
    invalid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                    'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'
    with pytest.raises(error.AccessError):
        u.user_profile(invalid_token, user1)


def test_user_profile_invalid_uid(_pre_setup):
    '''
    if u_id does not refer to valid user, raise input error
    '''
    token1 = _pre_setup[0]['token']
    invalid_uid = 999999

    # check that the assumed invalid id does not already exist
    all_users = o.users_all(token1)['users']
    print(all_users)

    # this used to be an assert if you're confused but what I'm trying to say is:
    # don't raise error to test for invalid id if in fact 99999 is actually a valid id
    if invalid_uid not in [user['u_id'] for user in all_users]:
        with pytest.raises(error.InputError):
            u.user_profile(token1, invalid_uid)


# ------ tests for user_profile_sethandle ------


def test_user_profile_sethandle(_pre_setup):
    '''
    testing that the handle is updated
    '''
    user1 = _pre_setup[0]

    # Update the authorised user's handle from miabueno0 ==> newmia
    u.user_profile_sethandle(user1['token'], "newmia")


def test_user_profile_sethandle_invalid_token():
    '''
    invalid token raises access error
    '''
    invalid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                    'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'
    with pytest.raises(error.AccessError):
        u.user_profile_sethandle(invalid_token, "validhandle")


def test_user_profile_sethandle_short(_pre_setup):
    '''
    if the handle is too short (< 3 char in length), raise input error
    case: updated handle is 2 characters long
    '''
    user1 = _pre_setup[0]

    with pytest.raises(error.InputError):
        u.user_profile_sethandle(user1['token'], "mi")


def test_user_profile_sethandle_long(_pre_setup):
    '''
    if the handle is too long (> 20 char in length), raise input error
    case: updated handle is 22 characters long
    '''
    user1 = _pre_setup[0]

    with pytest.raises(error.InputError):
        u.user_profile_sethandle(user1['token'], "miaissuperfergalicious")


def test_user_profile_sethandle_taken(_pre_setup):
    '''
    if the handle is already used by another user, raise input error

    case:
    > there are 2 x users named mia bueno and so
    > the default handles generated for user1 and user2
    > are respectively miabueno0 and miabueno1

    > user 2 will attempt to update their handle to miabueno0
    '''
    user1, user2 = _pre_setup

    # retrive user1 handle
    user1_handle = u.user_profile(user1['token'], user1['u_id'])['user']['handle_str']

    with pytest.raises(error.InputError):
        u.user_profile_sethandle(user2['token'], user1_handle)


@pytest.fixture
def images_url():
    """ Pytest fixture that stores url for image online

    Returns:
        [dict]: dictionary that contains url of images.
    """
    images = {
        0:  'https://media.geeksforgeeks.org/wp-content/'\
            'uploads/20190715231713/flower11.jpg',
        1:  'https://upload.wikimedia.org/wikipedia/commons'\
            '/4/47/PNG_transparency_demonstration_1.png',
        2:  'http://www.bilibili.com/none.jpg',
    }
    return images


def test_uploadphoto_normal(_pre_setup, images_url):
    """ Testing a normal function of user_profile_uploadphoto().

        From the spec: Given a URL of an image on the internet, crops
        the image within bounds (x_start, y_start) and (x_end, y_end).
        Position (0,0) is the top left.
    """
    user_1, __ = _pre_setup
    img_url = images_url[0]

    # Upload image
    u.user_profile_uploadphoto(user_1['token'], img_url, 0, 0, 200, 200)
    uploaded_url = u.user_profile(user_1['token'], user_1['u_id'])\
                    ['user']['profile_img_url']

    assert uploaded_url != ''


def test_uploadphoto_invalid_http_code(_pre_setup, images_url):
    """ Testing for img_url returns an HTTP status other than 200.

        Raises:
            InputError
    """
    token_1 = _pre_setup[0]['token']

    with pytest.raises(error.InputError):
        u.user_profile_uploadphoto(token_1, images_url[2], 0, 0, 200, 200)


def test_uploadphoto_exceeds_crop_length(_pre_setup, images_url):
    """ Testing for any of x_start, y_start, x_end, y_end that are
        not within the dimensions of the image at the URL.

        Raises:
            InputError
    """
    token_1 = _pre_setup[0]['token']

    with pytest.raises(error.InputError):
        u.user_profile_uploadphoto(token_1, images_url[0], 0, 0, 2000, 2000)


def test_uploadphoto_negative_dimensions(_pre_setup, images_url):
    """ Testing for giving negative input as coorinates to crop.

        Raises:
            InputError
    """
    token_1 = _pre_setup[0]['token']

    with pytest.raises(error.InputError):
        u.user_profile_uploadphoto(token_1, images_url[0], -8, -8, -5, 10)


def test_uploadphoto_invalid_file_type(_pre_setup, images_url):
    """ Testing when image uploaded is not a JPG.

        Raises:
            InputError
    """
    token_1 = _pre_setup[0]['token']

    with pytest.raises(error.InputError):
        u.user_profile_uploadphoto(token_1, images_url[1], 0, 0, 200, 200)
