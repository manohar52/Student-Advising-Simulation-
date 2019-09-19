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
import random                           # to get random numbers
from time import sleep                  #for sleep function

def push(msg):
# Description:
#     Sends either the 'PULL' msg or sends the approval or rejection for
#     a student-course input to the MQS
# Input:
#     msg --> PULL request or approvedrejected status
# Output: NA
    global mqs_close
    try:
        sock.send(bytes(msg, "utf8"))   # send the message to server
    except ConnectionResetError:
        mqs_close = True                # MQS terminated

def advise():
# Description:
#     Performs the following functions:
#     1.Randomly approves or rejects/approves a student-course input
#     2. Sends PULL request to MQS to fetch next in queue
#     3. If no message found in MQS, then sleeps for 3 seconds
# Input: NA
# Output: NA
    global mqs_close
    while quit == False:        #this runs untill the process is killed
        if mqs_close == True:
            # advisor process terminates if MQS is terminated
            msg_list.insert(tkinter.END,"MQS Terminated!")          #dispaly the same
            msg_list.see(tkinter.END)
            break
        push('pull')        #send PULL request to MQS ie; polling the server
        while True:         #this loop runs untill the next PULL message
            try:
                # read the input to be advised from the MQS buffer(queue)
                msg = sock.recv(buffer).decode("utf8")
                if msg == "None":       #if nothing to advise on, we get None
                    msg_list.insert(tkinter.END,"No Message found!")
                    msg_list.see(tkinter.END)
                    #sleep for 3 seconds;
                    sleep(3)
                    # break this loop so it can send the next PULL reuest to MQS again
                    break
                else:
                    # if there is msg to be advised, split the msg on ":"
                    key,student,subject = msg.split(":")
                    # approve/reject randomly
                    status = random.randint(1,2)
                    # send the status with message key to thr MQS
                    push(key+":"+str(status))
                    # set status text to be displayed
                    if status == 1:
                        status_txt = "Approved"
                    else:
                        status_txt = "Rejected"
                    # display the status of the input
                    msg_list.insert(tkinter.END,msg+":"+status_txt)
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
        quit = True             # set quit flag so all threads stop
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
    mqs_close = False
    quit = False
    wait = False

    top = tkinter.Tk()      # create a root window handler
    top.title("Advisor")     # set the window titlw as client; updated once the user enters name
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
        try:
            sock.send(bytes("name:advisor", "utf8"))   # send the message to server
            sleep(2)
        except ConnectionResetError:
                print("MQS disconnected")

        # start the advising thread
        pull_thread = Thread(target=advise)
        pull_thread.start()

        # start the GUI main loop
        tkinter.mainloop()
    except ConnectionRefusedError:      # if server connection failed
        top.destroy()                   # destroy the UI
        # display message that no server is active
        serv_msg = "MQS not listening. Please run 'MQS.py' first and try again"
        tkinter.messagebox.showinfo("Message",serv_msg)     #alert box
        print(serv_msg)
