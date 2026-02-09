import handlers
import tui_inputs
import state



def route(msg_type, payload): # maami advaith communication protocol: {'type': type, 'payload':<contents dictionary>}
    # registration
    if msg_type == "register_result":
        if payload.get("message") == "ok":
            state.current_user = state.pendingUsername
            state.pendingUsername = None
            print(f"Registration successful! Welcome, {state.current_user}")
            state.current_state = state.ClientState.IDLE
        else:
            handlers.show_registration_error("Username already taken. try another.")

    elif msg_type == "user_list":
        if state.current_state == state.ClientState.IDLE:
            handlers.show_user_list(payload["users"])

    elif msg_type == "chatrequest":
        if state.current_state == state.ClientState.IDLE:
            handlers.handle_chat_request(payload)
    
    elif msg_type == "chatrequest_result":
        if state.current_state == state.ClientState.IDLE:
            handlers.handle_chat_request_result(payload)
    
    elif msg_type == "chat_started":
        # Transition to CHATTING and set up chat interface
        state.current_state = state.ClientState.CHATTING
        state.chat_partner = payload.get("with")
        tui_inputs.start_chat(state.chat_partner)
        print(f"Chat started with {state.chat_partner}. Type messages to send.")

    elif msg_type == "chat":
        if state.current_state == state.ClientState.CHATTING:
            handlers.display_chat_message(payload)
    
    elif msg_type == "chat_ended":
        if state.current_state == state.ClientState.CHATTING:
            state.current_state = state.ClientState.IDLE
            state.chat_partner = None