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
import random

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
ledtrack = []

# game varables
mote_structs = []
grad_cal_distance = 0
hat_dip_level = 0
game_ready_hats = []
game_threads = []

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
        self.gradx = 0
        self.grady = 0
        self.gradz = 0

    """ decode the string received over the udp socket """
    def decode(self,socket_data):
        print "decoding"

        # mote id
        mote_id = unpack("B",socket_data[0])
        print "mote: " + (str)(mote_id[0])
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
            if( ((self.datax[temp] - self.datax[temp+grad_cal_distance])/(grad_cal_distance)) > self.gradx ):
                self.gradx = ((self.datax[temp] - self.datax[temp+grad_cal_distance])/(grad_cal_distance))
                
            # y components
            if( ((self.datay[temp] - self.datay[temp+grad_cal_distance])/(grad_cal_distance)) > self.grady ):
                self.grady = ((self.datay[temp] - self.datay[temp+grad_cal_distance])/(grad_cal_distance))  

            # z compoenents
            if( ((self.dataz[temp] - self.dataz[temp+grad_cal_distance])/(grad_cal_distance)) > self.gradz ):
                self.gradz = ((self.dataz[temp] - self.dataz[temp+grad_cal_distance])/(grad_cal_distance))   

        # print the highest changes in gradiant
        
        print "Grad x: " + (str)(self.gradx)
        print "Grad y: " + (str)(self.grady) 
        print "Grad z: " + (str)(self.gradz)


#add callbacks here
""" send data to the motes """ 
def send(): 
    address = Entryid.get()
    global_time = 600000
    timestamp_led_combo = []
    copy_list = []

    events = 1
    datalength = 19*events

    # put header in here
    send_data = pack("IIQQ",4294967295,1,0,datalength)
    print send_data

    # make a random led track
    # format [timestamp] [led1] [led2] [led3] [led4] [led5] ....
    
    for temp2 in range (0,(datalength/19)):
        timestamp_led_combo.append(1)
        for temp in range (0,16):
            timestamp_led_combo.append(127)
        ledtrack.append(timestamp_led_combo[:])

        print "timestamp_led_combo" + (str)(timestamp_led_combo)
        # delete the combo
        del timestamp_led_combo[:]

    print ledtrack

    # pack the list
    for temp in range(0,(datalength/19)):
        print "timestamp" + (str)(ledtrack[temp][0])
        send_data += pack("I",ledtrack[temp][0])
        print pack("I",(int)(ledtrack[temp][0]))
        
        for temp2 in range(1,17):
            send_data += pack("B",(int)(ledtrack[temp][temp2]))
            print "for: [" + (str)(temp) + "][" + (str)(temp2) + "] " + send_data
                           
    print send_data
    
    # broadcast
    if(address == "ffff"):
        for currentid in IDS:
            time.sleep(.05)
            UDPSock = socket(AF_INET6,SOCK_DGRAM)
            UDPSock.connect((currentid,1234))
            UDPSock.send(send_data)
    # specific mote
    else:
        UDPSock = socket(AF_INET6,SOCK_DGRAM)
        UDPSock.connect((address,1234))
        UDPSock.send(send_data)

    del ledtrack[:]

# receive function for getting data from the zig mote
""" receive data from the motes """
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

            mote_structs[mote_id].delete_data()
            mote_structs[mote_id].decode(data)
            mote_structs[mote_id].calc_grad()
            mote_structs[mote_id].draw()

            if(int(Entrygameid.get()) == 1):
                if ((mote_structs[mote_id].gradx >= hat_dip_level) or (mote_structs[mote_id].grady >= hat_dip_level)):
                    # add it to list of game ready hats
                    # this list when there is more then 1 hat will begin a game
                    # check that it hasn't already been added to this array first
                    try:
                        # this will give i a value if it is in the list already
                        i = game_ready_hats.index(mote_structs[mote_id])
                        print "hat already ready to start game"
                    except ValueError:
                        # not in list
                        i = -1 
                        print "hat moved to ready list"
                        game_ready_hats.append(mote_structs[mote_id])

                    if(len(game_ready_hats) > 1):
                        # start game
                        # thread off
                        # should make a list of threads
                        game_thread_1 = Thread(target = game_1)
                        game_thread_1.start()
                    

""" the first game designed """
def game_1():
    # run till someone losses
    while True:
        print "running game 1 wohoooo"
        time.sleep((random.randint(0,100))/10)
                     
# mainloop

# initilise the structues
grad_cal_distance = 5
hat_dip_level = 10
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
Entrygameid.insert(0,"1")

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
