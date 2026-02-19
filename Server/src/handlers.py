import router
import handle_client
import state
import servermain
import utilities
import json

def add_user(username, client, should_broadcast=True):
    state.users[username] = {
        "socket": client,
        "state": "IDLE",
        "chat_with": None
    }
    if should_broadcast:
        broadcast_user_list()
    print(state.users)


def remove_user(username):
    if username in state.users:
        del state.users[username]
        broadcast_user_list()
        print(state.users)



def set_user_state(username, new_state, chat_with=None):
    user = state.users[username]
    user["state"] = new_state
    user["chat_with"] = chat_with
    # only broadcast when returning to idle, not during chatting transitions
    if new_state == "IDLE":
        broadcast_user_list()
    print(state.users)


def handle_register(client, message):
    u = message.get('username')
    if not u:
        utilities.send_error(client, 'invalid_request', 'missing username')
        return

    if u in state.users:
        utilities.send(client, 'register_result', {"message": "Username_Taken"})
        return

    # register user without broadcasting yet
    add_user(u, client, should_broadcast=False)
    # send register result then broadcast to all idle users
    utilities.send(client, 'register_result', {"message": "ok"})
    broadcast_user_list()

def handle_chat(from_username, to, payload):
    utilities.send(state.users[to]['socket'], 'chat', payload)

# handles chat end from one user, notifies both and returns to idle
def handle_chat_end(client, from_username):
    from_user_info = state.users[from_username]
    partner = from_user_info.get('chat_with')
    
    if not partner or partner not in state.users:
        return
    
    # set both users back to idle
    set_user_state(from_username, "IDLE", None)
    set_user_state(partner, "IDLE", None)
    
    # notify both and broadcast
    utilities.send(from_username, 'chat_ended', {"message": "Chat ended"})
    utilities.send(partner, 'chat_ended', {"message": "Chat ended"})
    broadcast_user_list()

def broadcast_user_list():
    # only send idle users to idle users
    # snapshot to prevent 'dictionary changed size during iteration'
    user_items = list(state.users.items())
    idle_users = [u for u, info in user_items if info['state'] == "IDLE"]
    payload = {'users': idle_users}
    for username, info in user_items:
        if info['state'] == "IDLE":
            sock = info.get('socket')
            if sock:
                utilities.send(sock, 'user_list', payload)


def handle_chatrequest(client, from_username, payload):
    target_user = payload.get("target")
    
    # reject self-requests
    if from_username == target_user:
        utilities.send(client, 'chatrequest_result', {"message": "declined", "from": target_user, "reason": "Cannot chat with yourself"})
        return
    
    # check if target exists and is idle
    if target_user not in state.users:
        utilities.send(client, 'chatrequest_result', {"message": "declined", "from": target_user, "reason": "User not found"})
        return
    
    target_info = state.users[target_user]
    if target_info['state'] != "IDLE":
        utilities.send(client, 'chatrequest_result', {"message": "declined", "from": target_user, "reason": "User is busy"})
        return
    
    # forward request to target
    utilities.send(target_user, 'chatrequest', {"from": from_username})


def handle_chatrequest_result(client, from_username, payload):
    message = payload.get("message")
    to_user = payload.get("to")
    # check if to_user is still connected
    if to_user not in state.users:
        return
    
    if message == "accepted":
        # set both to chatting
        set_user_state(from_username, "CHATTING", to_user)
        set_user_state(to_user, "CHATTING", from_username)
        
        # notify both that chat has started
        utilities.send(to_user, 'chatrequest_result', {"message": "accepted", "from": from_username})
        utilities.send(to_user, 'chat_started', {"with": from_username})
        utilities.send(from_username, 'chat_started', {"with": to_user})
        
    elif message == "declined":
        # forward decline to initiator
        utilities.send(to_user, 'chatrequest_result',
                      {"message": "declined", "from": from_username})
        broadcast_user_list()
