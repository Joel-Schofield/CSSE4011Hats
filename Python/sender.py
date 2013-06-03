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

# gui varables
redval = 0
greenval = 0
blueval = 0
IDS = ["fec0::3","fec0::4","fec0::5","fec0::6"]
mote_id = 0

# mote data
datax = []
datay = []
dataz = []
highgradx = 0
highgrady = 0
highgradz = 0
motenumber = 0

# game varables
mote_structs = []

# classes
class mote:
    """ initiliastion """
    def __init__(self):
        self.id = motenumber
        self.game = 0
        self.score = 0
        self.partners = []
        self.datax = []
        self.datay = []
        self.dataz = []
        self.gradx = 0
        self.grady = 0
        self.gradz = 0

    """ change the score """
    def increment_score(self, x):
        self.score += x

    """ reset the score """
    def reset_score(self):
        self.score = 0

    """ add a game to the mote """
    def add_game(self, game):
        self.game = game

    """ add another mote that is participating in the same game """
    def add_partner(self, partner):
        self.partner.append(partner)

    """ delete the accelerometer data """
    def delete_data(self):
        del self.datax[:]
        del self.datay[:]
        del self.dataz[:]

    """ decode the string received over the udp socket """
    def decode(self,socket_data):
        print "decoding"

        # mote id
        mote_id = unpack("B",socket_data[0])
        print "mote: " + (str)(mote_id)
        self.id = mote_id

        # accelerometer data
        for temp in range(1,201,2):
            self.datax.append((int)(unpack("h",socket_data[temp:(temp + 2)])[0]) )
        print self.datax

        for temp in range(201,401,2):
            self.datay.append((int)(unpack("h",socket_data[temp:(temp + 2)])[0]) )
        print self.datay

        for temp in range(401,601,2):
            self.dataz.append((int)(unpack("h",socket_data[temp:(temp + 2)])[0]) )
        print self.dataz
        
    """ draw the data on the graph this is mainly for debugging """
    def draw(self):
        a.clear()
        a.plot(self.datax)
        a.plot(self.datay)
        a.plot(self.dataz)
        canvas.draw()

    """ calculate the maximum gradiant of the data decoded """
    def calc_grad(self):
        for temp in range(0,90,10):

            # x components
            if( ((self.datax[temp] - self.datax[temp+10])/(10)) > self.gradx ):
                self.gradx = ((self.datax[temp] - self.datax[temp+10])/(10))
            elif( ((self.datax[temp] - self.datax[temp+10])/(10)) < self.gradx ):
                self.gradx = ((self.datax[temp] - self.datax[temp+10])/(10))
                
            # y components
            if( ((self.datay[temp] - self.datay[temp+10])/(10)) > self.grady ):
                self.grady = ((self.datay[temp] - self.datay[temp+10])/(10))
            elif( ((self.datay[temp] - self.datay[temp+10])/(10)) < self.grady ):
                self.grady = ((self.datay[temp] - self.datay[temp+10])/(10))   

            # z compoenents
            if( ((self.dataz[temp] - self.dataz[temp+10])/(10)) > self.gradz ):
                self.gradz = ((self.dataz[temp] - self.dataz[temp+10])/(10))
            elif( ((self.dataz[temp] - self.dataz[temp+10])/(10)) < self.gradz ):
                self.gradz = ((self.dataz[temp] - self.dataz[temp+10])/(10))   

        # print the highest changes in gradiant
        
        print "Grad x: " + self.gradx
        print "Grad y: " + self.grady
        print "Grad z: " + self.gradz


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
            mote_id = unpack("B",data[0])[0]
            print "\nReceived message from " + (str)(mote_id)

            mote_structs[mote_id].decode(data)
            mote_structs[mote_id].calc_grad()

            
                
# mainloop

# initilise the structues
motenumber = 0
for temp in range(0,32):
    mote_structs.append(mote())
    motenumber += 1        

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
