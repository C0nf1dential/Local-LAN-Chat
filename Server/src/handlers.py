import router
import handle_client
import state
import servermain
import utilities
import json
import time

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
    # Only broadcast when users are returning to IDLE (after chat ends), not during CHATTING transitions
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

    # register user WITHOUT broadcasting yet
    add_user(u, client, should_broadcast=False)
    # Send register result to newly registered user
    utilities.send(client, 'register_result', {"message": "ok"})
    # NOW broadcast to all IDLE users (including the newly registered one)
    broadcast_user_list()

def handle_chat(from_username, to, payload):
    """Send chat message from sender to recipient."""
    # Send message to recipient
    sendsocket = state.users[to]['socket']
    utilities.send(sendsocket, 'chat', payload)

def handle_chat_end(client, from_username):
    """Handle chat end request from one user, notify both and return to IDLE."""
    from_user_info = state.users[from_username]
    partner = from_user_info.get('chat_with')
    
    if not partner or partner not in state.users:
        return
    
    # Set both users back to IDLE
    set_user_state(from_username, "IDLE", None)
    set_user_state(partner, "IDLE", None)
    
    # Notify both users that chat has ended
    utilities.send(from_username, 'chat_ended', {"message": "Chat ended"})
    utilities.send(partner, 'chat_ended', {"message": "Chat ended"})
    
    # Broadcast updated user list (now both are IDLE)
    broadcast_user_list()

def broadcast_user_list():
    time.sleep(0.05) # slight delay to ensure state is updated before broadcasting
    # Only include IDLE users in the list (filter out those chatting)
    idle_users = [u for u, info in state.users.items() if info['state'] == "IDLE"]
    payload = {'users': idle_users}
    for username, info in state.users.items():
        if info['state'] == "IDLE":
            # send to the user's socket
            sock = info.get('socket')
            if sock:
                utilities.send(sock, 'user_list', payload)


def handle_chatrequest(client, from_username, payload):
    target_user = payload.get("target")
    
    # Reject self-requests
    if from_username == target_user:
        utilities.send(client, 'chatrequest_result', {"message": "declined", "from": target_user, "reason": "Cannot chat with yourself"})
        return
    
    # Check if target user exists and is IDLE
    if target_user not in state.users:
        utilities.send(client, 'chatrequest_result', {"message": "declined", "from": target_user, "reason": "User not found"})
        return
    
    target_info = state.users[target_user]
    if target_info['state'] != "IDLE":
        utilities.send(client, 'chatrequest_result', {"message": "declined", "from": target_user, "reason": "User is busy"})
        return
    
    # Forward chat request to target user with sender info
    utilities.send(target_user, 'chatrequest', {"from": from_username})


def handle_chatrequest_result(client, from_username, payload):
    message = payload.get("message")
    to_user = payload.get("to")
    # Verify that to_user is still connected
    if to_user not in state.users:
        return
    
    to_user_info = state.users[to_user]
    
    if message == "accepted":
        # Change both users' states to CHATTING
        set_user_state(from_username, "CHATTING", to_user)
        set_user_state(to_user, "CHATTING", from_username)
        
        # Notify requester that request was accepted
        utilities.send(to_user, 'chatrequest_result', {"message": "accepted", "from": from_username})
        
        # Notify both users that chat has started
        utilities.send(to_user, 'chat_started', {"with": from_username})
        utilities.send(from_username, 'chat_started', {"with": to_user})
        
    elif message == "declined":
        # Just forward decline message to initiator
        utilities.send(to_user, 'chatrequest_result',
                      {"message": "declined", "from": from_username})
        # Both users remain IDLE, broadcast updated user list
        broadcast_user_list()
