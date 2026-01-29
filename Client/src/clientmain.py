import handlers
import router
import socket
import json
import threading


def connect():
    global server
    SERVER_IP = input("Enter the server's IP address: ").strip()
    PORT = int(input("Enter the server's port: ").strip())
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((SERVER_IP, PORT))



def receive(): #trys to receive raw data from the server (if any)
    global registration_result
    while True:
        try:
            data = server.recv(1024)
        except:
            print("Connection Error. Restart program.")
            break

        if not data:
            print('Disconnected from server')
            server.close()
            break

        try:
            datadict = json.loads(data.decode())
        except:
            continue
        
        router.route(server, datadict["type"], datadict["payload"])

def main():
    connect()
    threading.Thread(target=receive, daemon=True).start()
    handlers.registration(server)
    #idk what comes after this

if __name__ == "__main__":#code that will be run when the file is run (entry point) (i accidentally called it entry function in the chat)
    main()
