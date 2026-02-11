import servermain
import utilities
import state
import json
import router


def _cleanup_client(client):
    import handlers
    username, info = utilities.get_user_by_socket(client)
    if username and info:
        # notify chat partner if any
        chat_with = info.get('chat_with')
        if chat_with and chat_with in state.users:
            try:
                # set partner back to idle
                partner_info = state.users[chat_with]
                partner_info['state'] = 'IDLE'
                partner_info['chat_with'] = None
                # tell partner and broadcast
                utilities.send(state.users[chat_with]['socket'], 'chat_ended', {'message': 'Partner disconnected'})
                handlers.broadcast_user_list()
            except:
                pass

        try:
            del state.users[username]
        except KeyError: #for fun
            pass


def handle_client(client):
    while True:
        try:
            raw = client.recv(4096)

            # client closed connection
            if not raw:
                username, _ = utilities.get_user_by_socket(client)
                print(f"Client socket closed by peer. username={username}")
                _cleanup_client(client)
                try:
                    client.close()
                except:
                    pass
                break

            try:
                if isinstance(raw, bytes):
                    message = raw.decode('utf-8')
                else:
                    message = str(raw)
            except Exception:
                # cant decode, skip
                continue

            # parse json
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue

            msg_type = data.get('type')
            payload = data.get('payload', {})
            if not msg_type:
                continue

            try:
                router.route(client, msg_type, payload)
            except:
                continue

        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
            _cleanup_client(client)
            try:
                client.close()
            except:
                pass
            break