'''
User functions
user_profile, user_profile_sethandle done by Mia Bueno z5210209
user_profile_setemail, user_profile_setname done by Mia Bueno z5257404
Compiled October 21.

user_profile_uploadphoto().
@author Yiyang (Sophia) Huang (z5313425)
@date 2020/11/04

'''

# Libraries
import re
import pytest
from PIL import Image
import os
import urllib
import requests

# Src files
from channel import token_to_uid, is_uid_valid
import users_channels as uc
import error


def user_profile(token, u_id):
    """Return information about user (u_id, email, first + last name, handle)
    :param token, u_id
    :return: if valid, return user info. else, raise InputError
    """

    # check user requesting info valid token
    __ = token_to_uid(token)

    # check valid u_id
    is_uid_valid(u_id)

    email = uc.users[u_id]['email']
    first_name = uc.users[u_id]['name_first']
    last_name = uc.users[u_id]['name_last']
    handle = uc.users[u_id]['username']
    url = uc.users[u_id]['profile_img_url']

    return {
        'user': {
            'u_id': u_id,
            'email': email,
            'name_first': first_name,
            'name_last': last_name,
            'handle_str': handle,
            'profile_img_url': url,
        },
    }


def user_profile_setname(token, name_first, name_last):
    """
    Description: Update the token's first and last name
    Param: token, first name, last name
    Return: if token is invalid returns access AccessError, if first or last name
    isnt valid return InputError, else return nothing.
    """
    #if token is not valid cause access error
    user_uid = token_to_uid(token)
    #if the first name is not between 1-50 characters cause input error
    if len(name_first) < 1 or len(name_first) > 50:
        raise error.InputError("Invalid first name. First name should be between 1-50 charactesrs. (user_setname)")
    #if the last name is not between 1-50 characters cause input error
    if len(name_last) < 1 or len(name_last) > 50:
        raise error.InputError("Invalid last name. Last name should be between 1-50 charactesrs. (user_setname)")
    #update the token's first and last name
    uc.users[user_uid]['name_first'] = name_first
    uc.users[user_uid]['name_last'] = name_last

    return {}


def user_profile_setemail(token, email):
    """
    Description: Update the token's email
    Param: token, email
    Return: if token is invalid returns access AccessError, if email isn't valid
    return InputError, else return nothing.
    """
    #if token is not valid raise access error
    user_uid = token_to_uid(token)
    #if the email is not valid raise input error
    if '@' not in email:
        raise error.InputError("Invalid email adress. (user_profile_setemail)")
    #if the email address is already being used by another user raise input error
    u_id = 0
    for u_id in uc.users:
        if uc.users[u_id]['email'] == email:
            raise error.InputError("Email already exist. (user_profile_setemail)")
    u_id += 1
    #update the users email address
    uc.users[user_uid]['email'] = email

    return {}


def user_profile_sethandle(token, handle_str):
    """Update user's handle
    :param token, handle_str
    :valid: handle_str must be >= 3 and <= 20 AND handle is not already used
    :return: if valid, updates user's handle details. else, raise InputError
    """

    # check valid token
    u_id = token_to_uid(token)

    # check within character limit
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise error.InputError("Invalid handle, handle should be between 3-20 characters in length. (user_profile_sethandle)")

    # check handle not taken
    for __, user_info in uc.users.items():
        if user_info['username'] == handle_str:
            raise error.InputError("Handle already taken. (user_profile_sethandle)")

    # set new handle
    uc.users[u_id]['username'] = handle_str

    return {}


def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    """ Given a URL of an image on the internet, crops the image within
        bounds (x_start, y_start) and (x_end, y_end).

        Position (0,0) is the top left.

        Assumption: ASSUME ALL TESTS RUNNING FROM '/project'

    Args:
        token (str): the token of the authorized user
        img_url (str): the url of the image
        x_start (int): the x coordinate that user want to start cropping
        y_start (int): the y coordinate that user want to start cropping
        x_end (int): the x coordinate that user want to stop cropping
        y_end (int): the y coordinate that user want to stop cropping
    """

    # Check for invalid token
    uid = token_to_uid(token)

    # Error cases
    if img_url[-3:] != 'jpg':
        raise error.InputError("Invalid file type.")

    if requests.get(img_url).status_code != 200:
        raise error.InputError("Can't access the url")

    # Get the image
    # Change the name to make it harder to have duplicate names
    file_name = str(f'{token[-5:]}' + img_url.split('/')[-1])
    target_folder = f'src/static/{file_name}'
    urllib.request.urlretrieve(img_url, target_folder)

    # Open the image and get its size
    full_path = os.path.join(os.getcwd(), target_folder)
    photo = Image.open(full_path)
    width, height = photo.size

    # Invalid dimensions
    if any(point < 0 for point in (x_end, x_start, y_end, y_start)) or \
       any(point > width for point in (x_end, x_start)) or \
       any(point > height for point in (y_end, y_start)):
        os.remove(full_path)
        raise error.InputError("Invalid Image cropping dimension.")

    # Crop and save the image
    cropped = photo.crop((x_start, y_start, x_end, y_end))
    cropped.save('src/static/' + file_name)

    # Not sure to return 'full_path' or 'file_name'
    uc.users[uid]['profile_img_url'] = file_name
    return {}
