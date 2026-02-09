import threading
from enum import Enum
import queue

class ClientState(Enum):
    REGISTERING = 0
    IDLE = 1
    CHATTING = 2
    
current_state = ClientState.REGISTERING
pendingUsername = None
server_ip = None
registration_event = threading.Event()
connection_ready = threading.Event()
registration_result = None
messages = [] #eg: [{direction:"sent"/"recv"", content:"hi"}]
current_user = None
chat_partner = None
shutdown_event = threading.Event()
incoming = queue.Queue()
receive_thread = None