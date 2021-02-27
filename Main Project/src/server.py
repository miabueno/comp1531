""" This is the web server built for Flockr.
    File includes all http routes.

@date 22/10/2020

@author Yiyang Huang z5313425 (message/send, message/remove)

"""

# Libraries
# import sys
import os
from json import dumps
from flask import Flask, request, render_template
from flask_cors import CORS


# Src files
import auth as au
import message as msg
import channels as chs
import channel as ch
import user as u
import other
from error import InputError
import standup as st
import bonus as bn

def default_handler(err):
    """ Handling default error """
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response


# Helper functions for user_profile_uploadphoto


def img_server_path(profile):
    """ Combine the current server url with the image url

    Args:
        url (str): name of the image

    Returns:
        (str): the url to access image on current flockr server port
    """
    url = profile['profile_img_url']
    profile['profile_img_url'] = request.host_url + 'static/' + url
    return profile


def update_img_url(profile_list=None):
    """ Helper function that update img's url with current flask
        host url.

    Args:
        profile_list (list): list of profiles to be changed

    Returns:
        profile_list (list): list of profiles with 'profile_img_url' changed
    """
    try:
        if profile_list['profile_img_url'] != '':
            profile_list = img_server_path(profile_list)
    except:
        for index, profile in enumerate(profile_list):
            if profile['profile_img_url'] == '': continue
            profile_list[index] = img_server_path(profile)
    finally:
        return profile_list


APP = Flask(__name__)
CORS(APP)
APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, default_handler)


# Main routes


@APP.route("/echo", methods=['GET'])
def echo():
    """ Example """
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


@APP.route("/auth/login", methods=["POST"])
def auth_login_http():
    """ http route for auth_login funciton in auth.py
        wrapping the functionalities of auth_login in a
        http method
    """

    data = request.get_json()
    email, password = data['email'], data['password']
    return dumps(au.auth_login(email, password))


@APP.route("/auth/logout", methods=["POST"])
def auth_logout_http():
    """ http route for auth_logout funciton in auth.py
        wrapping the functionalities of auth_register in a
        http method
    """

    data = request.get_json()
    token = data['token']
    return dumps(au.auth_logout(token))


@APP.route("/auth/register", methods=["POST"])
def auth_register_http():
    """ http route for auth_register funciton in auth.py
        wrapping the functionalities of auth_register in a
        http method
    """
    data = request.get_json()
    email, password, name_first, name_last = data['email'], data['password'], \
                                       data['name_first'], data['name_last']
    return dumps(au.auth_register(email, password, name_first, name_last))


@APP.route("/auth/passwordreset/request", methods=["POST"])
def auth_passwordreset_request_http():
    """ http route for auth_passwordreset_request funciton in auth.py
        wrapping the functionalities in a http method
    """

    data = request.get_json()
    au.auth_passwordreset_request(data['email'])
    return {}


@APP.route("/auth/passwordreset/reset", methods=["POST"])
def auth_passwordreset_reset_http():
    """ http route for auth_passwordreset_reset funciton in auth.py
        wrapping the functionalities in a http method
    """

    data = request.get_json()
    au.auth_passwordreset_reset(data['reset_code'], data['new_password'])
    return {}


@APP.route('/channel/invite', methods=['POST'])
def channel_invite_http():
    '''http route for channel_invite'''

    token = request.get_json()['token']
    channel_id = int(request.get_json()['channel_id'])
    u_id = int(request.get_json()['u_id'])

    return dumps(ch.channel_invite(token, channel_id, u_id))


@APP.route('/channel/details', methods=['GET'])
def channel_details_http():
    '''http route for channel_details'''

    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    all_users = ch.channel_details(token, channel_id)
    all_users['owner_members'] = update_img_url(all_users['owner_members'])
    all_users['all_members'] = update_img_url(all_users['all_members'])

    return dumps(all_users)


@APP.route('/channel/messages', methods=['GET'])
def channel_messages_http():
    '''http route for channel_messages'''

    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))

    return dumps(ch.channel_messages(token, channel_id, start))


@APP.route("/channel/leave", methods=["POST"])
def channel_leave_http():
    """ http route for channel_leave()

        Return: Return values of channel_leave()
    """
    data = request.get_json()
    return dumps(ch.channel_leave(data['token'], int(data['channel_id'])))


@APP.route("/channel/join", methods=["POST"])
def channel_join_http():
    """ http route for channel_join()

        Return: Return values of channel_join()
    """
    data = request.get_json()
    return dumps(ch.channel_join(data['token'], int(data['channel_id'])))


@APP.route("/channel/addowner", methods=['POST'])
def channel_addowner_http():
    info = request.get_json()
    ch.channel_addowner(info['token'], int(info['channel_id']), int(info['u_id']))
    return {}


@APP.route("/channel/removeowner", methods=['POST'])
def channel_removeowner_http():
    info = request.get_json()
    ch.channel_removeowner(info['token'], info['channel_id'], info['u_id'])
    return {}


@APP.route("/channels/list", methods=["GET"])
def channels_list_http():
    """ http route for channels_list function in channels.py
        wrapping the functionalities of channels_list in a
        http method

        Return:
            (json) returns of channels_list
    """
    token = request.args.get('token')
    return dumps(chs.channels_list(token))


@APP.route("/channels/listall", methods=["GET"])
def channels_listall_http():
    """ http route for channels_listall function in channels.py
        wrapping the functionalities of channels_listall in a
        http method

        Return:
            (json) returns of channels_listall
    """
    token = request.args.get('token')
    return dumps(chs.channels_listall(token))


@APP.route("/channels/create", methods=["POST"])
def channels_create_http():
    """ http route for channels_create function in channels.py
        wrapping the functionalities of channels_create in a
        http method

        Return:
            (json) returns of channels_create
    """

    data = request.get_json()
    token, name, is_public = data['token'], data['name'], data['is_public']
    return dumps(chs.channels_create(token, name, is_public))


@APP.route("/message/send", methods=["POST"])
def message_send_http():
    """ http route for message_send()

        Return: Return values of message_send()
    """

    data = request.get_json()
    return dumps(msg.message_send(data['token'], int(data['channel_id']), data['message']))


@APP.route("/message/remove", methods=["DELETE"])
def message_remove_http():
    """ http route for message_remove()

        Return: Return values of message_remove()
    """

    data = request.get_json()
    return dumps(msg.message_remove(data['token'], int(data['message_id'])))


@APP.route("/message/edit", methods=["PUT"])
def message_edit_http():
    """ http route for message_edit funciton in message.py
        wrapping the functionalities of message_edit in a
        http method
    """

    data = request.get_json()
    msg.message_edit(data['token'], int(data['message_id']), data['message'])
    return {}


@APP.route("/message/sendlater", methods=["POST"])
def message_send_later_http():
    """ http route for message_sendlater function in message.py
    """
    token = request.get_json()['token']
    channel_id = int(request.get_json()['channel_id'])
    message = request.get_json()['message']
    time_sent = int(request.get_json()['time_sent'])

    return dumps(msg.message_send_later(token, channel_id, message, time_sent))


@APP.route("/message/react", methods=["POST"])
def message_react_http():
    """ http route for message_react()

        Return: Return values of message_react()
    """

    data = request.get_json()
    msg_id = int(data['message_id'])
    react_id = int(data['react_id'])
    msg.message_react(data['token'], msg_id, react_id)
    return {}


@APP.route("/message/unreact", methods=["POST"])
def message_unreact_http():
    """ http route for message_unreact()

        Return: Return values of message_unreact()
    """

    data = request.get_json()
    msg_id = int(data['message_id'])
    react_id = int(data['react_id'])
    msg.message_unreact(data['token'], msg_id, react_id)
    return {}


@APP.route("/message/pin", methods=['POST'])
def message_pin_http():
    '''http route for message_pin from message.py'''
    info = request.get_json()
    msg.message_pin(info['token'], int(info['message_id']))
    return {}


@APP.route("/message/unpin", methods=['POST'])
def message_unpin_http():
    '''http route for message_unpin from message.py'''
    info = request.get_json()
    msg.message_unpin(info['token'], int(info['message_id']))
    return {}


@APP.route("/message/broadcast", methods=['POST'])
def message_broadcast_http():
    """ **BONUS FUNCTION**
        http route for message_broadcast()
    """

    data = request.get_json()
    return dumps(msg.message_broadcast(data['token'], data['message']))


@APP.route('/user/profile', methods=['GET'])
def user_profile_http():
    '''http route for user_profile from user.py'''
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))

    profile_all = u.user_profile(token, u_id)
    profile_all['user'] = update_img_url(profile_all['user'])

    return dumps(profile_all)


@APP.route('/user/profile/setname', methods=['PUT'])
def user_profile_setname_http():
    info = request.get_json()
    u.user_profile_setname(info['token'], info['name_first'], info['name_last'])
    return {}


@APP.route('/user/profile/setemail', methods=['PUT'])
def user_profile_setemail_http():
    info = request.get_json()
    u.user_profile_setemail(info['token'], info['email'])
    return {}


@APP.route('/user/profile/sethandle', methods=['PUT'])
def user_profile_sethandle_http():
    '''http route for user_profile_sethandle from user.py'''
    info = request.get_json()
    u.user_profile_sethandle(info['token'], info['handle_str'])
    return {}


@APP.route("/users/all", methods=["GET"])
def users_all_http():
    """ http route for users_all function in channels.py
        wrapping the functionalities of users_all in a
        http method

        Return:
            (json) returns of users_all
    """
    token = request.args.get('token')

    users_all = other.users_all(token)
    users_all['users'] = update_img_url(users_all['users'])

    return dumps(users_all)


@APP.route("/admin/userpermission/change", methods=["POST"])
def admin_userpermission_change_http():
    """ http route for admin_userpermission_change function in channels.py
        wrapping the functionalities of admin_userpermission_change in a
        http method

        Return:
            (json) returns of admin_userpermission_change
    """

    data = request.get_json()
    token, u_id, permission_id = data['token'], data['u_id'], data['permission_id']
    return dumps(other.admin_userpermission_change(token, int(u_id), int(permission_id)))


@APP.route("/search", methods=["GET"])
def search_http():
    """ http route for other.search() """

    token = request.args.get('token')
    query_str = request.args.get('query_str')

    return dumps(other.search(token, query_str))


@APP.route("/other/clear", methods=['GET'])
def other_clear_http():
    """ http route for other.clear()
        Will clear all the information on stack.
    """
    other.clear()
    return {}


@APP.route("/standup/start", methods=['POST'])
def standup_start_http():
    """
    http route for standup_start
    will start a standup in channel
    Returns: time the standup finishes
    """
    info = request.get_json()
    response = st.standup_start(info['token'], int(info['channel_id']), info['length'])
    return dumps(response)


@APP.route("/standup/active", methods=['GET'])
def standup_active_http():
    """
    http route for standup_active
    will tell if a standup is active or not in the channel
    Returns: if there is an active standup and what time it finishes
    """
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(st.standup_active(token, channel_id))


@APP.route("/standup/send", methods=['POST'])
def standup_send_http():
    """
    http route for standup_send
    will send a message to get buffered into a standup queue
    """
    token = request.get_json()['token']
    channel_id = int(request.get_json()['channel_id'])
    message = request.get_json()['message']
    return dumps(st.standup_send(token, channel_id, message))


@APP.route('/user/profile/uploadphoto', methods=['POST'])
def user_profile_uploadphoto_http():
    """ Cropping and accessing photo of the given url.

    Returns:
        (str): name of the image
    """
    data = request.get_json()
    resp = u.user_profile_uploadphoto(data['token'], data['img_url'],
                            int(data['x_start']), int(data['y_start']),
                            int(data['x_end']), int(data['y_end']))
    return dumps(resp)


@APP.route('/imgurl/<filename>', methods=['GET'])
def user_photo(filename):
    """ When images are uploaded for a user profile,
        after processing them you should store them on the server
        such that your server now locally has a copy of the cropped
        image of the original file linked.

        *Now used for http testing only*

    Args:
        filename (str): name of the file (jpg)

    Returns:
        photo (html): render a html page with image on the top left corner.
    """

    return render_template('imgurl.html', name=filename)


if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
