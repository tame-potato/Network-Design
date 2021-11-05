#! /usr/bin/env python3
import tkinter
from socket import *
from tkinter import *
from tkinter.ttk import Progressbar

from packet import *
from rdt22 import *

HEIGHT = 768
WIDTH = 1024

entry1click = True
entry2click = True


def entryClick1(event):
    global entry1click
    if entry1click:  # if this is the first time they clicked it
        entry1click = False
        entryField1.delete(0, "end")  # delete all the text in the entry


def entryClick2(event):
    global entry2click
    if entry2click:  # if this is the first time they clicked it
        entry2click = False
        entryField2.delete(0, "end")  # delete all the text in the entry


def closewindow():
    gui.destroy()


gui = tkinter.Tk()

var1 = IntVar()
var2 = IntVar()
progress_var = IntVar()

forFilename = StringVar()
forFilename.set('Type the name of the image file to send w/ file type extension')

forSavename = StringVar()
forSavename.set('Type the name to save the image file as w/ file type extension')

labelText = "Network Design\nFall 2021\nCourse Project GUI\nPhase 4"

gui.title("Network Design Team 4 Project GUI")

canvas = Canvas(gui, height=HEIGHT, width=WIDTH, bg='#8f9ef5')
canvas.pack()

bgFrame = Frame(gui, bg='#6a6c77', bd=5)
bgFrame.place(relx=0.36, rely=0.06, relwidth=0.65, relheight=0.25, anchor='n')

entryField1 = Entry(bgFrame, font=50, textvariable=forFilename)
entryField1.place(relx=0.05, rely=0.1, relwidth=0.6, relheight=0.35)
entryField1.bind('<FocusIn>', entryClick1)

quitButton = Button(gui, text="QUIT", font=('Didot', 14, 'bold'), highlightbackground='#af0a0a'
                    , activebackground='#880606', command=closewindow)
quitButton.place(relx=0.94, rely=0.02, relwidth=0.05, relheight=0.05)

button1 = Button(bgFrame, text="ENTER", font=('Didot', 14, 'bold'), highlightbackground='#429B19'
                 , activebackground='#347A13', command=lambda: var1.set(1))
button1.place(relx=0.71, rely=0.11, relwidth=0.25, relheight=0.35)

entryField2 = Entry(bgFrame, font=50, textvariable=forSavename)
entryField2.place(relx=0.05, rely=0.55, relwidth=0.6, relheight=0.35)
entryField2.bind('<FocusIn>', entryClick2)

button2 = Button(bgFrame, text="ENTER", font=('Didot', 14, 'bold'), highlightbackground='#429B19'
                 , activebackground='#347A13', command=lambda: var2.set(1))
button2.place(relx=0.71, rely=0.555, relwidth=0.25, relheight=0.35)

label = Label(gui, text=labelText, bg='#8f9ef5', font=("Courier", 20))
label.place(relx=0.74, rely=0.12)

listbox = Listbox(gui, font=('Helvetica', 14, 'bold'))
listbox.place(relx=0.03, rely=0.48, relwidth=0.94, relheight=0.47)

progressBar = Progressbar(gui, length=750, mode='determinate', orient=HORIZONTAL, variable=progress_var)
progressBar.place(relx=0.14, rely=0.38, relheight=0.05)

# Timeout threshold for socket operations in secs
SOCK_TIMEOUT = 10

# Obtain the name of the local host
serverName = gethostname()

# Declare the port number of the server that the client will be communicating with
serverPort = 12000

# Assign a socket to the client using the arguments for a IPV4 address (AF_INET) and UDP protocol (SOCK_DGRAM)
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Set timeout value for the socket operations
clientSocket.settimeout(SOCK_TIMEOUT)

button1.wait_variable(var1)

image = str(entryField1.get())

listbox.insert(END, 'YOU WANT TO SEND FILE: "' + image + '"')

pktList, packetizeReturn = packetizeBinary(image, 1024)

listbox.insert(END, packetizeReturn)

button2.wait_variable(var2)

imageSave = str(entryField2.get())

listbox.insert(END, 'THE FILE WILL BE SAVED AS: "' + imageSave + '"')

header = str(len(pktList)) + ' ' + imageSave

pktList.insert(0, bytearray(header, 'utf-8'))

plabelText = 'Sending file ' + image + '...'

for i in range(len(pktList)):

    # Generate a sequence number for the given package
    seq = i % 2

    # Add the sequence number and a checksum to the package
    makeRDT22(pktList[i], seq)

    # Continue resending package until matching uncorrupted ACK has been received
    while True:

        # Randomly corrupt the checksum or some packages
        out = randomCorrupt(copy(pktList[i]))

        # Send out the packet
        clientSocket.sendto(bytearray(out), (serverName, serverPort))

        listbox.insert(END, 'Packet ' + str(i) + ' has been sent')

        # max_var.set(len(pktList))
        progressBar['maximum'] = len(pktList) - 1
        progress_var.set(i)
        gui.update()
        sleep(0.05)
        proUpdate = str(i) + ' Packets sent out of ' + str(len(pktList) - 1)

        proLabel = Label(gui, text=proUpdate, bg='#8f9ef5', font=("Courier", 11))
        proLabel.place(relx=0.43, rely=0.43, relheight=0.05)

        plabel = Label(gui, text=plabelText, bg='#8f9ef5', font=("Courier", 14))
        plabel.place(relx=0.14, rely=0.34)

        # Wait until ack is receieved
        ack = clientSocket.recv(2048)

        # Validate the ack, send next packet valid, else resend current packet
        if checkRDT22(ack, seq):
            listbox.insert(END, 'Valid ACK received for packet ' + str(i))
            break

        listbox.insert(END, 'Invalid ACK received for packet ' + str(i) + ' RESENDING')

listbox.insert(END, ' ')
listbox.insert(END, 'All packets have been sent succesfully!')

gui.mainloop()
# Close the client's socket
quit()
clientSocket.close()
