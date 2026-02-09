import servermain
import utilities
import state
import json
import router


def _cleanup_client(client):
    username, info = utilities.get_user_by_socket(client)
    if username and info:
        # notify chat partner if any
        chat_with = info.get('chat_with')
        if chat_with and chat_with in state.users:
            try:
                utilities.send(state.users[chat_with]['socket'], 'chat_end', {'message': 'Disconnected'})
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

            # client closed connection cleanly
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
                # unable to decode; skip this chunk
                continue

            # parse JSON safely
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                # malformed or partial message; ignore and continue
                continue

            msg_type = data.get('type')
            payload = data.get('payload', {})
            if not msg_type:
                # nothing useful, skip
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