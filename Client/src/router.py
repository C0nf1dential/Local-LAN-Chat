import handlers
import state

def route(server, type, payload):
    if type == 'chat':
        handlers.chat()
    if type == 'register_response':
        registration_result = payload['message']
        state.registration_event.set()
