# Name: Manohar Rajaram
# Student ID: 1001544414

# Code References
# 1. https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
# 2. https://www.sanfoundry.com/python-program-implement-queue-data-structure-using-linked-list/
# 3. https://www.geeksforgeeks.org/reading-writing-text-files-python/

class Node:
#class for the Node in the queue linked list
    def __init__(self, key,studentname,subject,status):
       self.key = key                       # Node key
       self.studentName = studentname       # Student name
       self.subject = subject               # course
       self.status = status                 # unadvised,approved or rejected
       self.next = None                     # next node in the queue

class Messagequeue:
#Description:
# Queue class implemented as a linked list

    nodecount = 0       #class variable to keep track of the key

    def __init__(self):     #constructor
        # Initalize the queue
        self.head = None        # first node is none
        self.last = None        # last node is none
        self.nodekey = 0        # queue has no node, so key set to zero

    def get_status_txt(self,status):
        # returns status description for input status
        if status == 0:
            return "Unadvised"
        elif status == 1:
            return "Approved"
        else:
            return "Rejected"

    def getQcontent(self,delimiter="",st=True):
    #Description: returns the current content of the queue
    #input: delimiter: if this is called on writing to a file, newline delimiter is
            # required
            # st: if its set, then status should be as it as else, return status description
    #output: Queue content
        currNode = self.head        # set the traversal node to first node
        cont = []                   # initialize the list to be returned
        while currNode:
            if st == True:
                # convrt status to its description
                status_txt = self.get_status_txt(currNode.status)
                item = str(currNode.key)+"."+currNode.studentName+"."+currNode.subject+"."+status_txt+delimiter
            else:
                item = str(currNode.key)+"."+currNode.studentName+"."+currNode.subject+"."+str(currNode.status)+delimiter
            cont.append(item)       # add Node content to the list
            currNode = currNode.next
        return cont

    def enqueue(self,studentName="",subject="",status=0):
    #description: add element to the queue
    #input-> studentName, subject, status

        #update the class variable keeping the node count
        Messagequeue.nodecount = Messagequeue.nodecount + 1
        self.nodekey = Messagequeue.nodecount   #assign the nodekey
        if self.last is None:       #if queue is empty,
            # add the create a new Node and assign it as first and last node
            self.head = Node(self.nodekey,studentName,subject,status)
            self.last = self.head
        else:
            # if there s already a Node in the queue, link it to the last node
            # in the Queue
            self.last.next = Node(self.nodekey,studentName,subject,status)
            self.last = self.last.next

    def dequeue(self) -> 'Node':
    #description: remove the first item in the Queue and return the same
    #output: removed Node
        if self.head is None:
            return None     #if queue is empty, return None
        else:
            to_return = self.head               #store the Node to be returend
            # if there is only one node, set both head and last to next (which is None)
            if self.head.key == self.last.key:
                self.head = self.head.next
                self.last = self.head
            else:
                # set the next node as head
                self.head = self.head.next
            return to_return

    def getnode2process(self) -> 'Node':
        #description: returns the node in the queue which is next in line for advising
        #output: Node to be advised
        if self.head == None:           #if queue empty, return None
            return None
        currNode = self.head            # set traversal node as the head node
        while currNode:                 #do unitll last node
            if currNode.status == 0:        #if status is unadvised(0), send it
                return currNode
            else:                       #go to next Node
                currNode = currNode.next
        return None

    def getnode2notify(self) -> 'Node':
    #description: returns the node to be notified and removes it from the queue
    #output: Node to be notified
        if self.head != None:           #if queue is not empty
            if self.head.status != 0:   #if the node is not 0(either approved or rejected)
                return self.dequeue()   # remove the node from queue and return same
            else:
                return None             #if all the node are processed , return None
        else:
            return None                 #if queue is empty, return None


    def getnodedata(self,node:'Node',stat):
    #description: returns a Node's content
    # Input: Node of class Node
    # Output: Node's student name, course, key and status
        if stat == True:    #is status description is needed
            return str(node.key)+":"+node.studentName+":"+node.subject+":"+str(node.status)
        else:
            return str(node.key)+":"+node.studentName+":"+node.subject

    def updatenode(self,key,status):
    #description: updates the status of a Node in the queue with the input key as to
                  # the input status
        start = self.head       #set traversal node to head
        while True:             #untill the end of queue
            if start == None:       #if queue is empty, exit
                break
            if start.key == key:        #if the key is found
                start.status = status       #update the status
                break                   #exit
            else:
                start = start.next          #go to next node
