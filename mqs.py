# Name: Manohar Rajaram
# Student ID: 1001544414

# Code References
# 1. https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
# 2. https://www.sanfoundry.com/python-program-implement-queue-data-structure-using-linked-list/
# 3. https://www.geeksforgeeks.org/reading-writing-text-files-python/

from socket import AF_INET, socket, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread                #required for multitherading
from mqueue import Messagequeue             # import custom queue class
import tkinter                              #required for GUI


def updateactiveprocess():
#Description:
# displays the list of connected clients
#Input: na
#Output:na

    active_list.delete(0,tkinter.END)   #set display to end
    active_list.insert(tkinter.END,"Connected Processes")   #heading
    for item in process:                     # add the clients to List box
        active_list.insert(tkinter.END,item)


def connect_to_client():
#Description:
# this thread runs untill the 3 process connects to the MQS
#Input:NA
#Output:NA
    connected = 0       #counter indicating count of connected clients
    while connected < 3:
        try:
            # welcome socket connection
            client, client_address = serverSocket.accept()
            connected = connected + 1
            if mqs_close == True:    # if server is disconnected, exit the loop
                break
            # start the thread to recieve data from clients
            Thread(target=listen_to_clients, args=(client, client_address)).start()
        except OSError:
            break

def student(conn):
#Description:
# reads input student name & course from student client and stores in its queue
#Input: conn=> socket connection
#Output:na
    global mqs_close        #MQS termaintion flag
    while True:             #continously listen to Student process
        try:
            # get data from student prcess
            msg = conn.recv(buffer).decode("utf8")
            if msg:
                # if the msg is not null, convert to string
                msg = str(msg)
                if msg == 'quit':           # if student is quitting, update connected list
                    del process['student']  #remove student from list
                    updateactiveprocess()   # update GUI
                else:
                    # if msg contains name & course, split it on ":"
                    name,course = msg.split(":")
                    # add entry to queue
                    msgq.enqueue(name,course)
                    msg_list.delete(0,tkinter.END)
                    # get current queue content to display
                    cont = msgq.getQcontent()
                    # display the content on the GUI
                    for item in cont:
                        msg_list.insert(tkinter.END,item)   #display the item
                        msg_list.see(tkinter.END)           #scroll to end
        except ConnectionAbortedError:
            mqs_close = True                      # server termination
            break
        except ConnectionResetError:
            break                               # socket issue

def advisor(conn):
#Description:
# Upon receving the PULL request from advisor, send the next unadvised student- course
# item to advisor for input
#Input: advisor socket
#Output:
    global mqs_close        # MQS termination flag
    while True:             # continously listen to advisor
        try:
            # read data from advisor
            msg = conn.recv(buffer).decode("utf8")
            if msg == 'pull':       # if the PULL request, get the node to be processed
                node = msgq.getnode2process()
                if node == None:     #if no node avalilabe for advise, send back None
                    adv_data = "None"
                else:
                    # get the node to be advised
                    adv_data = msgq.getnodedata(node,False)
                process['advisor'].send(bytes(adv_data,"utf8"))
            elif msg == 'quit':
                #update connected client lists on the MQS GUI
                del process['advisor']
                updateactiveprocess()
            else:
                # advisor sends status along with node key
                key,status = msg.split(":")     #split based on ":"
                msgq.updatenode(int(key),int(status))   # update node from unadvised to approve/reject
                msg_list.delete(0,tkinter.END)   #clear GUI screen
                cont = msgq.getQcontent()        # get current queue content
                # display the content
                for item in cont:
                    msg_list.insert(tkinter.END,item)
                    msg_list.see(tkinter.END)
        except ConnectionAbortedError:    # on client socket disconnection
            mqs_close = True              # server termination
            break
        except ConnectionResetError:
            break

def notifier(conn):
#Description:
# Upon receving PULL request from notifier, send the nodes that are already advised
#Input: notifer socket
#Output: NA
    global mqs_close        # MQS termination flag
    while True:             # continously listen to advisor
        try:
            # receive PULL request from notifier
            msg = conn.recv(buffer).decode("utf8")
            if msg == 'pull':       # if pull request from notifier
                # get the node to be notified
                node = msgq.getnode2notify()
                if node == None:
                    # if there is no data to be notified, send None
                    notif_data = "None"
                else:
                    # get the next node in the queue to be notified
                    notif_data = msgq.getnodedata(node,True)
                # send the above data (None or the node to be notified)
                process['notifier'].send(bytes(notif_data,"utf8"))
                cont = msgq.getQcontent()       #get current Queue content
                msg_list.delete(0,tkinter.END)
                # display the queue content on the MQS GUI
                for item in cont:
                    msg_list.insert(tkinter.END,item)
                    msg_list.see(tkinter.END)
            elif msg == 'quit':
                # upon quit, update connected client list
                del process['notifier']
                updateactiveprocess()       #update display
        except ConnectionAbortedError:          # on client socket disconnection
            mqs_close = True                # MQS termination
            break
        except ConnectionResetError:
            break

def listen_to_clients(conn, addr):
#Description:
# listen to clients and register based on the names they send.
# starts a thread for that client
#Input: client socket
#Output: NA
    identifier = conn.recv(buffer).decode("utf8")      #receive HTTP message
    # value contains either student,advisor, notifier
    namekey,value = identifier.split(":")       # split message from client
    print("connected="+value)
    if namekey == "name":       #if indeed this is name registration
        # add the client name and socket to global list
        connected_processes.append(value)
        process[value] = conn

        #update the display of connected clients
        updateactiveprocess()

        # we have a function declared for each of the client
        # this calls the clients function based on the client name
        switch = {'student':student, 'advisor':advisor,'notifier':notifier}
        func = switch.get(value)
        func(conn)


def disconnect():
# Description:
#   This function is called upon 'disconnect' button click
#   This function notifies all its clients about its own disconnection before and
#   then closes the client sockets and server socket
# Also writes, queue content to buffer.txt if there are any un-notifed node in the queue
# Input: NA
# Output: NA
    global mqs_close, process     # server close flag inidicates the server status in the program
    mqs_close = True     # set the termaination flag to True

    # write the content from the queue into a file
    cont = msgq.getQcontent("\n",False)
    file1 = open("buffer.txt","a")      #open the file
    file1.truncate(0)       #delete file content before writing into it
    file1.writelines(cont)      #write buffer content
    file1.close()               #close the file

    # close all the connected clients
    for conn in process:                            # close all the client sockets
        process[conn].close()
    serverSocket.close()                            # close the server socket
    top.quit()                                      # stop the GUI


if __name__ == "__main__":
# Description:
#   gloabal declarations, server socket connection and GUI initializations are done here
#   Also, the thread to listen to incoming client connections starts here
    connected_processes = []        #connected clients list
    process={}                      # connected clients dictionary with socket
    msgq = Messagequeue()           # initializze the message queue

    # load data frm file to check if any data was saved last time before exiting
    file1 = open("buffer.txt",'r')      #open the file in read mode
    data = file1.readlines()            # read the data
    if data:
        for item in data:               # get data and format it into name,course, status
            d = item[:-1]
            key,studentName,course,status = d.split(".")
            msgq.enqueue(studentName,course,int(status))        #add the data to queue
    file1.close()           #close file

    top = tkinter.Tk()          # create a root window handler
    top.title("Message Queue Server")         # set the window titlw as server; updated once the user enters name

    messages_frame = tkinter.Frame(top)     #message frame to display text on the window
    scrollbar = tkinter.Scrollbar(messages_frame)  # to navigate through past messages.
    # Listbox will contain the messages.
    msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
    # this is division in the server window to show the live client list
    active_list = tkinter.Listbox(messages_frame, height=15, width=25, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)      #scroll bar for clint lists
    msg_list.pack(side=tkinter.LEFT,expand=tkinter.YES,fill=tkinter.BOTH)
    msg_list.pack()
    # configure the geometry of the client list window
    active_list.pack(side=tkinter.BOTTOM,expand=tkinter.YES, fill=tkinter.BOTH)
    active_list.pack()
    messages_frame.pack(expand=tkinter.YES,fill=tkinter.BOTH)


    host = "127.0.0.1"      # server IP address; here its localhost
    port = 5002             # port number of the server (hardcoded)
    buffer = 1024           # buffer size
    addr = (host, port)     # IP address-port tuple
    mqs_close = False    # initialize the server disconnection flag
    #Welcome socket--- Common socket for all clients
    serverSocket = socket(AF_INET, SOCK_STREAM)     # creates a socket for TCP connection
    # makes the server port reusable
    serverSocket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    serverSocket.bind(addr)             #bind the socket with the above port, localhost

    # disconnect button
    discon_button = tkinter.Button(top, text="Disconnect", command=disconnect)
    discon_button.pack()
    # handler for window closing
    top.protocol("WM_DELETE_WINDOW", disconnect)

    serverSocket.listen(3)  # Listens for 3 connections at max.

    # set the inital mesages on the window
    msg_list.insert(tkinter.END,"Server listening...")
    active_list.insert(tkinter.END,"Active Clients")

    # display the queue content on the GUI
    cont = msgq.getQcontent()
    for item in cont:
        msg_list.insert(tkinter.END,item)
        msg_list.see(tkinter.END)

    # start thread for listening on its port for incoming connections
    accept_thread = Thread(target=connect_to_client)
    accept_thread.start()       # start the thread
    tkinter.mainloop()          # GUI loop  starts here
    serverSocket.close()        # once the server gets disconnected; this statement executes


