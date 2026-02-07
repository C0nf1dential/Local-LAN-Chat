import router
import handle_client
import state
import servermain
import utilities
import json

def add_user(username, client):
    state.users[username] = {
        "socket": client,
        "state": "IDLE",
        "chat_with": None
    }
    broadcast_user_list()


def remove_user(username):
    if username in state.users:
        del state.users[username]
        broadcast_user_list()


def set_user_state(username, new_state, chat_with=None):
    user = state.users[username]
    user["state"] = new_state
    user["chat_with"] = chat_with
    broadcast_user_list()

def handle_register(client, message):
    u = message['username']
    if u in state.users:
        payload = {"message": "Username_Taken"}
        utilities.send(client, 'register_result', payload)

    add_user(u, client)
    client.send(json.dumps({'type': 'register_result', 'message':'ok'}).encode())
    payload = {"message": "ok"}
    utilities.send(client, 'register_result', payload)

def handle_chat(to, payload):
    sendsocket = state.users[to]['socket']
    utilities.send(sendsocket, 'chat', payload)

def broadcast_user_list():
    payload = {"users": list(state.users.keys())}
    for username, info in state.users.items():
        if info['state'] == "IDLE":
            utilities.send(username, 'user_list', payload)
    
    