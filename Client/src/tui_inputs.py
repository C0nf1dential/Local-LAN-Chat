import tkinter as tk
import clientmain
import threading
import state
import utilities
import handlers

root = None
entry = None
prompt_label = None
uiReady = threading.Event()
pending_input_callback = None


def start():
    global root, entry, prompt_label

    root = tk.Tk()
    root.title("LAN Chat Input")
    root.configure(bg="#ffffff") 

    prompt_label = tk.Label(root, text="", font=("Cascadia Code", 12))
    prompt_label.grid(row=0, column=0, padx=(10, 2), pady=20)

    entry = tk.Entry(root, font=("Cascadia Code", 12), borderwidth=0, state = "disabled")
    entry.grid(row=0, column=1, padx=2, pady=20)
    entry.focus()#enter data right away
    entry.bind("<Return>", on_enter)

    root.protocol("WM_DELETE_WINDOW", clientmain.graceful_shutdown)# when window is closed run graceful shutdown
    
    uiReady.set()
    root.mainloop()

def on_enter(event):
    global pending_input_callback
    text = entry.get().strip() # type: ignore
    if not text:
        return

    entry.delete(0, tk.END) # type: ignore
    
    # Check for end chat keyword
    if text.lower() == "end()" and state.current_state == state.ClientState.CHATTING:
        handlers.end_chat()
        return
    
    if pending_input_callback:
        callback = pending_input_callback
        # For chat mode: keep callback and enabled state
        # For other prompts: clear callback and disable
        is_chat_mode = state.current_state == state.ClientState.CHATTING
        if not is_chat_mode:
            pending_input_callback = None
            set_enabled(False)
        callback(text)


def set_enabled(enabled):
    global root, prompt_label
    if enabled:
        state = "normal"
    else:
        state = "disabled"
        prompt_label.config(text="")
    root.after(0, lambda: entry.config(state=state))

def request_input(callback, prompt=""):
    global pending_input_callback, prompt_label
    pending_input_callback = callback
    prompt_label.config(text=prompt)
    set_enabled(True)

showingList = False
userLcached = []
def ShowUsersList(userlist):
    global showingList, userLcached

    if not showingList:
        showingList = True
        if not userlist:
            print("\n[No other users available yet]")
        else:
            print("\n📋 Available users to chat with:")
            for user in userlist:
                print(f"  • {user}")
        userLcached = userlist
        request_input(handle_username_selection, "Select user: ")

    else: #list is already printed
        if userlist != userLcached:
            added, removed = utilities.compareLists(userLcached, userlist)
            if added:
                print("[+]", added, "ready to chat")
            if removed:
                print("[-]", removed, "no longer available to chat")
            userLcached = userlist

def handle_username_selection(username):
    global showingList
    showingList = False
    # Validate that the selected username exists in the cached list
    if username not in userLcached:
        print(f"[ERROR] User '{username}' is not available in the list")
        request_input(handle_username_selection, "Select user: ")
        return
    
    handlers.initiate_chat(username)

def ShowError(message):
    print(f"[ERROR] {message}")

def start_chat(chat_partner):
    """Set up TUI for active chat mode."""
    global prompt_label, showingList, pending_input_callback
    showingList = False  # Exit user selection mode
    pending_input_callback = lambda msg: handlers.send_chat_message(msg)
    prompt_label.config(text=f"Chat with {chat_partner}:")
    set_enabled(True)

def DisplayChat(message):
    print(f"[MSG] {message}")