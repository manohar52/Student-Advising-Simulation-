# Name: Manohar Rajaram
# Student ID: 1001544414

# Code References
# 1. https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
# 2. https://www.sanfoundry.com/python-program-implement-queue-data-structure-using-linked-list/
# 3. https://www.geeksforgeeks.org/reading-writing-text-files-python/

import tkinter                          #required for GUI
from tkinter import messagebox          #required for alert box
from socket import AF_INET, socket, SOCK_STREAM     #required for socket programming
from threading import Thread            #required for multitherading
from time import sleep                  # import sleep function

def push(msg):
# Description:
#    Poll MQS by sednign PULL request
# Input: msg=> contains PULL request to send to MQS
# Output: NA
    global mqs_close
    try:
        sock.send(bytes(msg, "utf8"))   # send the message to server
    except ConnectionResetError:
        mqs_close = True            # exception occurs on MQS termination

def convert_status(msg):
# Description:
# converts status to status text
# Input: msg=> status
# Output: converted status

    # split msg based on delimiter :
    key,student,subject,status = msg.split(":")
    if status == "0":           #yet to be advised (not applicable to notifier)
        status_txt =  "Unadvised"
    elif status == "1":         # Approved
        status_txt =  "Approved"
    else:                       # rejected
        status_txt =  "Rejected"
    # send concatenated msg back
    return key+":"+student+":"+subject+":"+status_txt

def pull():
# Description:
# Polls MQS for new msgs and displays the same on the GUI
# Input: NA
# Output: NA

    global mqs_close            #MQS status
    while quit == False:        #run untill process is killed
        if mqs_close == True:   # end loop if MQS is terminated
            msg_list.insert(tkinter.END,"MQS Terminated!")
            msg_list.see(tkinter.END)
            break
        push('pull')        #Poll server for new msgs to notify
        while True:         # start loop for gettign messages from MQS
            try:
                # get messages from MQS
                msg = sock.recv(buffer).decode("utf8")
                if msg == "None":
                    # if there is no message to notify, sleep for 7 sec
                    # display the same on the GUI
                    msg_list.insert(tkinter.END,"No Message found!")
                    msg_list.see(tkinter.END)
                    sleep(7)
                    break       #end the loop so as to begin next Poll
                else:
                    # convert status to status text
                    cmsg = convert_status(msg)
                    # display the notification on GUI
                    msg_list.insert(tkinter.END,cmsg)
                    msg_list.see(tkinter.END)
                    break
            except OSError:  # Possible socket connection issue
                mqs_close = True
                break

def disconnect():
# Description:
#     Sends the quit message to MQS upon termination
# Input: NA
# Output: NA

    global quit,mqs_close
    try:
        quit = True                 # set quit flag so all threads stop
        if mqs_close == False:      # send quit msg to MQS only if MQS is still on
            sock.send(bytes("quit", "utf8"))   # send the message to server
    except ConnectionResetError:
        mqs_close = True
    top.quit()


if __name__ == "__main__":
# Description:
#     Execution starts from here; All globals are declared here;
#     The Tkinter GUI is initialized here
#     The concurrent thread for listening to server is also started here
# Input:
# Output:
    quit = False
    mqs_close = False

    top = tkinter.Tk()      # create a root window handler
    top.title("Notifier")     # set the window titlw as client; updated once the user enters name
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

    # configures the frame geometry allowing it to expand
    messages_frame.pack(expand=tkinter.YES,fill=tkinter.BOTH)

    # button to quit; calls win
    quit_button = tkinter.Button(top, text="Quit", command=disconnect)
    quit_button.pack()

    # on closing the window; call the win_close() function
    top.protocol("WM_DELETE_WINDOW", disconnect)


    host = "127.0.0.1"          # server IP address; here its localhost
    port = 5002                 # port number of the server (hardcoded)
    buffer = 1024               # buffer size
    addr = (host, port)         # IP address-port tuple
    sock = socket(AF_INET, SOCK_STREAM)     # creates a socket for TCP connection
    try:
        sock.connect(addr)                  # connects to the localhost server with its port
        sock.send(bytes("name:notifier", "utf8"))   # send the message to server
        sleep(2)        #sleep is reqired to avoid multiple pull messages being sent
        pull_thread = Thread(target=pull)
        pull_thread.start()
        # start the GUI main loop
        tkinter.mainloop()
    except ConnectionRefusedError:      # if server connection failed
        top.destroy()                   # destroy the UI
        # display message that no server is active
        serv_msg = "MQS not listening. Please run 'MQS.py' first and try again"
        tkinter.messagebox.showinfo("Message",serv_msg)     #alert box
        print(serv_msg)

