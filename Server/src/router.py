import handlers
import utilities
def router(client, type, payload):
    username, info = utilities.get_user_by_socket(client)
    if not username:
        if type == "register":
            handlers.handle_register(client, payload)
            return
        else:
            utilities.send_error(client, "not_registered")
            return

    userstate = info["state"]
    if userstate == "CHATTING":
        if type == "chat" :
            to = info["chat_with"]
            handlers.handle_chat(to, payload)
            return
        else:
            pass#error

