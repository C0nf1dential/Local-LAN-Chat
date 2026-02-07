import json
import clientmain
def send(type, payload):
    data = json.dumps({'type': type, 'payload': payload})
    clientmain.server.send(data.encode())
