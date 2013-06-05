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
import copy

global global_time
global_time = 0

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

def globaltimekeeper():
    global global_time
    while True:
        time.sleep(1)
        global_time += 1000

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
        self.gradx = []
        self.grady = []
        self.gradz = []
        self.listBox_string = ""
        self.state = ""
        self.game_status = "Waiting"
        self.in_game = 0

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
        del self.gradx[:]
        del self.grady[:]
        del self.gradz[:]

    """ decode the string received over the udp socket """
    def decode(self,socket_data):

        global global_time

        # mote id
        mote_id = unpack("B",socket_data[0])
        print "### mote: " + (str)(mote_id[0]) + " ###"
        self.id = mote_id

        # mote time
        time = unpack("I",socket_data[1:5])
        if(self.in_game != 1):
            self.time = time[0]
        print "time: " + (str)(self.time)

        if(self.time == 0):
            self.state = "Syncing"
        else:
            self.state = "Active"
            if (global_time == 0):
                global_time = self.time
                t = Thread(target = globaltimekeeper)
                t.start() 

        if(self.game_status == "Reconnect!"):
            self.game_status = "Waiting"

        self.time += 1

        # accelerometer data
        for temp in range(5,205,2):
            self.datax.append((int)(unpack("h",socket_data[temp:(temp + 2)])[0]) )
        #print self.datax

        for temp in range(205,405,2):
            self.datay.append((int)(unpack("h",socket_data[temp:(temp + 2)])[0]) )
        #print self.datay

        for temp in range(405,605,2):
            self.dataz.append((int)(unpack("h",socket_data[temp:(temp + 2)])[0]) )
        #print self.dataz
        
    """ draw the data on the graph this is mainly for debugging """
    def draw(self):
        a.clear()
        a.plot(self.datax)
        a.plot(self.datay)
        a.plot(self.dataz)
        canvas.draw()

    """ calculate the maximum gradiant of the data decoded """
    def calc_grad(self):
        value = 0
        grad_tuple = ()
        timestamp_grad = 0
        timestamp_grad = self.time
        for temp in range(0,(len(self.datax)-5),grad_cal_distance):
            
            # x components
            value = ((self.datax[temp] - self.datax[temp+grad_cal_distance])/(grad_cal_distance))
            if (value > hat_dip_level):
                grad_tuple = (timestamp_grad,value)
                print "gradx above limit: " + (str)(grad_tuple)
                self.gradx.append(copy.copy(grad_tuple))
                
            # y components            
            value = ((self.datay[temp] - self.datay[temp+grad_cal_distance])/(grad_cal_distance))
            if (value > hat_dip_level):
                grad_tuple = (timestamp_grad,value)
                print "grady above limit: " + (str)(grad_tuple)
                self.grady.append(copy.copy(grad_tuple))

            # z compoenents
            value = ((self.dataz[temp] - self.dataz[temp+grad_cal_distance])/(grad_cal_distance))
            if (value > hat_dip_level):
                grad_tuple = (timestamp_grad,value)
                print "gradz above limit: " + (str)(grad_tuple)
                self.gradz.append(copy.copy(grad_tuple))

            # increment timestamp
            timestamp_grad = (timestamp_grad + (250))

    def make_listBox_string(self):
        DATA_FORMAT = "{0:<9}{1:<12}{2:<14}{3:<10}"

        self.listBox_string = DATA_FORMAT.format("FEC0::" + (str)(self.id[0]),
            self.state, "Score:" + (str)(self.score), self.game_status)

        return self.listBox_string

""" get average global time """
def get_average_global_time():
    globaltime = 0
    number_of_active_motes = 0
    for temp in range(0,32):
        if (mote_structs[temp].time != 0):
            globaltime += mote_structs[temp].time
            number_of_active_motes += 1

    return (globaltime/number_of_active_motes)

""" a class to hold all the running game threads """
class game_thread:
    def __init__(self,game_thread,thread_number):
        self.game_id = 0
        self.thread_id = game_thread
        self.Thread_number = thread_number
        self.game_motes = []

    def set_game_id(self,game_id):
        self.game_id = game_id

    def set_thread_id(self,thread_id):
        self.thread_id = thread_id

    def get_game_id(self):
        return self.game_id

    def get_thread_id(self):
        return self.thread_id

"""  a class to manage all games """
class game_manager:
    def __init__(self):
        self.all_game_threads = []
        self.number_of_threads = 0

    def get_number_of_threads(self):
        return self.number_of_threads

    def append_game_thread(self,gane_thread):
        self.all_game_threads.append(game_thread[:])

""" send data to the motes """ 
def send(): 
    address = Entryid.get()

    print "the average globaltime is: " + (str)(get_average_global_time())

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
    send_data = pack("IIQQ",4294967295,1,global_time,datalength)

    # make a random led track
    # format [timestamp] [led1] [led2] [led3] [led4] [led5] ....
    for temp2 in range (0,(datalength/19)):
        timestamp_led_combo.append(global_time)
        global_time += random.randint(1,1000)
        for temp in range (0,16):
            random_colour = 0
            random_colour = random.randint(0,255)
            if(random_colour < 127):
                random_colour = 0
            else:
                random_colour = 255
            timestamp_led_combo.append(random_colour)
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
            if(mote_id > (int)(temp[0][6:7])):
                listBox.insert(count+1, push)
                break
            elif(mote_id < (int)(temp[0][6:7])):
                if(count == 0):
                    listBox.insert(0,push)
                    break
                else:
                    listBox.insert(count-1, push)
                    break

        if (len(listbox_list) == 0):
            listBox.insert(0,push)
        
    else:                
        add = 0
    del listbox_list[:]

def check_same_time_bow(hats_array):
    # take the received data chunks and detect grads in same location
    # this may prove difficult.
    
    grad_tuple_array = []
    grad_tuple = ()
    value = 0
    timestamp_grad = 0

    print "game_ready_hats: " + (str)(hats_array[0])

    # compare game_ready_hats[0] with game_ready_hats[1]
    if( (len(hats_array[0].gradx) != 0) and (len(hats_array[1].gradx) != 0) ):
        for temp in hats_array[0].gradx:
            for temp2 in hats_array[1].gradx:
                # if temp2 timestamp + 500 > temp timestamp and temp2 timestamp - 500 < temp timestamp then match 
                print "comparing " + (str)(temp[0]) + " between: " + (str)(temp2[0] + 500) + " and: " + (str)(temp2[0] - 500)
                if ( ((temp2[0] + 500) > temp[0]) and ((temp2[0] - 500)  < temp[0])):
                    # match
                    print "match"
                    return 1
    else:
        return 0


"""
    # itterate over the ready list, make a tuple of the time stamp and the grad, blocks of 5
    for blaa in game_ready_hats:
        timestamp_grad = blaa.time
        for temp in range(0,95,grad_cal_distance):
            value = (mote_structs[blaa.id[0]].datax[temp] - mote_structs[temp.id[0]].datax[temp+grad_cal_distance]) / (grad_cal_distance)
            if(value > hat_dip_level):
                grad_tuple = (timestamp_grad + (250*temp)
"""


# receive function for getting data from the zig mote
""" receive data from the motes """
def receive():
    UDPSockReceive = socket(AF_INET6,SOCK_DGRAM)
    UDPSockReceive.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    UDPSockReceive.bind(("",4321))
    datapos = 0

    game_ready_hats = []

    while True:
        data,addr = UDPSockReceive.recvfrom(1024)
        if not data:
            print "Client has exited!"
            break
        else:
            mote_id = unpack("B",data[0])[0]
            # print "\nReceived message from " + (str)(mote_id)

            # process all the data here
            if (mote_structs[mote_id].in_game != 1):
                mote_structs[mote_id].delete_data()
            mote_structs[mote_id].decode(data)
            mote_structs[mote_id].calc_grad()
            mote_structs[mote_id].draw()

            listBox_processor(mote_id)

            if(int(Entrygameid.get()) == 1):
                if(mote_structs[mote_id].game_status == "Waiting"):
                   
                    # rewrite this section........
                    # check for concurrent bows here

                    # if there is some grad changed
                    print "length of grad tuple " + (str)(len(mote_structs[mote_id].gradx))
                    if ( (((len(mote_structs[mote_id].gradx)) > 0) or ((len(mote_structs[mote_id].grady) > 0))) 
                        and mote_structs[mote_id].in_game != 1):
                        # add it to list of game ready hats
                        # this list when there is more then 1 hat will begin a game
                        # check that it hasn't already been added to this array first
                        try:
                            # this will give i a value if it is in the list already
                            i = game_ready_hats.index(mote_structs[mote_id])
                            print "hat " + (str)(mote_id) + " already ready to start game"
                            mote_structs[mote_id].game_status = "Ready"
                        except ValueError:
                            # not in list
                            i = -1 
                            print "hat " + (str)(mote_id) + " moved to ready list"
                            mote_structs[mote_id].game_status = "Ready"
                            game_ready_hats.append(mote_structs[mote_id])
                            listBox_processor(mote_id)

                        if(len(game_ready_hats) > 1):
                            print "before chekcing_bow_time " + (str)(game_ready_hats[0])
                            if (check_same_time_bow(game_ready_hats) == 1):
                                # start game
                                # thread off
                                # should make a list of threads
                                for temp in game_ready_hats:
                                    temp.game_status = "In Game:" + (str)(game_man.number_of_threads)
                                    listBox_processor(temp.id[0])
                                    mote_structs[temp.id[0]].in_game = 1


                                t = game_thread(Thread(target = game_1 , args=(game_man.number_of_threads,)) , game_man.number_of_threads )
                                game_man.number_of_threads += 1

                                # fill data
                                for temp in game_ready_hats:
                                    t.game_motes.append(copy.copy(temp))

                                # delete game ready hats
                                del game_ready_hats[:]
                                game_ready_hats = []

                                # append the game thread to the manager
                                game_man.all_game_threads.append(copy.copy(t))

                                game_man.all_game_threads[game_man.number_of_threads - 1].thread_id.start()

                                # start the game thread
                                # t.thread_id.start()
                            else:
                                # if not delete the game_ready_hats, revert status
                                for temp in game_ready_hats:
                                    mote_structs[temp.id[0]].game_status = "Waiting"
                                    listBox_processor(temp.id[0])
                                del game_ready_hats
                                game_ready_hats = []


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
def game_1(place_in_game_man):
    # run till someone losses
    global global_time
    
    random_led_track = make_led_track(global_time,20)
    random_audio_track = make_audio_track(global_time,20)
    
    print "the average globaltime is: " + (str)(get_average_global_time())

    for blaa in game_man.all_game_threads[place_in_game_man].game_motes:
        address = "fec0::" + (str)(blaa.id[0])
        
        UDPSock = socket(AF_INET6,SOCK_DGRAM)
        UDPSock.connect((address,1234))
        UDPSock.send(random_led_track)
        send_data = make_audio_track(10,20)
        UDPSock = socket(AF_INET6,SOCK_DGRAM)
        UDPSock.connect((address,1234))
        UDPSock.send(random_audio_track)
        time.sleep(0.05)

    for blaa in range(0,4):
        print "running game 1 wohoooo in thread" + (str)(place_in_game_man)
        time.sleep((random.randint(0,100))/10)

    # game end
    # change the motes back

    for blaa in game_man.all_game_threads[place_in_game_man].game_motes:
        print "motes finishing the game " + (str)(blaa.id[0])
        mote_structs[blaa.id[0]].state = "Active"
        mote_structs[blaa.id[0]].game_status = "Waiting"

    # process score
    for blaa in game_man.all_game_threads[place_in_game_man].game_motes:
        mote_structs[blaa.id[0]].score += blaa.id[0]
        mote_structs[blaa.id[0]].in_game = 0
        mote_structs[blaa.id[0]].delete_data()
        listBox_processor(blaa.id[0])
                     
# mainloop

# initilise the structues
grad_cal_distance = 5
hat_dip_level = 7
thread_number = 0
motenumber = 0
for temp in range(0,32):
    mote_structs.append(mote())
    motenumber += 1    
game_man = game_manager()    

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
