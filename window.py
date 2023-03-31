from tkinter import *
import tkinter as tk
import searcher as srch
import numpy as np
import msgspec
import json
import gensim
from gensim.models import FastText
import speech_recognition as sr

global entry
global button
global window
global canvas
global predicted_word
global tdm,word_to_row 
global fasttext_model
global isVoice,voice_query 
isVoice = False

global cache,prev_queries,memory_length
prev_queries = []
cache = {}
memory_length = 1

def searchbtn_clicked():
    global entry
    global canvas
    global tdm,word_to_row 
    global keywords
    global isVoice,voice_query
    global cache,memory_length,prev_queries
    if(not isVoice):
        keywords = entry.get()
        clear()
    else:
        keywords = voice_query
        isVoice = False
    # button.configure(command= close_win)
    # canvas.delete("all")
    # canvas.destroy()
    
    if(keywords!=''):
        if(keywords not in cache.keys()):
            s = srch.Searcher(tdm,word_to_row)
            best_documents_text,best_documents,time_taken  = s.search(keywords)
            for i in range(len(best_documents)):
                best_documents[i] = str(best_documents[i])
            if(len(prev_queries)):
                prev_queries.append(keywords)
                cache[keywords] = [best_documents,best_documents_text]
                if(len(prev_queries)>memory_length):
                    prev_queries.pop(0)
                    del cache[keywords]
            else:
                prev_queries.append(keywords)
                cache[keywords] = [best_documents,best_documents_text]
        else:
            best_documents = cache[keywords][0]
            best_documents_text = cache[keywords][1]
            time_taken = 0
    else:
        best_documents = [0]
        best_documents_text = [0]
        time_taken = 0

    resultpage(keywords,best_documents_text ,best_documents,'The time taken is ' + str(time_taken))





def voicebtn_clicked():
    global voice_query,isVoice
    r = sr.Recognizer()
    while(1):   
        # Exception handling to handle
        # exceptions at the runtime
        try:
            # use the microphone as source for input.
            with sr.Microphone() as source2:
                
                # wait for a second to let the recognizer
                # adjust the energy threshold based on
                # the surrounding noise level
                r.adjust_for_ambient_noise(source2, duration=0.2)
                
                #listens for the user's input
                audio2 = r.listen(source2)
                
                # Using google to recognize audio
                MyText = r.recognize_google(audio2)
                MyText = MyText.lower()
    
                response = input("Did you say '"+ MyText + "'?(y/n)")
                if(response.lower()=="y"):
                    voice_query = MyText
                    isVoice = True
                    searchbtn_clicked()
                    break

        except Exception as e:
            print("failed")

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
    vimg0 = PhotoImage(file=f"vimg0.png")
    button = Button(
        image=img0,
        borderwidth=0,
        highlightthickness=0,
        command=searchbtn_clicked,
        relief="flat")
    button.place(
        x=475, y=455,
        width=210,
        height=53)
    voicebutton = Button(
        text="Voice Search",
        font=25,
        borderwidth=0,
        highlightthickness=0,
        command=voicebtn_clicked,
        relief="flat")
    voicebutton.place(
        x=770, y=455,
        width=210,
        height=53)
    window.mainloop()

def motion(event):
    global predicted_word
    print("test")
    s = srch.Searcher()
    best_documents_text,best_documents,time_taken  = s.search(predicted_word)
    for i in range(len(best_documents)):
        best_documents[i] = str(best_documents[i])
    resultpage(predicted_word,best_documents_text ,best_documents,'The time taken is ' + str(time_taken))
    return

# Result page
def resultpage(key, best_documents_text,results, str_time):
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

    
    str_result = ""
    ctr = 1
    int_sum = 0
    for i in range(len(results)):
        #print(results[i])
        int_sum += int(results[i])
    if(int_sum==0):
        global predicted_word, fasttext_model

        predicted_word = fasttext_model.wv.most_similar(key)[0][0]

        str_result = 'Did you mean "' + predicted_word + '"?'
        #canvas.itemconfig(resultsBox, text=str_result)
        resultsBox = Message(canvas,text=str_result,width=938,bg="#FFFFFF",anchor='w' ,justify=tk.RIGHT,font=('times',20))
        resultsBox.config(justify=LEFT)
        resultsBox.bind('<ButtonRelease-1>',motion)
        resultsBox.place(
        x=130, y=170,
        width=938,
        height=45)
    else:
        resultsBox = canvas.create_text(
        130.0, 170,
        text="results list",
        anchor=NW,
        fill="#000000",
        font=("None", int(20.0)))
        for result in best_documents_text:
            str_result = str_result + str(ctr) + " " + result + '\n'
            ctr+=1
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
        width=120,
        height=47)
    
    voicebutton = Button(
        text="Voice Search",
        font=25,
        borderwidth=0,
        highlightthickness=0,
        command=voicebtn_clicked,
        relief="flat")
    voicebutton.place(
        x=1270, y=113,
        width=120,
        height=47)
    
    window.mainloop()


def init():
    global window
    global tdm,word_to_row 
    global fasttext_model
    fasttext_model = gensim.models.Word2Vec.load("Fasttext.model")

    tdm = np.load("term_document_matrix.npy")
    path = "./word_to_row.json"
    decoder = msgspec.json.Decoder()
    with open(path, "r") as outfile:
        x = outfile.read()

    word_to_row = decoder.decode(x)

    window = Tk()

    window.geometry("1440x768")
    window.configure(bg="#ffffff")
    window.resizable(False, False)
    searchpage()


if __name__ == "__main__":
    init()
