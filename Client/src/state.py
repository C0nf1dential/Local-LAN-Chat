import threading
from enum import Enum

class ClientState(Enum):
    REGISTERING = 0
    IDLE = 1
    CHATTING = 2
    
current_state = ClientState.REGISTERING
pendingUsername = None
registration_event = threading.Event()
registration_result = None
messages = [] #eg: [{direction:"sent"/"recv"", content:"hi"}]
current_user = None
chat_partner = None