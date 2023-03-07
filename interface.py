import tkinter as tk

global e1, frame
frame = None

RESULTS = ["a","b","d","e","f","g"]

def search_frame():
    global e1,frame
    frame = reset_all()
    tk.Label(frame, text='Searcher').grid(row=0,column=1)
    e1 = tk.Entry(frame)
    e1.bind("<Key>", enter_key_handler)

    e1.grid(row=1, column=1)

    button = tk.Button(frame, text='Search', width=10,fg="yellow")
    button.grid(row=1,column=2)

    button.bind("<Button-1>", click_handler)
    return

def other_click_handler(event):
    print("other click")
    search_frame()
    return

def display_results_frame(frame):
    for i in range(len(RESULTS)):
        tk.Label(frame, text=RESULTS[i]).pack()

    button1 = tk.Button(frame, text='Another Search', width=45,fg="yellow")
    button1.bind("<Button-1>", other_click_handler)
    button1.pack()
    return

def reset_all():
    global frame
    if frame is not None:
        frame.destroy()
    frame = tk.Frame(master, height = 700, width = 700)
    frame.pack()
    #frame = create
    return frame

def click_handler(event):
    global e1
    query = e1.get()
    print(query)
    print("The button was clicked")
    frame = reset_all()
    display_results_frame(frame)
    return

def enter_key_handler(event):
    global e1
    if(event.char=="p"):
        query = e1.get()
        print(query)
        frame = reset_all()
        display_results_frame(frame)
    return

def initializer():
    global master
    master=tk.Tk()
    search_frame()
    master.mainloop()
    return

if __name__ == "__main__":
    initializer()
    