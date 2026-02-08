import os
import signal
import router
import state
import tui_inputs
import socket
import json
import handlers
import utilities
import threading
import queue

ui_thread = None
receive_thread = None

def handle_sigint(sig, frame):
    graceful_shutdown()

signal.signal(signal.SIGINT, handle_sigint)

def connect():
    global server
    SERVER_IP = tui_inputs.get_input("Enter the server's IP address: ")
    PORT = int(tui_inputs.get_input("Enter the server's port: "))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((SERVER_IP, PORT))


incoming = queue.Queue() #for transporting data out of threaded functions
def receive():
    try:
        while True:
            data = server.recv(1024)
            if not data:
                break

            try:
                incoming.put(json.loads(data.decode()))# Puts the recieved dictionary into the queue
            except json.JSONDecodeError:
                continue
    finally:
        incoming.put(None)

def graceful_shutdown():
    global ui_thread, receive_thread
    print("Shutting down...")
    state.shutdown_event.set()

    try:
        utilities.send("disconnect", {})
    except:
        pass
    try:
        server.shutdown(socket.SHUT_RDWR)# sends tcp FIN
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
    tui_inputs.uiReady.wait()
    connect()
    receive_thread = threading.Thread(target=receive, daemon=True)
    receive_thread.start()

    while True:
        datadict = incoming.get()  # gets the dict from queue
        

        if datadict is None:
            print("Disconnected from server.")
            break

        try:
            router.route(datadict["type"], datadict["payload"])
        except (KeyError, TypeError):
            print("Malformed message from server:", datadict)


if __name__ == "__main__":#code that will be run when the file is run
    main()
