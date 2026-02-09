import json
import clientmain

def send(msg_type, payload):
    data = json.dumps({'type': msg_type, 'payload': payload})
    try:
        clientmain.server.send(data.encode())
    except:
        pass

def compareLists(old, new):
    old = set(old)
    new = set(new)
    added = new - old
    removed = old - new
    return added, removed
