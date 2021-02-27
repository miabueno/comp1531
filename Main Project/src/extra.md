# Bonus Functions

@Yiyang Huang z5313425

@date 2020/11/15

***

## bonus.py

`channel_todo_create`
- Create a todo list in that channel
- Args:
    - token (str): the token of the authroized user
    - channel_id (int): ID of the channel that user want to create todo list in
- Exceptions:
    - AccessError: If user is not an authorized user
    - AccessError: If user is not an member of the channel
    - InputError: If there is already a todo list in the channel

`channel_todo_show`
- Show all of the todo items in the channel's todo list
- Args:
    - token (str): the token of the authorized user
    - channel_id (int): the channel ID of the todo list's channel that the user want to check
    - sort (boolean): determine if the return list should be sorted by significance
- Returns:
    - todos (list): list of all todo items in the channel. Dictionary contains related information of each todo item.
- Exceptions:
    - AccessError: If user is not an authorized user
    - AccessError: If user is not an member of the channel

`channel_todo_add`
- Add an item to the channel's todo list
- Args:
    - token (str): the token of the authorized user
    - channel_id (int): the ID of the channel that user want to add todo list item in
    - message (str): the message (topic) of the todo list item
    - level (int): 1 (not significant), 2, 3, 4 (Extremely urgent)
- Exceptions:
    - InputError: If level is > 4 or level is < 0
    - InputError: If message length is > 50 characters
    - AccessError: If user is not an authorized user
    - AccessError: If there is no todo list in the channel
    - AccessError: If user is not an member of the channel

`channel_todo_update`
- **Test currently incompleted**
- Update the status of a todo list item
- Args:
    - token (str): token of the authorized user
    - channel_id (int): ID of the channel that user want to update todo list item in
    - statu (boolean): status of the todo list item, completed or incomplete
    - todo_id (int): the id of the todo item
- Excetpion:
    - InputError: the todo_id doesn't exist
    - AccessError: if user is not an authorized user
    - AccessError: If user is not an member of the channel

`channel_todo_remove`
- **Test currently incompleted**
- Remove a todo list item from the channel's todo list
- Args:
    - token (str): the token of the authorized user
    - channel_id (int): the ID of the channel
    - todo_id (int): the id of the todo list item
- Exceptions:
    - AccessError: if user is not an authorized user
    - AccessError: If user is not an member of the channel


`message_broadcast`
- Allow owner of the flockr to send a message over all channels
- Args:
    - token (str): token of the authorised user
    - message (str): message to be sent
- Return: List of dictionaries, where each dictionary contains types { message_id }
- Exceptions:
    - InputError: if message is longer than 1000 characters
    - AccessError: if token input is invalid
    - AccessError: if the authorised user is not owner of Flockr
