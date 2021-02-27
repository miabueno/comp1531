# Assumptions
> by thu13grape5

## Overall Assumptions
- Assume the user will always provide all the parameters needed
- Assume the user will always provide the parameters in the required type
    - e.g. For user using channel_join(token, channel_id), we assume that the channel_id will be an integer.
- ~~Assume the first user (user_0) that register on Flockr will become owner of the flockr (i.e. permission_id = 1), therefore:~~
    - ~~user_0 will be automatically become a member and owner of every channel since channel's creation~~

***

### users_channels.py

* the data structure (using the dictionary data structure) to store user information and channel information
* details about the users dictionary and the channels dictionary (data type and dictionary structure and keys) are
listed in details in users_channels.py.

***

### auth.py

#### Token authentication assumptions
* The authenticated token is encoded using the users' email (i.e. {'email': 'z0000000@ad.unsw.edu.au'}) and the SECRET message stored as a global variable inside the global database file (users_channels.py)
* token returned from auth_login (and auth_register) is the authenticated token using the jwt library.
* Only the decoded version of the token is stored inside the global database (in users_channels.py), the authenticated token is not stored in the global database.
* All token passed in from the front-end in other functions need to be decoded using a helper function (see channel.py) back into the users' email dictionary. The email string is then used inside functions as the token.
* Invalid tokens in testings currently uses a jwt encoded version of an empty string (i.e. {'email': ''}) with the constant SECRET. This invalid token is: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IiJ9.xHoCwEdcs3P9KwoIge-H_GW39f1IT3kECz_AhckQGVU'
* token expiry and session time is not implemented

##### `auth_login`

* checking the validily of the email follows the website that the specificaiton provided with alterations, it ensures that multiple dots '.', lowercase and uppercase letters is included as part of the email string before '@'. Following the '@', there can be any characters of any length then following a '.' then two or three more characters.

##### `auth_logout`

* the invalidation of the token to log the user out is currently handled by emptying the token string (e.g. original token is: token = 'useremail@email.com', after invalidation, the token will become token = '')

##### `auth_register`

* handle is only modifiable if the handle is automated handle is already taken
* modified handles are cut off at 20 characters
* the handle is treated as the username of the registered user, the last two characters of the string of the handle is preserved to store numbers for repeated handles. --> when a handle already exits in the data, the way to treat those repeated handle is to increment the digits at the end of the handle string (convert the integer to integer type, increment it, convert back to string type and append again at the end of the handle)
* email address must not already exist regardless if first name and last name exists
* when a user has successfully registered for an account, this user will be automatically logged in (i.e. will not be promoted back to the login page to be logged in) --> funciton wise, this means that auth_login is called inside auth_register for users that are successfully logged in. Hence, the token returned from auth_register will be the same token as returned from auth_login

##### `auth_passwordreset_request`
* The email used is a gmail account for emails to be sent successfully.
* Assume email sent will never raise exception error (i.e. email sent unsuccessfully)
* reset_code (secret_code):
    - reset_code always start with the substring "RS" (stands for reset code)
    - the thrid character in the string (following 'RS') is the u_id of the user
    - the rest of the string is randomly generate using python libraries (random & choice)
    - the length of the subsequent string follwoing 'RS' + str(u_id) is the same length as the encrypted password stored inside the users data strucutre
* The email provided in auth/passwordreset/request page must be a valid email that is stored inside the users dataa structure. This ensures that the email is provided by an originally registered user. It will raise AccessError if the email provided is not stored inside the users dictionary (i.e. unregistered email)
* The reset_code will be stored inside the users dictionary with the key ['reset_code'] for future checks.
* The email sent through request has body message in the form: "Security code: reset_code". 
* All tests related to auth_passwordreset_request is while box testing, since every groups' method of sending structuring the body message of the email is different.
* A receive_email helper function is added into the tests to extract the reset_code for testing reasons. This helper function is white-box and will not work for other groups' implementation of the reset_code.


##### `auth_passwordreset_reset`
* The user will be prompted back to the login page after resetting the password.
* The method to classify that the reset_code is incorrect is to compare the passed in string to the one stored inside the users dictionary.
* The new password will replace the original password in the users dictionary, and it is going to be encrypted using the password encryption method.

***

### channel.py

##### `token_to_uid`
* search for the uid of the user given token
* raise AccessError if the token does not exist in the dictionary

##### `channel_invite`

* The user does not need to accept / decline request
* Once invited, the user is added immediately without the users' approval
* Any member of the channel can invite other existing users into the channel
* The user being added is not already in the channel

##### `channel_details`

* details about the channel include name, owner members of the channel and all members

##### `channel_messages`

* return at most 50 message from the starting index
* if more than 1 message have the same rounded timestamp, it can be shown in any order relative to each other

##### `channel_leave`

- User can only leave the channel if the user is already a member/owner of the channel
- When an owner of the channel leaves the channel, the owner of the channel will be removed from both 'member' and 'owner''s lists.

##### `channel_join`
- When user with permission_id == 1 joins a channel:
    - the user automatically becomes owner and member of the channel when the user joins the channel
    - the user can join both private and public channel succesfully
- When user with permission_id == 2 joins a channel:
    - the user is just a member of the channel
- multiple channel_join of the same user will be ignored

##### `channel_addowner`
* owners of flockr are seen as super owner (owner of everything) and can add
to any group
* approval is not requested, if valid, the user associated with user_id is added immediately as an owner
* if a non-member is added as an owner they are also added as a member

##### `channel_removeowner`

* when an owner is removed it does not remove them as member
* same as channel_addowner
* a channel can have no owners - only the owner of all FLOCKR (the owner of flockr can remove a remaining channel owner)
* the owners of all FLOCKR can not be removed - if tried raises input error
* an owner can remove themselves

***

### channels.py

##### `channels_list`

* returns a list of channels associated with user_id

##### `channels_listall`

* returns a list of all existing channels regardless if the user is a member or not
* listing private and public is not considered at this iteration (1)
* channels are listed in order of *

##### `channels_create`

* anyone with an exisiting account can create a public or private channel
* channel_id generated by index in list
* ~~Channel name is unique~~
* the user that creates a new channel becomes the owner of the channel
* the user that creates a new channel also becomes a member of the channel
* owner of all FLOCKR automaticcally added into a new channel as owner and member of the channel

***

### other.py

##### `clear`
- clears both 'users' and 'channel' dictionary
- reset the TOTAL_MSG (# of messages inside the server) to 0

##### `users_all`
- returns a list of all existing users regardless of their status

##### `admin_userpermission_change`
- Change the users global permission, not related to any channel permission
- permission ID is located in user database in users_channels.py

##### `search`
- Upper-case and lower-case letters are treated differently (i.e 'Hello)' and 'hello' will give different results)
- All punctuations, symbols and spaces are inclusive in search

***

### messages.py

##### `message_send`
- Owner of the flockr can only send a message in the channel if himself is inside the 'members'/'owner' list of the channel
- User can not send empty string ("") as message, it raises error.InputError()

##### `message_remove`
- Owner of the flockr can remove message without joining the channel
- Owner of the flockr can remove message sent by anyone
- Owner of the channel can remove message sent by other owner of the channel or owner of the flockr
- Normal user (not owner in any kind) can only remove message sent by the user himself

##### `message_edit`
- InputError will be raised if the new message is greater than 1000 characters in length
- message_edit will call message_remove function is the new message is an empty string to delete the original message
- message_id of will not be stored inside the message_id key of the user who edited the message in the users database
(users dictionary in users_channels.py).
- The edited message will still be treated as sent by it's original user instead of being sent by the user who edited it.
- Same as message_remove, normal user (not owner in any kind) can only remove message sent by the user themselves.
- Same as message_send, owner of the flockr can only send a message in the channel if himself is inside the 'members'/'owner' list of the channel

##### `message_react`
- Types of reacts are stored in 'users_channels.py'
- Tests of message_react and message_unreact are generalized to suit future changes to the types of reacts.

***

### user.py

##### `user_profile_setemail`
* For an email to be valid it must have an @ sign

##### `user_profile_setname`
* Users can have the same first or last name or both

##### `user_profile`
* Users can request the user_profile details for any user
* including themselves

##### `user_profile_sethandle`
* Users can modify their handle to be any combination of characters
* (within input error exception limitation)

##### `user_profile_uploadphoto`
- url that does not end with '.jpg' are considered as invalid url (because it can't be opened through urllib.urlretreive)
- tests of user_profile_uploadphoto_normal_behavior is **not black box testing** because of the sever url '/imgurl/filename' in server.py. The test is unable to be black boxed, cosidering that not every group save the image in the same directory.
    - Details about this url is in section of server.py.
- 'profile_img_url' stores the path to local directory of 'static'. This path is updated in sever.py to give user access to image through the flask server url.

***

### server.py

##### `/imgurl/<filename>`
- This url is for testing the normal behavior of 'user_profile_uploadphoto' **only**.

#### 'standup_start'
* When the standup is done message_send places the accumulated message in channel messages

#### 'standup_send'
* All messages sent during an active standup activate standup_send.
