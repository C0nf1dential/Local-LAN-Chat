import tkinter as tk
import queue
import threading

# queue for sending user input to main program
input_queue = queue.Queue()

root = None
entry = None
uiReady = threading.Event()


def start():
    global root, entry

    root = tk.Tk()
    root.title("LAN Chat Input")
    root.configure(bg="#ffffff") 

    label = tk.Label(root, text=">", font=("Cascadia Code", 12))
    label.grid(row=0, column=0, padx=(10, 2), pady=20)

    entry = tk.Entry(root, font=("Cascadia Code", 12), borderwidth=0, state = "disabled")
    entry.grid(row=0, column=1, padx=2, pady=20)
    entry.focus()#enter data right away
    entry.bind("<Return>", on_enter)

    uiReady.set()
    root.mainloop()

def on_enter(event):
    text = entry.get().strip() # type: ignore
    if not text:
        return

    input_queue.put(text)
    entry.delete(0, tk.END) # type: ignore


def set_enabled(enabled):
    global root
    if enabled:
        state = "normal"
    else:
        state = "disabled"
    root.after(0, lambda: entry.config(state=state)) # type: ignore

def input_dispatcher():
    global input_queue
    a = input_queue.get()
    input_queue.task_done()
    return a

def get_input(prompt):
    try:
        set_enabled(True)
        print(prompt)
        a = input_dispatcher()
        print(a)
        return a
    finally:
        set_enabled(False)




