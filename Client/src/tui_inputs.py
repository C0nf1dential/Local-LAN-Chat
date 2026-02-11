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

    prompt_label = tk.Label(root, text="Disabled", font=("Cascadia Code", 12))
    prompt_label.grid(row=0, column=0, padx=(10, 2), pady=20)

    entry = tk.Entry(root, font=("Cascadia Code", 12), borderwidth=0, state = "disabled")
    entry.grid(row=0, column=1, padx=2, pady=20)
    entry.focus()#enter data right away
    entry.bind("<Return>", on_enter)

    root.protocol("WM_DELETE_WINDOW", clientmain.graceful_shutdown)# when window is closed run graceful shutdown
    
    uiReady.set()
    root.mainloop()

def on_enter(event): #event based callback system because i got fed up with dealing with these blocking functions
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
        if not state.current_state == state.ClientState.CHATTING:
            pending_input_callback = None
            set_enabled(False) #turns textbox off once done, but keeps on for chat
        callback(text) #!!!!!!!!!!!! crazy system dawg


def set_enabled(enabled):
    global root, prompt_label
    if enabled:
        state = "normal"
    else:
        state = "disabled"#enables/disables
        prompt_label.config(text="") #changes label based on context ts tuff
    root.after(0, lambda: entry.config(state=state)) #passing tis to tkinter loop which is in a seperate thread so we use root.after

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
            print("\nAvailable users to chat with:")
            for user in userlist:
                print(f"    -{user}")
        userLcached = userlist
        request_input(handle_username_selection, "Select user: ") #passing func through arg as callback for sequence of actions

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
    global prompt_label, showingList, pending_input_callback
    showingList = False  # Exit user selection mode
    pending_input_callback = lambda msg: handlers.send_chat_message(msg) #storing the function inside a variable is crazy, this is peak
    prompt_label.config(text=f"Chat with {chat_partner}:")
    set_enabled(True)

def DisplayChat(message):
    print(f"[MSG] {message}")