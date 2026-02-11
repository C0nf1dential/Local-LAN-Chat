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
    global server
    state.connection_ready.wait()

    if server is None:
        state.incoming.put(None)
        return

    import json as _json
    from json import JSONDecoder

    decoder = JSONDecoder()
    buffer = ""
    try:
        while not state.shutdown_event.is_set():
            try:
                server.settimeout(0.5)
            except:
                pass

            try:
                data = server.recv(4096)
            except socket.timeout:
                continue
            except OSError:
                break

            if not data:
                break

            try:
                chunk = data.decode()
            except Exception:
                continue
            buffer += chunk

            # handle concatenated JSON objects by progressively decoding
            while buffer:
                try:
                    obj, idx = decoder.raw_decode(buffer)
                    buffer = buffer[idx:].lstrip()
                    state.incoming.put(obj)
                except _json.JSONDecodeError:
                    # not enough data yet for a full JSON object
                    break
    finally:
        state.incoming.put(None)


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
