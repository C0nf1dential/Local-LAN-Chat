import threading

registration_event = threading.Event()
registration_result = None
messages = [] #eg: [{direction:"sent"/"recv"", content:"hi"}]
current_user = None
target_user = None