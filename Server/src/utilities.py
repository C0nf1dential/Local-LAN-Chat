import handle_client
import handlers
import servermain
import state
import router
import json


def get_socket_from_user(target):
    if isinstance(target, str):
        info = state.users.get(target)
        if not info:
            return None
        return info.get('socket')
    return target

def send(target, msg_type, payload):
    sock = get_socket_from_user(target)
    if not sock:
        return
    data = json.dumps({'type': msg_type, 'payload': payload})
    try:
        sock.send(data.encode())
    except:
        pass

def send_error(target, error_code, details=None):
    payload = {"error": error_code}
    if details is not None:
        payload['details'] = details
    send(target, 'error', payload)


def get_user_by_socket(client):
    for username, info in state.users.items():
        if info.get('socket') == client:
            return username, info
    return None, None