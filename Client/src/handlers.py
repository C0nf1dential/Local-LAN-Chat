import utilities
import state
def registration(server):
    global registration_result
    while True:
        username=input("Enter your username: ")
        utilities.send(server, 'register', {'username': username})

        state.registration_event.wait()
        state.registration_event.clear()

        if registration_result == 'ok':
            break
        else:
            print("Username is taken. Choose a new one")
            registration_result = None

def chat():
    pass #write