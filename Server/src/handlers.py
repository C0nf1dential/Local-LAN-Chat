import router
import handle_client
import Server.src.state as state
import servermain
import utilities
import json
def handle_register(client, message):
    u = message['username']
    if u in state.users:
        payload = {"message": "Username_Taken"}
        utilities.send(client, 'register_result', payload)

    state.users[u] = {'socket': client, \
                           'state': "IDLE", \
                            'chat_with': None}
    client.send(json.dumps({'type': 'register_result', 'message':'ok'}).encode())
    payload = {"message": "ok"}
    utilities.send(client, 'register_result', payload)

def handle_chat(to, payload):
    sendsocket = state.users[to]['socket']
    utilities.send(sendsocket, 'chat', payload)
    