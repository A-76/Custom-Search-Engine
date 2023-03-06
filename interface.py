import tkinter as tk
global e1



def create_frame(master):
    print("create frame")

    frame = Frame(master)

    b = Button(frame, text='Do Something')
    b.pack(pady=10)

    clearall = Button(frame, text='reset', command=reset_all)
    clearall.pack(pady=10)

    return frame

def reset_all():
    global frame

    frame.destroy()
    frame = create_frame(master)
    #frame = create
    return

def display_results():
    return
def click_handler(event):
    global e1
    query = e1.get()
    print(query)
    print("The button was clicked")
    return

def enter_key_handler(event):
    global e1
    if(event.char=="p"):
        query = e1.get()
        print(query)
    return

if __name__ == "__main__":
    print("axd")
    master=tk.Tk()
    tk.Label(master, text='Searcher').grid(row=0,column=1)
    e1 = tk.Entry(master)
    e1.bind("")
    e1.bind("<Key>", enter_key_handler)

    e1.grid(row=1, column=1)

    button = tk.Button(master, text='Search', width=10,fg="yellow")
    button.grid(row=1,column=2)

    button.bind("<Button-1>", click_handler)
    master.mainloop()