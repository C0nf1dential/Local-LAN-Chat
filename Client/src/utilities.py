import json
import clientmain
def send(server, type, payload):
    data = json.loads({'type': type, 'payload': payload})
    server.send(data.encode())
