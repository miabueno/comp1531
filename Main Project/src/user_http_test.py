"""
http tests for the user functions
Miriam Tuvel, z5257404 - user/setemail, user/setname
Mia Beuno, z5210209 - user/profile, user/sethandle
Compiled 25 October

user_profile_uploadphoto().
@author Yiyang (Sophia) Huang (z5313425)
@date 2020/11/04
Reviewed by Yue Dai (10/11/2020)

"""

import re
import json
import os
import urllib
from time import sleep

import pytest
import requests
from PIL import Image


@pytest.fixture
def _pre_setup(urls, data_setup):
    ''' Fixture of registering two users
    '''
    requests.get(urls['other_clear'])
    user_1 = requests.post(urls['auth_register'], json=data_setup[0]).json()
    user_2 = requests.post(urls['auth_register'], json=data_setup[1]).json()

    return user_1, user_2


def test_user_profile_updated(url, _pre_setup):
    '''testing when updates to profile are made,
    changes are reflected in return values of user_profile'''

    user_1 = _pre_setup[0]

    new_first = "jeff"
    new_last = "tatum"
    new_email = "mynameisjeff@gmail.com"
    new_handle = "mynameisjeff"

    # params to setname
    setname_data = {
        'token': user_1['token'],
        'name_first': new_first,
        'name_last': new_last,
    }

    # params to setemail
    setemail_data = {
        'token': user_1['token'],
        'email': new_email,
    }

    # params to sethandle
    sethandle_data = {
        'token':  user_1['token'],
        'handle_str': new_handle,
    }

    # update user_1's name to become new_first + new_last
    requests.put(url + "user/profile/setname", json=setname_data)

    # update user_1's email to become new_email
    requests.put(url + "user/profile/setemail", json=setemail_data)

    # update user_1's handle to become new_handle
    requests.put(url + "user/profile/sethandle", json=sethandle_data)

    # params for user/profile
    user_profile_data = {
        'token': user_1['token'],
        'u_id': user_1['u_id']
    }

    # by accessing the return value of user/profile, get data of user_1 before changes made
    user_profile_updated = requests.get(url + "user/profile", \
                                        params=user_profile_data).json()

    expected_data = {
        'u_id': user_1['u_id'],
        'email': new_email,
        'name_first': new_first,
        'name_last': new_last,
        'handle_str': new_handle,
        'profile_img_url': '',
    }

    # check that the updated output of user_profile matches expectations
    assert user_profile_updated['user'] == expected_data


def test_user_profile_invalid_uid(url, _pre_setup):
    '''testing input error, u_id does not exist'''

    user_1 = _pre_setup[0]

    users_all_data = {
        'token': user_1['token']
    }

    # access the return value of users/all
    all_users = requests.get(url + "users/all", params=users_all_data).json()
    all_uids = [int(user['u_id']) for user in all_users['users']]

    user_profile_data = {
        'token': user_1['token'],
        'u_id': max(all_uids) + 1,
    }

    # input error
    response = requests.get(url + "user/profile", params=user_profile_data)
    assert response.status_code == 400


def test_user_profile_invalid_token(url, _pre_setup):
    '''testing access error, token is invalid'''
    __, user_2 = _pre_setup

    # params for user_profile
    user_profile_data = {
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                 'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        'u_id': user_2['u_id']
    }

    # invalid token attempts to retrieve user info of user_2 (existing)
    # access error
    response = requests.get(url + "user/profile", params=user_profile_data)
    assert response.status_code == 400


def test_user_sethandle(url, _pre_setup):
    '''testing that the handle is updated'''

    # testing on user_1
    user_1 = _pre_setup[0]

    # intended new handle
    new_handle = "newmia"

    # params to sethandle
    sethandle_data = {
        'token':  user_1['token'],
        'handle_str': new_handle,
    }

    # update user_1's handle to become new_handle
    requests.put(url + 'user/profile/sethandle', json=sethandle_data)

    # params to retrive user_profile
    user_profile_data = {
        'token': user_1['token'],
        'u_id': user_1['u_id']
    }

    # by accessing the return value of user/profile, get data of user_1
    profile = requests.get(url + 'user/profile', params=user_profile_data)
    profile = json.loads(profile.text)

    # check user_1's handle updated to value of new_handle
    user_1_handle = profile['user']['handle_str']
    assert user_1_handle == new_handle


def test_sethandle_invalidtoken(url, _pre_setup):
    '''invalid token so returns an access error'''

    data = {
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                 'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        'handle_str': "validhandle",
    }

    # access error
    response = requests.put(url + "user/profile/sethandle", json=data)
    assert response.status_code == 400


def test_sethandle_shorthandle(url, _pre_setup):
    '''the handle is too short so returns input error'''

    user_1 = _pre_setup[0]

    data = {
        'token': user_1['token'],
        'handle_str': "mi",
    }

    # input error
    response = requests.put(url + "user/profile/sethandle", json=data)
    assert response.status_code == 400


def test_sethandle_longhandle(url, _pre_setup):
    '''handle too long so returns an input error'''
    user_1 = _pre_setup[0]

    data = {
        'token': user_1['token'],
        'handle_str': "miaissuperfergalicious",
    }

    # input error
    response = requests.put(url + "user/profile/sethandle", json=data)
    assert response.status_code == 400


def test_sethandle_taken(url, _pre_setup):
    '''handle is already used so raises input error'''

    user_1, user_2 = _pre_setup

    # params for user/profile
    data_1 = {
        'token': user_1['token'],
        'u_id': user_1['u_id'],
    }

    string = url + 'user/profile'

    user_1_profile = requests.get(string, params=data_1)
    user_1_profile = json.loads(user_1_profile.text)

    user_1_handle = user_1_profile['user']['handle_str']

    data_2 = {
        'token': user_2['token'],
        'handle_str': user_1_handle,
    }

    # input error
    response = requests.put(url + 'user/profile/sethandle', json=data_2)
    assert response.status_code == 400


def test_setname_invalidtoken(url, _pre_setup):
    '''invalid token so returns an access error'''
    data = {
        "token": 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                 'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        "name_first": "New",
        "name_last": "Name"
    }
    response = requests.put(url + "user/profile/setname", json=data)
    assert response.status_code == 400


def test_setname_smallfirstname(url, _pre_setup):
    '''firstname is less than 1 character so returns input error'''
    user1, __ = _pre_setup
    data = {
        "token": user1['token'],
        "name_first": "",
        "name_last": "Name"
    }
    response = requests.put(url + "user/profile/setname", json=data)
    assert response.status_code == 400


def test_setname_longfirstname(url, _pre_setup):
    '''firstname is longer than 50 characters so returns input error'''
    user1, __ = _pre_setup
    data = {
        "token": user1['token'],
        "name_first": "asseocarnisanguineoviscericartilaginonervomedullary",
        "name_last": "Name"
    }
    response = requests.put(url + "user/profile/setname", json=data)
    response.status_code == 400


def test_setname_shortlastname(url, _pre_setup):
    '''lastname is shorter than 1 characters so returns input error'''
    user1, __ = _pre_setup
    data = {
        "token": user1['token'],
        "name_first": "New",
        "name_last": ""
    }
    response = requests.put(url + "user/profile/setname", json=data)
    assert response.status_code == 400


def test_setname_longlastname(url, _pre_setup):
    '''lastname is longer than 50 characters so returns input error'''
    user1, __ = _pre_setup
    data = {
        "token": user1['token'],
        "name_first": "New",
        "name_last": "asseocarnisanguineoviscericartilaginonervomedullary"
    }
    response = requests.put(url + "user/profile/setname", json=data)
    assert response.status_code == 400


def test_setname_validnames(url, _pre_setup):
    '''if the function works it will update the first and last name'''
    user1, __ = _pre_setup
    data = {
        "token": user1['token'],
        "name_first": "New",
        "name_last": "Name"
    }
    resp = requests.put(url + "user/profile/setname", json=data).json()
    assert resp == {}

    new_resp = requests.get(url + "user/profile",
                                params={"token": user1['token'], "u_id": user1['u_id']}
                                ).json()
    assert new_resp['user']['name_first'] == "New" and  \
           new_resp['user']['name_last'] == "Name"


def test_setemail_invalidtoken(url, _pre_setup):
    '''
    if the token is invalid raises access error
    '''
    data = {
        "token": 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.'\
                 'xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU',
        "email": "z43678@gmail.com"
    }
    response = requests.put(url + "user/profile/setemail", json=data)
    assert response.status_code == 400


def test_invalid_email(url, _pre_setup):
    '''
    if the email is invalid raise input error
    '''
    user1, __ = _pre_setup
    data = {
        "token": user1['token'],
        "email": "z4268gmail.com"
    }
    response = requests.put(url + "user/profile/setemail", json=data)
    response.status_code == 400


def test_used_email(url, _pre_setup):
    '''
    if the email is already used raises input error
    '''
    user1, __ = _pre_setup
    data = {
        "token": user1['token'],
        "email": "comp1531.20t3.flockr@gmail.com",
    }
    response = requests.put(url + "user/profile/setemail", json=data)
    assert response.status_code == 400


def test_valid_email(url, _pre_setup):
    '''if function works it will update to a valid email'''
    user1, __ = _pre_setup
    data = {
        'token': user1['token'],
        "email": "newemail@gmail.com"
    }
    response = requests.put(url + "user/profile/setemail", json=data).json()
    assert response == {}

    # if correctly changes than the new email should update
    new_response = requests.get(url + "user/profile",
                                params={"token": user1['token'], "u_id": user1['u_id']}
                                ).json()
    assert new_response['user']['email'] == "newemail@gmail.com"


@pytest.fixture
def upload_data(_pre_setup):
    """ Pytest fixtures for data of user_profile_uploadphoto

    Args:
        _pre_setup (tuple): pytest fixtures with registration

    Returns:
        upload_data (dict): dictionary with parameters for user_profile_uploadphoto
    """
    user_1, __ = _pre_setup
    upload_data = {
        'token': user_1['token'],
        'img_url': 'https://media.geeksforgeeks.org/wp-content/'\
                   'uploads/20190715231713/flower11.jpg',
        'x_start': 0,
        'y_start': 0,
        'x_end': 200,
        'y_end': 200,
    }
    return upload_data


def test_upload_img_normal(url, _pre_setup, upload_data):
    """ Basic sanity test of uploading profile image.

        No specific ways to compare if 2 images are identical,
        so only compares dimensions here.

        Assumption: all tests are run from directory '/project'
    """

    user_1, __ = _pre_setup
    resp = requests.post(url + 'user/profile/uploadphoto', json=upload_data)
    assert resp.status_code == 200

    profile = requests.get(url + 'user/profile', params=user_1).json()
    uploaded_url = profile['user']['profile_img_url']
    assert uploaded_url != ''

    # Retrieve image from xxxxxx/imgurl/<filename>
    try:
        # Grab the html
        flask_img_path = f"{url}imgurl/{uploaded_url.split('/')[-1]}"
        page = urllib.request.urlopen(flask_img_path)
        html = page.read()
        # Find <img src=>
        tag = re.compile(rb'<img [^>]*src="([^"]+)')
        # Refine url
        img_url_str = '/'.join(tag.findall(html)[0].decode('utf-8').split('/')[1:])
        img_url_str = os.path.join(os.getcwd(), 'src', img_url_str)
        # Check size
        width, height = Image.open(img_url_str).size
        assert width == upload_data['x_end'] and height == upload_data['y_end']
    except FileNotFoundError:
        # No such directory
        pass


def test_upload_img_invalid_http_code(url, _pre_setup, upload_data):
    """ Testing for img_url returns an HTTP status other than 200.

        Raises:
            InputError
    """

    upload_data['img_url'] = 'http://www.bilibili.com/none'
    resp = requests.post(url + 'user/profile/uploadphoto', json=upload_data)

    assert resp.status_code == 400


def test_upload_img_exceeds_crop_length(url, _pre_setup, upload_data):
    """ Testing for any of x_start, y_start, x_end, y_end that are
        not within the dimensions of the image at the URL.

        Raises:
            InputError
    """

    upload_data['x_end'] = upload_data['y_end'] = 2000
    resp = requests.post(url + 'user/profile/uploadphoto', json=upload_data)

    assert resp.status_code == 400


def test_upload_img_negative_dimensions(url, _pre_setup, upload_data):
    """ Testing for giving negative input as coorinates to crop.

        Raises:
            InputError
    """

    upload_data['x_start'] = upload_data['y_start'] = -100
    upload_data['x_end'] = upload_data['y_end'] = -50
    resp = requests.post(url + 'user/profile/uploadphoto', json=upload_data)

    assert resp.status_code == 400


def test_uploadphoto_invalid_file_type(url, _pre_setup, upload_data):
    """ Testing when image uploaded is not a JPG.

        Raises:
            InputError
    """
    upload_data['img_url'] = 'https://www.pngkit.com/png/detail/300-3003753'\
                             '_jager-png-jager-rainbow-six-png.png'
    resp = requests.post(url + 'user/profile/uploadphoto', json=upload_data)

    assert resp.status_code == 400
