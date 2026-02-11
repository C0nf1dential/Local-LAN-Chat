import os
import signal
import router
import state
import tui_inputs
import socket
import json
from json import JSONDecoder
import handlers
import utilities
import threading
import queue
import time

ui_thread = None
receive_thread = None
server = None

def handle_sigint(sig, frame):
    graceful_shutdown()

signal.signal(signal.SIGINT, handle_sigint) #to handle termin

def connect(server_ip, port):
    global server
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((server_ip, port))
        state.connection_ready.set()  # Signal that connection is established
        print(f"Connected to server at {server_ip}:{port}")
    except Exception as e:
        handlers.show_server_connection_error(str(e))


# incoming queue stored in state
def receive():
    '''TCP is stream based 
    typically you'd use .recv() to receive data from the server but because of that 
    i have been losing messages between packets 
    so i use a buffer to store the data and decode it progressively
    also im too lazy to refactor server side to add \n after each line
    AI helped me here but i learnt every part of it'''
    global server
    state.connection_ready.wait()
    decoder = JSONDecoder()
    buffer = ""
    try:        
        try:
            server.settimeout(0.5) #ensures that the thread doesn't block forever, it polls every 0.5sec to check if new message arrived
        except:
            pass #incase socket object is destroyed

        while not state.shutdown_event.is_set():

            try:
                data = server.recv(4096)
            except socket.timeout: #no new message
                continue
            except OSError: #server disconnected
                break
            if not data: #server disconnected
                break

            try:
                chunk = data.decode()
            except Exception:
                continue
            buffer += chunk#accumulates decoded chunks until its fully usuable

            # handle concatenated JSON objects by progressively decoding
            while buffer:
                try:
                    obj, endIndex = decoder.raw_decode(buffer)#decodes one object of the buffer at a time
                    buffer = buffer[endIndex:].lstrip()#cuts the decoded object from the buffer
                    state.incoming.put(obj)#puts the decoded object in the queue
                except json.JSONDecodeError:
                    #we can't decode the buffer yet, so we wait for more data
                    break
    finally: 
        state.incoming.put(None) #graceful shutdown (main() loop will break in this case)


def graceful_shutdown():
    global ui_thread, receive_thread, server
    print("Shutting down...")
    state.shutdown_event.set()
    
    time.sleep(0.1)  #gib receive thread time to notice

    try:
        utilities.send("disconnect", {})
    except:
        pass
    try:
        if server:
            server.shutdown(socket.SHUT_RDWR)
            server.close()
    except:
        pass
    if receive_thread:
        receive_thread.join(timeout=2)
    if ui_thread:
        ui_thread.join(timeout=2)

    print("Terminal is safe to close. cya bro")
    os._exit(0)

def main():
    global ui_thread, receive_thread
    ui_thread = threading.Thread(target=tui_inputs.start, daemon=True)
    ui_thread.start()
    tui_inputs.uiReady.wait() #wait until ui isready
    
    # Prompt for server info (IP and port) before connecting
    handlers.prompt_for_server_info()

    while not state.shutdown_event.is_set():
        datadict = state.incoming.get()

        if datadict is None:
            print("Disconnected from server.")
            break

        try:
            router.route(datadict["type"], datadict["payload"])
        except (KeyError, TypeError):
            print("Malformed message from server:", datadict)


if __name__ == "__main__":#code that will be run when the file is run
    main()
