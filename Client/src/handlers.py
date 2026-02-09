import utilities
import threading
import state
import clientmain
import e2ee
import tui_inputs
from functools import partial


#to server
def prompt_for_server_info():
    tui_inputs.request_input(handle_server_ip, "Enter server IP address: ")

def handle_server_ip(ip_address):
    state.server_ip = ip_address
    tui_inputs.request_input(handle_server_port, "Enter server port: ")

def handle_server_port(port_str):
    try:
        port = int(port_str)
        clientmain.connect(state.server_ip, port)
        # only prompt for registration if connection was established
        if getattr(state, 'connection_ready', None) and state.connection_ready.is_set():
            # start the receive thread now that connection is ready
            if getattr(state, 'receive_thread', None) is None:
                state.receive_thread = threading.Thread(target=clientmain.receive, daemon=True)
                state.receive_thread.start()
            prompt_for_registration()
    except ValueError:
        tui_inputs.ShowError("Port must be a valid number")
        handle_server_ip(state.server_ip)

def show_server_connection_error(error_msg):
    tui_inputs.ShowError(f"Failed to connect to server: {error_msg}")
    prompt_for_server_info()


def prompt_for_registration():
    if state.current_state != state.ClientState.REGISTERING:
        return
    tui_inputs.request_input(submit_registration, "Enter username to register: ")

def submit_registration(username):
    if state.current_state != state.ClientState.REGISTERING:
        return
    
    if not username or len(username.strip()) == 0:
        tui_inputs.ShowError("Username cannot be empty")
        prompt_for_registration()
        return
    
    state.pendingUsername = username
    utilities.send("register", {"username": username})

def initiate_chat(target_user):
    """Send a chat request to initiate conversation with target user"""
    utilities.send("chatrequest", {"target": target_user})


def send_chat_message(message):
    """Send an encrypted chat message to the partner."""
    encrypted = e2ee.encrypt(message)
    # Display message immediately on sender's side
    tui_inputs.DisplayChat(f"You: {message}")
    utilities.send("chat", {"message": encrypted})


def end_chat():
    """End the current chat session and return to user selection."""
    if state.current_state != state.ClientState.CHATTING:
        return
    partner = state.chat_partner
    utilities.send("chat_end", {"message": "ended"})
    tui_inputs.DisplayChat(f"Chat with '{partner}' ended.")


def handle_chat_request(payload): #incomung
    from_user = payload.get("from")
    prompt = f"User '{from_user}' wants to chat. Accept? (yes/no): "
    tui_inputs.request_input(partial(_handle_chat_request_response, from_user), prompt)

def _handle_chat_request_response(from_user, response):
    response = response.lower().strip()
    if response == "yes":
        utilities.send("chatrequest_result", {"message": "accepted", "to": from_user})
    else:
        utilities.send("chatrequest_result", {"message": "declined", "to": from_user})


def handle_chat_accepted(partner):
    """Called when this user initiates a chat that is accepted."""
    state.current_state = state.ClientState.CHATTING
    state.chat_partner = partner
    tui_inputs.start_chat(partner)
    tui_inputs.DisplayChat(f"Chat with '{partner}' has been accepted! You can now type messages.")

def handle_chat_request_result(payload):
    message = payload.get("message")
    requester = payload.get("from")
    
    if message == "accepted":
        # Don't transition here; wait for chat_started to avoid conflicting with responder's transition
        tui_inputs.DisplayChat(f"Chat with '{requester}' has been accepted!")
    elif message == "declined":
        tui_inputs.DisplayChat(f"Chat request to '{requester}' was declined. You can try another user.")
        # State remains IDLE; next user_list broadcast will re-enable selection

#from server

def display_chat_message(payload):
    message = e2ee.decrypt(payload["message"])
    tui_inputs.DisplayChat(message)


def show_registration_error(error_msg="Username already taken"):
    tui_inputs.ShowError(error_msg)
    prompt_for_registration()

def show_user_list(users):
    tui_inputs.ShowUsersList(users)
