# Name: Manohar Rajaram
# Student ID: 1001544414

# Code References
# 1. https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
# 2. https://www.sanfoundry.com/python-program-implement-queue-data-structure-using-linked-list/
# 3. https://www.geeksforgeeks.org/reading-writing-text-files-python/

import tkinter                          #required for GUI
from tkinter import messagebox          #required for alert box
from socket import AF_INET, socket, SOCK_STREAM     #required for socket programming

def send(event=None):
# Description:
# Upon user sending input, this is called. It works in 2 phases:
#     1. get student name
#     2. get course name
# after getting both, it sends it to MQS
# Input:
# Output:
    global stage,name
    if stage == 0:      #get student name
        stage = 1             # set to next stage
        name = my_msg.get()   # read user input
        my_msg.set("")        # Clears input field.

        msg_list.insert(tkinter.END,name)       #display info to user
        msg_list.insert(tkinter.END,"Enter Course:")       #display info to user
        msg_list.see(tkinter.END)

    elif stage == 1:        #get course
        stage = 0                   # set to next stage
        course = my_msg.get()      # read user input
        my_msg.set("")              # Clears input field.

        msg_list.insert(tkinter.END,course)         #display entered data
        msg_list.insert(tkinter.END, "Enter Name:")   #prompt the user
        msg_list.see(tkinter.END)   # scroll to latest text

        try:
            sock.send(bytes(name+":"+course, "utf8"))   # send the message to server
        except ConnectionResetError:
        # This error occurs on server disconnection
            msg_list.insert(tkinter.END,"MQS Terminated")
            msg_list.see(tkinter.END)      #scrolls to the latest message
            # disable the input and send button upon MQS termination
            entry_field.config(state="disabled")
            send_button.config(state="disabled")


def disconnect():
# Description:
#     Sends the quit message to MQS upon termination
# Input: NA
# Output: NA
    global quit
    try:
        quit = True
        sock.send(bytes("quit", "utf8"))   # send the message to server
    except ConnectionResetError:
        pass
    top.quit()



if __name__ == "__main__":
# Description:
#     Execution starts from here; All globals are declared here;
#     The Tkinter GUI is initialized here
#     The concurrent thread for listening to server is also started here
# Input:
# Output:
    quit = False        #client termination flag
    stage = 0           #set stage to 0 (student name reading phase)

    top = tkinter.Tk()      # create a root window handler
    top.title("Student")     # set the window titlw as client; updated once the user enters name
    messages_frame = tkinter.Frame(top)         #message frame to display text on the window

    my_msg = tkinter.StringVar()  # to set and get text from tkinter.Entry (input box)
    my_msg.set("")                # set it to blank at first

    scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
    # creates listbox to display the text entered by the user
    msg_list = tkinter.Listbox(messages_frame, height=15, width=70, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)      #set the scrol bar for first view

    # configure list box geometry
    msg_list.pack(side=tkinter.LEFT,expand=tkinter.YES, fill=tkinter.BOTH)
    msg_list.pack()

    #Label for input box
    button_label = tkinter.Label(top, text="Enter Message:")
    button_label.pack()

    # Input box for user input: we can set the input and read value off it using
    # variable 'my_msg'; also the input font color is set to red
    entry_field = tkinter.Entry(top, textvariable=my_msg, foreground="Red")

    # calls the send() method on pressing enter
    entry_field.bind("<Return>", send)
    entry_field.pack()

    # button to send the message; calls send() method
    send_button = tkinter.Button(top, text="Send", command=send)
    send_button.pack()
    # configures the frame geometry allowing it to expand
    messages_frame.pack(expand=tkinter.YES,fill=tkinter.BOTH)

    # button to quit; calls win
    quit_button = tkinter.Button(top, text="Quit", command=disconnect)
    quit_button.pack()

    msg_list.insert(tkinter.END,"Enter Name:")       #display info to user
    msg_list.see(tkinter.END)

    # on closing the window; call the win_close() function
    top.protocol("WM_DELETE_WINDOW", disconnect)


    host = "127.0.0.1"          # server IP address; here its localhost
    port = 5002                 # port number of the server (hardcoded)
    buffer = 1024               # buffer size
    addr = (host, port)         # IP address-port tuple
    sock = socket(AF_INET, SOCK_STREAM)     # creates a socket for TCP connection
    try:
        sock.connect(addr)                  # connects to the localhost server with its port
        sock.send(bytes("name:student", "utf8"))   # send the message to server
        # start the GUI main loop
        tkinter.mainloop()
    except ConnectionRefusedError:      # if server connection failed
        top.destroy()                   # destroy the UI
        # display message that no server is active
        serv_msg = "MQS not listening. Please run 'MQS.py' first and try again"
        tkinter.messagebox.showinfo("Message",serv_msg)     #alert box
        print(serv_msg)

