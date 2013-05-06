from socket import *
from struct import pack
from Tkinter import *
import time

# global varables
redval = 0
greenval = 0
blueval = 0
IDS = ["fec0::3","fec0::4","fec0::5","fec0::6"]

# the tk root
top = Tk()

Scaleframe = Frame(top)
Scaleframe.pack(side = TOP, fill = X)

Moteselectframe = Frame(top)
Moteselectframe.pack(side = TOP, padx = 10, pady = 10, fill = X)

Gameidselectframe = Frame(top)
Gameidselectframe.pack(side = TOP, padx = 10, pady = 10, fill = X)

Buttonframe = Frame(top)
Buttonframe.pack(side = BOTTOM, padx = 10, fill = X)


#add callbacks here
def send(): 
	#UDPSock = socket(AF_INET6,SOCK_DGRAM)
	#address = Entryid.get()
	led = pack("BBBBB",int(Scalered.get())
				   ,int(Scalegreen.get())
				   ,int(Scaleblue.get())
				   ,int(Entrygameid.get())
				   ,int(Entrygameid.get()))
	for currentid in IDS:
		time.sleep(.05)
		UDPSock = socket(AF_INET6,SOCK_DGRAM)
		UDPSock.connect((currentid,1234))
		UDPSock.send(led)

# add widget code here

# Slider Frame
Scalered = Scale(Scaleframe, from_= 0, to = 255, orient = HORIZONTAL)
Scalegreen = Scale(Scaleframe, from_ = 0, to = 255, orient = HORIZONTAL)
Scaleblue = Scale(Scaleframe, from_ = 0, to = 255, orient = HORIZONTAL)

# pack them
Scalered.pack(side = TOP, fill = X, padx = 10)
Scalegreen.pack(side = TOP, fill = X, padx = 10)
Scaleblue.pack(side = TOP, fill = X, padx = 10)

# Mote ID frame
Sendl = Label(Moteselectframe, text = "TOS__ID: ")
Entryid = Entry(Moteselectframe, bd = 5)
Entryid.insert(0,"fec0::")

# pack them
Sendl.pack(side = LEFT)
Entryid.pack(side = RIGHT)

# Game ID frame
Gameidl = Label(Gameidselectframe, text = "Game ID: ")
Entrygameid = Entry(Gameidselectframe, bd = 5)

#pack them
Gameidl.pack(side = LEFT)
Entrygameid.pack(side = RIGHT)

# Button
B = Button(Buttonframe, text ="send", command = send, width = 20)
B.pack(side = TOP, pady = 10)

# do the main loop now
top.mainloop()
