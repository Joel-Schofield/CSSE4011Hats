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
mote_id = 0
datax = []
datay = []
dataz = []
highgradx = 0
highgrady = 0
highgradz = 0

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

# receive function for getting data from the zig mote
def receive():
    UDPSockReceive = socket(AF_INET6,SOCK_DGRAM)
    UDPSockReceive.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    UDPSockReceive.bind(("",4321))
    datapos = 0

    while True:
        data,addr = UDPSockReceive.recvfrom(1024)
        if not data:
            print "Client has exited!"
            break
        else:
            print "\nReceived message from "
            mote_id = unpack("B",data[0])
            print mote_id
            print "\nchecking for: " + Entryid.get()[6:]
            if(len(Entryid.get()) > 6):
                if(mote_id[0] == int((Entryid.get()[6:]))):
                
                    for temp in range(1,201,2):
                        datax.append((int)(unpack("h",data[temp:(temp + 2)])[0]) - 5)
                    
                    print datax
                    a.clear()
                    a.plot(datax)
                    canvas.draw()

                    for temp in range(201,401,2):
                        datay.append((int)(unpack("h",data[temp:(temp + 2)])[0]) )

                    print datay
                    a.plot(datay)
                    canvas.draw()

                    for temp in range(401,601,2):
                        dataz.append((int)(unpack("h",data[temp:(temp + 2)])[0]) - 125)

                    print dataz
                    a.plot(dataz)
                    canvas.draw()

                    # calculate some gradiants here
                    # highest x, y and z
                    
                    for temp in range(0,90,10):
                        
                        # x components
                        if( ((datax[temp] - datax[temp+10])/(temp)) > highgradx ):
                            highgradx = ((datax[temp] - datax[temp+10])/(temp))
                        elif( ((datax[temp] - datax[temp+10])/(temp)) < highgradx ):
                            highgradx = ((datax[temp] - datax[temp+10])/(temp))
                            
                        # y components
                        if( ((datay[temp] - datay[temp+10])/(temp)) > highgrady ):
                            highgrady = ((datay[temp] - datay[temp+10])/(temp))
                        elif( ((datay[temp] - datay[temp+10])/(temp)) < highgrady ):
                            highgrady = ((datay[temp] - datay[temp+10])/(temp))   

                        # z compoenents
                        if( ((dataz[temp] - dataz[temp+10])/(temp)) > highgradz ):
                            highgradz = ((dataz[temp] - dataz[temp+10])/(temp))
                        elif( ((dataz[temp] - dataz[temp+10])/(temp)) < highgradz ):
                            highgradz = ((dataz[temp] - dataz[temp+10])/(temp))   

                    # print the highest changes in gradiant
                    
                    print "Grad x: " + highgradx
                    print "Grad y: " + highgrady
                    print "Grad z: " + highgradz

                    del datax[:]
                    del datay[:]
                    del dataz[:]

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
