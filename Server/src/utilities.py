import handle_client
import handlers
import servermain
import router
import json

def send(client, type, payload):
    data = json.loads({'type': type, 'payload': payload})
    client.send(data.encode())

def get_user_by_socket(client):
    for username, info in servermain.users.items():
        if info['socket'] == client:
            return username, info
    return None, None