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
audiotrack = []
global_time = 0
timestamp_led_combo = []
copy_list = []

# game varables
mote_structs = []
grad_cal_distance = 0
hat_dip_level = 0
game_ready_hats = []
game_threads = []
thread_number = 0

# classes
class mote:
    """ initiliastion """
    def __init__(self):
        self.id = motenumber
        self.time = 0
        self.game = 0
        self.score = 0
        self.partners = []
        self.datax = []
        self.datay = []
        self.dataz = []
        self.gradx = 0
        self.grady = 0
        self.gradz = 0
        self.listBox_string = ""
        self.state = "Active"
        self.game_status = "Waiting"

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

        # mote time
        """
        time = unpack("Q",socket_data[1:5])
        print "time: " + (str)(mote_id[0])
        self.time = time
        """

        self.state = "Active"

        if(self.game_status == "Reconnect!"):
            self.game_status = "Waiting"

        self.time += 1

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

    def make_listBox_string(self):
        DATA_FORMAT = "{0:<14}{1:<14}{2:<10}{3:<10}"

        self.listBox_string = DATA_FORMAT.format("FEC0::" + (str)(self.id[0]),
            self.state, "Score:" + (str)(self.score), self.game_status)

        self.score += 1

        print "from make_listBox_string" + self.listBox_string

        return self.listBox_string


""" a class to hold all the running game threads """
class game_thread:
    def __init__(self,game_thread,thread_number):
        self.game_id = 0
        self.thread_id = game_thread

    def set_game_id(self,game_id):
        self.game_id = game_id

    def set_thread_id(self,thread_id):
        self.thread_id = thread_id

    def get_game_id(self):
        return self.game_id

    def get_thread_id(self):
        return self.thread_id

""" send data to the motes """ 
def send(): 
    address = Entryid.get()

    send_data = make_led_track(10,20)
    UDPSock = socket(AF_INET6,SOCK_DGRAM)
    UDPSock.connect((address,1234))
    UDPSock.send(send_data)
    send_data = make_audio_track(10,20)
    UDPSock = socket(AF_INET6,SOCK_DGRAM)
    UDPSock.connect((address,1234))
    UDPSock.send(send_data)

    # broadcast
    if(address == "ffff"):
        for currentid in IDS:
            time.sleep(.05)
            UDPSock = socket(AF_INET6,SOCK_DGRAM)
            UDPSock.connect((currentid,1234))
            UDPSock.send(send_data)
    # specific mote
    else:
        """
        UDPSock = socket(AF_INET6,SOCK_DGRAM)
        UDPSock.connect((address,1234))
        UDPSock.send(send_data)
        """
    send_data = 0

""" starting_global_time is only for testing number_of_events is important """
def make_led_track(starting_global_time,number_of_events):
    global_time = starting_global_time
    timestamp_led_combo = []
    copy_list = []
    events = number_of_events
    datalength = 19*events

    # put header in here
    send_data = pack("IIQQ",4294967295,1,0,datalength)

    # make a random led track
    # format [timestamp] [led1] [led2] [led3] [led4] [led5] ....
    for temp2 in range (0,(datalength/19)):
        timestamp_led_combo.append(global_time)
        global_time += random.randint(1,1000)
        for temp in range (0,16):
            timestamp_led_combo.append(random.randint(0,255))
        ledtrack.append(timestamp_led_combo[:])
        
        # delete the combo
        del timestamp_led_combo[:]

    # pack the list
    for temp in range(0,(datalength/19)):
        send_data += pack("I",(ledtrack[temp][0:1][0]))
        
        for temp2 in range(1,16):
            send_data += pack("B", (int)(ledtrack[temp][temp2:(temp2+1)][0]))

    hexprintout = send_data[:]

    print "LED TRACK"
    print ':'.join(x.encode('hex') for x in hexprintout)

    del ledtrack[:]
    return send_data

def make_audio_track(starting_global_time,number_of_events):
    global_time = starting_global_time
    timestamp_audio_combo = []
    copy_list = []
    audiotrack = []
    events = number_of_events
    # 4 + 2 = 6
    datalength = 6*events

    send_data = pack("IIQQ",4294967295,2,0,datalength)

    # format [timestamp] [frequency]
    for temp2 in range (0,(datalength/6)):
        timestamp_audio_combo.append(global_time)
        global_time += random.randint(1,1000)
        if(temp2 == (number_of_events - 1)):
            timestamp_audio_combo.append(0)
        else:
            timestamp_audio_combo.append(random.randint(0,20000))
        audiotrack.append(timestamp_audio_combo[:])

        # delete the combo
        del timestamp_audio_combo[:]

    # pack the list
    for temp in range(0,(datalength/6)):
        send_data += pack("I",(audiotrack[temp][0:1][0]))
        send_data += pack("H", (int)(audiotrack[temp][1:2][0]))

    hexprintout = send_data[:]

    print "AUDIO TRACK"
    print ':'.join(x.encode('hex') for x in hexprintout)

    del audiotrack
    return send_data

def listBox_processor(mote_id):
    # edit the listbox here
    # hunt through list
    current_list = []
    temp_list = []
    listbox_list = []
    add = 1 

    current_list = listBox.get(0,END)

    for x in current_list:
        for y in x.split(' '):
            if(y == ''):
                # del it
                y = ''
            else:
                temp_list.append(y[:])
        listbox_list.append(temp_list[:])
        del temp_list[:]

    count = 0
    for temp in listbox_list:
        if(temp[0] == ("FEC0::" + (str)(mote_id))):
            # already added update it
            listBox.delete(count)
            push = mote_structs[mote_id].make_listBox_string()
            listBox.insert(count,push[:])
            add = 0
            break
        else:
            add = 1
        count += 1

    if (add == 1):
        # if its new
        # find the spot to put it
        push = mote_structs[mote_id].make_listBox_string()
        count = 0
        for temp in listbox_list:
            print "checking: " + (str)(mote_id) + " against: " + (str)(temp[0][6:7])
            if(mote_id > (int)(temp[0][6:7])):
                listBox.insert(count+1, push)
            elif(mote_id < (int)(temp[0][6:7])):
                if(count == 0):
                    listBox.insert(0,push)
                else:
                    listBox.insert(count-1, push)

        if (len(listbox_list) == 0):
            listBox.insert(0,push)
        
    else:                
        add = 0
    del listbox_list[:]

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

            # process all the data here
            mote_structs[mote_id].delete_data()
            mote_structs[mote_id].decode(data)
            mote_structs[mote_id].calc_grad()
            mote_structs[mote_id].draw()

            listBox_processor(mote_id)

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
                        game_threads.append(Thread(target = game_1),thread_number)

                        # start the thread
                        game_thread_1 = Thread(target = game_1)
                        game_thread_1.start()

def activity_check():
    check_list = []
    for temp in range(0,32):
        check_list.append(temp)

    while True:
        for temp in range(0,32):
            check_list[temp] = mote_structs[temp].time

        time.sleep(13)

        for temp in range(0,32):
            if ((mote_structs[temp].time == check_list[temp])
            and (mote_structs[temp].time != 0)):
                mote_structs[temp].state = "Not Active"
                mote_structs[temp].game_status = "Reconnect!"
                listBox_processor(temp)
                    
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
thread_number = 0
motenumber = 0
for temp in range(0,32):
    mote_structs.append(mote())
    motenumber += 1        

# the tk root
top = Tk()
top.wm_title("CSSE4011 Super Awsome iGame iHats")

f = Figure(figsize=(3,2), dpi=100)
a = f.add_subplot(111)
t = arange(0.0,3.0,0.01)
s = sin(2*pi*t)

a.plot([1,2,3,4,5,6,7,8,9,10,0,4,2,8,20])

Moteselectframe = Frame(top)
Moteselectframe.pack(side = TOP, padx = 10, pady = 10, fill = X)

Gameidselectframe = Frame(top)
Gameidselectframe.pack(side = TOP, padx = 10, pady = 10, fill = X)

Scoreframe = Frame(top)
Scoreframe.pack(side = TOP, padx = 10, pady = 10, fill = X)

Graphframe = Frame(top)
Graphframe.pack(side = TOP, padx = 10, pady = 10, fill = X)

Buttonframe = Frame(top)
Buttonframe.pack(side = BOTTOM, padx = 10, fill = X)

# a tk.DrawingArea
canvas = FigureCanvasTkAgg(f, master = Graphframe)
#toolbar = NavigationToolbar2TkAgg( canvas, Graphframe)

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


# score frame
DATA_FORMAT = "{0:<14}{1:<12}{2:<16}{3:<10}"
listBox = Listbox(Scoreframe, selectmode=SINGLE, width = 50,
                       height = 10, font="Courier 10")
listBox.pack(side=LEFT,expand = True,fill = BOTH)

canvas.show()
canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = True)

#toolbar.update()
canvas._tkcanvas.pack(side = TOP, fill = BOTH, expand = True)

# Button
B = Button(Buttonframe, text ="send", command = send, width = 20)
B.pack(side = TOP, pady = 10)

# start thread
t = Thread(target=receive)
t.start()

q = Thread(target=activity_check)
q.start()

# do the main loop now
top.mainloop()
