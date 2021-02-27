'''
Standup functions
Compiled 8 November 2020
standup_start and standup_active - Miriam Tuvel, z5257404
standup_send - Mia Beuno z5210209
'''


# Files
import users_channels as uc
import error
from user import user_profile
import channel as ch
from message import message_send
import time
from threading import Timer
from datetime import datetime, timezone


def standup_occurs(channel_id):
    '''
    Description: Checks every second if any channel is done standup_active
    No parameters or returns
    '''
  
    token = uc.channel[channel_id]['standup']['token']
    message = '\n'.join(uc.channel[channel_id]['standup']['messages']) 
    #send all in standup as normal message
    #if len(message) > 1:
    #    message_send(token, channelId, message)
   
    #clear all of the standup in that channel 
    uc.channel[channel_id]['standup']['is_active'] = False
    uc.channel[channel_id]['standup']['time_finish'] = None
    uc.channel[channel_id]['standup']['messages'] = []
    #send all in standup as normal message
    if len(message) > 1:
        return message_send(token, channel_id, message)
def standup_start(token, channel_id, length):
    '''
    Description: starts a standup in a certain channel for a length of time
    Parameters: token, channel_id and length
    Returns: a dict of the time the standup finishes
    '''
    #if the token is invalid raise access error
    ch.token_to_uid(token)
    #if the channel is invalid raise input error
    ch.is_channel_id_valid(channel_id)

    #if the channel currently have a standup raise input error
    if uc.channel[channel_id]['standup']['is_active'] == True:
        raise error.InputError("Already active standup (standup_start)")

    #make standup active
    uc.channel[channel_id]['standup']['is_active'] = True
    uc.channel[channel_id]['standup']['token'] = token
    #make a time stamp for when it finishes
    timestamp = int(time.time()) + length
    uc.channel[channel_id]['standup']['time_finish'] = timestamp
    t = Timer(length, standup_occurs,[channel_id])
    t.start() 
    #returns the time the standup finishes
    return {
        'time_finish': uc.channel[channel_id]['standup']['time_finish']
    }
    
def standup_active(token, channel_id):
    """
    Description: says whether or not a channel has a standup currently
    Parameters: token and channel_id
    Returns: a dict telling if it is active and what time the standup finishes
    """
    #if the token is invalid raise access error
    ch.token_to_uid(token)
    #if the channel is invalid raise input error
    ch.is_channel_id_valid(channel_id)

    #return dictionary of if the standup is active and what time it finishes
    is_active = uc.channel[channel_id]['standup']['is_active']
    time_finish = uc.channel[channel_id]['standup']['time_finish']
    return {
        'is_active': is_active,
        'time_finish': time_finish
    }    



def standup_send(token, channel_id, message):
    """
    Sending a message to get buffered in the standup queue
    :params: token, channel_id, message
    :changes: appends message to standup data 
    """

    # convert token to uid --> also raise AccessError if invalid token
    u_id = ch.token_to_uid(token)

    # channel id invalid
    ch.is_channel_id_valid(channel_id)

    # auth user not member of channel
    if not ch.is_user_member(u_id, channel_id):
        raise error.AccessError("not member of channel (standup_send)")
    
    # standup not currently active
    if uc.channel[channel_id]['standup']['is_active'] == False:
        raise error.InputError("No active standup (standup_send)")
    
    # message too long (> 1000 char)
    if len(message) > 1000:
        raise error.InputError("Message to long (standup_send)")

    username = user_profile(token, u_id)['user']['handle_str']
    concat_msg = f"{username}: {message}"

    uc.channel[channel_id]['standup']['messages'].append(concat_msg)

    return {}
