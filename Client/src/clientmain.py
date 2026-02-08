import router
import state
import tui_inputs
import socket
import json
import threading
import queue


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


def main():
    ui_thread = threading.Thread(target=tui_inputs.start, daemon=True)
    ui_thread.start()
    tui_inputs.uiReady.wait()
    connect()
    threading.Thread(target=receive, daemon=True).start()

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
