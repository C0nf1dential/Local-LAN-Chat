import utilities
import state
import clientmain
import e2ee
import tui_inputs


#to server
def submit_registration(username):
    if state.current_state != state.ClientState.REGISTERING:
        return

    state.pending_username = username
    utilities.send("register", {"username": username})

def initiate_chat(target_user):
    utilities.send("chat_init", {"username": target_user})


def send_chat_message(message):
    encrypted = e2ee.encrypt(message)
    utilities.send("chat", {"message": encrypted})

#from server

def display_chat_message(payload):
    message = e2ee.decrypt(payload["message"])
    tui_inputs.DisplayChat(message)


def show_registration_error():
    tui_inputs.ShowError("Username already taken")


def show_user_list(users):
    tui_inputs.ShowUserList(users)