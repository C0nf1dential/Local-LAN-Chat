from enum import Enum
users = {}
class ClientState(Enum):
    REGISTERING = 0
    IDLE = 1
    CHATTING = 2