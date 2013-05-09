from socket import *

# matplotlib includes
import matplotlib
matplotlib.use("TkAgg")
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

from matplotlib.figure import Figure

from struct import pack, unpack
from Tkinter import *
from threading import Thread
import time



# global varables
redval = 0
greenval = 0
blueval = 0
IDS = ["fec0::3","fec0::4","fec0::5","fec0::6"]
datax = []
datay = []
dataz = []

#add callbacks here
def send(): 
	address = Entryid.get()
	led = pack("BBBBB",int(Scalered.get())
				   ,int(Scalegreen.get())
				   ,int(Scaleblue.get())
				   ,int(Entrygameid.get())
				   ,int(Entrygameid.get()))
	if(address == "ffff"):
		for currentid in IDS:
			time.sleep(.05)
			UDPSock = socket(AF_INET6,SOCK_DGRAM)
			UDPSock.connect((currentid,1234))
			UDPSock.send(led)
	else:
		UDPSock = socket(AF_INET6,SOCK_DGRAM)
		UDPSock.connect((address,1234))
		UDPSock.send(led)

def receive():
	UDPSockReceive = socket(AF_INET6,SOCK_DGRAM)
	UDPSockReceive.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	UDPSockReceive.bind(("",4321))

	while True:
	    data,addr = UDPSockReceive.recvfrom(1024)
	    if not data:
	        print "Client has exited!"
	        break
	    else:
	        print "\nReceived message"
	        print data
	        """
	        datax = unpack("h",data[:300])
	        print datax
	        datay = unpack("h",data[300:600])
	        print datay
	        dataz = unpack("h",data[600:900])
	        print dataz
	        """


# the tk root
top = Tk()
top.wm_title("CSSE4011 Super Awsome iGame iHats")

f = Figure(figsize=(6,3), dpi=100)
a = f.add_subplot(111)
t = arange(0.0,3.0,0.01)
s = sin(2*pi*t)

a.plot([1,2,3,4,5,6,7,8,9,10,0,4,2,8,20])

Scaleframered = Frame(top)
Scaleframered.pack(side = TOP, fill = X)

Scaleframegreen = Frame(top)
Scaleframegreen.pack(side = TOP, fill = X)

Scaleframeblue = Frame(top)
Scaleframeblue.pack(side = TOP, fill = X)

Moteselectframe = Frame(top)
Moteselectframe.pack(side = TOP, padx = 10, pady = 10, fill = X)

Gameidselectframe = Frame(top)
Gameidselectframe.pack(side = TOP, padx = 10, pady = 10, fill = X)

Graphframe = Frame(top)
Graphframe.pack(side = TOP, padx = 10, pady = 10, fill = X)

Buttonframe = Frame(top)
Buttonframe.pack(side = BOTTOM, padx = 10, fill = X)

# a tk.DrawingArea
canvas = FigureCanvasTkAgg(f, master = Graphframe)

toolbar = NavigationToolbar2TkAgg( canvas, Graphframe)

# Slider Frame
Scalered = Scale(Scaleframered, from_= 0, to = 255, orient = HORIZONTAL, )
redlable = Label(Scaleframered, text = "Red")
Scalegreen = Scale(Scaleframegreen, from_ = 0, to = 255, orient = HORIZONTAL)
greenlable = Label(Scaleframegreen, text = "Green")
Scaleblue = Scale(Scaleframeblue, from_ = 0, to = 255, orient = HORIZONTAL)
bluelable = Label(Scaleframeblue, text = "Blue")

# pack them
redlable.pack(side = LEFT, anchor = W, padx = 10)
Scalered.pack(side = LEFT, anchor = E, fill = X, padx = 10, expand = True)
greenlable.pack(side = LEFT, anchor = W, padx = 5)
Scalegreen.pack(side = LEFT, anchor = E, fill = X, padx = 10, expand = True)
bluelable.pack(side = LEFT, anchor = W, padx = 9)
Scaleblue.pack(side = LEFT, anchor = E, fill = X, padx = 10, expand = True)


# Mote ID frame
Sendl = Label(Moteselectframe, text = "TOS__ID: ")
Entryid = Entry(Moteselectframe, bd = 5)
Entryid.insert(0,"fec0::")

# pack them
Sendl.pack(side = LEFT, anchor = CENTER)
Entryid.pack(side = RIGHT, anchor = CENTER)

# Game ID frame
Gameidl = Label(Gameidselectframe, text = "Game ID: ")
Entrygameid = Entry(Gameidselectframe, bd = 5)

#pack them
Gameidl.pack(side = LEFT)
Entrygameid.pack(side = RIGHT)

canvas.show()
canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = True)

toolbar.update()
canvas._tkcanvas.pack(side = TOP, fill = BOTH, expand = True)

# Button
B = Button(Buttonframe, text ="send", command = send, width = 20)
B.pack(side = TOP, pady = 10)

# start thread
t = Thread(target=receive)
t.start()

# do the main loop now
top.mainloop()
