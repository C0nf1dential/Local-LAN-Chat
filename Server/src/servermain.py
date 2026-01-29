import socket
import threading
import handle_client
import router

def start_server():
    global server
    HOST = "0.0.0.0"
    PORT = 5555
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    while True:
        client, address = server.accept()
        t = threading.Thread(target=handle_client.handle_client, args=(client,))# starts a new thread per client
        t.daemon = True
        t.start()
        print(f"Connected to: {address}")

        