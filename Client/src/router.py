import handlers
import tui_inputs
import state



def route(type, payload): # maami advaith communication protocol: {'type': type, 'payload':<contents dictionary>}
        #registration
    if type == "register_result":
        if payload.get("message") == "ok":
            state.current_user = state.pending_username
            state.pending_username = None
            state.current_state = state.ClientState.IDLE
        else:
            handlers.show_registration_error()

    #idle user list
    elif type == "user_list":
        if state.current_state == state.ClientState.IDLE:
            handlers.show_user_list(payload.get("users", []))

    #hat lifecycle
    elif type == "chat_started":
        if state.current_state == state.ClientState.IDLE:
            state.current_state = state.ClientState.CHATTING
            state.chat_partner = payload.get("with")

    elif type == "chat_ended":
        if state.current_state == state.ClientState.CHATTING:
            state.current_state = state.ClientState.IDLE
            state.chat_partner = None

    #chat messages
    elif type == "chat":
        if state.current_state == state.ClientState.CHATTING:
            handlers.display_chat_message(payload)
