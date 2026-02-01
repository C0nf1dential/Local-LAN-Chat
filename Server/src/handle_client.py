import Server.src.servermain as servermain
import utilities
import state
import json
import router
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            data = json.loads(message)
            type, payload = data['type'], data['payload']
            router.route(client,type,payload)
            
        except:
            username, info = utilities.get_user_by_socket(client)
            if state.users['chat_with']:
                utilities.send(state.users['chat_with'], 'chat_end', {'message': 'Disconnected'})
            del state.clients[username]
            client.close()
            break