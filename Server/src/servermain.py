import socket
import threading
import handle_client

def start_server():
    global server
    HOST = "0.0.0.0" # listen on all interfaces
    PORT = 6969
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"server started on host: {socket.gethostbyname(socket.gethostname())}, port:{PORT}")
    while True:
        client, address = server.accept()
        t = threading.Thread(target=handle_client.handle_client, args=(client,))# starts a new thread per client
        t.daemon = True
        t.start()
        print(f"connected to {address}")

if __name__ == "__main__":
    start_server()