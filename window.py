from tkinter import *

import searcher as srch

global entry
global button
global window
global canvas


def searchbtn_clicked():
    global entry
    global canvas
    keywords = entry.get()
    clear()
    # button.configure(command= close_win)
    # canvas.delete("all")
    # canvas.destroy()
    s = srch.Searcher()
    best_documents,time_taken = s.search(keywords)
    for i in range(len(best_documents)):
        best_documents[i] = str(best_documents[i])
    resultpage(keywords, best_documents,'The time taken is ' + str(time_taken))


def clear():
    global canvas
    global entry
    entry.delete(0, END)
    canvas.destroy()


def searchpage(): 
    global entry
    global button
    global window
    global canvas

    canvas = Canvas(
        window,
        bg="#ffffff",
        height=768,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge")
    canvas.place(x=0, y=0)  
    logo = canvas.create_text(
        718.5, 284.0,
        text="SWE225 Search Engine",
        fill="#000000",
        font=("None", int(36.0)))

    entry0_img = PhotoImage(file=f"img_textBox0.png")
    entry0_bg = canvas.create_image(
        719.5, 382.0,
        image=entry0_img)

    entry = Entry(
        bd=0,
        bg="#d9d9d9",
        highlightthickness=0,
        font=("None", int(24.0)))
    entry.bind('<Return>', lambda event: searchbtn_clicked())
    entry.place(
        x=139, y=353,
        width=1161,
        height=56)

    img0 = PhotoImage(file=f"img0.png")
    button = Button(
        image=img0,
        borderwidth=0,
        highlightthickness=0,
        command=searchbtn_clicked,
        relief="flat")
    button.place(
        x=614, y=455,
        width=210,
        height=53)
    window.mainloop()


# Result page
def resultpage(key, results, str_time):
    global entry
    global button
    global window
    global canvas
    canvas = Canvas(
        window,
        bg="#ffffff",
        height=768,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge")
    canvas.place(x=0, y=0)  
    logo = canvas.create_text(
        171.0, 76.5,
        text="SWE225",
        fill="#000000",
        font=("None", int(36.0)))
    timeBox = canvas.create_text(
        130.0, 150,
        text=str_time,
        anchor=SW,
        fill="#941010",
        font=("None", int(15.0)))
    resultsBox = canvas.create_text(
        130.0, 270,
        text="results list",
        anchor=SW,
        fill="#000000",
        font=("None", int(20.0)))
    
    str_result = ""
    for result in results:
        str_result = str_result + key + " " + result + '\n'
    canvas.itemconfig(resultsBox, text=str_result)

    entry1_img = PhotoImage(file=f"img_textBox1.png")
    entry1_bg = canvas.create_image(
        765.0, 76.5,
        image=entry1_img)

    entry = Entry(
        bd=0,
        bg="#d9d9d9",
        highlightthickness=0,
        font=("None", int(24.0)))
    entry.bind('<Return>', lambda event: searchbtn_clicked())
    entry.place(
        x=296, y=53,
        width=938,
        height=45)
    entry.insert(0, key)
    img1 = PhotoImage(file=f"img1.png")
    # button.configure(image= img1)
    button1 = Button(
        image=img1,
        borderwidth=0,
        highlightthickness=0,
        command=searchbtn_clicked,
        relief="flat")

    button1.place(
        x=1270, y=53,
        width=86,
        height=47)
    window.mainloop()


def init():
    global window

    window = Tk()

    window.geometry("1440x768")
    window.configure(bg="#ffffff")
    window.resizable(False, False)
    searchpage()


if __name__ == "__main__":
    init()
