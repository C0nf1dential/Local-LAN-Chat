import handlers
import utilities

def route(client, msg_type, payload):
    username, info = utilities.get_user_by_socket(client)
    if not username:
        if msg_type == "register":
            handlers.handle_register(client, payload)
            return
        else:
            utilities.send_error(client, "not_registered")
            return

    userstate = info["state"]
    if userstate == "CHATTING":
        if msg_type == "chat":
            to = info["chat_with"]
            handlers.handle_chat(username, to, payload)
            return
        
        if msg_type == "chat_end":
            handlers.handle_chat_end(client, username)
            return
        
    if userstate == "IDLE":
        if msg_type == "chatrequest":
            handlers.handle_chatrequest(client, username, payload)
            return
        
        if msg_type == "chatrequest_result":
            handlers.handle_chatrequest_result(client, username, payload)
            return